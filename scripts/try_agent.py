"""Repeatable agent trial harness (for teaching / documentation).

Runs ONE agent on ONE question non-interactively, prints a structured record,
and optionally appends a markdown record block to a file.

Usage:
    uv run --env-file .env python scripts/try_agent.py \
        --config simple/sensor_sage_agent \
        --question "做一次全廠健康巡檢，挑最嚴重的設備分析並給建議。" \
        --out docs/pgm-docs/agent_trials.zh-TW.md

Notes:
    - Supports SimpleAgent (records tool calls) and OrchestratorAgent (records plan).
    - Read-only w.r.t. your configs; only writes the --out markdown file if given.
"""

import argparse
import asyncio
import time

from neurforge.agents import OrchestratorAgent, SimpleAgent, get_agent
from neurforge.config import ConfigLoader


def _extract_tool_calls(run_result) -> list[str]:
    """Pull (tool_name, short_args) pairs from a SimpleAgent RunResult."""
    calls = []
    for item in getattr(run_result, "new_items", []) or []:
        if item.__class__.__name__ != "ToolCallItem":
            continue
        raw = getattr(item, "raw_item", None)
        name = getattr(raw, "name", "?")
        args = getattr(raw, "arguments", "") or ""
        args = args.replace("\n", " ")
        if len(args) > 120:
            args = args[:120] + "..."
        calls.append(f"{name}({args})")
    return calls


async def run_simple(config, question: str) -> dict:
    async with SimpleAgent(config=config) as agent:
        t0 = time.time()
        rec = await agent.run(question, log_to_db=False)
        dt = time.time() - t0
    run_result = rec.get_run_result()
    return {
        "type": "simple",
        "elapsed": round(dt, 1),
        "steps": _extract_tool_calls(run_result),
        "final": rec.final_output or "",
    }


async def run_orchestrator(config, question: str) -> dict:
    agent = OrchestratorAgent(config)
    t0 = time.time()
    rec = await agent.run(question)
    dt = time.time() - t0
    steps = [f"{t.agent_name}{' [last]' if t.is_last_task else ''}" for t in (rec.tasks or [])]
    return {
        "type": "orchestrator",
        "elapsed": round(dt, 1),
        "steps": steps,
        "final": rec.final_output or "",
    }


def _record_block(config_name: str, question: str, r: dict) -> str:
    steps_label = "工具呼叫" if r["type"] == "simple" else "計畫 (plan)"
    steps = "\n".join(f"  {i + 1}. {s}" for i, s in enumerate(r["steps"])) or "  (無)"
    return (
        f"### Agent：`{config_name}`\n"
        f"- type：{r['type']}\n"
        f"- 啟動方式：`uv run --env-file .env python scripts/try_agent.py --config {config_name} --question \"...\"`\n"
        f"- 測試問題：{question}\n"
        f"- 執行時間：{r['elapsed']} 秒\n"
        f"- {steps_label}：\n{steps}\n"
        f"- 最終輸出長度：{len(r['final'])} 字元\n"
        f"- 是否正常產出：{'是' if r['final'].strip() else '否'}\n"
        f"- 最終輸出：\n\n```text\n{r['final'].strip()}\n```\n"
    )


async def main():
    p = argparse.ArgumentParser()
    p.add_argument("--config", required=True, help="e.g. simple/sensor_sage_agent")
    p.add_argument("--question", required=True)
    p.add_argument("--out", default=None, help="append a markdown record block to this file")
    args = p.parse_args()

    config = ConfigLoader.load_agent_config(args.config)
    agent = get_agent(config=config)
    if isinstance(agent, OrchestratorAgent):
        r = await run_orchestrator(config, args.question)
    elif isinstance(agent, SimpleAgent):
        r = await run_simple(config, args.question)
    else:
        raise SystemExit(f"Unsupported agent type: {type(agent).__name__}")

    print("=" * 70)
    print("CONFIG  :", args.config)
    print("TYPE    :", r["type"])
    print("ELAPSED :", r["elapsed"], "s")
    print("STEPS   :", r["steps"])
    print("FIN_LEN :", len(r["final"]))
    print("-" * 70)
    print(r["final"])
    print("=" * 70)

    if args.out:
        block = _record_block(args.config, args.question, r)
        with open(args.out, "a", encoding="utf-8") as f:
            f.write("\n" + block + "\n")
        print(f"[recorded] appended to {args.out}")


if __name__ == "__main__":
    asyncio.run(main())
