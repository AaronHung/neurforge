# NeurForge v0.1.0-baseline — Design & Architecture Specification

> **用途**：這份文件記錄 v0.1.0-baseline 的完整設計決策與實作細節。
> 未來若要拋棄 youtu-agent 框架、從頭重寫，這份 spec 是 UI、互動、Agent 架構的完整參考。
>
> Git tag: `v0.1.0-baseline` (2026-05-25)
> Commit: `5067ebb`

---

## 目錄

1. [品牌識別](#1-品牌識別)
2. [設計語言總覽](#2-設計語言總覽)
3. [色彩系統](#3-色彩系統)
4. [字型系統](#4-字型系統)
5. [Sidebar 設計](#5-sidebar-設計)
6. [工作區（Work Area）設計](#6-工作區work-area設計)
7. [Header](#7-header)
8. [輸入欄（Chat Input）](#8-輸入欄chat-input)
9. [訊息氣泡與 Agent 卡片](#9-訊息氣泡與-agent-卡片)
10. [工具呼叫展開列（Tool Call）](#10-工具呼叫展開列tool-call)
11. [設定齒輪（Settings）](#11-設定齒輪settings)
12. [動畫系統](#12-動畫系統)
13. [圖示系統](#13-圖示系統)
14. [互動設計與快捷鍵](#14-互動設計與快捷鍵)
15. [Agent 架構設計](#15-agent-架構設計)
16. [三個工業場景 Agent](#16-三個工業場景-agent)
17. [Config 分類系統](#17-config-分類系統)
18. [Web UI 技術架構](#18-web-ui-技術架構)
19. [Backend 架構摘要](#19-backend-架構摘要)
20. [從頭重建的建議起點](#20-從頭重建的建議起點)

---

## 1. 品牌識別

| 欄位 | 值 |
|------|-----|
| 產品英文名 | NeurForge |
| 產品中文名 | 薈智神鑄 |
| 公司英文名 | IIoTFab Inc. |
| 公司中文全名 | 薈智創新科技股份有限公司 |
| 公司中文短名 | 薈智創新 |
| Header 顯示文字 | 薈智創新 NeurForge |
| 主要語言 | 繁體中文（台灣慣用語） |
| 目標市場 | 工業 IoT / 智慧製造 / 企業 AI |

**品牌定位**：專業、精緻、工業級。設計風格接近 Linear（深色 sidebar + 乾淨工作區）+ Claude.ai（暖色系、橙色 accent）的融合。

---

## 2. 設計語言總覽

### 靈感來源

| 部分 | 參考對象 | 取用元素 |
|------|---------|---------|
| Sidebar | Linear | 深色背景、精緻字型、三色分類、hover 互動 |
| 工作區背景 | Claude.ai | 暖奶油色 `#f9f6f0`、乾淨留白 |
| 品牌色 | Claude.ai / 自定義 | 橙色 `#d4773a`、`#c8632a` |
| 圖示 | Lucide React | 統一線條風格，`strokeWidth: 1.5~2.0` |
| 字型 | Linear / Notion | Inter（Google Fonts） |

### 設計原則

1. **深色 sidebar × 暖色工作區**：高對比、有層次感，避免全白或全黑的單調
2. **去 emoji 化**：UI chrome 完全用 Lucide icon，emoji 只允許出現在 user 發的訊息內容中
3. **去 Font Awesome**：不再依賴 FA CDN，icon 全部 tree-shaken 進 bundle
4. **Inter everywhere**：包含 sidebar、input、按鈕、訊息，統一字型家族
5. **精緻而非花俏**：動畫只用 glow pulse 和旋轉，不用 bounce、slide 等眼花撩亂效果

---

## 3. 色彩系統

### Sidebar（深色，CSS 變數在 `SideBar.css`）

```css
--sb-bg:            #0f0f12;   /* 最深背景 */
--sb-border:        #22222a;   /* 分隔線 */
--sb-surface:       #16161c;   /* 卡片背景 */
--sb-hover:         #1c1c24;   /* hover 背景 */
--sb-text:          #b0b0c4;   /* 主要文字 */
--sb-text-strong:   #eaeaf4;   /* 強調文字 */
--sb-text-dim:      #6a6a80;   /* 次要文字 */
--sb-accent:        #a78bfa;   /* 全局 accent（紫色） */
--sb-accent-dim:    rgba(167,139,250,0.12);
--sb-accent-border: rgba(167,139,250,0.35);

/* 三色分類系統 */
--cat-mfg:          #22d3ee;   /* cyan-400   — Smart Manufacturing */
--cat-mfg-dim:      rgba(34,211,238,0.10);
--cat-multi:        #f59e0b;   /* amber-400  — Multi-Agent */
--cat-multi-dim:    rgba(245,158,11,0.10);
--cat-single:       #a78bfa;   /* violet-400 — Single Agent */
--cat-single-dim:   rgba(167,139,250,0.10);
```

### 工作區（暖色系，CSS 變數在 `index.css :root`）

```css
--color-bg:             #f9f6f0;   /* 主背景 — 暖奶油 */
--color-text:           #1a1812;   /* 主文字 — 暖近黑 */
--color-border:         #e4dfd6;   /* 邊框 — 暖米 */
--color-subtle-text:    #9e9080;   /* 次要文字 */
--color-accent:         #d4773a;   /* 主 accent — 橙 */
--color-row-hover:      #ede8e0;   /* hover 背景 */

/* 輸入卡片 */
--input-card-bg:        #ffffff;
--input-card-border:    #ddd8cf;
--input-card-radius:    16px;
--input-card-shadow:    0 2px 16px rgba(26,24,18,0.07), 0 1px 3px rgba(26,24,18,0.05);

/* Agent 卡片 */
--agent-bg:             #ffffff;
--agent-border:         #e8e3da;
--agent-name-color:     #b85c28;
--agent-status-color:   #d4773a;

/* 工具呼叫展開內容（取代舊黑底） */
--color-example-bg:     #f2ede6;   /* 暖淡色 */
--color-example-text:   #3a3228;
```

### 深色模式（dark class）

沿用舊 youtu-agent 的 dark mode 變數結構，`body.dark` 覆蓋，未來可依品牌色更新。

---

## 4. 字型系統

**全站字型：Inter**

```html
<!-- index.html 已載入 -->
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet" />
```

```css
body { font-family: 'Inter', system-ui, -apple-system, sans-serif; }
```

| 用途 | Size | Weight |
|------|------|--------|
| Sidebar 分類標籤 | 12px | 600 |
| Sidebar 項目 | 15px | 400 |
| Header 標題 | 1.25rem | 600 |
| 輸入框 placeholder | 14px | 400 |
| 訊息內文 | system default | 400 |
| Badge 文字 | 11.5px | 600 |

---

## 5. Sidebar 設計

**檔案**：`SideBar.tsx` + `SideBar.css`

**寬度**：`--sb-width: 260px`，固定左側，`position: fixed`。

**行為**：
- Desktop（>768px）：永遠顯示，不可關閉
- Mobile（≤768px）：預設收起（`translateX(-100%)`），hamburger 開關，點外側關閉

**區塊結構（由上到下）**：

```
[ New Chat button ]        ← SquarePen icon + 紫色邊框卡片
────────────────
[ AGENT HISTORY ]          ← History icon + 灰色大寫標籤
  item: Cpu icon + name    ← 代替舊的 🐙
────────────────
[ CURRENT CONFIG ]         ← CheckCircle2 icon + 灰色大寫標籤
  [ current card ]         ← 顯示 config 名稱、路徑、subagents
  + Add New Config         ← Plus icon + accent 色連結
────────────────
[ AVAILABLE CONFIGS ]      ← 大寫標籤 + Refresh 按鈕
  [ Search box ]           ← Search icon input
  [ Collapse toggle ]      ← ChevronRight/Down
  ── Smart Manufacturing ──  ← Factory icon + cyan 色
     item item item
  ── Multi-Agent ──         ← Network icon + amber 色
     item item item
  ── Single Agent ──        ← Bot icon + violet 色
     item item item
```

**Active 項目樣式**：
```css
.sb-item.active.cat-mfg    { background: var(--cat-mfg-dim);    color: var(--cat-mfg);    border-left: 2px solid var(--cat-mfg);    }
.sb-item.active.cat-multi   { background: var(--cat-multi-dim);   color: var(--cat-multi);   border-left: 2px solid var(--cat-multi);   }
.sb-item.active.cat-single  { background: var(--cat-single-dim);  color: var(--cat-single);  border-left: 2px solid var(--cat-single);  }
```

**Config list 高度**：`max-height: 420px`，超出可 scroll（約 10 筆）。

**Collapse 狀態**：存在 `localStorage` (`sidebar.availableConfigsCollapsed`)，refresh 後保留。

---

## 6. 工作區（Work Area）設計

**Layout**：
```
body background: #f9f6f0
  └── .chat-container  (max-width: 50rem, margin: auto, offset by sidebar)
        ├── .header-container
        ├── .chat-messages
        ├── ChatInput (fixed bottom)
        └── footer.app-footer (fixed bottom, height ~42px)
```

**背景**：整個工作區用暖奶油色 `#f9f6f0`，沒有 card wrapper，訊息直接浮在背景上。

**訊息列表**：`.chat-messages` 用 `padding: 8px 2em`，flex column，訊息間距靠 `.message` margin。

**Respond placeholder**（思考中）：
```tsx
<div className="respond-placeholder">
  <span className="nf-thinking-dot" />
</div>
```
`.nf-thinking-dot`：9×9px 橙色圓點，`nf-glow-warm` 動畫。

**Example queries**（初始畫面推薦問題）：
- 橙色系 border + 淡橙背景的 chip
- hover 上移 1px + 橙色陰影
- 點擊後填入 input、隱藏 chips

---

## 7. Header

**位置**：`.chat-container` 最頂部，`padding: 1.5rem 0 0.75rem`，居中

**樣式**：
```css
.chat-title {
  font-size: 1.25rem;
  font-weight: 600;
  letter-spacing: -0.01em;
  color: #c8632a;          /* 暖橙色，單一色不用漸層 */
  display: flex;
  align-items: center;
  gap: 0.4em;
}
.title-logo {
  height: 1.5em;
  filter: drop-shadow(0 1px 3px rgba(212,119,58,0.2));
}
```

**JSX**：
```tsx
<h1 className="chat-title">
  <img className="title-logo" src={logoSquareUrl} alt="logo" />
  薈智創新 NeurForge
</h1>
```

**設計考量**：刻意比一般 app 標題小（1.25rem）、低調。橙色讓標題和深色 sidebar 形成暖冷對比，而不是搶戲。

---

## 8. 輸入欄（Chat Input）

**結構**：

```
.chat-input-container  (fixed, bottom: 50px, z-index: 100)
  └── .chat-input-wrapper  ← 白色卡片
        ├── [Paperclip button]  ← 附件
        ├── [input text field]
        └── [Send button]       ← Send icon / nf-send-spinner
```

**卡片樣式**：
```css
.chat-input-wrapper {
  background: #ffffff;
  border: 1px solid #ddd8cf;
  border-radius: 16px;
  box-shadow: 0 2px 16px rgba(26,24,18,0.07), 0 1px 3px rgba(26,24,18,0.05);
  padding: 6px 10px 6px 14px;
}
.chat-input-wrapper:focus-within {
  border-color: rgba(212,119,58,0.45);
  box-shadow: 0 2px 20px rgba(212,119,58,0.10), ...;
}
```

**Send button 狀態**：
- 預設：灰色（subtle）
- 有文字輸入時：橙色（`.send-button--active { color: #d4773a }`）
- 送出中：`<span className="nf-send-spinner" />`（CSS spinner）

**Send 快捷鍵**：`⌘ + Enter`（Mac）/ `Ctrl + Enter`（Windows）。
Enter 單鍵不送出，給 IME 輸入法用（中文、日文等切換選字需要 Enter）。

**Icon**：
| 按鈕 | Lucide icon | size | strokeWidth |
|------|------------|------|-------------|
| Attach | `<Paperclip />` | 16 | 1.8 |
| Send | `<Send />` | 16 | 1.8 |
| File remove | `<X />` | 14 | 2 |
| File uploaded | `<FileText />` | 14 | 1.5 |
| Uploading | `<span className="breathing-circle" />` | CSS dot | — |

---

## 9. 訊息氣泡與 Agent 卡片

**User 訊息**：右對齊，無特別背景色（Linear 極簡風，保留原有）。

**Bot 訊息**：左對齊，無背景，`.markdown-content` 直接在暖色背景上。

**Agent 卡片**（`new_agent` type）：

```tsx
<div className="agent-content">
  <div className="agent-name">
    <Cpu size={14} strokeWidth={1.5} style={{ opacity: 0.6 }} />
    {agentName}
  </div>
  <div className="agent-status">
    {message.inprogress ? 'Initializing...' : 'Ready'}
  </div>
</div>
```

```css
.agent-content {
  background: #ffffff;
  border: 1px solid #e8e3da;
  border-radius: 10px;
  box-shadow: 0 1px 4px rgba(26,24,18,0.05);
  padding: 12px 14px;
}
.agent-name  { color: #b85c28; font-weight: 600; }
.agent-status { color: #d4773a; font-size: 0.9em; }
```

**Agent status dot（思考中）**：
```css
.agent-message[data-inprogress] .agent-status:before {
  animation: nf-glow 1.8s ease-in-out infinite;
}
```

---

## 10. 工具呼叫展開列（Tool Call）

舊版黑色底（`#333`）→ 現在暖淡色：

```css
--color-example-bg:   #f2ede6;   /* 暖淡米 */
--color-example-text: #3a3228;   /* 深暖棕 */
```

**Summary 列右側 icon**（依工具類型動態選）：

| toolName | Lucide icon |
|----------|------------|
| 預設（任何工具呼叫） | `<Wrench />` |
| `web_qa` | `<Globe />` |
| `document_qa` | `<BookOpen />` |
| `search` | `<Search />` |
| `ask_user` | `<MessageSquare />` |
| `final_answer` | `<Lightbulb />` |

全部 `size={13} strokeWidth={1.6} opacity={0.55}`。

**思考中 summary 左側**：CSS `::before` 偽元素，紫色 7×7px 圓點 + `nf-glow` 動畫。
完成後 `::before` 顯示 `✓`（CSS `content: '✓'`）。

---

## 11. 設定齒輪（Settings）

**位置**：`position: fixed; top: 18px; right: 18px; z-index: 100`

**正常狀態**：
```css
.settings-button {
  background: rgba(249,246,240,0.85);   /* 半透明暖白 */
  border: 1px solid #e4dfd6;
  border-radius: 10px;                  /* 非圓形，10px 圓角 */
  width: 34px; height: 34px;
  color: #9e9080;                       /* 灰色，低調 */
  backdrop-filter: blur(4px);
}
```

**Hover**：
```css
.settings-button:hover {
  background: rgba(212,119,58,0.10);
  border-color: rgba(212,119,58,0.35);
  color: #c8632a;                       /* 橙色 */
  transform: rotate(45deg);             /* 旋轉 45° */
  box-shadow: 0 2px 8px rgba(212,119,58,0.15);
  transition: ... cubic-bezier(0.34, 1.56, 0.64, 1);  /* 彈性曲線 */
}
```

**Icon**：`<Settings size={17} strokeWidth={1.6} />`

---

## 12. 動畫系統

### `nf-glow`（思考中 tool call 圓點）
```css
@keyframes nf-glow {
  0%, 100% { box-shadow: 0 0 3px 1px rgba(124,124,248,0.3); transform: scale(0.85); opacity: 0.6; }
  50%       { box-shadow: 0 0 10px 3px rgba(124,124,248,0.65); transform: scale(1.15); opacity: 1; }
}
```
用途：`.message-detail-summary[data-inprogress]:before`（紫色）

### `nf-glow-warm`（思考中 respond placeholder）
```css
@keyframes nf-glow-warm {
  0%, 100% { box-shadow: 0 0 3px 1px rgba(212,119,58,0.3); transform: scale(0.85); opacity: 0.6; }
  50%       { box-shadow: 0 0 10px 3px rgba(212,119,58,0.6); transform: scale(1.15); opacity: 1; }
}
```
用途：`.nf-thinking-dot`（橙色）

### `nf-spin`（送出中 spinner）
```css
@keyframes nf-spin { to { transform: rotate(360deg); } }
.nf-send-spinner {
  width: 15px; height: 15px;
  border: 2px solid rgba(212,119,58,0.25);
  border-top-color: #d4773a;
  border-radius: 50%;
  animation: nf-spin 0.8s linear infinite;
}
```

### `sb-spin`（sidebar refresh 按鈕）
```css
@keyframes sb-spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
```

### `sb-fadein`（sidebar tooltip 出現）
```css
@keyframes sb-fadein {
  from { opacity: 0; transform: translate(4px, -50%); }
  to   { opacity: 1; transform: translate(0, -50%); }
}
```

---

## 13. 圖示系統

**庫**：[Lucide React](https://lucide.dev/)，版本跟隨 `package.json`。

**原則**：
- 全站統一使用 Lucide，不混用 FA 或 emoji
- `strokeWidth` 通常 `1.5`（精緻）或 `2.0`（需要較重視覺）
- 小型 icon（badge 旁、列表）用 `size={12-13}`，中型（按鈕）用 `size={14-17}`

**Icon 對應表（完整）**：

| 位置 | Icon | Size | StrokeWidth |
|------|------|------|-------------|
| New Chat | `SquarePen` | 14 | 2 |
| Agent History | `History` | 11 | 2 |
| Agent History 項目 | `Cpu` | 13 | 1.5 |
| Current Config | `CheckCircle2` | 11 | 2.5 |
| Config 卡片 — MFG | `Factory` | 14 | 1.5 |
| Config 卡片 — Multi | `Network` | 14 | 1.5 |
| Config 卡片 — Single | `Bot` | 14 | 1.5 |
| Add New Config | `Plus` | 13 | 2 |
| Available Configs 標題 | 無 | — | — |
| Refresh | `RefreshCw` | 13 | 2 |
| Search | `Search` | 12 | 2 |
| Search 清除 | `X` | 12 | 2 |
| Collapse/Expand | `ChevronDown` / `ChevronRight` | 12 | 2 |
| Config 列表項目 | `Settings2` | 12 | 1.5 |
| Sub-agents 標籤 | `Users` | 10 | — |
| Agent 卡片名稱 | `Cpu` | 14 | 1.5 |
| Tool call — 預設 | `Wrench` | 13 | 1.6 |
| Tool call — web_qa | `Globe` | 13 | 1.6 |
| Tool call — document_qa | `BookOpen` | 13 | 1.6 |
| Tool call — search | `Search` | 13 | 1.6 |
| Tool call — ask_user | `MessageSquare` | 13 | 1.6 |
| Tool call — final_answer | `Lightbulb` | 13 | 1.6 |
| Settings gear | `Settings` | 17 | 1.6 |
| Attach file | `Paperclip` | 16 | 1.8 |
| Send | `Send` | 16 | 1.8 |
| File remove | `X` | 14 | 2 |
| File uploaded | `FileText` | 14 | 1.5 |

---

## 14. 互動設計與快捷鍵

### 送出訊息
- **觸發**：`⌘ + Enter`（Mac）/ `Ctrl + Enter`（Windows）
- **理由**：Enter 單鍵保留給 IME 輸入法選字（中文、日文）
- **按鈕視覺**：有文字時 Send icon 變橙色；送出中顯示 `nf-send-spinner`

### Sidebar Collapse
- 狀態存 `localStorage.sidebar.availableConfigsCollapsed`
- Search 有輸入時自動展開（即使是 collapsed 狀態）
- Focus search input 時也自動展開

### Tooltip
- Sidebar config 項目：hover 顯示完整路徑
- 使用 `position: fixed` + JS 計算位置（避免 overflow clipping）
- 300ms delay 前不顯示（實際實作依 CSS hover 即顯）

### Config 選擇
- Click sidebar 項目 → `onConfigSelect(config)` → App.tsx 更新 `currentConfig`
- 被選中的項目有 left-border accent + 分類對應色背景

---

## 15. Agent 架構設計

### Config 種類

```
configs/
  agents/
    simple/          ← 單一 Agent（積木）
    examples/        ← 較複雜的多步驟 / 展示用
    orchestra/       ← Orchestrator 模式
    generated/       ← 動態生成的 Agent
  tools/             ← Toolkit 設定
```

### Toolkit 系統

```python
# 正確方式
from utu.tools.base import AsyncBaseToolkit
from utu.tools.utils import register_tool

class MyToolkit(AsyncBaseToolkit):
    def __init__(self, config=None):  # config=None 必須
        super().__init__(config)

    @register_tool                    # 必須用這個，不是 @function_tool
    def my_tool(self, arg: str) -> str:
        """工具說明。"""
        ...
```

```yaml
# config yaml
name: my_toolkit
mode: customized
customized_filepath: examples/my_agent/tools/my_toolkit.py
customized_classname: MyToolkit
```

### Agent Config 基本結構

```yaml
agent_type: simple
agent_name: MyAgent
model:
  model_provider:
    type: chat.completions
    model: ${NEURFORGE_LLM_MODEL}
    base_url: ${NEURFORGE_LLM_BASE_URL}
    api_key: ${NEURFORGE_LLM_API_KEY}
agent:
  name: MyAgent
  instructions: |
    你是 MyAgent...
toolkits:
  my_toolkit:
    ...
```

### Env vars

| `NEURFORGE_*` | 實際用的 `UTU_*` |
|---------------|----------------|
| `NEURFORGE_LLM_TYPE` | `UTU_LLM_TYPE` |
| `NEURFORGE_LLM_MODEL` | `UTU_LLM_MODEL` |
| `NEURFORGE_LLM_BASE_URL` | `UTU_LLM_BASE_URL` |
| `NEURFORGE_LLM_API_KEY` | `UTU_LLM_API_KEY` |
| … 共 19 個 | 見 `utu/__init__.py` |

---

## 16. 三個工業場景 Agent

### SensorSageAgent（機況先知）

**場景**：石化廠預測性維護（PdM）

**10 個工具**：
| 工具名 | 功能 |
|--------|------|
| `get_heartbeat_snapshot` | 所有設備最新 HPI 快照 |
| `get_equipment_list` | 廠區設備基本資料 |
| `get_sensor_tags` | 指定設備 PI Tag 清單 |
| `get_hpi_history` | HPI 歷史趨勢（週）|
| `get_sensor_trends` | 各測點數值趨勢（週）|
| `search_failure_cases` | 老師傅知識庫搜尋 |
| `get_maintenance_history` | 維護工單紀錄 |
| `get_catalyst_status` | 觸媒反應器活性摘要 |
| `get_catalyst_history` | 觸媒月度歷史 |
| `get_catalyst_replacement_sop` | 觸媒更換 SOP |

**核心概念**：HPI（Health Performance Index）100=正常，<70=警告，<50=告警。6 步診斷原則：HPI → 感測器標籤 → 趨勢 → 知識庫 → 維護紀錄 → 建議。

**Mock data 位置**：`examples/sensor_sage/mock_data/`

---

### IndustrialQAAgent（廠務通）

**場景**：廠務一般 Q&A、SOP 查詢、巡檢助理

**Mock data 位置**：`examples/industrial_qa/mock_data/`

---

### CaseDetectiveAgent（案件偵探）

**場景**：電信客服案件分析（可推廣到任何 B2C 客服）

**10 個工具**：
| 工具名 | 功能 |
|--------|------|
| `get_customer_profile` | 客戶基本資料 |
| `search_customer_by_name` | 依姓名搜尋客戶 |
| `get_billing_history` | 帳單歷史 |
| `get_complaint_cases` | 申訴案件清單 |
| `get_case_detail` | 單一案件詳情 |
| `get_sla_records` | SLA 達成紀錄 |
| `get_speed_test_logs` | 網速測試記錄 |
| `lookup_construction` | 工程施工查詢 |
| `get_followup_tasks` | 追蹤任務清單 |
| `search_knowledge_base` | 客服知識庫 |

**Mock data 位置**：`examples/case_detective/mock_data/`

---

## 17. Config 分類系統

Sidebar 根據 config 路徑/名稱自動分三類：

```typescript
const MFG_KEYWORDS = ['sensor_sage', 'industrial_qa', 'case_detective'];
const MULTI_PATTERNS = ['examples/', 'orchestra', 'generated/'];

function getCategory(config: string): 'manufacturing' | 'multi' | 'single' {
  const key = config.toLowerCase();
  if (MFG_KEYWORDS.some(k => key.includes(k))) return 'manufacturing';
  if (MULTI_PATTERNS.some(k => key.includes(k))) return 'multi';
  return 'single';
}
```

| 分類 | 涵蓋 | Icon | 顏色 |
|------|------|------|------|
| Smart Manufacturing | `sensor_sage`, `industrial_qa`, `case_detective` | `Factory` | `#22d3ee` (cyan) |
| Multi-Agent | `examples/` 前綴、`orchestra`、`generated/` | `Network` | `#f59e0b` (amber) |
| Single Agent | 其他（`simple/` 積木、基礎 config） | `Bot` | `#a78bfa` (violet) |

---

## 18. Web UI 技術架構

### 技術棧

| 層 | 技術 | 備註 |
|----|------|------|
| Frontend | React 18 + TypeScript | Vite build |
| 樣式 | Pure CSS（CSS 變數） | 無 Tailwind |
| Icon | Lucide React | Tree-shaken |
| i18n | react-i18next | en / zh-TW / zh |
| WebSocket | react-use-websocket | 與 backend 通訊 |
| Markdown | SafeMarkdown（自包裝） | 含 KaTeX、Mermaid |
| Font | Inter（Google Fonts CDN） | |

### Build 流程

```bash
cd frontend/webui
npm run build          # TypeScript 編譯 + Vite bundle → dist/
bash build.sh          # 把 dist/ 打包進 Python wheel
cd ../..
uv pip install frontend/webui/build/utu_agent_ui-0.3.0-py3-none-any.whl --reinstall
```

Wheel 版本固定在 `0.3.0`（繼承自 upstream），未來重寫可自由定版。

### 主要檔案

```
frontend/webui/src/
  index.css                    ← 全局設計 token + layout
  App.tsx                      ← 根元件，WebSocket 管理，settings modal
  components/
    SideBar.tsx / SideBar.css  ← 左側導航
    ChatInput.tsx              ← 輸入欄
    MessageComponent.tsx       ← 訊息渲染（含 tool call、agent card）
    AgentTOC.tsx               ← Agent 目錄（sidebar 歷史）
    HamburgerButton.tsx        ← Mobile 漢堡按鈕
  i18n/
    locales/zh-TW/common.json  ← 繁體中文字串
    locales/en/common.json     ← 英文字串
  assets/
    logo-square.png            ← Header + Favicon logo
    pic.png                    ← Footer logo
```

### WebSocket Protocol（簡述）

Backend 推送 SSE-like events，格式為 JSON：

```json
{ "type": "text_delta", "content": "..." }
{ "type": "tool_call",  "content": { "toolName": "search", "input": {...}, "output": "..." } }
{ "type": "new_agent",  "content": "AgentName" }
{ "type": "plan",       "content": { "analysis": "...", "steps": [...] } }
{ "type": "report",     "content": "# Final Report..." }
{ "type": "error",      "content": "Error message" }
```

---

## 19. Backend 架構摘要

**目前框架（youtu-agent）**：

```
Tornado WebSocket server
  → utu.runner（OpenAI Agents SDK）
  → Agent config（Hydra/YAML）
  → Toolkit（@register_tool）
  → LLM（任何 OpenAI-compatible API）
```

**Observability**：OpenTelemetry，backend 可選 Phoenix / Langfuse（目前 OTel 設定在，但 endpoint 未設定時會 skip）。

**未來遷移方向**：Tornado → FastAPI + SSE（Phase 2-E）。

---

## 20. 從頭重建的建議起點

> 這節是給「拋掉 youtu-agent 框架從頭寫」時的指引。

### 必須保留的設計決策

1. **色彩系統**：深色 sidebar（`#0f0f12`）+ 暖奶油工作區（`#f9f6f0`）+ 橙色 accent（`#d4773a`）
2. **三色分類系統**：MFG cyan / Multi amber / Single violet，這三色搭配深色背景非常出色
3. **Inter 字型**：全站統一，不要用 system font（效果差很多）
4. **Lucide 圖示**：統一風格，不要混 FA 或 emoji
5. **⌘↵ 送出**：IME 使用者的基本需求，不要改回 Enter
6. **輸入卡片**：白底、圓角 16px、淡陰影，比 pill 更精緻

### 可以改善的地方（已知問題）

1. **訊息氣泡**：User 和 Bot 訊息目前無明顯視覺區分，可以給 user 加淡橙色泡泡
2. **字型大小**：訊息內文依賴 browser default，建議統一到 15px / 16px
3. **Dark mode**：深色模式目前沿用舊 youtu-agent 變數，未來可完整改為 NeurForge 品牌色
4. **Mobile 體驗**：基本可用但未細調，sidebar overlay 動畫還有優化空間
5. **Tooltip**：現在是 JS 計算 `position: fixed`，新框架可用現成 Tooltip library

### 建議技術棧（重寫）

| 層 | 建議 | 理由 |
|----|------|------|
| Backend | FastAPI + SSE | 比 Tornado 現代，原生 async |
| Frontend | React 19 + TypeScript | 維持現有選擇 |
| 樣式 | Tailwind CSS v4 + CSS 變數 | 加速開發，保留 token 系統 |
| Icon | Lucide React | 維持現有選擇 |
| 狀態管理 | Zustand | 比 Context 更適合 chat state |
| WS/SSE | TanStack Query + EventSource | 比 react-use-websocket 更 robust |
| i18n | react-i18next | 維持現有選擇，已有 zh-TW 字串 |

### Agent 系統重建（工具架構）

核心需求：
- Toolkit class → tools 自動 registry（不手動列 tool list）
- `mode: customized`（外部 class 注入）一定要支援
- Tool 的 docstring 直接當 description 傳給 LLM
- Env var: `NEURFORGE_*` 為主，向下相容 `UTU_*`

---

*文件結束。最後更新：2026-05-25。*
*對應 git tag: `v0.1.0-baseline`，commit `5067ebb`。*
