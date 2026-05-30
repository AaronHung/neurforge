"""[WIP] refactoring!"""

import argparse
import pathlib

from neurforge.ui.webui_agents import WebUIAgents
from neurforge.utils.env import EnvUtils

DEFAULT_CONFIG = "simple/base.yaml"
DEFAULT_IP = EnvUtils.get_env("UTU_WEBUI_IP", "127.0.0.1")
DEFAULT_PORT = EnvUtils.get_env("UTU_WEBUI_PORT", "8848")
DEFAULT_AUTOLOAD = EnvUtils.get_env("UTU_WEBUI_AUTOLOAD", "false") == "true"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default=DEFAULT_IP)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--autoload", type=bool, default=DEFAULT_AUTOLOAD)
    args = parser.parse_args()

    # Run the agent with a sample question
    # data from https://www.kaggle.com/datasets/joannanplkrk/its-raining-cats

    fn = pathlib.Path(__file__).parent / "demo_data_cat_breeds_clean.csv"
    assert fn.exists(), f"File {fn} does not exist."
    question = f"請分析位於`{fn}`的貓品種資料，提取有價值的資訊。"

    webui = WebUIAgents(default_config="examples/data_analysis", example_query=question)
    print(f"Server started at http://{args.ip}:{args.port}/")
    webui.launch(ip=args.ip, port=args.port, autoload=args.autoload)


if __name__ == "__main__":
    main()
