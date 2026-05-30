# NeurForge Namespace Migration SOP — `utu` → `neurforge`

> 本文件是這次 namespace migration 的「操作手冊 / SOP」。
> 你（小白友善版）只要 **照著每個 Phase,把標好的 English prompt 一段一段貼給 Cursor Agent**,
> 中間穿插 git / 測試指令即可。每個 Phase 都是一個可獨立 rollback 的 commit。

## 一個名字到底:`neurforge`

為了**徹底避免混淆**,整個專案只用**一個**識別字 `neurforge`,不再有 `nforge`、未來也要消滅所有 `utu`:

- import 套件名（程式裡 `from neurforge... import`）= **`neurforge`**
- distribution / PyPI 名（`pyproject.toml` `[project].name`）= **`neurforge`**（已是,不動）
- 環境變數前綴 = **`NEURFORGE_*`**（已是,不動）
- 品牌名 = **NeurForge**
- 舊 import 套件名 `utu` = 保留為真正套件並存,**最終要消滅**
- 前端 wheel `utu_agent_ui` = **最終改名為 `neurforge_agent_ui`**（見 Phase 4）

> 註:`numpy`/`pandas`/`fastapi` 都讓 import 名 == distribution 名,就是為了避免 `scikit-learn`/`sklearn`、`Pillow`/`PIL` 那種雙名困擾。我們採同樣原則。

## 策略 B（並存式遷移）

- 先建立 `neurforge` 當「forwarding shim（轉發層）」轉發到 `utu`,`utu` 維持為真正套件**完全不動**。
- 再把對外門面（examples / docs）換成 `neurforge`。
- 實體搬移資料夾（`utu/` → `neurforge/`）與消滅 `utu` 字樣,留到最後且測試穩定才做（Phase 5 deferred）。

---

## 0. 這個 repo 的真實情況（先讀,避免踩雷）

我已經盤點過 codebase,以下是**和一般教學文件不一樣、會影響做法的關鍵事實**:

- **Flat layout,不是 `src/` layout。** `utu/` 直接在 repo root,`pyproject.toml` 寫 `packages = ["utu"]`、`pythonpath = "."`、ruff `known-first-party = ["utu"]`、`mkdocs.yml` 指向 `utu`。
- **Prompts / data 住在 package 裡面。** `utu/utils/path.py` 用 `DIR_ROOT / "utu" / "prompts"`、`DIR_ROOT / "utu" / "data"` 這種**檔案系統路徑**載入 prompts/data。所以「直接把資料夾改名」比想像中麻煩（這正是把實體搬移延後的原因）。
- **`utu_agent_ui` 是獨立前端 wheel。** build 來源在 `frontend/webui/`,後端用 `resources.files("utu_agent_ui.static")` 取用。改名要**重建 wheel**,性質不同,獨立成 Phase 4。
- **沒有 `[project.scripts]` entry points**,少一個風險面。
- **原始教學文件有一個錯誤**:它說要小心「Python 標準庫的 `utu`」、不要動 `from utu import ABC, abstractmethod`。**Python 根本沒有標準庫 `utu`**（那行其實是 `from abc import ABC, abstractmethod`）。所以不存在「誤殺 stdlib」的問題。真正要小心的是**子字串誤判**（見下）。

### 真正的「不要動」清單（false positive 來源）

migration 時用搜尋抓 `utu` 一定會抓到一堆**不該（在那個 Phase）改**的東西:

- `youtu` / `youtube` / `youtu_agent`（例如 `configs/tools/mcp/mem0.yaml` 的 url、各種 prompt 文字）→ **不要動**。
- `name: utu-base`（`configs/agents/simple/base.yaml`）→ agent 顯示名稱,非 import,要改是 rebrand 不是 namespace。
- logger 名稱 `"utu"`、log 檔 `utu.log`（`utu/utils/log.py`）→ runtime identifier,本輪不動。
- `/tmp/utu/python_executor/...`、`/tmp/utu_webui_workspace`、`__utu_turn_counter`、`utu_input_filter` → 內部 identifier / 暫存路徑,本輪不動。
- 環境變數 `UTU_*`（已有 `NEURFORGE_*` alias 在 `utu/__init__.py`）→ 本輪不動。
- `LICENSE` / `NOTICE` / README 的 upstream attribution → **保留**（依 `CLAUDE.md` 規則）。
- `utu_agent_ui` → 前端 wheel,**集中在 Phase 4 一次處理**,其他 Phase 不要碰。

