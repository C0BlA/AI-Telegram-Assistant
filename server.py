import asyncio
import websockets
import json
from datetime import datetime

# ===== Agent 저장소 =====
agents = {}

# ===== Manager (여기 너 코드 연결하면 됨) =====
def manager_route(task: str):
    # 간단한 라우팅 (나중에 ManagerAgent로 교체)
    if "일정" in task:
        return "Calendar Agent"
    elif "메일" in task:
        return "Email Agent"
    else:
        return None


# ===== WebSocket Handler =====
async def handler(websocket):
    agent_id = None

    try:
        async for message in websocket:
            data = json.loads(message)

            # 1. 등록
            if data["type"] == "register":
                agent_id = data["agent_name"]

                agents[agent_id] = {
                    "ws": websocket,
                    "last_seen": datetime.now(),
                    "prompt": data.get("prompt", "")
                }

                print(f"[등록] {agent_id}")

            # 2. heartbeat
            elif data["type"] == "heartbeat":
                if agent_id in agents:
                    agents[agent_id]["last_seen"] = datetime.now()

            # 3. 결과 수신
            elif data["type"] == "result":
                print(f"[응답] {agent_id}: {data['result']}")

    except Exception as e:
        print(f"[에러] {e}")

    finally:
        if agent_id and agent_id in agents:
            del agents[agent_id]
            print(f"[종료] {agent_id}")


# ===== Task 전송 =====
async def send_task(agent_name, task):
    if agent_name not in agents:
        print("Agent 없음")
        return

    ws = agents[agent_name]["ws"]

    await ws.send(json.dumps({
        "type": "task",
        "task": task
    }))


# ===== heartbeat 체크 =====
async def monitor_agents():
    while True:
        now = datetime.now()
        for name in list(agents.keys()):
            delta = (now - agents[name]["last_seen"]).seconds
            if delta > 20:
                print(f"[오프라인] {name}")
                del agents[name]
        await asyncio.sleep(10)


async def cli():
    loop = asyncio.get_event_loop()

    while True:
        print("\n=== Agents ===")
        for a in agents:
            print(f"- {a}")

        cmd = await loop.run_in_executor(None, input, ">> ")

        if cmd.startswith("send"):
            try:
                _, task = cmd.split(" ", 1)
                agent = manager_route(task)

                if not agent:
                    print("라우팅 실패")
                    continue

                await send_task(agent, task)

            except:
                print("사용법: send <task>")


# ===== 서버 실행 =====
async def main():
    async with websockets.serve(handler, "localhost", 8000):
        print("Server started")

        await asyncio.gather(
            monitor_agents(),
            cli()
        )

asyncio.run(main())