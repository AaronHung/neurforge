# SWE-bench Evaluation

SWE-bench 評測流程：agent 在獨立 Docker 沙箱中修復真實 GitHub issue，提取 patch，離線執行測試判定是否解決。

## Quick Start

```bash
# 1. 匯入資料集
python scripts/data/process_swe_bench.py --subset verified --split test

# 2. Rollout（agent 在沙箱中修 bug + 提取 patch）
python scripts/run_eval.py --config_name swe_bench --exp_id swe_bench_verified-test01

# 3. 匯出 patch
python scripts/data/export_swe_bench_patches.py --exp_id swe_bench_verified-test01

# 4. 離線評測（需要 Docker 環境）
python -m swebench.harness.run_evaluation \
  --dataset_name princeton-nlp/SWE-bench_Verified \
  --predictions_path patches.jsonl \
  --max_workers 4 \
  --run_id swe_bench_verified-test01
```

## 配置檔案

### 環境配置 `configs/env/swerex.yaml`

定義 AGS 沙箱引數：映象、資源規格、SWE-ReX 埠、儲存掛載等。

```yaml
name: swerex
config:
  deployment_type: ags          # "ags" 或 "remote"
  image: ${oc.env:AGS_SANDBOXTOOL_IMAGE}  # SWE-bench 評測時會被 per-instance 覆蓋
  cpu: "2"
  memory: "4Gi"
  timeout: "2h"
  workspace: /                  # agent 工作目錄，評測時覆蓋為 /testbed
  bash_timeout: 120             # 單條命令超時（秒）
```

關鍵點：`image` 和 `workspace` 在評測時由 `SWEBenchmark.rollout_one()` 按 instance 覆蓋。

### Agent 配置 `configs/agents/swe/swe_bench.yaml`

```yaml
defaults:
  - /model/base@model
  - /env/swerex@env

agent:
  name: swe
  instructions: |
    You are a skilled software engineer...

env:
  name: swerex
  config:
    workspace: /repo
```

Agent 使用 SWERexEnv 提供的工具（bash, read_file, write_file, edit_file），無需額外配置 toolkits。

### 評測配置 `configs/eval/swe_bench.yaml`

```yaml
defaults:
  - /agents/swe/swe_bench@agent

exp_id: "swe_bench_verified"
data:
  dataset: "SWEBench_Verified"
concurrency: 3
```

## 程式碼實現

### SWERexEnv (`utu/env/swerex_env.py`)

AGS 沙箱環境，封裝 SWE-ReX runtime。

```
SWERexEnv
├── build()          # 啟動 AGS 沙箱 → 連線 runtime → 建立 bash session
│   ├── _build_ags()     # TencentAGSDeployment
│   └── _build_remote()  # RemoteDeployment（除錯用）
├── get_tools()      # 返回 [bash, read_file, write_file, edit_file]
├── cleanup()        # 停止沙箱，釋放資源
└── _run_bash() / _read_file() / _write_file() / _edit_file()
```

設計要點：
- **Post-startup 自動停用 pager**：`export GIT_PAGER=cat PAGER=cat`，避免 git 命令在 pexpect 偽終端中阻塞
- **工具獨立提供**：透過 `get_tools()` 暴露，不依賴框架的 toolkit 機制
- **_MAX_OUTPUT_CHARS = 50,000**：工具輸出截斷上限

### SWEBenchmark (`utu/eval/benchmarks/swe_benchmark.py`)

繼承 `BaseBenchmark`，override `rollout_one()` 實現 per-instance 沙箱生命週期。

```
rollout_one(sample):
  1. agent_config = self.config.agent.model_copy(deep=True)   # 深複製，併發安全
  2. agent_config.env.config["image"] = sample.meta["image_name"]
     agent_config.env.config["workspace"] = "/testbed"
  3. agent = get_agent(agent_config)
     await agent.build(trace_id)
  4. try:
       result = await agent.run(sample.augmented_question)
       # 寫檔案 + read_file 提取 patch（繞過 pager 問題）
       await agent.env._run_bash("git add -A && git diff --cached > /tmp/model.patch")
       patch = await agent.env._read_file("/tmp/model.patch")
     finally:
       await agent.cleanup()          # 必須銷燬沙箱
  5. sample.update(response=..., extracted_final_answer=patch, stage="rollout")
```

