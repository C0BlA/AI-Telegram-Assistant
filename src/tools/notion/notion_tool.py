from langchain.tools import BaseTool


class NotionTool(BaseTool):
    name: str = "NotionTool"
    description: str = "Mock notion tool"

    def _run(self, query: str) -> str:
        return f"Notion result for: {query}"