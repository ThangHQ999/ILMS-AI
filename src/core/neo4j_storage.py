import os
from lightrag.kg.neo4j_impl import Neo4JStorage
from neo4j import AsyncGraphDatabase

class CustomNeo4jStorage(Neo4JStorage):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USERNAME", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "password")
        
        self.driver = AsyncGraphDatabase.driver(uri, auth=(user, password))

    async def close(self):
        """Đóng kết nối khi hoàn tất"""
        if hasattr(self, "driver") and self.driver:
            await self.driver.close()
            
    async def upsert_nodes(self, nodes: list[dict]):
        """Lưu trữ Entity và bung các Node con (Definition, Process, Exercise, Example)"""
        if not nodes:
            return

        cypher_query = """
        UNWIND $nodes AS node
        
        // 1. Tạo/Cập nhật Node Entity chính
        MERGE (n:Entity {id: node.name})
        SET n.type = coalesce(node.type, n.type),
            n.description = coalesce(node.description, n.description),
            n.updated_at = timestamp()

        // 2. Bung mảng Definitions (Đã thêm conditions và exceptions)
        FOREACH (def IN coalesce(node.definitions, []) |
            MERGE (d:Definition {content: def.content})
            SET d.conditions = coalesce(def.conditions, []),
                d.exceptions = coalesce(def.exceptions, [])
            MERGE (n)-[:HAS_DEFINITION]->(d)
        )

        // 3. Bung mảng Processes và ProcessSteps
        FOREACH (proc IN coalesce(node.processes, []) |
            MERGE (p:Process {name: proc.name})
            SET p.description = coalesce(proc.description, "")
            MERGE (n)-[:HAS_PROCESS]->(p)
            
            // Lồng FOREACH để tạo các bước (Tạo ID duy nhất bằng cách ghép tên)
            FOREACH (step IN coalesce(proc.steps, []) |
                MERGE (s:ProcessStep {id: n.id + '_' + proc.name + '_step_' + toString(step.step_number)})
                SET s.action = step.action,
                    s.step_number = step.step_number
                MERGE (p)-[:HAS_STEP]->(s)
            )
        )

        // 4. Bung mảng Exercises
        FOREACH (ex IN coalesce(node.exercises, []) |
            MERGE (e:Exercise {title: ex.title})
            SET e.content = ex.content,
                e.difficulty = ex.difficulty
            MERGE (n)-[:HAS_EXERCISE]->(e)
        )

        // 5. Bung mảng Examples
        FOREACH (eg IN coalesce(node.examples, []) |
            MERGE (x:Example {title: eg.title})
            SET x.code_snippet = coalesce(eg.code_snippet, ""),
                x.explanation = eg.explanation
            MERGE (n)-[:HAS_EXAMPLE]->(x)
        )
        """

        if hasattr(self.driver, "session") and hasattr(self.driver, "execute_query"):
            async with self.driver.session() as session:
                await session.run(cypher_query, nodes=nodes)
        else:
            with self.driver.session() as session:
                session.run(cypher_query, nodes=nodes)

    async def upsert_edges(self, edges: list[dict]):
        """Lưu trữ KnowledgeRelationSchema giữa các Entity"""
        if not edges:
            return

        cypher_query = """
        UNWIND $edges AS edge
        
        MERGE (source:Entity {id: edge.source})
        MERGE (target:Entity {id: edge.target})
        
        MERGE (source)-[r:RELATED_TO {relation_type: edge.label}]->(target)
        SET r.description = edge.description,
            r.updated_at = timestamp()
        """

        if hasattr(self.driver, "session") and hasattr(self.driver, "execute_query"):
            async with self.driver.session() as session:
                await session.run(cypher_query, edges=edges)
        else:
            with self.driver.session() as session:
                session.run(cypher_query, edges=edges)

    async def upsert_document_context(self, doc_id: str, metadata: dict, arguments: list[dict]):
        """
        Hàm mới: Lưu trữ Siêu dữ liệu (Metadata) và Luận điểm (Arguments) 
        rồi liên kết chúng với Node gốc của tài liệu (Document).
        """
        cypher_query = """
        // Tạo Node đại diện cho tài liệu đang quét
        MERGE (doc:Document {id: $doc_id})
        SET doc.domain = $metadata.domain,
            doc.main_topic = $metadata.main_topic,
            doc.updated_at = timestamp()

        // Bung mảng Arguments (Luận điểm) liên kết với tài liệu này
        WITH doc
        UNWIND $arguments AS arg
        MERGE (a:Argument {hypothesis: arg.hypothesis})
        SET a.evidence = coalesce(arg.evidence, []),
            a.conclusion = arg.conclusion
        MERGE (doc)-[:HAS_ARGUMENT]->(a)
        """

        if hasattr(self.driver, "session") and hasattr(self.driver, "execute_query"):
            async with self.driver.session() as session:
                await session.run(cypher_query, doc_id=doc_id, metadata=metadata, arguments=arguments)
        else:
            with self.driver.session() as session:
                session.run(cypher_query, doc_id=doc_id, metadata=metadata, arguments=arguments)