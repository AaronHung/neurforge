# Agent 試用紀錄與 SOP（pgm-docs）

> 目的：給一套「不用猜、照著做」的 SOP，逐一試用各 agent，並把每一輪的
> 問題／步驟（plan 或工具呼叫）／輸出記成統一格式的教材。
>
> 配套工具：[scripts/try_agent.py](../../scripts/try_agent.py)（可重複執行的試用 harness）。

---

## 0. 紀錄模板（techflow §10 提醒）

每試一個 agent，產生一塊這樣的紀錄（`try_agent.py --out` 會自動產生）：

```markdown
### Agent：`<config 路徑>`
- type：simple / orchestrator
- 啟動方式：<指令>
- 測試問題：
- 執行時間：N 秒
- 工具呼叫 / 計畫(plan)：
  1. ...
- 最終輸出長度：N 字元
- 是否正常產出：是 / 否
- 最終輸出：
```

> simple agent 記「工具呼叫」；orchestrator 記「計畫(plan)」。兩者欄位一致。

---

## 1. SOP：怎麼試用任何一個 agent

### 前置（只做一次）
```bash
cd /Users/aaron/xk8/00_neurforge
uv sync                      # 安裝相依
ls .env                      # 確認 .env 存在且含 NEURFORGE_LLM_API_KEY
```

### 方式 A：自動化試用 + 自動記錄（推薦，給教材用）
固定一行指令，換 `--config` 與 `--question` 即可：
```bash
uv run --env-file .env python scripts/try_agent.py \
  --config simple/sensor_sage_agent \
  --question "你的問題" \
  --out docs/pgm-docs/agent_trials.zh-TW.md
```
- 終端會印出：CONFIG / TYPE / ELAPSED / STEPS（工具或 plan）/ 最終輸出。
- `--out` 會把同樣內容以紀錄格式**附加**到本檔末尾。
- 不帶 `--out` 就只印不寫檔（先試水溫時用）。

### 方式 B：互動式手動試（自己對話、看即時串流）
```bash
# simple agent（機況先知）
uv run --env-file .env python examples/sensor_sage/main.py
# 廠務通
uv run --env-file .env python examples/industrial_qa/main.py
# 案件偵探
uv run --env-file .env python examples/case_detective/main.py
# 通用 CLI（任何 config）
uv run --env-file .env python scripts/cli_chat.py --config_name simple/sensor_sage_agent
```
輸入問題、看回覆，`q` 離開。

### 方式 C：Web UI（看渲染效果，如 SVG）
```bash
uv run --env-file .env python examples/svg_generator/main_web.py
# 開 http://127.0.0.1:8848/index.html
```

### 判讀重點（每輪都看這三項）
1. **STEPS**：simple 看「呼叫了哪些工具、順序對不對」；orchestrator 看「plan 的最後一步是不是該產出的 agent」。
2. **是否正常產出**：最終輸出非空、且符合預期型態（診斷/答案/SVG）。
3. **異常歸因**：沒產出 → 是工具沒被呼叫？資料查不到？還是模型沒整合？（對 SVG 另見 techflow §9）

---

## 2. 建議試用清單與題目（已驗證可跑）

| 順序 | config | 類型 | 建議題目 |
| --- | --- | --- | --- |
| 1 | `simple/sensor_sage_agent` | simple | 做一次全廠健康巡檢，挑最嚴重的設備深入分析並給建議。 |
| 2 | `simple/industrial_qa_agent` | simple | 亞東水泥要預測水泥品質：轉速 12rpm、水灰比 28%、攪拌 90 秒，結果如何？順便查相關 SOP。 |
| 3 | `simple/case_detective_agent` | simple | 客戶 C-10001 一直申訴，幫我釐清根因、判斷是否符合補償，並給處理建議。 |
| 4 | `examples/svg_generator` | orchestrator | （見 techflow §9.5 已記錄） |

---

## 3. 實測紀錄（2026-05-30）

以下由 `scripts/try_agent.py` 實跑自動產生。

> 三輪速覽：sensor_sage 呼叫 8 個工具（107s）、industrial_qa 4 個（56s）、
> case_detective 9 個（53s），三者皆正常產出。詳見 §4 教材重點。

### Agent：`simple/sensor_sage_agent`
- type：simple
- 啟動方式：`uv run --env-file .env python scripts/try_agent.py --config simple/sensor_sage_agent --question "..."`
- 測試問題：做一次全廠健康巡檢，挑最嚴重的設備深入分析並給建議。
- 執行時間：107.1 秒
- 工具呼叫：
  1. get_heartbeat_snapshot({})
  2. get_hpi_history({"equipment_id": "COMP-102R-B", "weeks": 20})
  3. get_hpi_history({"equipment_id": "COMP-102R-B"})
  4. get_sensor_trends({"equipment_id": "COMP-102R-B", "weeks": 8})
  5. get_sensor_tags({"equipment_id": "COMP-102R-B"})
  6. search_failure_cases({"symptom_keywords": "出口溫度上升 電流上升 壓力下降"})
  7. search_failure_cases({"symptom_keywords": "往復式壓縮機 溫度 電流 壓力"})
  8. get_maintenance_history({"equipment_id": "COMP-102R-B"})
