# Data Analysis Agent 排錯與補套件紀錄（pgm-docs）

> 場景：在 Web UI 切到 `examples/data_analysis`、上傳 CSV 提問後，回覆出現
> `Error processing query: name 'InteractiveShell' is not defined`。
> 本文紀錄根因、修復、驗證與預防，給教育訓練與日後維運用。
>
> 處理日期：2026-05-30。語言 zh-TW；英文技術名詞保留原文。

---

## 1. 症狀

- 在 Web UI 選 `examples/data_analysis`，上傳 `demo_data_cat_breeds_clean.csv` 並提問。
- 助理回覆紅框錯誤：
  ```
  Error processing query: name 'InteractiveShell' is not defined
  ```
- 重試仍然一樣（每次都失敗，非偶發）。

---

## 2. 根因（root cause）

`data_analysis` 會用到**本地 Python 執行器** [utu/tools/local_env/python.py](../../utu/tools/local_env/python.py)，
它在檔頭把繪圖/IPython 套件包在 `try/except ImportError: pass` 內匯入：

```python
try:
    import matplotlib
    import matplotlib.pyplot as plt
    from IPython.core.interactiveshell import InteractiveShell
    from traitlets.config.loader import Config
    matplotlib.use("Agg")
except ImportError:
    pass   # ← 套件沒裝時「靜默跳過」，InteractiveShell 從此未定義
```

這些套件屬於**選用 extra `local-python`**（見 [pyproject.toml](../../pyproject.toml) 第 49–55 行）：
`chardet / ipython / matplotlib / scipy / seaborn`。

當前 venv 沒裝這個 extra（`uv sync` 預設不裝選用 extra）→ 匯入失敗被 `except` 吞掉 →
`InteractiveShell` 從未定義。接著 [utu/tools/python_executor_toolkit.py](../../utu/tools/python_executor_toolkit.py)
在 **toolkit build 階段**就呼叫：

```python
self._ipython_shell = create_ipython_shell()   # 內部用到 InteractiveShell
```

這行不在 try 區塊內 → 直接拋 `NameError` → 冒到 UI 變成「Error processing query」。

> 為什麼其他 agent 不會壞？ sensor_sage / industrial_qa / case_detective / svg_generator
> 都**沒有**載入這個本地 Python 執行器 toolkit，所以不受影響。

---

## 3. 修復步驟（已執行）

### 3.1 安裝缺少的 extra
```bash
uv sync --extra local-python
```
安裝內容：`ipython 9.5.0 / matplotlib 3.10.6 / scipy 1.16.2 / seaborn 0.13.2 /
traitlets 5.14.3 / chardet 5.2.0`（含相依）。

### 3.2 重要副作用：補回前端 UI wheel
`uv sync` 會「修剪」**不在 pyproject 宣告**的套件。前端 UI wheel
（`neurforge_agent_ui`）是先前手動 `uv pip install` 進來的，因此被 `uv sync` 移除了。
必須補回，否則 Web UI 靜態頁會壞：

```bash
uv pip install frontend/webui/build/neurforge_agent_ui-0.3.0-py3-none-any.whl --reinstall
```

> 通則：**每次跑 `uv sync` / `uv sync --all-extras` 之後，都要再 reinstall 一次前端 wheel。**

---

## 4. 驗證（如何確認真的修好）

### 4.1 套件可匯入
```bash
uv run python -c "import importlib.util as u; \
print({m: bool(u.find_spec(m)) for m in ['IPython','matplotlib','traitlets','neurforge_agent_ui']})"
# 期望全部 True
```
實測結果：`{'IPython': True, 'matplotlib': True, 'traitlets': True, 'neurforge_agent_ui': True}`。

