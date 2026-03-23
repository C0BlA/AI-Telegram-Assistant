import asyncio
import json
from datetime import datetime

import websockets

from src.agents.email_agent import invoke_email_agent
from src.agents.calendar_agent import invoke_calendar_agent
from src.agents.notion_agent import invoke_notion_agent

SERVER_URI = "ws://input_your_server_ip:8000"


AGENT_REGISTRY = {
    "1": {
        "name": "Email Agent",
        "handler": invoke_email_agent,
    },
    "2": {
        "name": "Calendar Agent",
        "handler": invoke_calendar_agent,
    },
    "3": {
        "name": "Notion Agent",
        "handler": invoke_notion_agent,
    },
}


def print_menu():
    print("\n=== Agent Launcher ===")
    print("1. Email Agent")
    print("2. Calendar Agent")
    print("3. Notion Agent")
    print("q. 종료")


async def heartbeat(ws):
    while True:
        await ws.send(json.dumps({
            "type": "heartbeat",
            "timestamp": datetime.now().isoformat()
        }))
        await asyncio.sleep(10)


async def run_agent_client(agent_name: str, agent_handler):
    print(f"[시작] {agent_name} 서버 접속 시도: {SERVER_URI}")

    async with websockets.connect(SERVER_URI) as ws:
        # 등록
        await ws.send(json.dumps({
            "type": "register",
            "agent_name": agent_name,
            "prompt": f"{agent_name.lower()}"
        }))

        print(f"[연결 완료] {agent_name}")

        hb_task = asyncio.create_task(heartbeat(ws))

        try:
            async for msg in ws:
                data = json.loads(msg)

                msg_type = data.get("type")

                if msg_type == "task":
                    task = data.get("task", "")
                    thread_id = data.get("thread_id", "default")

                    print(f"[{agent_name}] 작업 수신: {task} (thread_id={thread_id})")

                    try:
                        # invoke_*_agent는 동기 함수라 thread로 분리
                        result = await asyncio.to_thread(agent_handler, task)
                    except Exception as e:
                        result = f"{agent_name} 실행 중 에러: {e}"

                    await ws.send(json.dumps({
                        "type": "result",
                        "agent_name": agent_name,
                        "thread_id": thread_id,
                        "result": result
                    }))

                elif msg_type == "ping":
                    await ws.send(json.dumps({
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    }))

        finally:
            hb_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await hb_task


def select_agent():
    while True:
        print_menu()
        choice = input("에이전트 선택: ").strip()

        if choice.lower() == "q":
            return None

        if choice in AGENT_REGISTRY:
            return AGENT_REGISTRY[choice]

        print("잘못된 선택이다. 번호 다시 입력해라.")


async def main():
    selected = select_agent()
    if selected is None:
        print("종료")
        return

    await run_agent_client(
        agent_name=selected["name"],
        agent_handler=selected["handler"]
    )


if __name__ == "__main__":
    import contextlib
    asyncio.run(main())