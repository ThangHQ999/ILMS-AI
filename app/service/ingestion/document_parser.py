"""Local source admission and parsers with honest, format-specific locators."""
import hashlib
import io
import zipfile
from pathlib import Path
from urllib.parse import unquote, urlsplit
from uuid import uuid5

from app.schema.ingestion_contracts import DocumentBlock, ParsedDocument, SourceSnapshot
from app.service.ingestion.config import IngestionSettings


class IngestionError(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def local_file_path(value: str) -> Path:
    value = value.strip().strip('"')
    if value.lower().startswith('file:'):
        parsed = urlsplit(value)
        if parsed.netloc not in ('', 'localhost'):
            raise IngestionError('UNSUPPORTED_SOURCE', 'Use a local file URI, not a remote host')
        value = unquote(parsed.path)
        if len(value) > 2 and value[0] == '/' and value[2] == ':':
            value = value[1:]
    elif '://' in value:
        raise IngestionError('UNSUPPORTED_SOURCE', 'This runner accepts local paths/file:/// only')
    path = Path(value).expanduser().resolve()
    if not path.is_file():
        raise IngestionError('SOURCE_NOT_FOUND', f'File does not exist: {path}')
    return path


def read_source(path: Path, config: IngestionSettings) -> bytes:
    with path.open('rb') as source:
        content = source.read(config.max_file_mb * 1024 * 1024 + 1)
    validate_source(path, content, config)
    return content


def validate_source(path: Path, content: bytes, config: IngestionSettings) -> None:
    extension = path.suffix.lower().lstrip('.')
    supported = {'pdf', 'docx', 'pptx', 'txt', 'md', 'py', 'js', 'ts', 'java', 'go', 'sql'}
    if extension not in config.extensions or extension not in supported:
        raise IngestionError('UNSUPPORTED_FILE', f'No enabled parser for .{extension}')
    limit = config.max_file_mb * 1024 * 1024
    if len(content) > limit:
        raise IngestionError('FILE_LIMIT_EXCEEDED', f'File exceeds {config.max_file_mb} MB')
    if not content:
        raise IngestionError('EMPTY_DOCUMENT', 'Source file is empty')
    if extension == 'pdf' and b'%PDF-' not in content[:1024]:
        raise IngestionError('INVALID_FILE_SIGNATURE', 'Expected a PDF header')
    if extension in {'docx', 'pptx'}:
        try:
            with zipfile.ZipFile(io.BytesIO(content)) as archive:
                if sum(item.file_size for item in archive.infolist()) > config.max_archive_uncompressed_mb * 1024**2:
                    raise IngestionError('FILE_LIMIT_EXCEEDED', 'Office archive expands beyond configured limit')
                expected = 'word/document.xml' if extension == 'docx' else 'ppt/presentation.xml'
                if expected not in archive.namelist():
                    raise IngestionError('INVALID_FILE_SIGNATURE', f'Missing {expected}')
        except zipfile.BadZipFile as exc:
            raise IngestionError('INVALID_FILE_SIGNATURE', 'Invalid Office archive') from exc


def parse_document(snapshot: SourceSnapshot, config: IngestionSettings, *, content: bytes) -> ParsedDocument:
    if hashlib.sha256(content).hexdigest() != snapshot.source_hash:
        raise IngestionError('SOURCE_HASH_MISMATCH', 'Snapshot was changed before parsing')
    blocks: list[DocumentBlock] = []
    warnings: list[str] = []
    characters = 0

    def add(text: str, locator: str, kind='TEXT', page=None, headings=None):
        nonlocal characters
        if not text.strip():
            return
        characters += len(text)
        if characters > config.max_parsed_characters:
            raise IngestionError('PARSED_LIMIT_EXCEEDED', 'Parsed text exceeds configured character limit')
        blocks.append(DocumentBlock(
            block_id=str(uuid5(snapshot.material_version_id, locator)), text=text,
            kind=kind, locator=locator, page_or_slide=page, heading_path=headings or [],
        ))

    extension = snapshot.extension
    if extension == '.pdf':
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(content))
        if reader.is_encrypted:
            raise IngestionError('ENCRYPTED_DOCUMENT', 'Password-protected PDF is not supported')
        if len(reader.pages) > config.max_pages:
            raise IngestionError('PAGE_LIMIT_EXCEEDED', 'PDF exceeds configured page count')
        empty_pages = []
        for number, page in enumerate(reader.pages, 1):
            text = page.extract_text() or ''
            if not text.strip():
                empty_pages.append(number)
            add(text, f'page:{number}', page=number)
        warnings.append('PDF text order, tables, formulas and embedded images require visual review; OCR is not implemented in this package.')
        if empty_pages:
            warnings.append(f'NO_TEXT_PAGE: {empty_pages}')
        adapter = 'pypdf-text'
    elif extension == '.docx':
        from docx import Document
        from docx.oxml.ns import qn
        from docx.table import Table
        from docx.text.paragraph import Paragraph
        document = Document(io.BytesIO(content))
        headings: list[str] = []
        for index, element in enumerate(document.element.body):
            if element.tag == qn('w:p'):
                paragraph = Paragraph(element, document)
                style = paragraph.style.name if paragraph.style else ''
                if style.startswith('Heading'):
                    headings = [paragraph.text]
                add(paragraph.text, f'body:{index}:paragraph', headings=headings.copy())
            elif element.tag == qn('w:tbl'):
                table = Table(element, document)
                text = '\n'.join('\t'.join(cell.text for cell in row.cells) for row in table.rows)
                add(text, f'body:{index}:table', kind='TABLE', headings=headings.copy())
        warnings.append('DOCX locators are body elements, not page numbers. Headers, footnotes, equations, images and merged-cell layout require source review.')
        adapter = 'python-docx-body'
    elif extension == '.pptx':
        from pptx import Presentation
        document = Presentation(io.BytesIO(content))
        if len(document.slides) > config.max_slides:
            raise IngestionError('SLIDE_LIMIT_EXCEEDED', 'PPTX exceeds configured slide count')

        def shapes(items, slide_number, prefix):
            for index, shape in enumerate(items):
                locator = f'{prefix}:shape:{index}'
                if shape.shape_type == 6:  # Group shape
                    shapes(shape.shapes, slide_number, locator)
                elif shape.has_table:
                    text = '\n'.join('\t'.join(cell.text for cell in row.cells) for row in shape.table.rows)
                    add(text, locator, kind='TABLE', page=slide_number)
                elif shape.has_text_frame:
                    add(shape.text, locator, page=slide_number)

        for number, slide in enumerate(document.slides, 1):
            before = len(blocks)
            shapes(slide.shapes, number, f'slide:{number}')
            if len(blocks) == before:
                warnings.append(f'Slide {number} has no extracted text; visual review required.')
        warnings.append('PPTX speaker notes, image content, charts and visual reading order are not fully extracted.')
        adapter = 'python-pptx-shapes'
    else:
        try:
            text = content.decode(config.text_encoding)
        except (UnicodeDecodeError, LookupError) as exc:
            raise IngestionError('TEXT_ENCODING_ERROR', 'Set INGESTION_TEXT_ENCODING to the actual source encoding') from exc
        if '\x00' in text:
            raise IngestionError('INVALID_TEXT', 'NUL bytes found; verify file format/encoding')
        code = extension not in {'.txt', '.md'}
        # Preserve exact Unicode characters/newlines. No whitespace sanitization.
        add(text, 'text:0', kind='CODE' if code else 'TEXT')
        adapter = 'plain-text'
    if not blocks:
        raise IngestionError('NO_EXTRACTABLE_TEXT', 'Parser produced no non-empty text blocks')
    return ParsedDocument(
        material_version_id=snapshot.material_version_id, source_hash=snapshot.source_hash,
        parser_version=config.parser_version, adapter=adapter, blocks=blocks, warnings=warnings,
    )
