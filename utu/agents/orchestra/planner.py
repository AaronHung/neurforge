import json
import pathlib
import re

from agents import RunResultStreaming

from ...agents.llm_agent import LLMAgent
from ...config import AgentConfig
from ...utils import FileUtils, get_logger
from .common import AgentInfo, CreatePlanResult, OrchestraStreamEvent, OrchestraTaskRecorder, Subtask

logger = get_logger(__name__)


class OutputParser:
    # Map full-width / "smart" quotes to ASCII so JSON parsing tolerates LLM output noise.
    _QUOTE_NORMALIZE = str.maketrans({"\u201c": '"', "\u201d": '"', "\uff02": '"', "\u201f": '"'})

    def __init__(self):
        self.analysis_pattern = r"<analysis>(.*?)</analysis>"

    def parse(self, output_text: str) -> CreatePlanResult:
        analysis = self._extract_analysis(output_text)
        plan = self._extract_plan(output_text)
        return CreatePlanResult(analysis=analysis, todo=plan)

    def _extract_analysis(self, text: str) -> str:
        match = re.search(self.analysis_pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return ""

    def _extract_plan(self, text: str) -> list[Subtask]:
        """Parse the task list from planner output, tolerant to formatting noise.

        Handles: optional <plan> tags, markdown ```json fences, extra whitespace
        (e.g. `{ "agent_name"`), key order, missing `completed`, and smart quotes.
        """
        block = self._extract_plan_block(text)
        if block is None:
            return []
        block = block.translate(self._QUOTE_NORMALIZE)
        # 1) preferred: parse as JSON (whitespace / key-order / extra-field tolerant)
        tasks = self._tasks_from_json(block)
        if not tasks:
            # 2) fallback: whitespace-tolerant regex (`completed` optional)
            tasks = self._tasks_from_regex(block)
        if not tasks:
            logger.error(f"No tasks parsed from plan. Raw planner output:\n{text}")
            raise ValueError(
                "No tasks parsed from plan: the planner output did not contain a parseable "
                f"<plan> task list. Raw planner output:\n{text}"
            )
        return tasks

    @staticmethod
    def _extract_plan_block(text: str) -> str | None:
        match = re.search(r"<plan>(.*?)</plan>", text, re.DOTALL)
        candidate = match.group(1) if match else text
        candidate = re.sub(r"```(?:json)?", "", candidate)  # strip optional code fences
        match = re.search(r"\[.*\]", candidate, re.DOTALL)  # the JSON array of tasks
        return match.group(0) if match else None

    @staticmethod
    def _tasks_from_json(block: str) -> list[Subtask]:
        try:
            data = json.loads(block)
        except (json.JSONDecodeError, TypeError):
            return []
        if not isinstance(data, list):
            return []
        tasks: list[Subtask] = []
        for item in data:
            if not isinstance(item, dict):
                continue
            name = item.get("agent_name") or item.get("name")
            task = item.get("task")
            if not (name and task):
                continue
            completed = bool(item["completed"]) if "completed" in item else None
            tasks.append(Subtask(agent_name=str(name).strip(), task=str(task).strip(), completed=completed))
        return tasks

    @staticmethod
    def _tasks_from_regex(block: str) -> list[Subtask]:
        task_pattern = (
            r'\{\s*"(?:agent_name|name)"\s*:\s*"([^"]+)"\s*,\s*"task"\s*:\s*"([^"]+)"'
            r'(?:\s*,\s*"completed"\s*:\s*(true|false))?'
        )
        tasks: list[Subtask] = []
        for agent_name, task_desc, completed_str in re.findall(task_pattern, block, re.IGNORECASE | re.DOTALL):
            completed = completed_str.lower() == "true" if completed_str else None
            tasks.append(Subtask(agent_name=agent_name.strip(), task=task_desc.strip(), completed=completed))
        return tasks


class PlannerAgent:
    def __init__(self, config: AgentConfig):
        self.config = config
        self.prompts = FileUtils.load_prompts("agents/orchestra/planner.yaml")

        self.output_parser = OutputParser()
        self._load_planner_examples()
        self._load_available_agents()

    def _load_planner_examples(self) -> None:
        examples_path = self.config.planner_config.get("examples_path", "")
        if examples_path and pathlib.Path(examples_path).exists():
            examples_path = pathlib.Path(examples_path)
        else:
            examples_path = pathlib.Path(__file__).parent / "data" / "planner_examples.json"
        with open(examples_path, encoding="utf-8") as f:
            self.planner_examples = json.load(f)

    def _load_available_agents(self) -> None:
        available_agents = []
        for info in self.config.workers_info:
            available_agents.append(AgentInfo(**info))
        self.available_agents = available_agents

    @property
    def name(self) -> str:
        return self.config.planner_config.get("name", "planner")

    async def create_plan(self, task_recorder: OrchestraTaskRecorder) -> CreatePlanResult:
        # format examples to string. example: {question, available_agents, analysis, plan}
        examples_str = []
        for example in self.planner_examples:
            examples_str.append(
                f"Question: {example['question']}\n"
                f"Available Agents: {example['available_agents']}\n\n"
                f"<analysis>{example['analysis']}</analysis>\n"
                f"<plan>{json.dumps(example['plan'], ensure_ascii=False)}</plan>\n"
            )
        examples_str = "\n".join(examples_str)
        sp = FileUtils.get_jinja_template_str(self.prompts["PLANNER_SP"]).render(planning_examples=examples_str)
        llm = LLMAgent(
            name="planner",
            instructions=sp,
            model_config=self.config.workforce_planner_model,
        )
        up = FileUtils.get_jinja_template_str(self.prompts["PLANNER_UP"]).render(
            available_agents=self._format_available_agents(self.available_agents),
            question=task_recorder.task,
            background_info=await self._get_background_info(task_recorder),
        )
        task_recorder._event_queue.put_nowait(OrchestraStreamEvent(name="plan_start"))
        res = llm.run_streamed(up)
        await self._process_streamed(res, task_recorder)
        plan = self.output_parser.parse(res.final_output)
        task_recorder._event_queue.put_nowait(OrchestraStreamEvent(name="plan", item=plan))
        return plan

    def _format_available_agents(self, agents: list[AgentInfo]) -> str:
        agents_str = []
        for agent in agents:
            agents_str.append(
                f"- {agent.name}: {agent.desc}\n  Best for: {agent.strengths}\n"
                if agent.strengths
                else f"  Weaknesses: {agent.weaknesses}\n"
                if agent.weaknesses
                else ""
            )
        return "\n".join(agents_str)

    async def _get_background_info(self, task_recorder: OrchestraTaskRecorder) -> str:
        """Get background information for the query. Leave empty by default."""
        return ""

    async def _process_streamed(self, run_result_streaming: RunResultStreaming, task_recorder: OrchestraTaskRecorder):
        async for event in run_result_streaming.stream_events():
            task_recorder._event_queue.put_nowait(event)
