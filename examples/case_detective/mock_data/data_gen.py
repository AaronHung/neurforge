"""
Generate mock data for CaseDetectiveAgent (案件偵探) — telecom customer service scenario.

Run:
    python examples/case_detective/mock_data/data_gen.py

Output files:
    customer_profiles.json       — 10 customers with contract/plan info
    billing_history.json         — 12 months billing records per customer
    complaint_cases.json         — 15 complaint cases (open/closed/escalated)
    sla_records.json             — SLA performance records (uptime, latency, jitter)
    speed_test_logs.json         — Speed test measurements (download/upload/ping)
    construction_lookup.json     — Nearby construction projects affecting signal
    followup_tasks.json          — Pending follow-up tasks assigned to agents
    knowledge_base.json          — KB articles: billing FAQ, SLA policy, escalation rules
"""

import json
import pathlib
import random
from datetime import date, datetime, timedelta

OUT = pathlib.Path(__file__).parent
random.seed(42)


def jd(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2)


# ─── helpers ────────────────────────────────────────────────────────────────

def daterange(start: str, months: int):
    d = date.fromisoformat(start + "-01")
    for _ in range(months):
        yield d.strftime("%Y-%m")
        if d.month == 12:
            d = d.replace(year=d.year + 1, month=1)
        else:
            d = d.replace(month=d.month + 1)


# ─── 1. Customer Profiles ────────────────────────────────────────────────────

PLANS = [
    {"plan_id": "FBB-500", "name": "光纖寬頻 500M", "monthly_fee": 599, "speed_down": 500, "speed_up": 100, "sla_uptime": 99.5},
    {"plan_id": "FBB-1G",  "name": "光纖寬頻 1Gbps", "monthly_fee": 899, "speed_down": 1000, "speed_up": 300, "sla_uptime": 99.7},
    {"plan_id": "MOB-5G",  "name": "5G 行動方案 30GB", "monthly_fee": 799, "speed_down": 300, "speed_up": 50, "sla_uptime": 98.5},
    {"plan_id": "MOB-4G",  "name": "4G 行動方案 15GB", "monthly_fee": 499, "speed_down": 100, "speed_up": 20, "sla_uptime": 97.0},
    {"plan_id": "BIZ-FBB", "name": "企業光纖 10G", "monthly_fee": 3500, "speed_down": 10000, "speed_up": 5000, "sla_uptime": 99.9},
]

CUSTOMERS = [
    ("C-10001", "陳怡君", "FBB-500",  "2022-03-15", "新北市板橋區文化路二段"),
    ("C-10002", "林志豪", "FBB-1G",   "2021-07-01", "台北市大安區仁愛路四段"),
    ("C-10003", "王美玲", "MOB-5G",   "2023-01-20", "台中市西屯區台灣大道三段"),
    ("C-10004", "張建國", "MOB-4G",   "2020-11-05", "高雄市前鎮區中山二路"),
    ("C-10005", "李佳穎", "FBB-1G",   "2023-06-10", "台北市信義區松仁路"),
    ("C-10006", "黃俊傑", "BIZ-FBB",  "2019-09-01", "新竹科學園區台積電路"),
    ("C-10007", "鄭雅婷", "FBB-500",  "2024-02-14", "桃園市中壢區中山路"),
    ("C-10008", "吳家豪", "MOB-5G",   "2022-08-30", "台南市東區長榮路"),
    ("C-10009", "許淑芬", "FBB-500",  "2021-04-22", "新北市三重區重新路"),
    ("C-10010", "蔡明宏", "MOB-4G",   "2023-10-01", "彰化市中正路"),
]

plan_map = {p["plan_id"]: p for p in PLANS}

customer_profiles = []
for cid, name, plan_id, since, addr in CUSTOMERS:
    plan = plan_map[plan_id]
    customer_profiles.append({
        "customer_id": cid,
        "name": name,
        "plan": {**plan},
        "contract_start": since,
        "contract_end": str((date.fromisoformat(since) + timedelta(days=730)).isoformat()),
        "address": addr,
        "phone": f"09{random.randint(10000000, 99999999)}",
        "email": f"{name.lower().replace('　', '')}@example.com",
        "credit_score": random.choice(["A", "A", "A", "B", "B"]),
        "vip_tier": "企業" if "BIZ" in plan_id else random.choice(["一般", "一般", "銀卡", "金卡"]),
    })

(OUT / "customer_profiles.json").write_text(jd(customer_profiles), encoding="utf-8")
print("✓ customer_profiles.json")


