from langgraph.prebuilt import create_react_agent
from langchain_ollama import ChatOllama
from langsmith import traceable
from langchain_core.messages import SystemMessage, HumanMessage

# from src.tools.email import SendEmail, FindContactEmail, ReadEmails

# 모킹
from src.tools.email.mock import (
    MockSendEmail,  
    MockFindContactEmail,
    MockReadEmails,
)


from src.prompts import EMAIL_AGENT_PROMPT
from src.utils import print_agent_output


_email_agent = None


def get_email_agent():
    global _email_agent

    if _email_agent is None:
        model = ChatOllama(
            model="llama3.1:8b",
            temperature=0.1,
        )

        # tools = [
        #     SendEmail(),
        #     FindContactEmail(),
        #     ReadEmails(),
        # ]

        # 모킹
        tools = [
            MockSendEmail(),
            MockFindContactEmail(),
            MockReadEmails(),
        ]


        _email_agent = create_react_agent(
            model,
            tools,
        )

    return _email_agent


@traceable(run_type="llm", name="Email Agent")
def invoke_email_agent(task: str) -> str:
    email_agent = get_email_agent()

    inputs = {
        "messages": [
            SystemMessage(content=EMAIL_AGENT_PROMPT),
            HumanMessage(content=task),
        ]
    }

    output = email_agent.invoke(inputs)
    print_agent_output(output)

    return output["messages"][-1].content