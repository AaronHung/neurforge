# NeurForge — Project Context for Claude Code

> **Current milestone: `demo-v0.1` — tagged 2026-05-31 on `main`. Fully functional demo baseline.**
> Phase 1-A ✅ · Phase 2-A ✅ (3 industrial agents) · Phase 3 🟡 (`neurforge` forwarding shim live).
> To return to this stable point anytime: `git checkout demo-v0.1`
> Previous baseline still available: `git checkout v0.1.0-baseline`. See §9 for full plan, §12 for latest status.

---

## 1. What this project is

**NeurForge** is an Agent platform built on top of `youtu-agent` (this codebase
is a fork). It is being developed by:

- **Company (English):** IIoTFab Inc.
- **Company (Chinese full name):** 薈智創新科技股份有限公司
- **Company (Chinese short name):** 薈智創新
- **Product name:** NeurForge (中文：薈智神鑄)

The codebase is **forked from `youtu-agent`** and is being rebranded and extended.
We are **not** rewriting the agent runtime from scratch — we extend the existing
open-source baseline.

When you see `youtu` / `Youtu` / `YOUTU` in code, configs, docs, or UI strings,
it is a rebranding candidate — but check the rules in §3 before changing anything.

---

## 2. Phase goal: ship a working baseline

The single priority right now is **a stable rebranded baseline that runs end-to-end
the same way upstream youtu-agent does.**

This means:

- ✅ Rebrand user-facing surfaces (README, CLI banner, docs, UI strings, package metadata)
- ✅ Keep all existing functionality working
- ✅ Preserve upstream attribution and license
- ❌ Do **not** add new features
- ❌ Do **not** refactor module structure
- ❌ Do **not** introduce new dependencies unless required for rebranding
- ❌ Do **not** rename Python packages, modules, or import paths in this phase
  (breaking imports has high cost — ask first)

If you find yourself wanting to "improve" or "modernize" something while doing
the rebrand: stop, note it, and bring it up. We will address it after baseline.

---

## 3. Rebranding rules (youtu-agent → NeurForge / IIoTFab)

| Surface                                                        | Action                                                                          |
| -------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| README, docs, marketing copy, UI strings, CLI banner           | Rebrand to **NeurForge**                                                        |
| Company attribution where needed                               | **IIoTFab Inc.** (English) / **薈智創新科技股份有限公司** (Chinese)             |
| Python package names, module names, import paths               | **Keep as-is for now.** Ask before renaming.                                    |
| Upstream attribution ("based on youtu-agent", LICENSE, NOTICE) | **Keep.** We are not hiding the fork.                                           |
| Config keys / env vars / API routes                            | Add `neurforge_*` / `NEURFORGE_*` aliases, keep old names as deprecated aliases |
| Test fixtures / internal identifiers                           | Leave alone unless user-visible                                                 |
| Comments referencing internal mechanics                        | Leave alone                                                                     |

**When unsure whether a string is a "brand surface" or a "technical identifier", ask.**

---

## 4. Code-style preferences

- Prefer explicit over clever
- Match the existing style of the file you are editing
- Small, reviewable diffs — one concern per change
- Don't reformat files you aren't otherwise touching

---

## 5. What to ask before doing

Stop and ask the user before:

- Renaming any Python package, module, or import path
- Adding a new dependency
- Changing config schema in a non-backward-compatible way
- Touching anything related to license, NOTICE, or upstream attribution
- Any change that would force users to update their existing setup

---

## 6. Development roadmap

See §9 for full plan. Summary:

| Phase | Goal | Status |
|-------|------|--------|
| 1-A | Visual rebrand (CLI, Web UI, logos, title, full UI redesign) | ✅ Done (2026-05-25) |
| 1-B | Traditional Chinese (zh-TW) conversion across repo | 🔲 Partial |
| 1-C | Push baseline to remote | ✅ Done — `v0.1.0-baseline` |
| 2-A | Industrial scenario examples | ✅ Done — 3 agents |
| 2-B | Tool Registry → MCP-compatible | 🔲 After baseline |
| 2-C | Orchestration (human-in-loop, retry, durable) | 🔲 After baseline |
| 2-D | Observability backend options | 🔲 After baseline |
| 2-E | UI: Tornado → FastAPI + SSE | 🔲 Medium term |
| 3 | Python namespace: utu → neurforge | 🟡 In progress — `neurforge` forwarding shim live (imports migrated); physical folder move still deferred |

---

## 7. Baseline rebrand — what was done (2025-05-03)

**Status: rebrand complete, smoke test pending.**

All changes were user-facing surface only. Python packages, module names,
and import paths were NOT renamed (still `utu.*`). Everything below is done:

### Files changed / created

| File                                                | Change                                                          |
| --------------------------------------------------- | --------------------------------------------------------------- |
| `pyproject.toml`                                    | `name = "neurforge"`, description, URLs → iiotfab/neurforge     |
| `CLAUDE.md`                                         | Created (this file)                                             |
| `PRODUCT_DIRECTION.md`                              | Created — post-baseline platform vision                         |
| `README.md`                                         | Full rebrand; Tencent promos removed; upstream attribution kept |
| `README_ZH.md`                                      | **Deleted.** Replaced by `README_ZHTW.md` (Traditional Chinese) |
| `README_ZHTW.md`                                    | New file: opencc s2twp conversion + NeurForge brand             |
| `README_JA.md`                                      | Brand strings updated                                           |
| `mkdocs.yml`                                        | `site_name`, `repo_url` → NeurForge / iiotfab                   |
| `frontend/webui/src/App.tsx`                        | Title `"Youtu Agent"` → `"NeurForge"`                           |
| `frontend/webui/src/i18n/i18n.ts`                   | zh locale → zh-TW                                               |
| `frontend/webui/src/i18n/locales/zh-TW/common.json` | New file: Traditional Chinese UI strings                        |
| `utu/__init__.py`                                   | Added `NEURFORGE_*` → `UTU_*` env var alias block (19 vars)     |
| `.env.example`                                      | Rewritten to use `NEURFORGE_*` as primary                       |
| `docs/*.md`, `docs/howto/*.md`                      | opencc s2twp + brand replacement                                |
| `configs/agents/**/*.yaml` (selected)               | opencc s2twp                                                    |
| `utu/prompts/**/*.yaml`                             | opencc s2twp                                                    |
| `examples/**/*.py` (selected)                       | opencc s2twp                                                    |

### What was NOT changed (intentional)

- Python package name: still `utu` — do not rename without asking
- Internal env var names: `UTU_*` still work (aliases forward to them)
- LICENSE, NOTICE, upstream attribution in README — kept deliberately
- `utu/agents/`, `utu/tools/`, `utu/runner/` core logic — untouched

### Env var alias map (in `utu/__init__.py`)

`NEURFORGE_LLM_TYPE/MODEL/BASE_URL/API_KEY` → `UTU_*` equivalents.
Set `NEURFORGE_*` in `.env` and it just works.

---

## 8. Smoke test checklist (next session)

Run these in order. If any step fails, fix before committing.

```bash
# 0. Install deps
uv sync

# 1. Copy and fill in your API key
cp .env.example .env
# Edit .env: set NEURFORGE_LLM_API_KEY=<your key>

# 2. Import test
python -c "import utu; print('OK')"

# 3. CLI chat test (no tools, minimal)
python scripts/cli_chat.py --config simple/base
# Type "hello" — expect a response

# 4. CLI chat with search (optional, needs SERPER_API_KEY + JINA_API_KEY)
python scripts/cli_chat.py --config simple/base_search

# 5. Web UI test
python examples/svg_generator/main_web.py
# Open http://127.0.0.1:8848 — check title shows "NeurForge"
```

Once all pass → `git add -A && git commit -m "feat: NeurForge baseline rebrand"`

---

## 9. Full development plan (v1.0, 2026-05-24)

---

### Phase 1-A：Visual rebrand（進行中）

| # | 項目 | 狀態 | 檔案 |
|---|------|------|------|
| 1 | CLI banner | ✅ | `scripts/cli_chat.py` |
| 2 | 瀏覽器 tab title | ✅ | `frontend/webui/index.html` |
| 3 | Footer logo 圖片 | ✅ | `src/assets/pic.png` |
| 4 | Favicon + title logo | ✅ | `src/assets/logo-square.png` |
| 5 | Example query | ✅ | `examples/svg_generator/main*.py` |
| 6 | App 標題文字 | 🔲 | `App.tsx:979` → `薈智創新 NeurForge` |
| 7 | Web UI build + 瀏覽器確認 | 🔲 | 見 build 指令 |
| 8 | Commit + push | 🔲 | — |

**Build 指令（每次改 src/ 或圖片後執行）：**
```bash
cd /Users/aaron/xk8/00_ag_v01_2/youtu-agent/frontend/webui
npm run build && bash build.sh
cd /Users/aaron/xk8/00_ag_v01_2/youtu-agent
uv pip install frontend/webui/build/neurforge_agent_ui-0.3.0-py3-none-any.whl --reinstall
uv run --env-file .env python examples/svg_generator/main_web.py
# 開 http://127.0.0.1:8848 確認
```

---