# ─── 2. Billing History ──────────────────────────────────────────────────────

billing_history = []
BILLING_START = "2025-06"

for c in customer_profiles:
    cid = c["customer_id"]
    base_fee = c["plan"]["monthly_fee"]
    for month in daterange(BILLING_START, 12):
        # occasional extra charges or credits
        extras = []
        extra_total = 0
        if random.random() < 0.1:
            amt = random.choice([99, 199, 299])
            extras.append({"item": "國際漫遊費", "amount": amt})
            extra_total += amt
        if random.random() < 0.05:
            amt = -base_fee * 0.1
            extras.append({"item": "服務品質補償折抵", "amount": round(amt)})
            extra_total += round(amt)
        if cid == "C-10001" and month in ("2025-09", "2025-10"):
            extras.append({"item": "超量使用費", "amount": 150})
            extra_total += 150

        total = base_fee + extra_total
        billing_history.append({
            "customer_id": cid,
            "billing_month": month,
            "base_fee": base_fee,
            "extras": extras,
            "total_amount": total,
            "due_date": f"{month}-20",
            "paid_date": f"{month}-{random.randint(10, 19):02d}" if random.random() > 0.05 else None,
            "status": "paid" if random.random() > 0.05 else "overdue",
            "invoice_id": f"INV-{cid}-{month.replace('-', '')}",
        })

(OUT / "billing_history.json").write_text(jd(billing_history), encoding="utf-8")
print("✓ billing_history.json")


# ─── 3. Complaint Cases ──────────────────────────────────────────────────────

