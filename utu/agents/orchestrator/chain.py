import json
import re

from ...config import AgentConfig, ConfigLoader
from ...utils import AgentsUtils, FileUtils, get_logger
from ..common import DataClassWithStreamEvents
from ..llm_agent import LLMAgent
from ..simple_agent import SimpleAgent
from .common import OrchestratorStreamEvent, Plan, Recorder, Task

logger = get_logger(__name__)


class ChainPlanner:
    """Task planner that handles task decomposition."""

    def __init__(self, config: AgentConfig):
        self.config = config
        self.prompts = FileUtils.load_prompts("agents/orchestrator/chain.yaml")

        if config.orchestrator_router is None:  # set default
            config.orchestrator_router = ConfigLoader.load_agent_config("orchestrator/router")
        self.router = SimpleAgent(config=config.orchestrator_router)

        examples_path = self.config.orchestrator_config.get("examples_path", "plan_examples/chain.json")
        self.planner_examples = FileUtils.load_json_data(examples_path)
        self.additional_instructions = self.config.orchestrator_config.get("additional_instructions", "")

    async def handle_input(self, recorder: Recorder) -> None | Plan:
        # handle input. return a plan
        async with self.router as router:
            input = recorder.history_messages + [{"role": "user", "content": recorder.input}]
            res = router.run_streamed(input)
            await self._process_streamed(res, recorder)
            recorder.history_messages = res.to_input_list()  # update chat history
            # add trajectory
            recorder.trajectories.append(AgentsUtils.get_trajectory_from_agent_result(res, "router"))
        need_plan = res.final_output.strip().endswith("<plan>")  # special token!
        if need_plan:
            return await self.create_plan(recorder)

    async def create_plan(self, recorder: Recorder) -> Plan:
        """Plan tasks based on the overall task and available agents."""
        # format examples to string. example: {question, available_agents, analysis, plan}
        examples_str = []
        for example in self.planner_examples:
            examples_str.append(
                f"<question>{example['question']}</question>\n"
                f"<available_agents>{example['available_agents']}</available_agents>\n"
                f"<analysis>{example['analysis']}</analysis>\n"
                f"<plan>{json.dumps(example['plan'], ensure_ascii=False)}</plan>"
            )
        examples_str = "\n".join(examples_str)
        sp = FileUtils.get_jinja_template_str(self.prompts["orchestrator_sp"]).render(planning_examples=examples_str)
        llm = LLMAgent(
            name="orchestrator",
            instructions=sp,
            model_config=self.config.orchestrator_model,
        )
        up = FileUtils.get_jinja_template_str(self.prompts["orchestrator_up"]).render(
            additional_instructions=self.additional_instructions,
            question=recorder.input,
            available_agents=self.config.orchestrator_workers_info,
            # background_info=await self._get_background_info(recorder),
        )
        if recorder.history_plan:
            input = recorder.history_plan + [{"role": "user", "content": up}]
        else:
            input = up
        recorder._event_queue.put_nowait(OrchestratorStreamEvent(name="plan.start"))
        res = llm.run_streamed(input)
        await self._process_streamed(res, recorder)
        plan = self._parse(res.final_output, recorder)
        recorder._event_queue.put_nowait(OrchestratorStreamEvent(name="plan.done", item=plan))
        # set tasks & record trajectories
        recorder.add_plan(plan)
        recorder.trajectories.append(AgentsUtils.get_trajectory_from_agent_result(res, "orchestrator"))
        return plan

    # Map full-width / "smart" quotes to ASCII so JSON parsing tolerates LLM output noise.
    _QUOTE_NORMALIZE = str.maketrans({"\u201c": '"', "\u201d": '"', "\uff02": '"', "\u201f": '"'})

    def _parse(self, text: str, recorder: Recorder) -> Plan:
        match = re.search(r"<analysis>(.*?)</analysis>", text, re.DOTALL)
        analysis = match.group(1).strip() if match else ""

        tasks = self._parse_tasks(text)
        if not tasks:
            logger.error(f"No tasks parsed from plan. Raw planner output:\n{text}")
            raise ValueError(
                "No tasks parsed from plan: the planner output did not contain a parseable "
                f"<plan> task list. Raw planner output:\n{text}"
            )
        tasks[-1].is_last_task = True  # FIXME: polish this
        return Plan(input=recorder.input, analysis=analysis, tasks=tasks)

    def _parse_tasks(self, text: str) -> list[Task]:
        """Parse the task list from planner output, tolerant to formatting noise.

        Handles: optional <plan> tags, markdown ```json fences, extra whitespace
        (e.g. `{ "name"`), key order, extra fields, and full-width/smart quotes.
        """
        block = self._extract_plan_block(text)
        if block is None:
            return []
        block = block.translate(self._QUOTE_NORMALIZE)
        # 1) preferred: parse as JSON (whitespace / key-order / extra-field tolerant)
        tasks = self._tasks_from_json(block)
        if tasks:
            return tasks
        # 2) fallback: whitespace-tolerant regex (also accepts `agent_name` key)
        return self._tasks_from_regex(block)

    @staticmethod
    def _extract_plan_block(text: str) -> str | None:
        # prefer an explicit <plan>...</plan> block; otherwise scan the whole text
        match = re.search(r"<plan>(.*?)</plan>", text, re.DOTALL)
        candidate = match.group(1) if match else text
        candidate = re.sub(r"```(?:json)?", "", candidate)  # strip optional code fences
        match = re.search(r"\[.*\]", candidate, re.DOTALL)  # the JSON array of tasks
        return match.group(0) if match else None

    @staticmethod
    def _tasks_from_json(block: str) -> list[Task]:
        try:
            data = json.loads(block)
        except (json.JSONDecodeError, TypeError):
            return []
        if not isinstance(data, list):
            return []
        tasks: list[Task] = []
        for item in data:
            if not isinstance(item, dict):
                continue
            name = item.get("name") or item.get("agent_name")
            task = item.get("task")
            if name and task:
                tasks.append(Task(agent_name=str(name).strip(), task=str(task).strip()))
        return tasks

    @staticmethod
    def _tasks_from_regex(block: str) -> list[Task]:
        task_pattern = r'\{\s*"(?:name|agent_name)"\s*:\s*"([^"]+)"\s*,\s*"task"\s*:\s*"([^"]+)"'
        tasks: list[Task] = []
        for agent_name, task_desc in re.findall(task_pattern, block, re.IGNORECASE | re.DOTALL):
            tasks.append(Task(agent_name=agent_name.strip(), task=task_desc.strip()))
        return tasks

    async def get_next_task(self, recorder: Recorder) -> Task | None:
        """Get the next task to be executed."""
        if not recorder.tasks:
            raise ValueError("No tasks available. Please create a plan first.")
        if recorder.current_task_id >= len(recorder.tasks):
            return None
        task = recorder.tasks[recorder.current_task_id]
        recorder.current_task_id += 1
        return task

    async def _process_streamed(self, res: DataClassWithStreamEvents, recorder: Recorder):
        async for event in res.stream_events():
            recorder._event_queue.put_nowait(event)
