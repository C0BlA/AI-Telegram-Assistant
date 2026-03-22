import json
from datetime import datetime
from typing import Optional, Type
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun


class GetEventsInput(BaseModel):
    start_date: str
    end_date: str


class GetCalendarEvents(BaseTool):
    name: str = "GetCalendarEvents"
    description: str = "Get events in date range"
    args_schema: Type[BaseModel] = GetEventsInput

    def _run(
        self,
        start_date: str,
        end_date: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:

        try:
            with open("mock_calendar.json", "r") as f:
                data = json.load(f)
        except:
            return "No data"

        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)

        results = []

        for e in data:
            t = datetime.fromisoformat(e["start"])
            if start <= t <= end:
                results.append(f"{e['title']} | {e['start']}")

        return "\n".join(results) if results else "No events"