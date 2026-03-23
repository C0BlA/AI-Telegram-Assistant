from langgraph.prebuilt import create_react_agent
from langchain_ollama import ChatOllama
from langsmith import traceable
from langchain_core.messages import SystemMessage, HumanMessage

# from src.tools.notion import GetMyTodoList, AddTaskInTodoList
# 모킹
from src.tools.notion.mock import (
    MockGetMyTodoList,
    MockAddTaskInTodoList
)

from src.prompts import NOTION_AGENT_PROMPT
from src.utils import print_agent_output


_notion_agent = None


def get_notion_agent():
    global _notion_agent

    if _notion_agent is None:
        model = ChatOllama(
            model="llama3.1:8b",
            temperature=0.1,
        )

        # tools = [
        #     GetMyTodoList(),
        #     AddTaskInTodoList(),
        # ]

        # 모킹
        tools = [
            MockGetMyTodoList(),
            MockAddTaskInTodoList(),
        ]

        _notion_agent = create_react_agent(
            model,
            tools,
        )

    return _notion_agent


@traceable(run_type="llm", name="Notion Agent")
def invoke_notion_agent(task: str) -> str:
    notion_agent = get_notion_agent()

    inputs = {
        "messages": [
            SystemMessage(content=NOTION_AGENT_PROMPT),
            HumanMessage(content=task),
        ]
    }

    output = notion_agent.invoke(inputs)
    print_agent_output(output)

    return output["messages"][-1].content