import asyncio
import websockets
import json
from datetime import datetime

# ===== LangGraph / Ollama Agent =====
from langgraph.prebuilt import create_react_agent
from langchain_ollama import ChatOllama

from src.tools.calendar.create_event import CreateEvent
from src.tools.calendar.get_events import GetCalendarEvents
from src.tools.email.find_email import FindContactEmail
from src.prompts.calendar_agent_prompt import CALENDAR_AGENT_PROMPT


AGENT_NAME = "Calendar Agent"


# ===== Agent 생성 =====
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

    agent = create_react_agent(model, tools)
    return agent


# ===== Agent 실행 =====
def run_agent(agent, task: str) -> str:
    result = agent.invoke({
        "messages": [
            ("system", CALENDAR_AGENT_PROMPT),
            ("user", task)
        ]
    })

    return result["messages"][-1].content


# ===== WebSocket 클라이언트 =====
async def run():
    uri = "ws://localhost:8000"

    # 🔥 중요: agent는 한 번만 생성
    agent = build_agent()

    async with websockets.connect(uri) as ws:

        # 등록
        await ws.send(json.dumps({
            "type": "register",
            "agent_name": AGENT_NAME,
            "prompt": "calendar agent"
        }))

        print("[연결 완료]")

        # ===== heartbeat =====
        async def heartbeat():
            while True:
                await ws.send(json.dumps({
                    "type": "heartbeat",
                    "timestamp": datetime.now().isoformat()
                }))
                await asyncio.sleep(10)

        asyncio.create_task(heartbeat())

        # ===== 메시지 처리 =====
        async for msg in ws:
            data = json.loads(msg)

            if data["type"] == "task":
                task = data["task"]
                print(f"[작업] {task}")

                try:
                    # 🔥 blocking 방지 (중요)
                    result = await asyncio.to_thread(run_agent, agent, task)

                except Exception as e:
                    result = f"에러 발생: {str(e)}"

                await ws.send(json.dumps({
                    "type": "result",
                    "result": result
                }))


# ===== 실행 =====
if __name__ == "__main__":
    asyncio.run(run())