complaint_cases = [
    {
        "case_id": "CASE-2025-0831",
        "customer_id": "C-10001",
        "opened_date": "2025-09-03",
        "category": "billing_dispute",
        "subject": "9月帳單多收費用申訴",
        "description": "客戶反映 2025 年 9 月帳單顯示超量使用費 NT$150，但客戶表示當月未超過合約流量上限，要求說明計費依據並退費。",
        "status": "closed",
        "resolution": "查核後確認為系統計費錯誤，已退還 NT$150 並列入下月帳單折抵。",
        "closed_date": "2025-09-10",
        "assigned_to": "客服一組",
        "priority": "medium",
        "satisfaction_score": 4,
    },
    {
        "case_id": "CASE-2025-1102",
        "customer_id": "C-10002",
        "opened_date": "2025-11-08",
        "category": "speed_degradation",
        "subject": "網速持續低於合約保證值",
        "description": "客戶反映近三週下載速度僅 200-250 Mbps，遠低於方案保證 1Gbps，已自行測試多次可提供截圖。",
        "status": "in_progress",
        "resolution": None,
        "closed_date": None,
        "assigned_to": "網路技術二組",
        "priority": "high",
        "satisfaction_score": None,
    },
    {
        "case_id": "CASE-2025-1215",
        "customer_id": "C-10003",
        "opened_date": "2025-12-16",
        "category": "service_outage",
        "subject": "5G 訊號全日中斷，影響上班視訊",
        "description": "2025/12/15 全天無法使用 5G 服務，只能降至 4G，造成遠距工作視訊嚴重卡頓。要求 SLA 補償。",
        "status": "escalated",
        "resolution": None,
        "closed_date": None,
        "assigned_to": "SLA 主管審核",
        "priority": "critical",
        "satisfaction_score": None,
    },
    {
        "case_id": "CASE-2026-0112",
        "customer_id": "C-10004",
        "opened_date": "2026-01-12",
        "category": "billing_dispute",
        "subject": "合約到期後仍被收費",
        "description": "客戶表示合約應於 2025-11-05 到期，但 2025 年 11、12 月及 2026 年 1 月帳單仍以舊費率收費，要求退還差額。",
        "status": "open",
        "resolution": None,
        "closed_date": None,
        "assigned_to": "帳務處理組",
        "priority": "high",
        "satisfaction_score": None,
    },
    {
        "case_id": "CASE-2026-0203",
        "customer_id": "C-10005",
        "opened_date": "2026-02-03",
        "category": "speed_degradation",
        "subject": "夜間 10-12 點速度驟降",
        "description": "每天晚上 22:00-24:00 下載速度從正常 800 Mbps 降至 100-150 Mbps，懷疑是附近施工影響。",
        "status": "in_progress",
        "resolution": None,
        "closed_date": None,
        "assigned_to": "網路技術一組",
        "priority": "medium",
        "satisfaction_score": None,
    },
    {
        "case_id": "CASE-2026-0318",
        "customer_id": "C-10006",
        "opened_date": "2026-03-18",
        "category": "sla_violation",
        "subject": "企業光纖 SLA 99.9% 未達標，要求違約金",
        "description": "2026 年 2 月實測可用率僅 99.2%，低於企業方案 SLA 保證 99.9%，依合約第 12 條要求違約補償 NT$35,000。",
        "status": "escalated",
        "resolution": None,
        "closed_date": None,
        "assigned_to": "企業客服主管",
        "priority": "critical",
        "satisfaction_score": None,
    },
    {
        "case_id": "CASE-2026-0401",
        "customer_id": "C-10007",
        "opened_date": "2026-04-01",
        "category": "billing_dispute",
        "subject": "促銷折扣未套用",
        "description": "申辦時業務承諾前 6 個月每月折扣 NT$100，但 3 月及 4 月帳單均未見折扣，要求補扣。",
        "status": "open",
        "resolution": None,
        "closed_date": None,
        "assigned_to": "客服一組",
        "priority": "low",
        "satisfaction_score": None,
    },
    {
        "case_id": "CASE-2026-0415",
        "customer_id": "C-10008",
        "opened_date": "2026-04-15",
        "category": "service_outage",
        "subject": "台南地區 5G 斷線超過 4 小時",
        "description": "2026/04/14 下午 14:00-18:30，台南東區 5G 服務中斷，客戶無法正常使用，要求說明原因及補償方案。",
        "status": "closed",
        "resolution": "因台南東區基地台設備更換作業，已事先公告（SMS 發送）。提供客戶 1 日免費數據加量 5GB 補償。",
        "closed_date": "2026-04-16",
        "assigned_to": "客服二組",
        "priority": "medium",
        "satisfaction_score": 3,
    },
    {
        "case_id": "CASE-2026-0502",
        "customer_id": "C-10009",
        "opened_date": "2026-05-02",
        "category": "speed_degradation",
        "subject": "搬家後網速異常",
        "description": "2026/04/28 搬遷至新北市三重區，原本 500M 方案，搬遷後實測僅 80-120 Mbps，懷疑新址線路問題。",
        "status": "in_progress",
        "resolution": None,
        "closed_date": None,
        "assigned_to": "技術維修三組",
        "priority": "high",
        "satisfaction_score": None,
    },
    {
        "case_id": "CASE-2026-0518",
        "customer_id": "C-10001",
        "opened_date": "2026-05-18",
        "category": "billing_dispute",
        "subject": "5 月帳單再次出現異常費用",
        "description": "2026 年 5 月帳單出現 NT$150 超量費，客戶表示去年 9 月已申訴並要求永久修正，懷疑系統問題未完全修復。",
        "status": "open",
        "resolution": None,
        "closed_date": None,
        "assigned_to": "帳務處理組",
        "priority": "high",
        "satisfaction_score": None,
    },
]

(OUT / "complaint_cases.json").write_text(jd(complaint_cases), encoding="utf-8")
print("✓ complaint_cases.json")


# ─── 4. SLA Records ──────────────────────────────────────────────────────────

sla_records = []
for c in customer_profiles:
    cid = c["customer_id"]
    sla_target = c["plan"]["sla_uptime"]
    for month in daterange("2025-06", 12):
        # most months meet SLA; a few don't
        if cid == "C-10006" and month == "2026-02":
            actual = 99.2
        elif cid == "C-10003" and month == "2025-12":
            actual = 97.8
        elif cid == "C-10008" and month == "2026-04":
            actual = 98.1
        else:
            actual = round(sla_target - random.uniform(0, 0.3), 2)
            actual = min(actual, 100.0)

        downtime_minutes = round((100 - actual) / 100 * 43200, 1)  # in a 30-day month
        sla_records.append({
            "customer_id": cid,
            "month": month,
            "plan_sla_target": sla_target,
            "actual_uptime_pct": actual,
            "met_sla": actual >= sla_target,
            "downtime_minutes": downtime_minutes,
            "avg_latency_ms": round(random.uniform(5, 25), 1),
            "avg_jitter_ms": round(random.uniform(1, 8), 1),
            "packet_loss_pct": round(random.uniform(0, 0.5), 2),
        })

(OUT / "sla_records.json").write_text(jd(sla_records), encoding="utf-8")
print("✓ sla_records.json")


# ─── 5. Speed Test Logs ──────────────────────────────────────────────────────

