from langchain.tools import BaseTool
from src.tools.json_db import load_json, save_json


class MockGetMyTodoList(BaseTool):
    name : str = "GetMyTodoList"
    description : str = "Mock: 내 할 일 목록 가져오기"
    def _run(self):
        data = load_json("notion.json")
        todos = data["todos"]

        result = []
        for t in todos:
            status = "✅" if t["done"] else "❌"
            result.append(f"{status} {t['task']}")

        return "\n".join(result) if result else "할 일 없음"


class MockAddTaskInTodoList(BaseTool):
    name : str = "AddTaskInTodoList"
    description : str = "Mock: 할 일 추가"

    def _run(self, task: str = ""):
        data = load_json("notion.json")

        data["todos"].append({
            "task": task,
            "done": False
        })

        save_json("notion.json", data)

        return f"{task} 추가됨 (mock)"