核心設計：
- **`model_copy(deep=True)`**：每個 instance 獨立 config 副本，避免併發覆蓋
- **`finally: cleanup()`**：AGS 沙箱必須顯式銷燬，否則資源洩漏
- **Patch 提取走檔案 API**：`git diff --cached > file` + `read_file`，比直接 `git diff` 更可靠（避免 pexpect pager 阻塞和 buffer 溢位）

### SWEBenchProcesser (`utu/eval/processer/swe_bench.py`)

```
SWEBenchProcesser (name="SWEBench")
├── preprocess_one()      # 構造 augmented_question（注入 repo 名 + problem_statement）
├── judge_one()           # 跳過（SWE-bench 離線評測）
└── calculate_metrics()   # 統計 patch_rate（有 patch 的比例）
```

### 資料匯入 (`scripts/data/process_swe_bench.py`)

從 HuggingFace 載入 SWE-bench 資料集，寫入 `DatasetSample` 表。

```
DatasetSample(
  dataset="SWEBench_Verified",
  source="SWEBench",
  question=instance["problem_statement"],
  meta={
    "instance_id": "astropy__astropy-12907",
    "repo": "astropy/astropy",
    "base_commit": "abc123",
    "image_name": "swebenchdocker.tencentcloudcr.com/swebench/sweb.eval.x86_64.astropy__astropy-12907:latest",
    "FAIL_TO_PASS": "...",
    "PASS_TO_PASS": "...",
    "patch": "...",           # gold patch
  },
)
```

映象名規則：`sweb.eval.x86_64.{instance_id_escaped}:latest`，其中 `__` → `_1776_`，全小寫。

### Patch 匯出 (`scripts/data/export_swe_bench_patches.py`)

從 DB 讀取 rollout 結果，生成 `swebench.harness.run_evaluation` 所需的 JSONL：

```json
{"instance_id": "astropy__astropy-13033", "model_name_or_path": "utu-agent", "model_patch": "diff --git a/..."}
```

## 架構總覽

```
process_swe_bench.py          scripts/run_eval.py              export_swe_bench_patches.py
      │                              │                                   │
      │ HuggingFace                  │ Hydra config                      │ DB query
      ▼                              ▼                                   ▼
 ┌──────────┐    ┌─────────────────────────────────┐    ┌──────────────────────┐
 │DatasetSample│──>│ SWEBenchmark.rollout_one()       │──>│ patches.jsonl        │
 │  (DB)       │   │  ├── deep copy config            │   │  (JSONL)             │
 └──────────┘   │  ├── inject image + workspace      │   └──────────────────────┘
                │  ├── build agent (AGS sandbox)     │             │
                │  ├── agent.run() (fix bug)         │             ▼
                │  ├── git diff > file + read_file   │   swebench.harness
                │  └── cleanup (destroy sandbox)     │   .run_evaluation
                └─────────────────────────────────┘   (Docker, 離線)
```

## 環境變數

評測相關（在 `.env` 中配置）：

| 變數 | 說明 |
|------|------|
| `AGS_SANDBOXTOOL_ID` | AGS SandboxTool ID |
| `AGS_SANDBOXTOOL_IMAGE` | 預設容器映象（SWE-bench 時被覆蓋） |
| `AGS_SANDBOXTOOL_ROLEARN` | AGS 角色 ARN |
| `AGS_MOUNT_IMAGE_ID` | SWE-ReX 二進位制掛載映象 |
| `TENCENTCLOUD_SECRET_ID` | 騰訊雲 Secret ID |
| `TENCENTCLOUD_SECRET_KEY` | 騰訊雲 Secret Key |

## 注意事項

- SWE-bench 每個 instance 使用**不同的 Docker 映象**（預裝了對應倉庫程式碼），由 `SWEBenchmark` 在 rollout 時動態注入
- 離線評測需要 Docker 環境（本地 macOS 無 Docker 時可在遠端伺服器執行）
- `--subset` 支援 `verified`（500 條）、`lite`、`full`
- `--concurrency` 控制並行沙箱數量，注意 AGS 資源配額