- 最終輸出長度：1678 字元
- 是否正常產出：是
- 最終輸出：

```text
根據我獲得的資訊，現在進行綜合分析：

## 📋 **全廠健康巡檢報告**

### 🔍 **當前最嚴重設備：COMP-102R-B（往復式壓縮機 B台）**

**即時狀態（2026年5月24日 06:00）：**
- **HPI：61.1** ⚠️ **警戒狀態**
- **持續異常：** 二級出口溫度、電動機電流持續上升，二級出口壓力持續下降

**關鍵指標異常模式：**
1. **TI2_OUTLET 二級出口溫度**：+6.3°C（從基準141.0°C上升到147.3°C，+4.5%）
2. **II_CURRENT 電動機電流**：+8.2A（從基準158.0A上升到166.2A，+5.2%）
3. **PI2_OUTLET 二級出口壓力**：-0.58MPa（從基準16.4MPa下降到15.82MPa，-3.5%）

### 📊 **故障模式比對分析**

從老師傅知識庫中發現 **2個相關歷史案例**：

**1. CASE-002：騎環（Rider Ring）破損（高嚴重性）**
- **相似度：中高**
- **特徵模式：** 
  - FI_FLOW 下降 -10~-25%
  - II_CURRENT 電流波動加大，平均上升
  - TI2_OUTLET 快速上升 +8~+20°C
- **根因：** 騎環長期磨耗達到設計壽命或因異物進入
- **歷史上同設備曾有：** 2024年8月27日進行壓縮機檢修拆裝

**2. CASE-003：出口閥座洩漏（中嚴重性）**
- **相似度：中**
- **特徵模式：**
  - 出口壓力微降
  - 流量緩慢下降
  - 出口溫度輕微上升
- **根因：** 閥座密封面因高壓衝擊疲勞

### 🔄 **維護歷史分析**

根據維護紀錄，COMP-102R-B **無最近維護紀錄**，這可能意味著：
1. 設備已長時間運轉而無預防性保養
2. 關鍵耗材（如活塞環、閥座）可能已接近或超過預期壽命
3. 上次維護為2024年8月，已超過20個月

### ⚠️ **風險評估與建議**

**當前風險等級：中高風險**

**建議行動：**

**🟡 立即行動（未來7天內）：**
1. **安裝流量監測：** 立即監控 FI_FLOW 是否出現明顯下降趨勢
2. **加強振動監測：** 檢查是否伴隨振動異常（可能是騎環破損徵兆）
3. **每日檢查清單：**
   - 記錄出口溫度每日變化
   - 監控電流波動幅度
   - 確認壓力下降趨勢是否加速

**🟠 規劃性行動（2-4週內）：**
1. **安排預防性檢查：** 建議排定設備全面檢查工單
2. **準備備品：** 提前準備可能需要的耗材（騎環、活塞環組、閥座）
3. **啟用備用機：** 考慮讓 COMP-102R-S（備用台）熱機待命

**🚨 觸發緊急停機條件：**
- 若 FI_FLOW 在48小時內下降 >15%（騎環破損徵兆）
- 若TI2_OUTLET超過150°C（正常上限約145-148°C）
- 若電流超過170A且持續上升

### 📈 **監控重點**

1. **流量監控：** 目前缺乏FI_FLOW數據，應立即補充
2. **趨勢惡化速度：** 關注異常是否加速發展
3. **交叉檢查：** 比對COMP-102R-A正常運轉參數基準值

### 💡 **長期建議**

1. **建立預防性維護計畫：** 往復式壓縮機每12-18個月應進行預防性檢查
2. **強化狀態監測：** 增加振動、油液分析等監測手段
3. **備品庫存管理：** 確保關鍵耗材有足夠庫存

**結論：** COMP-102R-B呈現典型的往復式壓縮機性能衰退模式，最可能為**騎環磨耗或閥座洩漏**。雖然目前未達緊急停機標準，但HPI持續下降且趨勢明確，建議立即規劃2-4週內進行預防性檢查，並密切監控異常指標是否加速惡化。

需要我針對其他設備或觸媒反應器進行進一步分析嗎？
```


