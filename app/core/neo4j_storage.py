import os
from neo4j import AsyncGraphDatabase

class CustomNeo4jStorage():
    def __init__(self):
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USERNAME", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "password")
        
        self.driver = AsyncGraphDatabase.driver(uri, auth=(user, password))

    async def close(self):
        """Đóng kết nối khi hoàn tất"""
        if hasattr(self, "driver") and self.driver:
            await self.driver.close()
            
    async def _run_query(self, query: str, parameters: dict):
        """Hàm hỗ trợ chạy Cypher query để tối ưu code"""
        if hasattr(self.driver, "session") and hasattr(self.driver, "execute_query"):
            async with self.driver.session() as session:
                await session.run(query, **parameters)
        else:
            with self.driver.session() as session:
                session.run(query, **parameters)

    async def upsert_nodes(self, nodes: list[dict]):
        """Lưu trữ Entity và bung toàn bộ các Node con (Definition, Process, Exercise, Example) từ cấu trúc lồng nhau"""
        
        if not nodes:
            return
            
        cypher_nodes = """
        UNWIND $nodes AS node
        
        // Tạo Entity gốc
        MERGE (n:Entity {id: node.name})
        SET n.type = coalesce(node.type, n.type),
            n.description = coalesce(node.description, n.description),
            n.updated_at = timestamp()

        // Xử lý Definition
        WITH node, n, 
             CASE WHEN node.definition IS NOT NULL THEN [node.definition] ELSE [] END as def_array
        FOREACH (def IN def_array |
            MERGE (d:Definition {id: n.id + '_definition'})
            SET d.content = def.content,              
                d.conditions = coalesce(def.conditions, []),
                d.exceptions = coalesce(def.exceptions, [])
            MERGE (n)-[:HAS_DEFINITION]->(d)
        )

        // Xử lý Processes và ProcessSteps
        FOREACH (proc IN coalesce(node.processes, []) |
            // ĐÃ SỬA LỖI: Thêm proc.name vào ID để tránh ghi đè nếu có nhiều Process
            MERGE (p:Process {id: n.id + '_' + proc.name + '_process'})
            SET p.name = proc.name,
                p.description = coalesce(proc.description, "")
            MERGE (n)-[:HAS_PROCESS]->(p)
            
            FOREACH (step IN coalesce(proc.steps, []) |
                MERGE (s:ProcessStep {id: n.id + '_' + proc.name + '_step_' + toString(step.step_number)})
                SET s.action = step.action,
                    s.step_number = step.step_number
                MERGE (p)-[:HAS_STEP]->(s)
            )
        )
        
        // Xử lý Exercises
        FOREACH (ex IN coalesce(node.exercises, []) |
            MERGE (e:Exercise {id: n.id + '_' + ex.title})
            SET e.title = ex.title,
                e.content = ex.content,
                e.difficulty = ex.difficulty
            MERGE (n)-[:HAS_EXERCISE]->(e)
        )

        // Xử lý Examples
        FOREACH (eg IN coalesce(node.examples, []) |
            MERGE (x:Example {id: n.id + '_' + eg.title})
            SET x.title = eg.title,
                x.code_snippet = coalesce(eg.code_snippet, ""),
                x.explanation = eg.explanation
            MERGE (n)-[:HAS_EXAMPLE]->(x)
        )
        """
        await self._run_query(cypher_nodes, {"nodes": nodes})

    async def upsert_edges(self, edges: list[dict]):
        """Lưu trữ KnowledgeRelationSchema giữa các Entity"""
        if not edges:
            return

        cypher_query = """
        UNWIND $edges AS edge
        
        MERGE (source:Entity {id: edge.source})
        MERGE (target:Entity {id: edge.target})
        
        // Đảm bảo Neo4j Server của bạn đã cài plugin APOC để chạy được hàm này
        CALL apoc.merge.relationship(
            source, 
            coalesce(edge.label, 'RELATED_TO'), 
            {}, 
            {description: coalesce(edge.description, ''), updated_at: timestamp()}, 
            target,
            {description: coalesce(edge.description, ''), updated_at: timestamp()}
        ) 
        YIELD rel
        RETURN count(rel)
        """
        await self._run_query(cypher_query, {"edges": edges})

    async def upsert_document_context(self, doc_id: str, metadata: dict, arguments: list[dict]):
        """Lưu trữ Siêu dữ liệu (Metadata) và Luận điểm (Arguments)"""
        cypher_query = """
        MERGE (doc:Document {id: $doc_id})
        SET doc.domain = $metadata.domain,
            doc.main_topic = $metadata.main_topic,
            doc.updated_at = timestamp()

        WITH doc
        UNWIND $arguments AS arg
        // Lưu ý: Có thể arg.hypothesis sẽ bị trùng giữa các tài liệu. Nên thêm doc.id vào ID để tránh ghi đè
        MERGE (a:Argument {id: doc.id + '_' + left(arg.hypothesis, 30)})
        SET a.hypothesis = arg.hypothesis,
            a.evidence = coalesce(arg.evidence, []),
            a.conclusion = arg.conclusion
        MERGE (doc)-[:HAS_ARGUMENT]->(a)
        """
        await self._run_query(cypher_query, {"doc_id": doc_id, "metadata": metadata, "arguments": arguments})