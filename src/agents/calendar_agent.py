from langgraph.prebuilt import create_react_agent
from langchain_ollama import ChatOllama

from src.tools.calendar.create_event import CreateEvent
from src.tools.calendar.get_events import GetCalendarEvents
from src.tools.email.find_email import FindContactEmail
from src.prompts.calendar_agent_prompt import CALENDAR_AGENT_PROMPT


def build_agent():

    model = ChatOllama(
        model="llama3.1:8b",
        temperature=0.1
    )

    tools = [
        CreateEvent(),
        GetCalendarEvents(),
        FindContactEmail()
    ]

    agent = create_react_agent(
        model,
        tools
    )

    return agent


def run_agent(agent, task: str):
    result = agent.invoke({
        "messages": [
            ("system", CALENDAR_AGENT_PROMPT),
            ("user", task)
        ]
    })
    return result["messages"][-1].content