speed_test_logs = []
# Generate ~5 tests per customer over recent 3 months
test_customers = {
    "C-10002": (1000, 300, 0.5),   # plan speed, expected dn/up/loss — having issues
    "C-10005": (1000, 300, 0.3),   # having night issues
    "C-10009": (500, 100, 0.3),    # post-move degradation
    "C-10006": (10000, 5000, 0.1), # enterprise
    "C-10001": (500, 100, 0.2),
}
test_dates = ["2026-03-01", "2026-04-01", "2026-04-15", "2026-05-01", "2026-05-10"]

for cid, (dn_plan, up_plan, loss_base) in test_customers.items():
    for i, dt in enumerate(test_dates):
        hour = random.choice([9, 14, 22, 23])
        is_night = hour >= 22
        if cid == "C-10002":
            dn_actual = random.randint(200, 260) if True else random.randint(int(dn_plan * 0.8), dn_plan)
            up_actual = random.randint(80, 120)
        elif cid == "C-10005" and is_night:
            dn_actual = random.randint(100, 160)
            up_actual = random.randint(40, 70)
        elif cid == "C-10009" and i >= 3:
            dn_actual = random.randint(80, 130)
            up_actual = random.randint(20, 40)
        else:
            dn_actual = random.randint(int(dn_plan * 0.8), dn_plan)
            up_actual = random.randint(int(up_plan * 0.8), up_plan)

        speed_test_logs.append({
            "log_id": f"SPD-{cid}-{i+1:02d}",
            "customer_id": cid,
            "test_datetime": f"{dt} {hour:02d}:00",
            "download_mbps": dn_actual,
            "upload_mbps": up_actual,
            "ping_ms": random.randint(5, 30),
            "packet_loss_pct": round(random.uniform(0, 1.5), 2),
            "test_server": random.choice(["台北-01", "台北-02", "新竹-01", "台中-01"]),
            "plan_download_mbps": dn_plan,
            "plan_upload_mbps": up_plan,
            "below_guarantee": dn_actual < dn_plan * 0.5,
        })

(OUT / "speed_test_logs.json").write_text(jd(speed_test_logs), encoding="utf-8")
print("✓ speed_test_logs.json")


# ─── 6. Construction Lookup ──────────────────────────────────────────────────

construction_lookup = [
    {
        "project_id": "CONS-2026-NB-001",
        "district": "新北市板橋區",
        "address": "文化路二段 120-180 號路段",
        "project_name": "板橋文化路地下管線更新工程",
        "contractor": "捷達工程股份有限公司",
        "start_date": "2026-03-01",
        "expected_end": "2026-07-31",
        "status": "in_progress",
        "impact_radius_m": 300,
        "telecom_impact": True,
        "impact_description": "地下光纖管道施工，可能影響沿線用戶光纖品質，預估 C-10001 所在地址位於影響範圍內",
        "notes": "工程期間網路品質可能出現波動，已通知受影響用戶（通知日期 2026-02-20）",
    },
    {
        "project_id": "CONS-2026-TP-002",
        "district": "台北市信義區",
        "address": "松仁路 80-150 號",
        "project_name": "信義區 5G 基礎設施擴容工程",
        "contractor": "承昱電信工程有限公司",
        "start_date": "2026-01-15",
        "expected_end": "2026-06-30",
        "status": "in_progress",
        "impact_radius_m": 500,
        "telecom_impact": True,
        "impact_description": "5G 小基站安裝施工，夜間 21:00-06:00 進行高空作業，施工期間 5G 訊號可能切換至 4G",
        "notes": "影響區域包含 C-10005 客戶地址，施工已知原因造成夜間降速",
    },
    {
        "project_id": "CONS-2025-TN-003",
        "district": "台南市東區",
        "address": "長榮路一段至三段",
        "project_name": "台南東區機房設備汰換",
        "contractor": "電信自辦工程",
        "start_date": "2026-04-14",
        "expected_end": "2026-04-14",
        "status": "completed",
        "impact_radius_m": 2000,
        "telecom_impact": True,
        "impact_description": "台南東區 5G 機房主要設備更換，施工期 14:00-18:30 造成服務中斷",
        "notes": "已提前 3 天 SMS 通知受影響用戶（含 C-10008），施工完成後服務完全恢復",
    },
    {
        "project_id": "CONS-2026-HC-004",
        "district": "新竹科學園區",
        "address": "台積電路全區",
        "project_name": "科學園區智慧電網整合工程",
        "contractor": "台電配合工程",
        "start_date": "2026-02-01",
        "expected_end": "2026-03-15",
        "status": "completed",
        "impact_radius_m": 1000,
        "telecom_impact": True,
        "impact_description": "園區電力系統切換導致光纖機房多次短暫斷電，造成 SLA 可用率下降",
        "notes": "2026/02 可用率降至 99.2%，低於企業 SLA 99.9% 目標。工程已於 3/15 結束",
    },
    {
        "project_id": "CONS-2026-SJ-005",
        "district": "新北市三重區",
        "address": "重新路三段 200-350 號",
        "project_name": "三重區舊管道汰換工程",
        "contractor": "三和工程有限公司",
        "start_date": "2026-04-20",
        "expected_end": "2026-08-31",
        "status": "in_progress",
        "impact_radius_m": 400,
        "telecom_impact": True,
        "impact_description": "舊式銅線管道換光纖工程，施工期間線路品質不穩定",
        "notes": "C-10009 搬遷後所在地址位於施工範圍，預計 8 月完工後恢復正常速度",
    },
]