---

## 範圍盤點（這次要碰的東西有多少）

- `utu/` 內部使用 `from utu.*` 絕對 import 的檔案:約 **8 個**（大多在 `utu/ui/`、`utu/eval/processer/`、`utu/practice/verify/`、`utu/utils/sqlmodel_utils.py`）。其餘多數是相對 import（`from ..runner ...`）,不需動。
- `examples/**/*.py` 用到 `from utu.*`:約 **37 個檔**（這是「新 namespace 的門面」,最值得先換）。
- `tests/**/*.py` 用到 `utu`:約 **50 個檔**。
- 動態 import:`utu/utils/common.py` 的 `load_class_from_file`（用 `customized_filepath` 從**檔案路徑**載入,不是用套件名）。例子 toolkit 走這條路,所以 toolkit 內部 import 寫 `neurforge` 或 `utu` 都行。

---

## Git 安全策略總覽

- 一個 feature branch:`refactor/namespace-utu-to-neurforge`
- 開工前打一個 baseline tag + empty commit,隨時可以無痛回到原點。
- **每個 Phase 結束就 commit 一次**,commit 訊息見各 Phase。
- 不確定就先 `git diff` 看清楚再決定。
- 出事的救援指令見最後「壞掉怎麼修」。

---

## Phase 0 — 乾淨工作區 + 開 branch（你手動跑,不用 Agent）

```bash
cd /Users/aaron/xk8/00_neurforge
git status
```

如果有未提交變更（例如 `memory/project_agents.md`）,先處理:

```bash
git add -A && git commit -m "chore: wip before namespace migration"
# 或先收起來
git stash push -m "wip before namespace migration"
```

開 branch + 打 baseline 安全點:

```bash
git checkout -b refactor/namespace-utu-to-neurforge
git commit --allow-empty -m "chore: mark baseline before namespace migration"
git tag pre-namespace-migration
```

> 之後任何時候想整個打掉重來:`git reset --hard pre-namespace-migration && git clean -fd`

---

## Phase 1 — 建立 `neurforge` forwarding shim（核心,風險最低）

**目標:** 讓 `import neurforge.tools.base`、`from neurforge.agents import SimpleAgent` 這類 import 全部成立,
而且**指向和 `utu.*` 完全相同的物件**（同一個 module,不是複製）。`utu/` 一行都不改。

做法:在 repo root 新增 `neurforge/__init__.py`,裝一個 **forwarding MetaPathFinder**,把 `neurforge` 與 `neurforge.X` 自動對應到 `utu` 與 `utu.X`。這樣**不需要逐一鏡像每個子模組**,只有一個檔案,review 很容易。

參考實作（Agent 應產生類似內容；你 review 時對照這份）:

```python
# neurforge/__init__.py
"""`neurforge` 是統一的 import namespace（distribution / env / 品牌同名）。

目前所有實作仍住在 `utu.*`；本套件把對 `neurforge.*` 的存取「轉發」到對應的
`utu.*` 模組（回傳同一個 module 物件,零複製、行為完全一致）。
新程式請 import `neurforge.*`；舊程式的 `utu.*` 不受影響。
實體搬移（把程式從 utu 搬到 neurforge、消滅 utu 字樣）留待後續穩定後再做。
"""
import importlib
import importlib.abc
import importlib.util
import sys

_LEGACY = "utu"

# 觸發 utu 的初始化（env 檢查、logging、tracing）,與直接 import utu 行為相同。
_legacy_pkg = importlib.import_module(_LEGACY)


class _ForwardingFinder(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    """把 neurforge / neurforge.<sub> 解析成 utu / utu.<sub>（同一物件）。"""

    def find_spec(self, fullname, path=None, target=None):
        if fullname != __name__ and not fullname.startswith(__name__ + "."):
            return None
        legacy_name = _LEGACY + fullname[len(__name__):]
        real_module = importlib.import_module(legacy_name)
        sys.modules[fullname] = real_module
        return importlib.util.spec_from_loader(fullname, self)

    def create_module(self, spec):
        return sys.modules[spec.name]

    def exec_module(self, module):
        pass


sys.meta_path.insert(0, _ForwardingFinder())


def __getattr__(name):  # PEP 562:讓 `from neurforge import X` 也能轉發到 utu
    return getattr(_legacy_pkg, name)
```

