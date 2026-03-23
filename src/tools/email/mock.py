from langchain.tools import BaseTool
from src.tools.json_db import load_json, save_json


class MockSendEmail(BaseTool):
    name : str = "SendEmail"
    description : str = "Mock: 이메일 전송"

    def _run(self, to: str = "", content: str = ""):
        print(f"[MOCK] 이메일 전송 → {to}")
        return f"{to}에게 이메일 전송 완료 (mock)"


class MockFindContactEmail(BaseTool):
    name : str = "FindContactEmail"
    description : str = "Mock: 연락처 이메일 찾기"

    def _run(self, name: str = ""):
        data = load_json("email.json")
        return data["contacts"].get(name, "unknown@example.com")


class MockReadEmails(BaseTool):
    name : str = "ReadEmails"
    description : str = "Mock: 이메일 읽기"

    def _run(self):
        data = load_json("email.json")
        emails = data["inbox"]

        result = []
        for e in emails:
            result.append(f"From: {e['from']}, Subject: {e['subject']}")

        return "\n".join(result) if result else "받은 이메일 없음"