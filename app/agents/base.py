from typing import Any, Dict

class BaseAgent:
    name: str = "base"

    async def run(self, query: str) -> Dict[str, Any]:
        raise NotImplementedError