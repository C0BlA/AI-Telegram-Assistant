from langchain.tools import BaseTool
from src.tools.json_db import load_json, save_json


class MockGetCalendarEvents(BaseTool):
    name : str = "GetCalendarEvents"
    description : str = "Mock: 캘린더 이벤트 조회"

    def _run(self, date: str = ""):
        data = load_json("calendar.json")

        events = data["events"]

        result = []
        for e in events:
            if date in e["datetime"]:
                result.append(f"{e['title']} @ {e['datetime']}")

        return "\n".join(result) if result else "일정 없음"


class MockCreateEvent(BaseTool):
    name : str = "CreateEvent"
    description : str = "Mock: 일정 생성"

    def _run(self, title: str = "", datetime: str = ""):
        data = load_json("calendar.json")

        data["events"].append({
            "title": title,
            "datetime": datetime,
            "location": ""
        })

        save_json("calendar.json", data)

        return f"{title} 일정 생성됨 (mock)"