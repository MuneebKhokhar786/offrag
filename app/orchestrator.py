# app/orchestrator.py
from app.agents.search_agent import SearchAgent
from app.agents.web_search_agent import WebSearchAgent

class Orchestrator:
    def __init__(self):
        self.search_agent = SearchAgent()
        self.web_search_agent = WebSearchAgent()

    async def handle(self, query: str, k: int = 5):
        search_result = await self.search_agent.run(query, k)
        if search_result["complete"]:
            return {"query": query, "path": ["search"], "answer": search_result}
        else:
            enrichment = await self.web_search_agent.run(query)
            return {"query": query, "path": ["search", "enrichment"], "answer": enrichment}