### Phase 1-B：繁體中文化（1-A 完成後）

把 repo 裡所有簡體中文換成繁體台灣慣用語。

| 類別 | 路徑 |
|------|------|
| Agent prompts | `utu/prompts/**/*.yaml` |
| Agent configs | `configs/agents/**/*.yaml` |
| 文件 | `docs/*.md`（部分已做，需全面確認） |
| Python 字串 | `examples/**/*.py`、`utu/ui/`、`scripts/` |
| i18n | `frontend/webui/src/i18n/locales/` |

工具：`opencc s2twp` 批次轉換 + 人工審閱台灣慣用語。
技術識別碼（function name、變數名）不動。

---

### Phase 1-C：Push baseline

```bash
git push
```

---

### Phase 2-A：工業場景範例（baseline 後）

把 `examples/` 裡的 generic demo 換成工業場景：
- 巡檢助理、異常調查、品質檢查、報修分流、Evidence path 輸出

---

### Phase 2-B：Tool Registry → MCP-compatible

- 內部 Tool Registry 抽象層
- MCP adapter（讓 MES / SCADA / 文件系統等外部系統接入）

---

### Phase 2-C：Orchestration 強化

- Human-in-the-loop 審批節點
- Retry / timeout 機制
- Durable execution（評估 LangGraph）
- Evidence path 追溯紀錄

---

### Phase 2-D：Observability 優化

- 保留 OTel 標準
- Tracing backend 改為可選：Phoenix / Langfuse / 自建

---

### Phase 2-E：UI 升級（中期）

- Tornado + WebSocket → FastAPI + SSE
- 工業 console 風格 UI

---

### Phase 3：Python Namespace utu → neurforge（進行中）

採「forwarding shim」策略並存遷移（SOP：`docs/NEURFORGE_namespace_migration_cursor.md`）：

- ✅ `neurforge/__init__.py` forwarding shim（轉發到 `utu`，零複製、行為不變）
- ✅ examples / docs 改用 `neurforge.*`；`utu/` 內部絕對 import 也改 `neurforge.*`
- ✅ 前端 wheel `utu_agent_ui` → `neurforge_agent_ui`（需重建 wheel + 重發 GitHub release）
- 🔲 DEFERRED（最後、高風險）：實體把 `utu/` 搬成 `neurforge/`，處理 `utu/utils/path.py` 的
  `DIR_ROOT/"utu"/"prompts"`、`/"data"` 路徑、`mkdocs.yml`、反向 shim。前提：測試覆蓋率夠高。

import 命名原則：`neurforge`（import == distribution == env == 品牌，避免雙名混淆）。

---

### 技術決策備忘

| 決策 | 結論 |
|------|------|
| OpenAI Agents SDK | 保留 |
| Hydra config | 保留，production 對外介面日後簡化 |
| Tornado / WebSocket | 保留現在，中期遷移 FastAPI + SSE |
| OTel tracing | 保留標準，backend 可選 |
| MCP | 中期加 adapter |
| Python package rename | Phase 3，最後才動 |

---

### 快速 resume 指南

```bash
git log --oneline -5   # 看 commit 狀態
git status             # 看是否有未 commit 的修改
git tag                # 看 milestone tags
# 然後讀 §9 看目前進度
# 回到穩定版本：git checkout v0.1.0-baseline
```

---

## 10. Phase 2-A 補充：工業場景 Agent 實作紀錄（2026-05-25）

### 三個 Agent 總覽

| Agent | 中文名 | 場景 |
|-------|--------|------|
| SensorSageAgent | 機況先知 | 預測性維護（PdM）— 壓縮機 HPI、觸媒反應器 |
| IndustrialQAAgent | 廠務通 | 廠務 Q&A — SOP、巡檢、故障分流 |
| CaseDetectiveAgent | 案件偵探 | 電信客服案件分析 — 帳單、SLA、申訴 |

### 關鍵技術陷阱（必須保留）

**`@register_tool` vs `@function_tool`**：
- `utu.tools.utils.register_tool` 設定 `_is_tool = True`，這是 `AsyncBaseToolkit.tools_map` 唯一識別方式
- `agents.function_tool` 是 OpenAI Agents SDK 給獨立 function 用的，**不會被 toolkit 識別 → 0 tools loaded**
- 兩個 decorator 名字相似，非常容易混淆，永遠用 `@register_tool`

**Toolkit `__init__` 簽名**：
- `_load_customized_toolkit` 呼叫 `toolkit_class(toolkit_config)`，傳入一個位置參數
- 必須是 `def __init__(self, config=None)` 然後 `super().__init__(config)`
- 少了 `config=None` 會得到 `takes 1 positional argument but 2 were given`

