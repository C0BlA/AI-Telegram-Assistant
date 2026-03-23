from typing import Optional, Type

from langchain_core.callbacks import CallbackManagerForToolRun
from langsmith import traceable
from pydantic import BaseModel, Field
from langchain.tools import BaseTool


class DelegateInput(BaseModel):
    agent_name: str = Field(description="위임할 하위 에이전트 이름")
    task: str = Field(description="하위 에이전트에게 전달할 작업")


class Delegate(BaseTool):
    name: str = "Delegate"
    description: str = (
        "Use this tool to delegate a task to one of the subagents. "
        "Valid agent names: Email Agent, Calendar Agent, Notion Agent."
    )
    args_schema: Type[BaseModel] = DelegateInput

    def delegate(self, agent_name: str, task: str) -> str:
        """
        실제 에이전트를 호출하지 않고,
        매니저가 라우팅할 수 있도록 위임 정보만 남긴다.
        """
        print(f"[Delegate] agent={agent_name}, task={task}")
        return f"Task delegated to {agent_name}: {task}"

    @traceable(run_type="tool", name="Delegate")
    def _run(
        self,
        agent_name: str,
        task: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        return self.delegate(agent_name, task)