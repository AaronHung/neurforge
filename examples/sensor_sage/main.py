"""
CLI usage:
    python examples/sensor_sage/main.py
"""
import asyncio

from neurforge.agents import SimpleAgent
from neurforge.config import ConfigLoader


async def main():
    config = ConfigLoader.load_agent_config("simple/sensor_sage_agent")
    print("=" * 60)
    print("機況先知 — NeurForge 設備健康監控 PdM 助理")
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