同時做最小 packaging 更新（**只動這兩處,且向後相容**）:

- `pyproject.toml` → `[tool.hatch.build.targets.wheel]` 的 `packages = ["utu"]` 改成 `packages = ["utu", "neurforge"]`
- `pyproject.toml` → `[tool.ruff.lint]` 的 `known-first-party = ["utu"]` 改成 `["utu", "neurforge"]`

> `pyproject.toml` 的 `name` 已是 `neurforge`,**不要再動**。

### Phase 1 貼給 Cursor 的 prompt（English）

```text
Execute Phase 1 of the namespace migration only.
The unified package name is `neurforge` (import name == distribution name == env prefix == brand).

Context:
- This repo is a FLAT layout: the real package `utu/` lives at repo root. Do NOT move or rename it.
- There is NO Python stdlib named `utu`; ignore any such concern.
- pyproject [project].name is already "neurforge"; do NOT change it.

Scope (do ONLY this):
- Create `neurforge/__init__.py` at the repo root that forwards ALL access for
  `neurforge` and `neurforge.<submodule>` to the existing `utu` / `utu.<submodule>`
  modules, returning the SAME module objects (zero duplication). Implement it with a
  MetaPathFinder/Loader inserted into sys.meta_path, plus a module-level `__getattr__`
  (PEP 562) that forwards attribute access to the imported `utu` package.
- Update pyproject.toml minimally and backward-compatibly:
  - [tool.hatch.build.targets.wheel] packages: ["utu"] -> ["utu", "neurforge"]
  - [tool.ruff.lint] known-first-party: ["utu"] -> ["utu", "neurforge"]

Hard constraints:
- Do NOT modify any file inside utu/.
- Do NOT change business logic.
- Do NOT change internal imports anywhere.
- Do NOT touch utu_agent_ui (frontend wheel), env vars (UTU_*/NEURFORGE_*), LICENSE/NOTICE.

After editing:
- Show me the full content of neurforge/__init__.py and the pyproject.toml diff.
- List exactly which files you changed.
```

### Phase 1 測試（你跑 / 或 approve Agent 跑）

```bash
# 用 .env 餵環境變數（utu/__init__.py 會 assert_env）
uv run --env-file .env python -c "import neurforge; print('neurforge OK')"
uv run --env-file .env python -c "from neurforge.tools.base import AsyncBaseToolkit; print(AsyncBaseToolkit)"
uv run --env-file .env python -c "from neurforge.tools.utils import register_tool; print(register_tool)"
uv run --env-file .env python -c "from neurforge.agents import SimpleAgent; print(SimpleAgent)"
# 確認 neurforge.tools.base 與 utu.tools.base 是同一個 module（轉發成功）
uv run --env-file .env python -c "import neurforge.tools.base as n, utu.tools.base as u; print('SAME' if n is u else 'DIFFERENT')"
# 既有 utu import 不能壞
uv run --env-file .env python -c "from utu.tools.base import AsyncBaseToolkit; print('utu still OK')"
```

預期:全部印出物件、最後印 `SAME`、`utu still OK`。

### Phase 1 commit

```bash
git add -A
git commit -m "refactor: introduce neurforge namespace as forwarding shim over utu"
```

---

## Phase 2 — 把 examples / docs 換成 `neurforge`（門面切換,葉節點安全）

**為什麼先做 examples 而不是內部 import?** 因為 `neurforge` 已經轉發到 `utu`,
改 examples 是「葉節點」（沒有別的東西 import examples）,就算錯了也只影響該範例,最安全,
而且這就是「對外宣告我們用 neurforge」的實際動作。

範圍:
- `examples/**/*.py`:`from utu.xxx import ...` → `from neurforge.xxx import ...`
- 新 toolkit 範本（如 `examples/sensor_sage/tools/...`、`industrial_qa`、`case_detective`）統一用:
  - `from neurforge.tools.base import AsyncBaseToolkit`
  - `from neurforge.tools.utils import register_tool`
- `docs/**/*.md`、`README*.md` 裡的 `from utu...` 程式碼範例（**只改 import 範例,不改敘述性 `utu` 字樣**）。

### Phase 2 貼給 Cursor 的 prompt（English）

