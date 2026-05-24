import argparse
import pathlib

from utu.ui.webui_agents import WebUIAgents
from utu.utils.env import EnvUtils

DEFAULT_CONFIG = "simple/sensor_sage_agent"
DEFAULT_IP = EnvUtils.get_env("UTU_WEBUI_IP", "127.0.0.1")
DEFAULT_PORT = EnvUtils.get_env("UTU_WEBUI_PORT", "8848")
DEFAULT_AUTOLOAD = EnvUtils.get_env("UTU_WEBUI_AUTOLOAD", "false") == "true"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default=DEFAULT_IP)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--autoload", type=bool, default=DEFAULT_AUTOLOAD)
    args = parser.parse_args()

    data_dir = pathlib.Path(__file__).parent / "data"
    data_dir.mkdir(exist_ok=True)
    question = "目前哪台設備狀態最需要關注？請給我最新的心跳掃描摘要。"

    webui = WebUIAgents(default_config=DEFAULT_CONFIG, example_query=question)
    print(f"Server started at http://{args.ip}:{args.port}/")
    webui.launch(ip=args.ip, port=args.port, autoload=args.autoload)
