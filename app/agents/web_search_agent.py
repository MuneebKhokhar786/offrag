import httpx

class WebSearchAgent:
    name = "web_search"

    async def run(self, query: str):
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query.replace(' ', '_')}"
        async with httpx.AsyncClient() as client:
            r = await client.get(url)
            if r.status_code == 200:
                data = r.json()
                return {
                    "agent": self.name,
                    "enrichment": True,
                    "title": data.get("title"),
                    "summary": data.get("extract"),
                    "url": data.get("content_urls", {}).get("desktop", {}).get("page"),
                }
            return {"agent": self.name, "enrichment": False, "error": "not found"}