### Agent：`simple/industrial_qa_agent`
- type：simple
- 啟動方式：`uv run --env-file .env python scripts/try_agent.py --config simple/industrial_qa_agent --question "..."`
- 測試問題：亞東水泥要預測水泥品質：轉速 12rpm、水灰比 28%、攪拌 90 秒，結果如何？順便查相關 SOP。
- 執行時間：55.9 秒
- 工具呼叫：
  1. predict_cement_quality({"mixing_time_min": 1.5, "rpm": 12, "water_ratio_pct": 28})
  2. search_sop({"keyword": "水泥攪拌"})
  3. search_sop({"keyword": "品質控制"})
  4. search_sop({"keyword": "坍度"})
- 最終輸出長度：807 字元
- 是否正常產出：是
- 最終輸出：

```text
## 水泥品質預測結果

根據您提供的參數：
- **攪拌轉速**：12 rpm
- **水灰比**：28%
- **攪拌時間**：90秒（1.5分鐘）

**預測結果如下：**
1. **預測坍度**：36.6 cm
   - 標準範圍：14-20 cm
   - **不符合要求**（嚴重超標）

2. **預測28天抗壓強度**：11.7 MPa
   - 最低要求：40.0 MPa
   - **不符合要求**（嚴重不足）

3. **整體品質判定**：**不合格**
   - 坍度測試：❌ 失敗
   - 強度測試：❌ 失敗

**工程師建議：**
> "坍度超標，請降低加水率或提升轉速。"

**問題分析：**
- 水灰比28%偏高，造成坍度超過標準近一倍
- 強度僅達要求的29.25%，無法達到結構用水泥的最低強度要求
- 建議調整參數為：水灰比降至18-22%，攪拌轉速提升至15-18 rpm，攪拌時間維持90-120秒

## 相關SOP文件

**找到1份相關SOP：**

**SOP-MIX-001：水泥攪拌機葉片定期檢查作業程序**
- 版本：v3.2（2024年8月1日更新）
- 適用設備：EQ-001、EQ-002
- 檢查頻率：每月一次
- **關鍵步驟**：
  1. 停機上鎖（LOTO程序）
  2. 檢查葉片裂紋、磨損、變形
  3. 確認M16螺栓扭力180 Nm
  4. 測量葉片與桶壁間隙（5±1 mm標準）
  5. 確認主軸轉動無異音
- **重要警告**：葉片螺栓鬆脫可能導致葉片飛脫，嚴禁在攪拌機運轉中進行任何調整

**建議行動：**
1. 立即調整攪拌參數，降低水灰比並提升轉速
2. 進行水泥試拌後重新檢測坍度與強度
3. 定期執行SOP-MIX-001的葉片檢查，確保攪拌機機械狀態正常
4. 聯絡亞東水泥品質團隊進行進一步的參數優化建議
```


### Agent：`simple/case_detective_agent`
- type：simple
- 啟動方式：`uv run --env-file .env python scripts/try_agent.py --config simple/case_detective_agent --question "..."`
- 測試問題：客戶 C-10001 一直申訴，幫我釐清根因、判斷是否符合補償，並給處理建議。
- 執行時間：52.5 秒
- 工具呼叫：
  1. get_customer_profile({"customer_id": "C-10001"})
  2. get_complaint_cases({"customer_id": "C-10001"})
  3. get_billing_history({"customer_id": "C-10001", "months": 12})
  4. get_case_detail({"case_id": "CASE-2026-0518"})
  5. get_followup_tasks({"customer_id": "C-10001"})
  6. search_knowledge_base({"keywords": "超量使用費 退費 政策"})
  7. get_sla_records({"customer_id": "C-10001", "months": 6})
  8. get_speed_test_logs({"customer_id": "C-10001"})
  9. lookup_construction({"district": "新北市板橋區"})
- 最終輸出長度：1418 字元
- 是否正常產出：是
- 最終輸出：

