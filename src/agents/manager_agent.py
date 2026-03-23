from langgraph.prebuilt import create_react_agent
from langchain_ollama import ChatOllama
from langsmith import traceable

# from src.tools.calendar import CreateEvent, GetCalendarEvents
# from src.tools.email import FindContactEmail
from src.tools.calendar.mock import (
    MockCreateEvent,
    MockGetCalendarEvents,
)
from src.tools.email.mock import MockFindContactEmail

from src.prompts import CALENDAR_AGENT_PROMPT
from src.utils import print_agent_output


def build_calendar_agent():
    model = ChatOllama(
        model="llama3.1:8b",
        temperature=0.1,
    )

    tools = [
        CreateEvent(),
        GetCalendarEvents(),
        FindContactEmail(),
    ]

    agent = create_react_agent(
        model,
        tools,
        state_modifier=CALENDAR_AGENT_PROMPT
    )
    return agent


# 전역 1회 생성
calendar_agent = build_calendar_agent()


@traceable(run_type="llm", name="Calendar Agent")
def invoke_calendar_agent(task: str) -> str:
    inputs = {
        "messages": [
            ("user", task)
        ]
    }

    output = calendar_agent.invoke(inputs)
    print_agent_output(output)

    return output["messages"][-1].content