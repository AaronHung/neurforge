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

    question = "薈智創新 NeurForge 的 AI Agent 可以幫企業安全地自動化哪些工作流程？"

    res = runner.run_streamed(question)
    await AgentsUtils.print_stream_events(res.stream_events())
    print(f"Final output: {res.final_output}")


if __name__ == "__main__":
    asyncio.run(main())