(OUT / "construction_lookup.json").write_text(jd(construction_lookup), encoding="utf-8")
print("✓ construction_lookup.json")


# ─── 7. Follow-up Tasks ──────────────────────────────────────────────────────

followup_tasks = [
    {
        "task_id": "TASK-2026-0518-01",
        "case_id": "CASE-2026-0518",
        "customer_id": "C-10001",
        "created_date": "2026-05-18",
        "due_date": "2026-05-22",
        "status": "overdue",
        "task_type": "billing_review",
        "description": "查核帳務系統是否仍存在超量計費 bug（CASE-2025-0831 已修正但客戶再次申訴），確認修正狀態並回電客戶",
        "assigned_to": "帳務處理組",
        "priority": "high",
        "notes": "客戶曾於 2025/09 申訴同一問題，若再次確認系統錯誤需主動聯繫道歉並提供額外補償",
    },
    {
        "task_id": "TASK-2026-0401-01",
        "case_id": "CASE-2026-0401",
        "customer_id": "C-10007",
        "created_date": "2026-04-02",
        "due_date": "2026-04-08",
        "status": "in_progress",
        "task_type": "discount_adjustment",
        "description": "確認業務代表承諾的 6 個月每月 NT$100 折扣是否已輸入系統，補扣 3 月及 4 月共 NT$200",
        "assigned_to": "客服一組",
        "priority": "medium",
        "notes": "已聯繫業務代表確認確有承諾，系統輸入疏失，折扣將於下月帳單補扣",
    },
    {
        "task_id": "TASK-2026-0318-01",
        "case_id": "CASE-2026-0318",
        "customer_id": "C-10006",
        "created_date": "2026-03-20",
        "due_date": "2026-04-03",
        "status": "pending_approval",
        "task_type": "sla_compensation",
        "description": "計算 2026/02 SLA 違約補償金額（依合約第 12 條），擬補償 NT$35,000，需總監批准後開立支票",
        "assigned_to": "企業客服主管",
        "priority": "critical",
        "notes": "C-10006（黃俊傑）為 VIP 企業客戶，建議主管親自致電說明並道歉",
    },
    {
        "task_id": "TASK-2026-0502-01",
        "case_id": "CASE-2026-0502",
        "customer_id": "C-10009",
        "created_date": "2026-05-02",
        "due_date": "2026-05-16",
        "status": "in_progress",
        "task_type": "site_inspection",
        "description": "安排技術人員到府確認新址（三重區重新路）線路狀況，判斷是否為施工影響或室內配線問題",
        "assigned_to": "技術維修三組",
        "priority": "high",
        "notes": "已查詢施工資料，CONS-2026-SJ-005 工程影響範圍涵蓋客戶地址，到府時需告知客戶施工期程",
    },
    {
        "task_id": "TASK-2025-1102-01",
        "case_id": "CASE-2025-1102",
        "customer_id": "C-10002",
        "created_date": "2025-11-10",
        "due_date": "2025-11-24",
        "status": "overdue",
        "task_type": "network_investigation",
        "description": "調查 C-10002（林志豪）台北大安區 1Gbps 方案速度長期不足（200-250 Mbps）的根本原因，提供解決方案",
        "assigned_to": "網路技術二組",
        "priority": "high",
        "notes": "客戶已提供多次測速截圖，問題持續超過 3 週，需儘速處理避免升級投訴",
    },
]

