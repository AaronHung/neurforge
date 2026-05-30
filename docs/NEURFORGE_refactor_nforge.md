## 建議結論
我要請Cursor先進入Plan Mode幫我規劃如何來做我的程式的refactoring/namespace migrating from utu 到 nforge。然後計劃做完我們再分批來做。以下是計劃的概況。你先讀一下。我會一個一個輸入給你prompt，我做錯的時候，你可以提醒。

這種工作我會用：

> **Plan Mode → 小範圍 Agent → Review diff → Test → Commit → 下一批 Agent**

不要一開始就叫 Cursor 全自動把整個 repo 改完。
你這個任務屬於 **namespace migration / import path refactor**，風險不是單一檔案，而是「整個 repo 的 module resolution 會不會被破壞」。

Cursor 官方的 Plan Mode 是為了讓 Agent 先研究 codebase、找相關檔案、問問題、產生可編輯的計畫；官方也建議在複雜任務中先 review / edit plan，再從 plan 開始 build。([Cursor](https://cursor.com/blog/plan-mode))

------

# 你應該進什麼 mode？

## 第一輪：Plan Mode

用途：**只做盤點，不改 code。**

在 Cursor Agent 輸入框按 **Shift + Tab** 進 Plan Mode。Cursor 官方說 Plan Mode 會讓 Agent 研究 codebase、review docs、問 clarifying questions，最後產生 Markdown plan，裡面包含 file paths 和 code references。([Cursor](https://cursor.com/blog/plan-mode))

你第一個 prompt 應該是：

```text
你的回答以及中間流程如果需要輸出給我看，可以用中文，但是是繁體中文（ZhTW），儘管我給你的prompt是英文。

We are doing a namespace migration from the upstream package name `utu` to our product package name `nforge`.

Goal:
- Migrate imports such as `from utu.tools.base import ...` to `from nforge.tools.base import ...`
- Prepare the codebase for future product-specific tools under `nforge`
- Preserve runtime behavior
- Avoid breaking tests
- Prefer a staged migration with backward compatibility shims if appropriate

Important:
- Do not edit files yet.
- First inspect the repository and produce a detailed migration plan.
- Identify all references to `utu`, including:
  - Python imports
  - string-based imports
  - importlib usage
  - pyproject.toml / setup.py / setup.cfg
  - package metadata
  - CLI entry points
  - tests
  - docs
  - examples
  - Docker / CI files
  - notebooks
- Identify risky areas and propose a safe order of changes.
- Propose test commands to run after each phase.
- Output the plan as a checklist grouped by commit-sized phases.
```

------

## 第二輪：Agent Mode，但限制範圍

用途：**照 plan 做第一批最安全的改動。**

不要叫它一次改全部。第一批最好只做：

1. 建立 `nforge` package 骨架
2. 保留 `utu` compatibility shim
3. 不大規模改業務邏輯
4. 跑 import smoke test

Prompt：

```text
Execute Phase 1 of the migration plan only.

Scope:
- Create the new `nforge` package namespace corresponding to the current `utu` package structure.
- Add compatibility shims so existing imports from `utu.*` still work.
- Do not update all call sites yet.
- Do not change business logic.
- Do not delete the old `utu` package.
- Add deprecation warnings only if they will not break tests.
- Update only the minimum files needed for the new namespace to import successfully.

After editing:
- Run the smallest relevant import smoke test.
- Show me the diff summary.
- List any files that still reference `utu`.
```

------

# Git branch 怎麼開？

我建議這樣：

```bash
git checkout main
git pull
git status
git checkout -b refactor/namespace-utu-to-nforge
```

如果你們還在產品化早期，也可以叫：

```bash
git checkout -b productization/namespace-utu-to-nforge
```

我比較推薦：

```bash
refactor/namespace-utu-to-nforge
```

因為這件事本質是 **refactor**，不是 feature。它應該保持行為不變，只改 package identity / import path / 架構入口。

------

# 開工前先做安全點

在 branch 開好後，先做一個 baseline tag 或 baseline commit。

```bash
git status
git tag pre-namespace-migration
```

或：

```bash
git commit --allow-empty -m "chore: mark baseline before namespace migration"
```

我更推薦 empty commit，因為團隊比較容易在 branch history 看到。

------

# 整套 SOP

## Phase 0：乾淨工作區

```bash
git status
```

確認沒有未提交變更。
如果有，先 commit 或 stash：

```bash
git stash push -m "wip before namespace migration"
```

------

## Phase 1：Plan Mode 盤點

在 Cursor 用 **Plan Mode**，只讓它產出 plan，不改 code。

目標是得到這種清單：

```text
Phase 1: Create nforge namespace and compatibility shims
Phase 2: Update internal imports from utu.* to nforge.*
Phase 3: Update package metadata and entry points
Phase 4: Update tests and examples
Phase 5: Update docs and remove deprecated paths later
```

這個 plan 可以存成：

```text
docs/migration/namespace-utu-to-nforge.md
```

Cursor 官方也提到 Plan Mode 可以把 plan 存成 Markdown file，作為後續 reference。([Cursor](https://cursor.com/blog/plan-mode))

------

## Phase 2：建立 `nforge`，但先不要砍 `utu`

這是最重要的安全策略。

理想結構：

```text
src/
  nforge/
    __init__.py
    tools/
      __init__.py
      base.py
      utils.py

  utu/
    __init__.py
    tools/
      __init__.py
      base.py
      utils.py
```

舊的 `utu` 先保留，但變成 shim：

```python
# utu/tools/base.py

from nforge.tools.base import AsyncBaseToolkit
```

如果要加 warning：

```python
import warnings

warnings.warn(
    "utu.tools.base is deprecated. Use nforge.tools.base instead.",
    DeprecationWarning,
    stacklevel=2,
)

from nforge.tools.base import AsyncBaseToolkit
```

這樣新 code 可以用：

```python
from nforge.tools.base import AsyncBaseToolkit
from nforge.tools.utils import register_tool
```

舊 code 暫時也不會壞：

```python
from utu.tools.base import AsyncBaseToolkit
```

------

## Phase 3：跑最小測試

先不要全測。先跑 import smoke test。

```bash
python -c "from nforge.tools.base import AsyncBaseToolkit; print(AsyncBaseToolkit)"
python -c "from nforge.tools.utils import register_tool; print(register_tool)"
python -c "from utu.tools.base import AsyncBaseToolkit; print(AsyncBaseToolkit)"
```

如果專案是 `src` layout，可能要先：

```bash
pip install -e .
```

然後跑：

```bash
python -m pytest tests -q
```

或你們專案自己的測試命令。

------

## Phase 4：第一個 commit

如果 Phase 1 成功，馬上 commit。

```bash
git add .
git commit -m "refactor: introduce nforge namespace with utu compatibility shims"
```

這個 commit 很重要。
它是你的第一個安全回復點。

------

## Phase 5：再叫 Cursor 改 internal imports

第二個 Agent prompt：

```text
Execute Phase 2 of the migration plan only.

Goal:
- Update internal project imports from `utu.*` to `nforge.*`.
- Do not change public compatibility shims yet.
- Do not delete `utu`.
- Do not change unrelated formatting.
- Do not rename concepts outside import paths unless required.
- Preserve behavior.

Rules:
- Update Python imports.
- Search for string-based references like "utu.tools" and update only when they clearly refer to our package.
- Be careful with Python's standard library `utu`. Do not replace imports like `from utu import ABC, abstractmethod`.
- After edits, run:
  - import smoke tests
  - project unit tests if available
- Show unresolved references to `utu` and classify them as:
  1. should remain because they refer to Python stdlib utu
  2. compatibility shim
  3. docs/examples to update later
  4. suspicious unresolved reference
```

這句非常重要：

```text
Do not replace imports like `from utu import ABC, abstractmethod`.
```

因為 Python 標準庫真的有 `utu`。你的 migration 很容易誤殺標準庫 import。

------

## Phase 6：第二個 commit

```bash
git add .
git commit -m "refactor: migrate internal imports to nforge namespace"
```

------

## Phase 7：改 package metadata

第三個 Agent prompt：

```text
Execute Phase 3 only.

Goal:
- Update package metadata from `utu` to `nforge` where appropriate.
- Review and update:
  - pyproject.toml
  - setup.py
  - setup.cfg
  - package discovery config
  - CLI entry points
  - importlib metadata
  - README install/import examples
  - CI references
  - Docker references

Important:
- Do not change runtime logic.
- If package name and import namespace differ, call that out explicitly.
- After editing, run package/build checks if available.
- Show the final package/import structure.
```

然後測：

```bash
pip install -e .
python -c "import nforge; print(nforge)"
python -c "from nforge.tools.base import AsyncBaseToolkit; print(AsyncBaseToolkit)"
pytest -q
```

commit：

```bash
git add .
git commit -m "chore: update package metadata for nforge namespace"
```

------

## Phase 8：改 docs、examples、toolkits

第四個 Agent prompt：

```text
Execute Phase 4 only.

Goal:
- Update docs, examples, and toolkit templates to use the new `nforge` namespace.
- Update examples like:
  `from utu.tools.base import AsyncBaseToolkit`
  to:
  `from nforge.tools.base import AsyncBaseToolkit`

Important:
- Do not modify core runtime logic.
- Do not remove compatibility shims.
- Keep any upstream license attribution intact.
- After editing, search for remaining `utu` references and classify them.
```

commit：

```bash
git add .
git commit -m "docs: update examples to use nforge namespace"
```

------

# 做壞了怎麼修？

## 情況 1：Cursor 改到一半，你還沒 commit

看改了什麼：

```bash
git diff
```

丟掉某個檔案的改動：

```bash
git restore path/to/file.py
```

丟掉全部未提交改動：

```bash
git restore .
```

如果有新增檔案也要清掉：

```bash
git clean -fd
```

完整回到最後一次 commit：

```bash
git reset --hard HEAD
git clean -fd
```

------

## 情況 2：已經 commit 了，但這個 commit 壞掉

回到上一個 commit，保留改動在工作區：

```bash
git reset --soft HEAD~1
```

回到上一個 commit，改動也不要了：

```bash
git reset --hard HEAD~1
```

------

## 情況 3：你已經做了好幾個 commit，想回到 migration 前

如果你有做 baseline tag：

```bash
git reset --hard pre-namespace-migration
```

如果你有做 empty baseline commit，就先看 log：

```bash
git log --oneline
```

然後：

```bash
git reset --hard <baseline_commit_hash>
```

------

## 情況 4：已經 push 給別人了

不要隨便 `reset --hard` 再 force push。
比較安全是 revert：

```bash
git revert <bad_commit_hash>
```

或 revert 一段：

```bash
git revert <oldest_bad_commit>^..<newest_bad_commit>
```

------

# 做好了怎麼切？

## 如果你們用 GitHub / GitLab

完成後：

```bash
git push -u origin refactor/namespace-utu-to-nforge
```

然後開 PR / MR。

PR 標題：

```text
Refactor: migrate namespace from utu to nforge
```

PR description 可以寫：

```text
## Summary

This PR introduces the new `nforge` package namespace and migrates internal imports from the upstream `utu` namespace to `nforge`.

## Changes

- Added `nforge` namespace package
- Preserved `utu` compatibility shims
- Migrated internal imports to `nforge.*`
- Updated package metadata
- Updated docs and examples

## Safety

- `utu.*` compatibility imports are still supported
- Python stdlib `utu` imports were not modified
- Tests/import smoke checks pass

## Follow-up

- Remove `utu` compatibility shims in a future breaking-change release
- Update external integration docs
```

------

# Cursor 裡面要不要用 Auto-review / YOLO 類模式？

對你這種 migration，我的建議是：

| 階段                | Cursor 模式                     |
| ------------------- | ------------------------------- |
| 盤點                | **Plan Mode**                   |
| 建 `nforge` 骨架    | **Agent，手動 review**          |
| 改 internal imports | **Agent，分批改**               |
| 跑測試              | 可以讓 Agent 跑，但要你 approve |
| 大量 docs/examples  | Agent 可以比較放手              |
| 最後 review         | 你自己看 diff + 測試            |

Cursor 2026 年 5 月的 changelog 有提到 **Auto-review Run Mode**，它允許 Cursor 做更長工作、減少 approval prompts，並對 shell / MCP / fetch tools 做 allowlist、sandbox 或分類判斷。([Cursor](https://cursor.com/changelog))
但我不建議你在第一輪 namespace migration 就完全放手。這種任務最怕「看起來都改了，但某些 dynamic import / package metadata 壞掉」。

------

# 最重要的 Cursor 規則

你可以在 `.cursor/rules` 或 Cursor project rules 裡加一條 migration rule。Cursor 官方 docs 說 Rules 可以放 persistent instructions，包括 Project、Team、User Rules 與 AGENTS.md。([Cursor](https://cursor.com/docs/rules?utm_source=chatgpt.com))

可以加這段：

```text
During the utu-to-nforge namespace migration:

- Treat `utu` as the old upstream package namespace.
- Treat `nforge` as the new product package namespace.
- Do not replace Python standard library imports:
  - from utu import ABC
  - from utu import abstractmethod
  - import utu when it clearly refers to Python stdlib
- Prefer backward-compatible shims over deleting old modules.
- Do not change business logic during namespace migration.
- Keep changes commit-sized and easy to review.
- After edits, run import smoke tests and list remaining references to `utu`.
```

------

# 搜尋指令也要給 Cursor 跑

你可以叫 Cursor 跑：

```bash
rg "from utu\.|import utu\.|utu\.tools|\"utu\.|'utu\." .
```

也要檢查：

```bash
rg "importlib|entry_points|console_scripts|packages|package_data|find_packages|utu" pyproject.toml setup.py setup.cfg src tests docs examples .github Dockerfile
```

但注意，這個搜尋會抓到 Python 標準庫 `utu`，不能全部替換。

------

# 我的建議切法：四個 commit，不要一個大爆炸 commit

最佳 commit 結構：

```text
1. refactor: introduce nforge namespace with utu compatibility shims
2. refactor: migrate internal imports to nforge namespace
3. chore: update package metadata for nforge namespace
4. docs: update examples to use nforge namespace
```

這樣壞掉時很好 rollback。

不要做成：

```text
refactor: rename utu to nforge everywhere
```

這種超大 commit 很難 review，也很難修。

------

# 你的 Toolkit 範例，最後應該長這樣

```python
import json

from nforge.tools.base import AsyncBaseToolkit
from nforge.tools.utils import register_tool


class MyFactoryToolkit(AsyncBaseToolkit):
    def __init__(self, config=None):
        super().__init__(config)

    @register_tool
    def get_equipment_status(self, equipment_id: str) -> str:
        """查詢設備目前運行狀態與最近保養紀錄。"""
        return json.dumps(query_mes(equipment_id))
```

------

# 最短 SOP 總結

```bash
git checkout main
git pull
git checkout -b refactor/namespace-utu-to-nforge
git commit --allow-empty -m "chore: mark baseline before namespace migration"
```

然後在 Cursor：

```text
1. Plan Mode：只盤點，不改 code
2. Agent：建立 nforge + utu compatibility shim
3. Test
4. Commit
5. Agent：分批改 internal imports
6. Test
7. Commit
8. Agent：改 metadata / docs / examples
9. Test
10. Commit
11. Push branch
12. Open PR
```

你這件事的原則是：

> **先讓新舊 namespace 共存，再逐步把內部 code 遷到新 namespace，最後才考慮移除舊 namespace。**

這樣最安全，也最像專業的 library migration。