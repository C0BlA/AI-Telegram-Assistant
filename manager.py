import asyncio
import websockets
import json
from datetime import datetime

from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import tools_condition
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from typing import Annotated, TypedDict, Literal

from src.tools.delegate_tool import Delegate
from src.prompts.manager_agent_prompt import TELEGRAM_ASSISTANT_MANAGER_PROMPT

from src.agents.email_agent import invoke_email_agent
from src.agents.calendar_agent import invoke_calendar_agent
from src.agents.notion_agent import invoke_notion_agent

from langchain_ollama import ChatOllama


# ===== 상태 =====
class State(TypedDict):
    messages: Annotated[list, add_messages]


class ManagerAgent:
    def __init__(self):
        self.model = ChatOllama(
            model="llama3.1:8b",
            temperature=0.1
        ).bind_tools([Delegate()])

        self.app = self._build()

        # 🔥 메모리 기반 상태 저장
        self.memory = {}

    def _build(self):
        workflow = StateGraph(State)

        workflow.add_node("manager", self.call_model)
        workflow.add_node("email", self.call_email)
        workflow.add_node("calendar", self.call_calendar)
        workflow.add_node("notion", self.call_notion)

        workflow.add_edge(START, "manager")

        workflow.add_conditional_edges(
            "manager",
            self.route,
            {
                "email": "email",
                "calendar": "calendar",
                "notion": "notion",
                END: END,
            }
        )

        workflow.add_edge("email", "manager")
        workflow.add_edge("calendar", "manager")
        workflow.add_edge("notion", "manager")

        return workflow.compile()  # ✅ checkpointer 제거

    # ===== LLM 호출 =====
    def call_model(self, state):
        res = self.model.invoke(state["messages"])
        return {"messages": [res]}

    # ===== 라우팅 =====
    def route(self, state) -> Literal["email", "calendar", "notion", "__end__"]:
        route = tools_condition(state)

        if route == END:
            return END

        tool = state["messages"][-1].tool_calls[0]
        name = tool["args"]["agent_name"]

        if name == "Email Agent":
            return "email"
        elif name == "Calendar Agent":
            return "calendar"
        elif name == "Notion Agent":
            return "notion"

        raise ValueError("Invalid route")

    # ===== worker 호출 =====
    def call_email(self, state):
        return self._call_worker(state, invoke_email_agent)

    def call_calendar(self, state):
        return self._call_worker(state, invoke_calendar_agent)

    def call_notion(self, state):
        return self._call_worker(state, invoke_notion_agent)

    def _call_worker(self, state, fn):
        tool = state["messages"][-1].tool_calls[0]
        task = tool["args"]["task"]
        tool_id = tool["id"]

        res = fn(task)

        return {
            "messages": [
                ToolMessage(
                    content=res,
                    tool_call_id=tool_id,
                    name="Delegate"
                )
            ]
        }

    # ===== invoke (메모리 기반) =====
    def invoke(self, message, thread_id="default"):

        # 🔥 thread별 메모리 관리
        if thread_id not in self.memory:
            self.memory[thread_id] = [
                SystemMessage(content=TELEGRAM_ASSISTANT_MANAGER_PROMPT)
            ]

        self.memory[thread_id].append(HumanMessage(content=message))

        result = self.app.invoke({
            "messages": self.memory[thread_id]
        })

        # 마지막 응답 추가
        self.memory[thread_id].append(result["messages"][-1])

        return result["messages"][-1].content


# ===== WebSocket =====
async def run():
    agent = ManagerAgent()

    async with websockets.connect("ws://input_your_server_ip:8000") as ws:

        await ws.send(json.dumps({
            "type": "register",
            "agent_name": "Manager Agent"
        }))

        async def heartbeat():
            while True:
                await ws.send(json.dumps({
                    "type": "heartbeat",
                    "timestamp": datetime.now().isoformat()
                }))
                await asyncio.sleep(10)

        asyncio.create_task(heartbeat())

        async for msg in ws:
            data = json.loads(msg)

            if data["type"] == "task":
                task = data["task"]

                # 🔥 user 기준으로 나중에 바꿔도 됨
                result = await asyncio.to_thread(
                    agent.invoke,
                    task,
                    "default"
                )

                await ws.send(json.dumps({
                    "type": "result",
                    "result": result
                }))


if __name__ == "__main__":
    asyncio.run(run())