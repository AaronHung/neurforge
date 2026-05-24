"""
CLI usage:
    python examples/case_detective/main.py
"""
import asyncio

from utu.agents import SimpleAgent
from utu.config import ConfigLoader


async def main():
    config = ConfigLoader.load_agent_config("simple/case_detective_agent")
    print("=" * 60)
    print("案件偵探 — NeurForge 電信客服分析助理")
    print("輸入 exit / quit / q 離開")
    print("=" * 60)
    async with SimpleAgent(config=config) as agent:
        while True:
            try:
                q = input("\n> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n再見！")
                break
            if not q:
                continue
            if q.lower() in ("exit", "quit", "q"):
                print("再見！")
                break
            res = await agent.chat(q)
            print(f"\n{res.final_output}")


if __name__ == "__main__":
    asyncio.run(main())
