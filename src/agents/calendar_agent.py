from langgraph.prebuilt import create_react_agent
from langchain_ollama import ChatOllama
from langsmith import traceable
from langchain_core.messages import SystemMessage, HumanMessage

# from src.tools.calendar import CreateEvent, GetCalendarEvents
# from src.tools.email import FindContactEmail

# 모킹
from src.tools.calendar.mock import (
    MockCreateEvent,
    MockGetCalendarEvents,
)
from src.tools.email.mock import MockFindContactEmail

from src.prompts import CALENDAR_AGENT_PROMPT
from src.utils import print_agent_output


_calendar_agent = None


def get_calendar_agent():
    global _calendar_agent

    if _calendar_agent is None:
        model = ChatOllama(
            model="llama3.1:8b",
            temperature=0.1,
        )

        # tools = [
        #     CreateEvent(),
        #     GetCalendarEvents(),
        #     FindContactEmail(),
        # ]

        tools = [
            MockCreateEvent(),
            MockGetCalendarEvents(),
            MockFindContactEmail(),
        ]
        

        _calendar_agent = create_react_agent(
            model,
            tools,
        )

    return _calendar_agent


@traceable(run_type="llm", name="Calendar Agent")
def invoke_calendar_agent(task: str) -> str:
    calendar_agent = get_calendar_agent()

    inputs = {
        "messages": [
            SystemMessage(content=CALENDAR_AGENT_PROMPT),
            HumanMessage(content=task),
        ]
    }

    output = calendar_agent.invoke(inputs)
    print_agent_output(output)

    return output["messages"][-1].content