(OUT / "followup_tasks.json").write_text(jd(followup_tasks), encoding="utf-8")
print("✓ followup_tasks.json")


# ─── 8. Knowledge Base ───────────────────────────────────────────────────────

knowledge_base = [
    {
        "kb_id": "KB-BILLING-001",
        "category": "billing",
        "title": "帳單爭議處理標準流程",
        "content": (
            "客戶提出帳單爭議時：\n"
            "1. 查核當月帳單明細（invoice_id），確認每筆費用項目\n"
            "2. 比對客戶合約方案費率，確認是否有額外費用觸發條件\n"
            "3. 若確認計費錯誤，授權範圍：客服人員可退費 NT$500 以內，NT$500 以上需組長審核\n"
            "4. 退費方式：下月帳單折抵或信用卡退款（3-5 工作天）\n"
            "5. 記錄案件並追蹤系統是否有系統性問題"
        ),
        "applies_to": ["billing_dispute"],
        "updated": "2026-01-15",
    },
    {
        "kb_id": "KB-SLA-001",
        "title": "SLA 違約補償政策",
        "category": "sla",
        "content": (
            "各方案 SLA 保證與補償規定：\n"
            "- 一般家庭方案（FBB-500/1G）：可用率 < 保證值，每月超出部分按比例折抵月租費（上限月租費 30%）\n"
            "- 5G/4G 行動方案：連續 4 小時以上中斷，補償 1 日免費數據 5GB\n"
            "- 企業方案（BIZ-FBB）：可用率 < 99.9%，依合約第 12 條，每 0.1% 缺口補償月租費 5%，無上限\n"
            "補償申請有效期：事件發生後 60 天內\n"
            "申請方式：客服專線或線上客服，提供帳號與發生時間"
        ),
        "applies_to": ["sla_violation", "service_outage"],
        "updated": "2025-11-01",
    },
    {
        "kb_id": "KB-SPEED-001",
        "title": "網速異常排查步驟",
        "category": "technical",
        "content": (
            "接到網速申訴時的標準排查流程：\n"
            "1. 確認客戶測速工具及時間（避免尖峰時段誤判）\n"
            "2. 查詢附近施工工程（construction_lookup），確認是否施工影響\n"
            "3. 查詢近 30 天該地區測速紀錄（speed_test_logs）\n"
            "4. 若下載速度持續低於方案保證速度 50%，視為 SLA 違反，啟動補償流程\n"
            "5. 安排技術人員到府檢測（室內配線、數據機、光纖終端設備）\n"
            "尖峰時段定義：平日 19:00-23:00，假日 12:00-23:00"
        ),
        "applies_to": ["speed_degradation"],
        "updated": "2026-02-10",
    },
    {
        "kb_id": "KB-ESCAL-001",
        "title": "案件升級（Escalation）規則",
        "category": "escalation",
        "content": (
            "以下情況應立即升級至主管或專責組別：\n"
            "1. 企業客戶（VIP 企業）的任何 critical 案件\n"
            "2. 同一客戶同一問題重複申訴（第二次以上）\n"
            "3. 補償金額超過 NT$5,000\n"
            "4. 客戶明確表示不滿意並要求主管處理\n"
            "5. 案件逾期未處理超過 3 個工作天\n"
            "升級路徑：客服人員 → 組長 → 部門主管 → 總監（依金額/嚴重性）"
        ),
        "applies_to": ["billing_dispute", "sla_violation", "service_outage", "speed_degradation"],
        "updated": "2026-03-01",
    },
    {
        "kb_id": "KB-CONST-001",
        "title": "施工影響查詢與客戶說明話術",
        "category": "construction",
        "content": (
            "確認施工影響後，對客戶說明要點：\n"
            "1. 說明施工名稱、預計完工日期\n"
            "2. 施工期間無法保證正常品質屬不可抗力，SLA 條款第 8 條免責\n"
            "3. 但應主動提供補償方案（例如：延長合約、優惠月租費）以維持客戶關係\n"
            "4. 確認客戶是否於施工通知日期前已收到 SMS 通知（若否則須道歉）\n"
            "施工免責條款不適用於：未提前通知客戶的情況"
        ),
        "applies_to": ["speed_degradation", "service_outage"],
        "updated": "2025-09-20",
    },
]

(OUT / "knowledge_base.json").write_text(jd(knowledge_base), encoding="utf-8")
print("✓ knowledge_base.json")


print("\n✅ 所有假資料生成完成，輸出目錄：", OUT)
