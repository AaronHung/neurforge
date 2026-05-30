"""
CLI usage: python scripts/cli_chat.py --config examples/svg_generator
"""

import asyncio

from neurforge.agents import OrchestratorAgent
from neurforge.config import ConfigLoader
from neurforge.utils import AgentsUtils


async def main():
    config = ConfigLoader.load_agent_config("examples/svg_generator")
    runner = OrchestratorAgent(config)

    question = "用一張 SVG 資訊卡，介紹「番茄工作法（Pomodoro Technique）」的核心步驟與三個好處。"

    res = runner.run_streamed(question)
    await AgentsUtils.print_stream_events(res.stream_events())
    print(f"Final output: {res.final_output}")


if __name__ == "__main__":
    asyncio.run(main())
