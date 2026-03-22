from src.agents.calendar_agent import build_agent, run_agent

agent = build_agent()

while True:
    q = input(">> ")
    if q == "exit":
        break

    res = run_agent(agent, q)
    print("\n[AI]")
    print(res)
    print()