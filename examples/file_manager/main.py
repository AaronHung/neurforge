import asyncio
import pathlib

from neurforge.agents import SimpleAgent
from neurforge.config import ConfigLoader
from neurforge.utils import AgentsUtils, FileUtils

EXAMPLE_QUERY = (
    "整理一下當前資料夾下面的所有檔案，按照 學號-姓名 的格式重新命名。"
    "我只接受學生提交的pdf，如果不是pdf檔案，歸檔到一個資料夾裡面。"
)


config = ConfigLoader.load_agent_config("examples/file_manager")
worker_agent = SimpleAgent(config=config)


async def main():
    async with worker_agent as agent:
        result = agent.run_streamed(EXAMPLE_QUERY)
        await AgentsUtils.print_stream_events(result.stream_events())

        print(f"Final output: {result.final_output}")
        FileUtils.save_json(pathlib.Path(__file__).parent / "trajectories.json", result.to_input_list())


if __name__ == "__main__":
    asyncio.run(main())
