"""
CLI usage:
    python examples/industrial_qa/main.py
"""
import asyncio

from utu.agents import SimpleAgent
from utu.config import ConfigLoader
from utu.utils import AgentsUtils


async def main():
    config = ConfigLoader.load_agent_config("simple/industrial_qa_agent")
    async with SimpleAgent(config=config) as agent:
        questions = [
            "EQ-002 攪拌機最近有什麼異常紀錄？目前工單狀態如何？",
        ]
        for q in questions:
            print(f"\n{'='*60}\n問：{q}\n{'='*60}")
            res = await agent.chat(q)
            print(f"答：{res}")


if __name__ == "__main__":
    asyncio.run(main())