```text
Execute Phase 2 of the namespace migration only. Unified package name is `neurforge`.

Goal:
- In examples/ and docs/, update Python import statements from `utu.*` to `neurforge.*`.
- Update toolkit templates to import from neurforge.tools.base / neurforge.tools.utils.

Rules:
- ONLY change actual import statements (from utu.X import ... / import utu.X).
- Do NOT touch: utu_agent_ui, the string "youtu"/"youtube"/"youtu_agent", the config
  name "utu-base", env vars UTU_*/NEURFORGE_*, logger names, /tmp/utu paths, LICENSE/NOTICE.
- Do NOT modify anything inside utu/.
- Do NOT change compatibility shims (neurforge/__init__.py).
- Do NOT reformat unrelated code.

After editing:
- Run an import smoke test on 2-3 representative example main.py files.
- List every file changed.
- Search for remaining `utu` references in examples/ and docs/, and classify each as:
  1) intentional non-import string (keep), 2) leftover import to fix, 3) needs human review.
```

### Phase 2 測試

```bash
uv run python -m py_compile examples/**/*.py
```

### Phase 2 commit

```bash
git add -A
git commit -m "docs: migrate examples and docs to neurforge namespace"
```

---

## Phase 3 —（選做）把 `utu/` 內部少數絕對 import 換成 `neurforge`

**注意:** 這一步在策略 B 下是**純美觀（cosmetic）**——因為 `neurforge` 只是轉發到 `utu`,
改內部 import 不會改變 runtime,只是「讓內部也講新名字」。風險 > 收益,**可做可不做**。
若要做,只動「絕對 import」那 8 個檔,**不要動相對 import**（`from ..runner import`）。

涉及檔案（絕對 `from utu.` import）:`utu/ui/*.py`、`utu/eval/processer/__init__.py`、`utu/practice/verify/*.py`、`utu/utils/sqlmodel_utils.py`。

### Phase 3 貼給 Cursor 的 prompt（English,要做才貼）

```text
Execute Phase 3 of the namespace migration only. Unified package name is `neurforge`.

Goal:
- Inside utu/, replace ABSOLUTE imports of the form `from utu.X import ...` / `import utu.X`
  with `from neurforge.X import ...` / `import neurforge.X`.

Rules:
- Do NOT touch relative imports (from ..x import ...). Leave them as-is.
- Do NOT touch non-import `utu` strings: logger name "utu", "utu.log",
  "/tmp/utu/...", "__utu_turn_counter", DIR_ROOT / "utu" / "prompts" or .../"data",
  resources.files("utu_agent_ui...").
- Do NOT change business logic or formatting.

After editing:
- Run the full Phase 1 import smoke tests again.
- Run: uv run pytest tests/test_config.py -q
- List changed files and any remaining utu references with classification.
```

### Phase 3 commit

```bash
git add -A
git commit -m "refactor: migrate internal absolute imports in utu to neurforge"
```

---

## Phase 4 —（可現在做,也可延後）前端 wheel `utu_agent_ui` → `neurforge_agent_ui`

**目的:** 消滅前端 wheel 名稱裡的 `utu`。這塊性質特殊(要**重建 wheel**),所以獨立成一個 Phase。

要改的東西:
- `frontend/webui/utu_agent_ui/`（目錄）→ `neurforge_agent_ui/`；刪除過時的 `frontend/webui/utu_agent_ui.egg-info/`
- `frontend/webui/pyproject.toml`:`name = "utu_agent_ui"` → `"neurforge_agent_ui"`；description 的 `utu-agent` 一併更新
- `frontend/webui/build.sh`:兩行 `./utu_agent_ui/static` → `./neurforge_agent_ui/static`
- 後端兩處引用:`utu/ui/webui_agents.py`、`utu/ui/webui_chatbot.py` 的 `resources.files("utu_agent_ui.static")` → `resources.files("neurforge_agent_ui.static")`
- `Makefile`:`frontend/webui/build/utu_agent_ui-0.2.0-py3-none-any.whl` → 新檔名 `neurforge_agent_ui-0.3.0-py3-none-any.whl`
- `docker/Dockerfile`:目前指向 GitHub release 的 `utu_agent_ui-0.3.0-...whl` URL → **需要把新檔名的 wheel 重新上傳一個 release**,或改成複製本地 build 的 wheel。**這是唯一的外部依賴。**

重建步驟（需要 `npm`）:

```bash
cd frontend/webui
npm run build
bash build.sh          # 產出 build/neurforge_agent_ui-0.3.0-py3-none-any.whl
cd ../..
uv pip install frontend/webui/build/neurforge_agent_ui-0.3.0-py3-none-any.whl --reinstall
uv run --env-file .env python examples/svg_generator/main_web.py
# 開 http://127.0.0.1:8848 確認 UI 正常 + 標題顯示 NeurForge
```

### Phase 4 貼給 Cursor 的 prompt（English）

```text
Execute Phase 4 only: rename the frontend UI wheel from `utu_agent_ui` to `neurforge_agent_ui`.

Do these edits:
- Rename dir frontend/webui/utu_agent_ui/ -> frontend/webui/neurforge_agent_ui/ and delete frontend/webui/utu_agent_ui.egg-info/.
- frontend/webui/pyproject.toml: name "utu_agent_ui" -> "neurforge_agent_ui"; update description.
- frontend/webui/build.sh: replace ./utu_agent_ui/static with ./neurforge_agent_ui/static (both lines).
- utu/ui/webui_agents.py and utu/ui/webui_chatbot.py: change resources.files("utu_agent_ui.static") to resources.files("neurforge_agent_ui.static").
- Makefile: update the wheel filename to neurforge_agent_ui-0.3.0-py3-none-any.whl.
- docker/Dockerfile: point to the renamed wheel; FLAG that the GitHub release asset must be re-uploaded with the new filename, or switch to installing the locally built wheel.

Constraints:
- Do NOT change React/TS source behavior; this is a packaging rename only.
- Do NOT rebuild or publish anything yourself; just make the source edits and tell me the exact build/publish commands to run.

After editing: list all changed paths and the remaining manual steps (rebuild wheel, republish release).
```

### Phase 4 commit

```bash
git add -A
git commit -m "chore: rename frontend UI wheel utu_agent_ui to neurforge_agent_ui"
```

---

## Phase 5 — 收尾 + （DEFERRED）實體把 `utu/` 搬成 `neurforge/`

收尾（可做）:
- （選做）新增 `.cursor/rules` migration rule,把「不要動清單」與「沒有 stdlib utu」寫進去。
- 更新 `CLAUDE.md` §9 Phase 3 狀態。
- 開 PR:

```bash
git push -u origin refactor/namespace-utu-to-neurforge
```

**DEFERRED（本輪不做,之後另開 plan）**:實體把 `utu/` 搬成 `neurforge/`、徹底消滅 `utu` 字樣。風險最高,因為要同時處理:
- `utu/utils/path.py` 的 `DIR_ROOT / "utu" / "prompts"`、`/ "utu" / "data"` 檔案系統路徑（prompts/data 要跟著搬）。
- `pyproject.toml` 的 `packages`、`mkdocs.yml` 的 `paths: ["utu"]` 與 nav `- utu`。
- logger 名稱、`/tmp/utu` 路徑等 identifier。
- 反向 shim:改成 `utu/` 轉發到 `neurforge/`,給外部舊使用者過渡期。

---

## 壞掉怎麼修（救援指令）

```bash
# 還沒 commit,想丟掉全部未提交改動:
git restore .            # 已追蹤檔
git clean -fd            # 新增檔
# 或一次到位（回到上一個 commit 狀態）:
git reset --hard HEAD && git clean -fd

# 已經 commit 但這個 commit 壞了,想退回上一個（保留改動在工作區）:
git reset --soft HEAD~1

# 想整個回到 migration 之前:
git reset --hard pre-namespace-migration && git clean -fd
```

---

## 一頁總結（你照這個順序操作就對了）

1. Phase 0:`git status` → 開 branch `refactor/namespace-utu-to-neurforge` → empty commit + tag `pre-namespace-migration`
2. Phase 1:貼 Phase 1 prompt → review `neurforge/__init__.py` + pyproject diff → smoke test（要看到 `SAME`）→ commit
3. Phase 2:貼 Phase 2 prompt → review diff → smoke test → commit
4. Phase 3（選做）:貼 Phase 3 prompt → smoke + `pytest tests/test_config.py` → commit
5. Phase 4（可現在/延後）:前端 wheel 改名 + 重建 + 重新發 release → commit
6. Phase 5:收尾 PR；實體搬移**之後另開 plan 再做**

> 核心原則:**一個名字到底（`neurforge`）；先讓新舊 namespace 並存（neurforge 轉發到 utu）,再慢慢把門面換成 neurforge,實體搬移與消滅 utu 留到最後。**
