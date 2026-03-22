import json
from typing import Optional, Type
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun


class CreateEventInput(BaseModel):
    title: str
    description: str
    start_time: str


class CreateEvent(BaseTool):
    name: str = "CreateEvent"
    description: str = "Create a new event"
    args_schema: Type[BaseModel] = CreateEventInput

    def _run(
        self,
        title: str,
        description: str,
        start_time: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:

        try:
            with open("mock_calendar.json", "r") as f:
                data = json.load(f)
        except:
            data = []

        data.append({
            "title": title,
            "description": description,
            "start": start_time
        })

        with open("mock_calendar.json", "w") as f:
            json.dump(data, f, indent=2)

        return f"Created: {title}"