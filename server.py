import asyncio
import websockets
import json
from datetime import datetime
from rich.live import Live
from rich.table import Table
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text

agents = {}
logs = []

def add_log(msg):
    logs.append(f"{datetime.now().strftime('%H:%M:%S')} | {msg}")
    if len(logs) > 30:
        logs.pop(0)

# ===== UI =====
def render_agents():
    table = Table(expand=True)
    table.add_column("Name")
    table.add_column("IP")
    table.add_column("Port")
    table.add_column("Latency")
    table.add_column("Status")

    for name, info in agents.items():
        latency = info.get("latency", 0)

        color = "green" if latency < 20 else "yellow" if latency < 50 else "red"

        status = "ACTIVE"
        if (datetime.now() - info["last_seen"]).seconds > 15:
            status = "[red]DEAD[/red]"

        table.add_row(
            name,
            info["ip"],
            str(info["port"]),
            f"[{color}]{latency} ms[/]",
            status
        )

    return Panel(table, title="Agent Monitor")


def render_logs():
    return Panel("\n".join(logs), title="Logs")


def build_layout():
    layout = Layout()
    layout.split_column(
        Layout(render_agents(), size=12),
        Layout(render_logs())
    )
    return layout

# ===== WebSocket =====
async def handler(websocket):
    agent_id = None

    try:
        async for message in websocket:
            data = json.loads(message)

            if data["type"] == "register":
                agent_id = data["agent_name"]

                addr = websocket.remote_address
                if isinstance(addr, tuple):
                    ip = addr[0] if len(addr) > 0 else "unknown"
                    port = addr[1] if len(addr) > 1 else "unknown"
                else:
                    ip, port = "unknown", "unknown"

                agents[agent_id] = {
                    "ws": websocket,
                    "ip": ip,
                    "port": port,
                    "last_seen": datetime.now(),
                    "latency": 0
                }

                add_log(f"[등록] {agent_id}")

            elif data["type"] == "heartbeat":
                now = datetime.now()
                sent = datetime.fromisoformat(data["timestamp"])
                latency = int((now - sent).total_seconds() * 1000)

                agents[agent_id]["last_seen"] = now
                agents[agent_id]["latency"] = latency

            elif data["type"] == "result":
                add_log(f"[응답] {agent_id}: {data['result']}")

    except Exception as e:
        add_log(f"[에러] {e}")

    finally:
        if agent_id and agent_id in agents:
            del agents[agent_id]
            add_log(f"[종료] {agent_id}")

# ===== Manager에게만 전달 =====
async def send_to_manager(task):
    if "Manager Agent" not in agents:
        add_log("Manager 없음")
        return

    ws = agents["Manager Agent"]["ws"]

    await ws.send(json.dumps({
        "type": "task",
        "task": task
    }))

# ===== UI 루프 =====
async def ui_loop():
    with Live(build_layout(), refresh_per_second=4, screen=False) as live:
        while True:
            live.update(build_layout())
            await asyncio.sleep(0.3)

# ===== 입력 =====
async def input_loop():
    loop = asyncio.get_event_loop()

    while True:
        cmd = await loop.run_in_executor(None, input)

        add_log(f"[명령] {cmd}")

        if cmd.startswith("send"):
            try:
                _, task = cmd.split(" ", 1)
                await send_to_manager(task)
            except:
                add_log("사용법: send <task>")

# ===== 실행 =====
async def main():
    async with websockets.serve(handler, "0.0.0.0", 8000):
        print("Server started")

        await asyncio.gather(
            ui_loop(),
            input_loop()
        )

if __name__ == "__main__":
    asyncio.run(main())