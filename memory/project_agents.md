---
name: project-agents
description: NeurForge 三個核心 Agent 的命名、定位與對應場景
metadata:
  type: project
---

## NeurForge 三個核心 Agent

| 場景 | 中文名 | 英文 ID | 個性定位 | 狀態 |
|------|--------|---------|---------|------|
| Scenario 2 — 多產業問答 | **廠務通** | `IndustrialQAAgent` | 老練的工廠知識管理員，查設備台帳、工單、SOP、製程參數 | ✅ 已完成 (`feat/scenario2-industrial`) |
| Scenario 1 — PdM 預知保養 | **機況先知** | `SensorSageAgent` | 像老師傅看感測器，偵測溫度/震動/轉速趨勢，預測設備故障 | 🔲 待開發 |
| Scenario 3 — 電信客服調查 | **案件偵探** | `CaseDetectiveAgent` | 查帳單、SLA、網速紀錄、施工資訊，抽絲剝繭找根因，自動 follow-up | 🔲 待開發 |

**Why:** 使用者確認此命名方案（2026-05-24）。三個角色層次：管理員 / 先知 / 偵探。
**How to apply:** 之後開發 Scenario 1/3 時用這些名字命名 agent config 和 instructions。