```text
## 📊 案件分析報告：客戶 C-10001（洪欣瑋）

### 🔍 根本原因分析

1. **主要問題：帳單系統重複錯誤**
   - **案件 CASE-2025-0831**：2025年9月帳單出現NT$150超量使用費（錯誤計費），已退費
   - **案件 CASE-2026-0518**：客戶申訴2026年5月帳單「再次」出現同樣費用，但帳單紀錄顯示總金額599元，無超量費
   - **疑點**：客戶可能看到未更新的系統資料或有誤解，需確認實際帳單內容

2. **潛在嚴重問題：連續6個月SLA未達標**
   - 從2025年12月到2026年5月，連續6個月未達99.5%可用率保證
   - 最差月份：2026年5月僅99.33%（缺口0.17%），2026年1月99.34%（缺口0.16%）
   - **客戶未針對此問題申訴**，表示可能不知情或容忍度較高

3. **外部因素：附近施工工程**
   - 板橋文化路地下管線更新工程（2026年3月-7月）
   - 客戶地址位於影響範圍內（文化路二段）
   - 這是造成SLA下降的合理原因

### 📋 待處理事項
- **TASK-2026-0518-01**：帳務系統bug查核（已逾期，應立即處理）
- 客戶不知情的SLA違約補償

### 💰 符合補償條件分析

**依據知識庫政策：**
1. **帳單爭議**：若確認計費錯誤，客服可退費NT$500以內
2. **SLA違約補償**：家庭方案可用率低於保證值，按比例折抵月租費（上限30%）

**SLA補償計算：**
- FBB-500方案：月租NT$599
- 以2026年5月為例：缺口0.17% (99.5% - 99.33%)
- 應補償：599 × (0.17% / 0.5%) = 約NT$204
- 連續6個月總補償估計：約NT$1,200-1,400

### 🎯 處理建議

**立即行動：**
1. **處理逾期任務**：立即聯繫帳務處理組，查核系統是否仍有超量計費bug
2. **主動聯繫客戶**：
   - 釐清2026年5月帳單實際狀況
   - 主動告知SLA未達標情況及可申請補償
   - 說明附近施工工程的影響

**補償方案：**
1. **帳單問題**：若確認系統錯誤，退還NT$150並致歉
2. **SLA違約**：依政策提供6個月補償，總計約NT$1,200-1,400
3. **施工影響**：建議提供一次性補償NT$200-300作為客戶體驗關懷

**預防措施：**
1. **系統修復**：確認帳務系統已完全修正，避免重複問題
2. **施工通知**：加強施工期間的客戶溝通與服務預警
3. **主動監控**：對SLA連續未達標客戶建立主動通報機制

**升級建議：**
- 此客戶信用評分A，屬優質客戶
- 建議提升至VIP客戶，提供專人服務
- 考慮提供方案升級優惠（如升級FBB-1G）

### ⏰ 時程建議
1. **今日內**：處理逾期任務，聯繫客戶釐清帳單問題
2. **3天內**：完成SLA補償計算與申請流程
3. **5天內**：完成所有補償作業，客戶滿意度回訪

**結論：** 客戶C-10001符合多項補償條件，應積極處理以維護客戶關係。主要問題是帳務系統重複錯誤及未主動告知的SLA違約，需立即改善。
```


---

## 4. 觀察小結（教材重點）

把三輪實測拉在一起看，這就是「**會用工具的單一 agent（simple）**」的共同行為樣態，
拿來教學最直觀：

### 4.1 共同流程模式：查資料 → 交叉比對 → 整合建議
| Agent | 起手式（先掌握全局） | 中段（聚焦查證） | 收尾（整合產出） |
| --- | --- | --- | --- |
| sensor_sage | `get_heartbeat_snapshot` 全廠掃描 | HPI 趨勢 + 感測器 + 故障案例 + 維護史 | PdM 診斷報告 + 分級建議 |
| industrial_qa | `predict_cement_quality` 算結果 | 多次 `search_sop` 找作業程序 | 品質判定 + SOP + 行動建議 |
| case_detective | `get_customer_profile` 確認身份 | 帳單/案件/SLA/測速/施工 多源比對 | 根因 + 補償試算 + 處理時程 |

這正好印證三個 agent 的 instructions 裡寫的「**先查再答、引用具體數值、多工具整合**」原則
——模型確實照著系統提示的診斷流程走。

### 4.2 與 orchestrator（SVG）的關鍵差異
- **simple agent 沒有 plan**：它在「同一個 agent」內用 ReAct 迴圈連續呼叫多個工具
  （think→call tool→observe→再想），由 OpenAI Agents SDK 的 Runner 驅動。
- **orchestrator 才有 plan**：把任務拆給「多個不同 agent」依序執行（見 techflow §4）。
- 所以紀錄欄位才分「工具呼叫」(simple) vs「計畫(plan)」(orchestrator)。

### 4.3 觀察到的模型亮點與注意點（教學可討論）
- 亮點：industrial_qa 自動把「90 秒」換算成 `mixing_time_min: 1.5`；case_detective 主動
  發現「逾期任務」與「客戶未申訴的 SLA 違約」，超出字面問題。
- 注意點：這些工具讀的是 `examples/<name>/mock_data/` 的**模擬資料**，數值僅供 demo；
  正式導入需接真實資料源（PI System / MES / 帳務系統）。
- 成本：純本地資料工具的 simple agent 約 50–110 秒（多輪 LLM 呼叫為主），比 orchestrator
  + 網路搜尋（SVG 那輪 ~306s）快很多。

### 4.4 下一步可擴充
- 把 §2 表格的題目換成你培訓現場要 demo 的情境，重跑 `try_agent.py --out` 即可累積教材。
- 想看「畫面/渲染」效果就走方式 C（Web UI）。
- 要對外展示多代理（plan）就用 `examples/svg_generator`（orchestrator）。
