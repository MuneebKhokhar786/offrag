from .base import BaseAgent
from app.services.search_service import run_search

class SearchAgent(BaseAgent):
    name = "search"

    async def run(self, query: str, k: int = 5):
        result = await run_search(query, k)
        return {"agent": self.name, **result}