**`mode: customized` 設定**：
```yaml
name: sensor_sage
mode: customized
customized_filepath: examples/sensor_sage/tools/sensor_sage_toolkit.py
customized_classname: SensorSageToolkit
```
這樣可以加新 toolkit 不動 `utu/tools/__init__.py`。

### Agent 分類規則（sidebar）

Sidebar 依路徑/關鍵字把 config 分三類：

```typescript
const MFG_KEYWORDS = ['sensor_sage', 'industrial_qa', 'case_detective'];
const MULTI_PATTERNS = ['examples/', 'orchestra', 'generated/'];
// 其他全歸 single
```

---

## 11. UI 設計重構紀錄（2026-05-25）

完整 design spec 見 `SPEC_v0.1.0.md`。

### 做了什麼

1. **Sidebar 全重寫**（`SideBar.tsx` + `SideBar.css`）
   - Linear 風格深色主題（`#0f0f12` 背景）
   - 三色分類系統：MFG 青色 / Multi-Agent 琥珀 / Single Agent 紫色
   - Lucide 全套圖示，Inter 字型
   - 思考動畫 `nf-glow` 取代舊的彈跳點

2. **工作區重設計**（`index.css`）
   - 暖奶油色背景 `#f9f6f0`（Claude.ai 風格）
   - 標題「薈智創新 NeurForge」換橙色 `#c8632a`，縮小到 1.25rem
   - 輸入框從 pill → 白色卡片（`border-radius: 16px`，有 shadow）
   - 工具呼叫展開：黑色底 → 暖淡色 `#f2ede6`

3. **Icon 系統全換 Lucide**（`ChatInput.tsx`、`MessageComponent.tsx`、`AgentTOC.tsx`、`App.tsx`）
   - 消滅所有 FA icon 和 emoji（🐙 🖥️ fa-cog fa-paperclip fa-paper-plane 等）
   - Settings gear：Lucide `<Settings>` + 45° 彈性旋轉 hover
   - Tool call icon：依工具類型動態選（Wrench / Globe / BookOpen / Search / MessageSquare / Lightbulb）

4. **輸入快捷鍵**
   - `Enter` 改成 `⌘↵`（Mac）/ `Ctrl↵`（Windows），避免 IME 輸入法選字誤送

### Web UI Build 指令（正確路徑）

```bash
# 從 repo root 執行
cd frontend/webui
npm run build
bash build.sh
cd ../..
uv pip install frontend/webui/build/neurforge_agent_ui-0.3.0-py3-none-any.whl --reinstall
uv run --env-file .env python examples/svg_generator/main_web.py
# 開 http://127.0.0.1:8848/index.html 確認
```

---

## 12. 目前狀態與沉澱期計畫（2026-05-31）

### 已切線：`demo-v0.1` 穩定基線
- `main`、`origin/main`、tag `demo-v0.1` 三者同指 commit `407461b`（已 push 到 GitHub）。
- 這條線把 `refactor/namespace-to-neurforge`（13 commits）fast-forward 進 `main`，內容包含：
  - **Namespace（Phase 3 部分）**：`neurforge` forwarding shim、內部 import 改寫、UI wheel `utu_agent_ui → neurforge_agent_ui`。
  - **Demo 打磨**：web UI 圖片（matplotlib）inline 渲染、sidebar 同名去歧義 +
    切 agent 同步 example query、`python_executor` workspace 修正。
  - **case_detective 改名**：10 個客戶名 + 3 個承包商公司名換成公司熟悉名字（含 docs 試跑紀錄一致化）。
  - **教材文件**：`docs/pgm-docs/*`、`docs/pgm-spec/*`。
- ⚠️ smoke test 尚未跑（使用者已知並接受）；若出問題，`git checkout demo-v0.1` 即為可用版本。

### 保留的分支
- `refactor/namespace-to-neurforge`（本地 + origin）刻意留著當紀錄，**暫不清理**。

### 沉澱期（預計約 1 個月，暫不大改 code）
使用者接下來重心：**測試、準備 training**；之後請 AI **徹底讀懂 codebase**（不急著改）。

### 下一次高風險工作的開法（務必照此）
實體移除 `utu/` 時，從基線開**新分支**，不要接舊分支：
```bash
git checkout main && git checkout -b refactor/remove-utu
```
DEFERRED 待辦（§9 Phase 3 尾段）：`utu/utils/path.py` 的 `DIR_ROOT/"utu"/"prompts"`、`/"data"`
路徑、`mkdocs.yml`、反向 shim。前提：測試覆蓋率足夠。`main` 全程停在 demo-v0.1 基線。
