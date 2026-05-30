# NeurForge — 產品概覽與能力清單

> **版本**：v0.1.0-baseline（2026-05-25）
> **用途**：產品 Pitch 素材、功能盤點、未來規劃參考
> 本文件忠實記錄目前已實作的能力，不誇大，不預設。

---

## 目錄

- [一、公司與產品定位](#一公司與產品定位)
- [二、NeurForge 平台核心能力](#二neurforge-平台核心能力)
- [三、旗艦工業場景 Agent](#三旗艦工業場景-agent)
  - [3.1 廠務通 — 工廠智慧助理](#31-廠務通--工廠智慧助理)
  - [3.2 機況先知 — 預測性維護專家](#32-機況先知--預測性維護專家)
  - [3.3 案件偵探 — 客服案件分析師](#33-案件偵探--客服案件分析師)
- [四、Agent 技術架構詳解](#四agent-技術架構詳解)
- [五、通用型 Agent 能力庫](#五通用型-agent-能力庫)
  - [5.1 SVG 生成 Orchestrator](#51-svg-生成-orchestrator)
  - [5.2 資料分析 Pipeline](#52-資料分析-pipeline)
  - [5.3 GAIA 多工評測框架](#53-gaia-多工評測框架)
  - [5.4 論文收集與摘要](#54-論文收集與摘要)
  - [5.5 PowerPoint 生成](#55-powerpoint-生成)
  - [5.6 檔案管理 Agent](#56-檔案管理-agent)
  - [5.7 RAG 知識庫問答](#57-rag-知識庫問答)
  - [5.8 Gmail 整合 Agent](#58-gmail-整合-agent)
  - [5.9 網路研究 Agent](#59-網路研究-agent)
  - [5.10 程式碼執行 Agent](#510-程式碼執行-agent)
  - [5.11 MCP 整合示範](#511-mcp-整合示範)
- [六、Simple 積木 Agent 一覽](#六simple-積木-agent-一覽)
- [七、願景與未來路線圖](#七願景與未來路線圖)

---

## 一、公司與產品定位

| 欄位 | 內容 |
|------|------|
| 公司（英） | IIoTFab Inc. |
| 公司（中） | 薈智創新科技股份有限公司 |
| 產品（英） | NeurForge |
| 產品（中） | 薈智神鑄 |
| 定位 | 工業 AI Agent 開發與部署平台 |
| 目標市場 | 製造業、電信業、企業 IT，任何需要 AI 輔助決策的場景 |

**NeurForge 解決什麼問題？**

傳統工廠和企業累積了大量的設備資料、工單紀錄、SOP 文件、客戶案件，卻長期困在「資料在系統裡，知識在老師傅腦子裡」的困境。NeurForge 把 LLM 的語言理解能力與企業既有資料系統連接，讓工程師、客服、管理者可以用自然語言直接取得答案，Agent 自動呼叫工具、交叉比對資料、給出具體建議——不再需要跨系統手動查詢。

---

## 二、NeurForge 平台核心能力

### 2.1 自然語言驅動工具呼叫

Agent 讀懂使用者的問題後，自主決定呼叫哪些工具、呼叫幾次、以什麼順序。不需要使用者知道工具名稱或資料格式：

```
使用者：「COMP-102R-B 最近狀況怎樣，有沒有需要注意的地方？」

Agent 自動執行：
  1. get_heartbeat_snapshot()          → 掌握整廠 HPI 快照
  2. get_hpi_history("COMP-102R-B")   → 拉出 20 週 HPI 趨勢
  3. get_sensor_trends("COMP-102R-B") → 找出偏差測點
  4. search_failure_cases("出口溫度 電流 壓力下降")  → 查老師傅知識庫
  5. get_maintenance_history("COMP-102R-B")  → 核查上次保養時間

最後整合五個工具的輸出，給出「繼續觀察 / 排程檢查 / 緊急停機」的建議。
```

### 2.2 快速搭建領域 Agent

新增一個領域 Agent 只需要三件事：

1. **寫一個 Toolkit class**（Python）— 把資料庫查詢、API 呼叫、計算邏輯包成帶有 `@register_tool` 裝飾器的方法
2. **寫一個 Agent config**（YAML）— 定義 Agent 名稱、instructions、使用哪些 toolkit
3. **執行入口**（Python 2–3 行）— 呼叫 `run_chat_agent()` 或 `run_web_agent()`

```python
# 一個完整的 Toolkit 骨架
from neurforge.tools.base import AsyncBaseToolkit
from neurforge.tools.utils import register_tool

class MyFactoryToolkit(AsyncBaseToolkit):
    def __init__(self, config=None):
        super().__init__(config)

    @register_tool
    def get_equipment_status(self, equipment_id: str) -> str:
        """查詢設備目前運行狀態與最近保養紀錄。"""
        # 連到 MES / 資料庫 / 任何資料源
        return json.dumps(query_mes(equipment_id))
```

```yaml
# configs/agents/simple/my_agent.yaml
agent:
  name: 我的廠務 Agent
  instructions: |
    你是廠務專家，擅長查詢設備狀態...
toolkits:
  my_factory:
    mode: customized
    customized_filepath: examples/my_agent/tools/my_toolkit.py
    customized_classname: MyFactoryToolkit
```

### 2.3 Orchestrator 模式：多 Agent 協同

複雜任務可以用 Orchestrator 模式，由主 Agent 規劃，分派給多個專業 sub-agent 執行，最後彙整報告：

```
User: 「幫我分析這份 CSV 銷售數據，生成視覺化 HTML 報告」

OrchestratorAgent 規劃：
  → SearchAgent：查詢行業背景資料
  → DataAnalysisAgent：執行 Python 分析 CSV，產出統計結果
  → HTMLGenerator：把分析結果轉成 Bento Grid 視覺化 HTML

最終輸出完整 HTML 報告
```

### 2.4 MCP（Model Context Protocol）整合

支援三種 MCP transport 模式接入外部系統：
- **stdio**：本地工具（ncnn 視覺模型、file manager）
- **SSE**：遠端服務（RAGFlow 知識庫、自建後端）
- **Streamable HTTP**：HTTP 串流服務

任何符合 MCP 規範的工具，Agent 可以直接使用，不需要修改 Agent 程式碼。

### 2.5 可觀測性（Observability）

內建 OpenTelemetry tracing，每一個 tool call、LLM 呼叫都有 span 記錄。支援接入：
- Phoenix（本地觀測）
- Langfuse（雲端，開源）
- 任何 OTel-compatible backend

### 2.6 多 LLM 後端支援

只要 LLM 提供 OpenAI-compatible API，即可接入：
- GPT-4o / GPT-4o-mini
- Claude（via 相容層）
- DeepSeek v3 / v2.5
- 任何開源模型（Ollama, vLLM）
- 企業私有部署模型

---

## 三、旗艦工業場景 Agent

以下三個 Agent 是 NeurForge v0.1.0 的核心展示，配備完整的模擬資料，可以立即 demo。

---

### 3.1 廠務通 — 工廠智慧助理

> **定位**：工廠日常運維的第一線 AI 助手，回答工程師、生產主管的各類廠務問題

**適用場景**：水泥廠、紡織廠、電廠、化工廠等製造業

**已服務的虛構客戶（模擬資料）**：亞東水泥、東豐纖維、煉研所觸媒研發中心、中鋁集團

#### 能做什麼

| 能力 | 說明 |
|------|------|
| 設備查詢 | 查設備位置、製造商、負責團隊、最近保養日期 |
| 工單查詢 | 查故障維修紀錄、預防保養歷史、異常處置結果 |
| 異常紀錄 | 查設備異常事件、感測器數值、是否已解決 |
| SOP 搜尋 | 搜尋作業程序文件、安全注意事項、執行步驟 |
| 製程參數 | 水泥強度預測、紡織定型機設定、電廠效率分析 |
| 品質預測 | 輸入轉速/水灰比/攪拌時間，預測水泥坍度和 28 天強度 |

#### 工具清單（8 個）

```
get_equipment_info(equipment_id)
  → 設備基本資料（位置、製造商、負責團隊、上次保養）

query_work_orders(equipment_id, status)
  → 工單篩選（已完成 / 進行中 / 待處理）

get_anomaly_records(equipment_id, resolved)
  → 異常紀錄（resolved: true/false 篩選）

search_sop(keyword)
  → SOP 文件全文搜尋

get_process_params(facility_type)
  → 製程參數表（cement / textile / power_plant）

predict_cement_quality(rpm, water_ratio_pct, mixing_time_min)
  → 預測水泥坍度（mm）和 28 天抗壓強度（MPa）

get_stenter_setting(fabric_code)
  → 依布料代碼查定型機溫度/速度設定

get_power_plant_trend(months)
  → 電廠熱效率、鍋爐效率、發電量趨勢
```

#### Demo 對話範例

```
Q: 亞東水泥的磨碎機 GR-001 最近有什麼工單？
A: [呼叫 query_work_orders("GR-001")]
   目前有 3 張工單：WO-2025-0341（進行中，更換磨球）、
   WO-2025-0287（已完成，軸承潤滑）、WO-2025-0210（已完成，清潔）

Q: 轉速 72rpm、水灰比 42%、攪拌時間 180 秒的配比，水泥品質預估如何？
A: [呼叫 predict_cement_quality(72, 42, 180)]
   預估坍度：185mm（符合 SC 級要求）
   預估 28 天強度：47.3 MPa（高於標準 42.5 MPa）
   建議：此配比適合高強度結構混凝土，可進入試拌程序。
```

---

### 3.2 機況先知 — 預測性維護專家

> **定位**：石化廠設備健康監控與預測性維護（PdM）的 AI 主治醫師

**適用場景**：石化廠、電廠、任何配備 SCADA / PI System 的高價值設備群

**監控設備（模擬）**：
- COMP-102R-A / B / S — 往復式壓縮機（A台/B台/備用台）
- COMP-101C — 離心式壓縮機
- REACT-201 — 氫裂解觸媒反應器

#### 核心技術概念

**PRiSM 系統**：Process Reliability integrated Sensing and Monitoring
- **MSET**（Multivariate State Estimation Technique）：多變量感測器評估，建立設備正常行為基準線
- **MDS**（Multidimensional Similarity）：多維度相似度，量化偏離程度
- **HPI**（Health Performance Index）：健康績效指數，OMR 偏差的反向指標

```
HPI 100 = 完全正常
HPI  70 = 警戒（Warning）→ 排程檢查
HPI  50 = 警報（Alarm）  → 緊急評估
```

每日 06:00 自動產生**心跳掃描快照**，標示所有設備目前狀態。

#### 工具清單（10 個）

```
get_heartbeat_snapshot()
  → 所有設備最新 HPI + 警示摘要，快速掌握整廠狀況

get_equipment_list()
  → 廠區設備基本資料（ID、名稱、類型、規格、安裝日期）

get_sensor_tags(equipment_id)
  → 指定設備 PI Tag 清單 + 正常操作範圍

get_hpi_history(equipment_id, weeks=20)
  → HPI 週趨勢圖（找出惡化起點）

get_sensor_trends(equipment_id, weeks=8)
  → 各測點週均值趨勢（識別偏差測點）

search_failure_cases(symptom_keywords)
  → 老師傅知識庫搜尋（歷史故障模式比對）

get_maintenance_history(equipment_id)
  → 維護工單歷史（PM / 預測性維護 / 緊急搶修）

get_catalyst_status()
  → REACT-201 觸媒活性指數 + 衰退趨勢 + 更換時程預測

get_catalyst_history(months=18)
  → 觸媒活性月度歷史（每月下降速率）

get_catalyst_replacement_sop()
  → 觸媒更換 SOP + 作業程序 + 安全注意事項 + 費用估算
```

#### 六步診斷原則

1. `get_heartbeat_snapshot()` — 掌握整廠狀況，確認哪台設備 HPI 下降
2. `get_hpi_history()` + `get_sensor_trends()` — 確認惡化起點、識別偏差測點
3. `search_failure_cases()` — 與老師傅知識庫比對，找出最相似歷史故障模式
4. `get_maintenance_history()` — 核查上次保養時間與過往處置
5. 整合分析 — 給出**繼續觀察 / 排程檢查 / 緊急停機**建議，引用具體數值
6. 觸媒問題額外步驟：`get_catalyst_status()` → `get_catalyst_history()` → `get_catalyst_replacement_sop()`

#### Demo 對話範例

```
Q: 今天廠區整體狀況怎樣？
A: [呼叫 get_heartbeat_snapshot()]
   ⚠ 警戒：COMP-102R-B HPI 68（↓ 低於 70 警戒線）
   ✓ 正常：COMP-102R-A HPI 94, COMP-101C HPI 89, REACT-201 HPI 82
   建議：立即深查 COMP-102R-B

Q: 深查 COMP-102R-B
A: [呼叫 get_hpi_history + get_sensor_trends + search_failure_cases]
   HPI 自第 14 週起持續下降（94→68），偏差測點：
   - 出口溫度：+12°C（超出正常範圍）
   - 電流：+8%
   - 壓力差：-5%
   比對知識庫：與 2022-Q3 Case #FL-019「活塞環磨損」高度相似
   建議：排程 72 小時內停機檢修，預計工時 6 小時
```

---

### 3.3 案件偵探 — 客服案件分析師

> **定位**：電信業（可推廣至任何 B2C 行業）客服分析 AI，整合多系統資料快速釐清申訴根因

**適用場景**：電信業客服、保險理賠、銀行客訴、任何需要跨系統整合客戶資料的客服場景

**已模擬的電信方案**：
| 方案 | 速度 | 月租 | SLA |
|------|------|------|-----|
| FBB-500 | 光纖 500M | NT$599 | 99.5% |
| FBB-1G | 光纖 1Gbps | NT$899 | 99.7% |
| MOB-5G | 5G 30GB | NT$799 | 98.5% |
| BIZ-FBB | 企業光纖 10G | NT$3,500 | 99.9% |

#### 工具清單（10 個）

```
get_customer_profile(customer_id)
  → 客戶基本資料、方案、合約到期、VIP 等級

search_customer_by_name(name)
  → 以姓名搜尋（支援部分比對）

get_billing_history(customer_id, months=6)
  → 帳單紀錄（基本費、加收費用、繳款狀態）

get_complaint_cases(customer_id)
  → 所有申訴案件（開放 + 已結案）

get_case_detail(case_id)
  → 單一案件完整詳情（時間線、處置記錄、負責人）

get_sla_records(customer_id, months=6)
  → SLA 達成紀錄（可用率、延遲、封包遺失率）

get_speed_test_logs(customer_id)
  → 測速記錄（含 below_guarantee 旗標）

lookup_construction(district)
  → 附近施工工程（可能影響網路品質的原因）

get_followup_tasks(customer_id, case_id)
  → 後續追蹤任務（含逾期任務主動提示）

search_knowledge_base(keywords)
  → 客服知識庫（補償政策、SLA 規則、升級流程）
```

#### 七大分析原則

1. 先確認客戶身份與方案
2. 多面向交叉比對：帳單異常 ↔ 系統記錄 ↔ SLA 數據 ↔ 施工因素
3. 引用具體數字（案件編號、帳單金額、SLA 百分比）
4. 判斷補償條件前，先查知識庫確認政策
5. 主動提示逾期的後續追蹤任務
6. 同一問題重複申訴→ 建議是否升級處理
7. 明確建議：退費金額、補償方式、是否需到府維修、是否升級

#### Demo 對話範例

```
Q: 客戶陳大明說他上個月帳單多收了，我要怎麼處理？
A: [呼叫 search_customer_by_name("陳大明")]
   找到：C001234，FBB-1G 方案（NT$899/月），VIP 金卡

   [呼叫 get_billing_history + get_complaint_cases + get_sla_records]
   發現：
   - 5 月帳單 NT$1,249（較平常多 NT$350，加收「超量數據費」）
   - 申訴 CASE-2025-0891（開放中，已 5 天未處理）
   - SLA 5 月達成率 98.3%（低於 FBB-1G 的 99.7% 保證）

   [呼叫 search_knowledge_base("FBB SLA 補償")]
   結論：
   - 超量費用建議核查是否為系統誤計（有 pending 追蹤任務已逾期）
   - SLA 未達 → 依政策可退 1 日月租（約 NT$30）
   - 建議：優先處理逾期追蹤任務，致電客戶說明
```

---

## 四、Agent 技術架構詳解

### 4.1 三種 Agent 模式

```
SimpleAgent
  ├── 單一 Agent，單回合推理
  ├── 適合：明確工具集 + 領域問答
  └── 例：廠務通、機況先知、案件偵探

OrchestratorAgent
  ├── 主 Agent（規劃）→ Sub-agents（執行）→ Reporter（彙整）
  ├── 適合：多步驟、跨領域任務
  └── 例：SVG 生成、資料分析 Pipeline

WorkforceAgent
  ├── 任務分解 → 並行 Worker → 整合結果
  ├── 適合：大量平行子任務
  └── 例：GAIA 評測、廣域研究
```

### 4.2 Toolkit 系統設計

```python
# 外部資料源連接的標準模式
class MyToolkit(AsyncBaseToolkit):
    def __init__(self, config=None):
        super().__init__(config)

    @register_tool
    def tool_name(self, param: str) -> str:
        """
        工具說明（這段 docstring 直接成為 LLM 看到的 tool description）。
        
        Args:
            param: 參數說明
        """
        return json.dumps(...)
```

**關鍵機制**：
- `@register_tool` 設定 `_is_tool = True`，才會被 `AsyncBaseToolkit.tools_map` 識別
- Docstring 的第一行成為 tool 的功能描述，傳給 LLM
- Args section 的說明成為每個參數的 description
- LLM 自主決定呼叫順序和次數，不需要預設工作流程

### 4.3 Config 系統（YAML）

```yaml
# 完整 Agent config 範例
agent:
  name: 廠務通
  instructions: |
    你是廠務通，一位熟悉多種製造業場景的工廠智慧助理...

toolkits:
  industrial_qa:
    mode: customized                               # 使用外部 class
    customized_filepath: examples/.../toolkit.py   # toolkit 檔案路徑
    customized_classname: IndustrialQAToolkit       # class 名稱

model:
  model_provider:
    type: chat.completions
    model: ${NEURFORGE_LLM_MODEL}
    base_url: ${NEURFORGE_LLM_BASE_URL}
    api_key: ${NEURFORGE_LLM_API_KEY}

max_turns: 50    # 最大推理輪次
```

### 4.4 支援的 LLM 後端

任何符合 OpenAI API 規範的模型：

| 類型 | 例子 |
|------|------|
| OpenAI | GPT-4o, GPT-4o-mini |
| Anthropic（相容層） | Claude Sonnet, Opus |
| DeepSeek | deepseek-v3.2, deepseek-chat |
| 本地開源 | Ollama, vLLM, LM Studio |
| 企業私有部署 | 任何 OpenAI-compatible 端點 |

### 4.5 Web UI 技術

- **前端**：React 18 + TypeScript，Vite 打包
- **通訊**：WebSocket（即時串流 Agent 思考與工具呼叫過程）
- **設計**：Linear 風格深色 sidebar + Claude.ai 暖奶油工作區
- **圖示**：Lucide React（統一線條風格）
- **字型**：Inter（Google Fonts）
- **多語**：react-i18next（繁體中文 / English）

---

## 五、通用型 Agent 能力庫

以下是除了三個工業場景 Agent 之外，系統內建的通用型 Agent。這些是真實可用的功能，但對應的展示資料和使用者介面完善程度不一。

---

### 5.1 SVG 生成 Orchestrator

**入口**：`examples/svg_generator/main_web.py`（這也是 v0.1.0 的 Web UI 預設展示）

**架構**：OrchestratorAgent，含兩個 sub-agent

| Worker | 功能 |
|--------|------|
| SearchAgent | 用 `search()` + `web_qa()` 查詢主題相關資料 |
| SVGGenerator | 根據研究結果生成 SVG 卡片（1200×800px，小紅書風格） |

**SVG 生成規格**：
- 尺寸：1200×800px 橫式
- 風格：現代極簡，軟漸層背景（淺粉→淺藍）
- 設計元素：圓角卡片、幾何裝飾、清晰可讀的標題層次
- 輸出：完整可用的 SVG 代碼

**Demo 問法**：
```
「畫一張關於台灣智慧製造的 SVG 資訊圖」
「幫我做一張 2025 年 AI 趨勢摘要卡片」
```

---

### 5.2 資料分析 Pipeline

**入口**：`examples/data_analysis/`

**架構**：OrchestratorAgent，含三個 sub-agent

| Worker | 工具 | 功能 |
|--------|------|------|
| SearchAgent | `search()`, `web_qa()` | 查詢行業背景 |
| DataAnalysisAgent | `get_tabular_columns()`, `execute_python_code()` | 讀 CSV，執行 Python 統計分析 |
| HTMLGenerator | LLM | 把分析結果轉成 Bento Grid 視覺化 HTML 報告 |

**能做什麼**：
- 上傳 CSV 資料，Agent 自動理解欄位結構
- 執行描述統計、趨勢分析、異常值識別
- 搜尋行業背景資料補充分析脈絡
- 輸出完整 HTML 報告（含圖表、表格、摘要）

---

### 5.3 GAIA 多工評測框架

**入口**：`examples/gaia/`

**架構**：WorkforceAgent（多工同時進行），這是 NeurForge 中技術難度最高的 Agent 組合

**GAIA 是什麼**：General AI Assistants benchmark，測試 AI 解決需要真實世界工具的複雜任務，包含：
- 網路搜尋 + 深度閱讀
- 文件 / 圖片 / 音訊 / 影片處理
- 推理 + 程式碼執行
- Excel 資料處理

**三個專業 Worker**：

| Worker | Toolkit | 代表能力 |
|--------|---------|---------|
| Web Search Worker | SearchToolkit | `search_google()` 多關鍵字平行搜尋；`multi_query_deep_search()` 深度搜尋；`extract_web_content()` 網頁全文擷取 |
| Document Processing Worker | DocumentProcessingToolkit | 文件 OCR、圖片分析、音訊轉文字、影片理解（多模態） |
| Reasoning + Coding Worker | CodeExecutionToolkit + ExcelToolkit | Python 沙箱執行、Excel 讀寫計算、數學推理 |

**SearchToolkit 進階功能**：
- `parallel_search(queries)` — 多個搜尋同時進行，節省時間
- `multi_query_deep_search(question)` — 自動拆解問題、多角度搜尋、彙整
- `extract_web_content(url)` — 超越 Google 摘要，讀取完整頁面內容

**實際使用場景**：
```
「找出 2023 年諾貝爾物理學獎得主，並查詢他們的主要論文引用數」
「這張圖裡的表格數據是什麼？幫我計算其中的統計指標」
「分析這個 Excel 檔案，找出銷售額最高的三個月份」
```

---

### 5.4 論文收集與摘要

**入口**：`examples/paper_collector/`

**架構**：OrchestratorAgent

| Worker | 功能 |
|--------|------|
| SearchAgent | 從網路搜尋目標領域的論文連結 |
| PaperSummarizeAgent | 逐篇閱讀，提取摘要、方法、結論 |

**工具**：`document` toolkit（document_qa 讀取 PDF/文件）

**適合場景**：
- 快速瀏覽某主題的研究現狀
- 整理文獻，生成摘要清單
- 研究助手：「整理近三年台灣半導體製造 AI 應用的論文」

---

### 5.5 PowerPoint 生成

**入口**：`examples/ppt_gen/`

**Agent 類型**：SimpleAgent + search toolkit

**能做什麼**：
- 接受文件、URL 或主題描述
- 搜尋相關資料
- 輸出 PowerPoint 格式的投影片內容（結構化大綱）

**注意**：目前輸出為結構化內容，與完整 PPTX 渲染尚有距離，需進一步開發才能直接輸出 .pptx 檔案。

---

### 5.6 檔案管理 Agent

**入口**：`examples/file_manager/`

**Agent 類型**：SimpleAgent + bash toolkit

**能做什麼**：
- 批次重新命名檔案
- 整理目錄結構
- 根據規則移動 / 分類檔案
- 任何可以用 shell 指令完成的檔案操作

**Example config 說明**：使用 bash toolkit，允許 Agent 執行 shell 指令，對本地檔案系統進行操作。適合處理「把這個資料夾裡所有 2024 開頭的 CSV 移到 archive/」這類任務。

---

### 5.7 RAG 知識庫問答

**Config**：`configs/agents/examples/rag.yaml`

**架構**：SimpleAgent + RAGFlow MCP

**能做什麼**：
- 連接 RAGFlow 本地知識庫
- 對企業文件、手冊、SOP 等進行問答
- 支援向量搜尋 + LLM 生成回答

**需要**：本地或遠端部署的 RAGFlow 實例。適合「企業知識庫內部問答」場景。

---

### 5.8 Gmail 整合 Agent

**Config**：`configs/agents/examples/gmail.yaml`

**架構**：SimpleAgent + Gmail MCP（stdio transport）

**能做什麼**：
- 讀取、搜尋 Gmail 信件
- 依指示撰寫和發送郵件
- 自動歸類、摘要郵件

**注意**：需要 Gmail OAuth 授權。MCP server 在本地執行，憑證留在本地，不經過第三方。

---

### 5.9 網路研究 Agent

**Config**：`configs/agents/simple/search_agent.yaml`

**架構**：SimpleAgent + search toolkit（search + web_qa）

**工具**：
- `search(query, num_results)` — Google 搜尋
- `web_qa(url, query)` — 針對特定網頁的深度問答

**特色**：明確的繁體中文輸出規則，適合台灣市場的資料搜集任務。

---

### 5.10 程式碼執行 Agent

**Config**：`configs/agents/simple/general_simple_agent.yaml`

**架構**：SimpleAgent + search + python_executor

**工具**：
- `execute_python_code(code)` — 在沙箱執行 Python
- `search()` + `web_qa()` — 查詢資料

**適合**：需要「搜尋 + 計算 + 分析」的複合型任務，例如「查台灣去年 GDP 數字，用 Python 算出人均」。

---

### 5.11 MCP 整合示範

**位置**：`configs/agents/examples/mcp/`

提供三種 MCP transport 的完整範例：

| 範例 | Transport | 說明 |
|------|-----------|------|
| `sse_example.yaml` | SSE | Server-Sent Events，適合遠端服務 |
| `stdio_example.yaml` | stdio | 標準輸入輸出，適合本地工具 |
| `streamablehttp_example.yaml` | Streamable HTTP | HTTP 串流，適合 Web 服務 |

這三個範例是新增 MCP 整合的起點，可以直接 fork 修改為任何外部系統的連接器。

---

## 六、Simple 積木 Agent 一覽

這些是 `configs/agents/simple/` 下的單一 Agent，是組成更複雜 Orchestrator 的積木：

| Agent | 用途 | Toolkit |
|-------|------|---------|
| `base` | 最基礎的對話 Agent，無工具 | 無 |
| `base_search` | 基礎對話 + 網路搜尋 | search |
| `search_agent` | 專業網路研究，繁中輸出 | search |
| `general_simple_agent` | 搜尋 + Python 執行的萬用 Agent | search + python_executor |
| `data_analysis_agent` | 專門分析 CSV/表格資料 + 執行 Python | tabular + python_executor |
| `paper_summarize_agent` | 閱讀學術論文，提取摘要/方法/結論 | document |
| `svg_generator` | 生成 SVG 卡片（小紅書格式，1200×800） | 無（LLM 直接生成） |
| `html_generator` | 生成 HTML 報告（Bento Grid + Framer Motion + Tailwind） | 無（LLM 直接生成） |
| `gaia_web_search` | GAIA 評測用的深度網路搜尋 Worker | search + document_processing |
| `gaia_document_processing` | 多模態文件處理（PDF/圖/音/影） | code_runner + document_processing |
| `gaia_reasoning_coding` | 推理 + Python + Excel 計算 | excel + code_runner + document_processing |
| `chitchat` | 簡單閒聊（搜尋 + Python 備用） | search + python_executor |
| `ncnn` | 連接 NCNN 視覺模型（MCP stdio） | ncnn (MCP) |

---

## 七、願景與未來路線圖

### 近期（Phase 2-B / 2-C）

**MCP 工具生態**：讓任何 MES、SCADA、ERP 系統可以快速接入，而不需要寫大量連接碼。廠區的 PI System、SAP 工單、CMMS 都可以成為 Agent 的工具。

**Human-in-the-Loop**：在 Agent 執行高風險操作（如建議停機、批准採購）前，加入人工審批節點。Agent 提出建議，人類確認後執行。

**Durable Execution**：長時間任務（跨小時、跨天）的中斷恢復能力，Agent 不因 LLM 連線中斷而遺失進度。

### 中期（Phase 2-D / 2-E）

**Observability Dashboard**：每次 Agent 對話的完整 trace，工具呼叫時間、LLM token 消耗、成功/失敗率，讓企業可以評估 ROI。

**FastAPI + SSE 升級**：把底層 WebSocket 伺服器遷移到更現代的 FastAPI + Server-Sent Events 架構，支援更高並發、更容易部署到雲端。

### 長期願景

**從「問答工具」到「自主執行」**：目前的 Agent 主要是「查詢 + 建議」模式，未來可以對接真實的設備控制系統、工單建立 API，讓 Agent 直接執行核准後的動作。

**跨廠知識積累**：多個廠區的 Agent 共享知識庫，一個廠的故障模式可以預防另一個廠的同樣問題。

**垂直深化**：廠務通、機況先知、案件偵探只是開始。電廠調度、化工製程優化、供應鏈預警——每個領域都可以用相同框架快速建立。

---

> 文件最後更新：2026-05-25
> 對應版本：v0.1.0-baseline（git tag）
> 本文件位置：`docs/NEURFORGE_PRODUCT_OVERVIEW.md`
