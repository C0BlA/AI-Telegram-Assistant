from langchain.tools import BaseTool


class FindContactEmail(BaseTool):
    name: str = "FindContactEmail"
    description: str = "Mock email lookup"

    def _run(self, name: str) -> str:
        return f"{name.lower()}@example.com"