### 4.2 直接打 Python 執行器（最快、不必跑完整 agent）
```python
import asyncio
from neurforge.tools.local_env.python import create_ipython_shell, execute_python_code_async

async def t():
    shell = create_ipython_shell()           # 修復前就是這行拋 NameError
    r = await execute_python_code_async(
        "import pandas as pd\n"
        "df = pd.read_csv('/絕對路徑/demo_data_cat_breeds_clean.csv')\n"
        "print('SHAPE', df.shape)\n",
        "/tmp/nf_da_test", timeout=60, shell=shell)
    print(r["success"], r["message"][:300])

asyncio.run(t())
```
實測：**不再有 `NameError`**，`shell` 正常建立、`run_cell` 正常執行 pandas 程式碼。

> 注意兩個容易誤判的點：
> - 執行器會 `os.chdir(workdir)`，所以 code 內若用**相對路徑**會找不到檔。Web UI 上傳的檔
>   是**絕對路徑**（`/tmp/utu_webui_workspace/...csv`），所以實際使用沒問題；自己手動測時請用絕對路徑。
> - 回傳的 `success` 是用「字串裡有沒有 `Error`」這種粗略啟發式判斷，偶爾會 false-negative；
>   要看實際對錯請讀 `message` / `error` 全文，不要只看 `success`。

---

## 5. 重新試用 data_analysis（SOP）

### Web UI（看 HTML 報告渲染）
```bash
uv run --env-file .env python examples/svg_generator/main_web.py
# 開 http://127.0.0.1:8848/index.html
# sidebar 切到 examples/data_analysis → 重新上傳 demo_data_cat_breeds_clean.csv → 提問
```

### CLI / harness（自動記錄）
```bash
uv run --env-file .env python scripts/try_agent.py \
  --config simple/data_analysis_agent \
  --question "請分析位於 <CSV 絕對路徑> 的資料，提取有價值的資訊。" \
  --out docs/pgm-docs/agent_trials.zh-TW.md
```

注意事項：
- `examples/data_analysis`（整機）是 **orchestrator**：DataAnalysisAgent + SearchAgent +
  HTMLGenerator，跑一輪需數分鐘屬正常（比單代理慢）。
- 只想驗證資料分析本身，可改用單代理 `simple/data_analysis_agent`（較快，無多代理規劃）。

---

## 6. 預防與建議

1. **一次裝齊**：`uv sync --all-extras`，再 reinstall 前端 wheel（見 §3.2）。
   缺哪個功能就少裝哪個 extra，對照 [pyproject.toml](../../pyproject.toml) 的
   `[project.optional-dependencies]`：

   | extra | 用途 |
   | --- | --- |
   | `local-python` | 本地 Python 執行器（data_analysis 必裝） |
   | `local-bash` | 本地 bash 工具 |
   | `documents` | PDF/Office 文件解析 |
   | `search` / `scholar` / `wiki` | 搜尋 / arXiv / Wikipedia |
   | `image` / `video` | 影像 / 影片工具 |
   | `e2b` | E2B 雲端沙箱 |

2. **程式碼健壯化（建議，未實作）**：把 `python.py` 的 `except ImportError: pass`
   改成記錄清楚訊息（例如「請執行 `uv sync --extra local-python`」），讓缺套件時不再出現
   難懂的 `NameError: InteractiveShell`。屬小幅 robustness 改善，需要時再動。

---

### 附錄：本文引用的關鍵檔案

| 主題 | 檔案 |
| --- | --- |
| 本地 Python 執行器（錯誤源頭） | [utu/tools/local_env/python.py](../../utu/tools/local_env/python.py) |
| Python 執行器 toolkit | [utu/tools/python_executor_toolkit.py](../../utu/tools/python_executor_toolkit.py) |
| 選用 extra 宣告 | [pyproject.toml](../../pyproject.toml) |
| data_analysis 整機 config | [configs/agents/examples/data_analysis.yaml](../../configs/agents/examples/data_analysis.yaml) |
| data_analysis 單代理 config | [configs/agents/simple/data_analysis_agent.yaml](../../configs/agents/simple/data_analysis_agent.yaml) |
| Web UI 啟動範例 | [examples/data_analysis/main_web.py](../../examples/data_analysis/main_web.py) |
| 試用 harness | [scripts/try_agent.py](../../scripts/try_agent.py) |
