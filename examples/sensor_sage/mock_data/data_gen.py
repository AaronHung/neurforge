"""
NeurForge — SensorSage mock data generator.
Run: python examples/sensor_sage/mock_data/data_gen.py
Generates all JSON files used by SensorSageAgent (機況先知).

Design narrative
----------------
COMP-102R-B (往復式壓縮機 B台) — DECLINING
  Jan 2026: HPI ~88, all tags normal
  Feb 2026: TI13094B (二級出口溫度) starts creeping up
  Mar 2026: PI13030B (二級出口壓力) dips; II1302B (電流) rises
  Apr 6 2026: HPI crosses warning threshold 70
  May 24 2026 (current): HPI 61.1 → Agent triggered
  Root cause (匹配歷史案例): 二級活塞桿磨損 → 預計 ~Jun 10 斷裂
  Recommendation: schedule maintenance within 2 weeks

COMP-102R-A — HEALTHY (HPI ~87)
COMP-102R-S — STANDBY (offline)
COMP-101C  — HEALTHY (HPI ~89, 離心式)
REACT-201  — Catalyst activity declining 100→62 (loaded Jan 2025, 16 months in)
"""
import json
import math
import random
from datetime import date, timedelta
from pathlib import Path

OUT = Path(__file__).parent
random.seed(42)


# ── helpers ──────────────────────────────────────────────────────────────────

def date_range(start: date, end: date):
    d = start
    while d <= end:
        yield d
        d += timedelta(days=1)

def weekly_dates(start: date, end: date):
    """Return Mondays in range."""
    d = start
    while d.weekday() != 0:
        d += timedelta(days=1)
    while d <= end:
        yield d
        d += timedelta(weeks=1)

def noisy(base, std=0.5):
    return round(base + random.gauss(0, std), 2)

TODAY = date(2026, 5, 24)
START = date(2026, 1, 5)  # first Monday


# ── 1. equipment_registry.json ───────────────────────────────────────────────

equipment = [
    {
        "equipment_id": "COMP-102R-A",
        "name": "往復式壓縮機 A台",
        "type": "reciprocating_compressor",
        "facility": "低溫工場",
        "location": "C棟 壓縮機房",
        "install_date": "2010-06-15",
        "last_major_overhaul": "2026-03-12",
        "status": "運行中",
        "responsible_team": "轉機維護組",
        "design_capacity": "120 TON/HR",
        "stages": 2,
        "driver": "電動馬達",
    },
    {
        "equipment_id": "COMP-102R-B",
        "name": "往復式壓縮機 B台",
        "type": "reciprocating_compressor",
        "facility": "低溫工場",
        "location": "C棟 壓縮機房",
        "install_date": "2010-06-15",
        "last_major_overhaul": "2024-12-31",
        "status": "運行中",
        "responsible_team": "轉機維護組",
        "design_capacity": "120 TON/HR",
        "stages": 2,
        "driver": "電動馬達",
        "pdm_note": "⚠️ PRiSM 預警中 — HPI 持續下降，請查閱機況先知診斷報告",
    },
    {
        "equipment_id": "COMP-102R-S",
        "name": "往復式壓縮機 備用台",
        "type": "reciprocating_compressor",
        "facility": "低溫工場",
        "location": "C棟 壓縮機房",
        "install_date": "2010-06-15",
        "last_major_overhaul": "2025-12-25",
        "status": "備用(離線)",
        "responsible_team": "轉機維護組",
        "design_capacity": "120 TON/HR",
        "stages": 2,
        "driver": "電動馬達",
    },
    {
        "equipment_id": "COMP-101C",
        "name": "離心式壓縮機",
        "type": "centrifugal_compressor",
        "facility": "低溫工場",
        "location": "D棟 主機房",
        "install_date": "2010-06-15",
        "last_major_overhaul": "2025-09-15",
        "status": "運行中",
        "responsible_team": "轉機維護組",
        "design_capacity": "57,000 KG/HR",
        "stages": 3,
        "driver": "蒸汽渦輪 (11,500 RPM)",
    },
    {
        "equipment_id": "REACT-201",
        "name": "加氫裂解觸媒反應器",
        "type": "catalytic_reactor",
        "facility": "煉製工場",
        "location": "E棟 反應器區",
        "install_date": "2018-03-01",
        "catalyst_load_date": "2025-01-15",
        "status": "運行中",
        "responsible_team": "製程維護組",
        "catalyst_type": "Ni-Mo / Al₂O₃",
        "design_conversion_pct": 95.0,
        "catalyst_replacement_cost_ntd": 32_000_000,
    },
]
(OUT / "equipment_registry.json").write_text(
    json.dumps(equipment, ensure_ascii=False, indent=2), encoding="utf-8"
)
print("✓ equipment_registry.json")


# ── 2. sensor_tags.json ───────────────────────────────────────────────────────

tags = {
    "COMP-102R": {
        "TI1_INLET": {"desc": "一級進口溫度", "unit": "°C", "normal_min": 18, "normal_max": 32},
        "TI1_OUTLET": {"desc": "一級出口溫度", "unit": "°C", "normal_min": 138, "normal_max": 148},
        "TI2_INLET": {"desc": "二級進口溫度", "unit": "°C", "normal_min": 30, "normal_max": 42},
        "TI2_OUTLET": {"desc": "二級出口溫度", "unit": "°C", "normal_min": 138, "normal_max": 148},
        "PI1_INLET": {"desc": "一級進口壓力", "unit": "kg/cm²", "normal_min": 0.05, "normal_max": 0.15},
        "PI1_OUTLET": {"desc": "一級出口壓力", "unit": "kg/cm²", "normal_min": 3.5, "normal_max": 4.2},
        "PI2_OUTLET": {"desc": "二級出口壓力", "unit": "kg/cm²", "normal_min": 15.5, "normal_max": 17.5},
        "II_CURRENT": {"desc": "電動機電流", "unit": "A", "normal_min": 150, "normal_max": 168},
        "FI_FLOW": {"desc": "出口流量", "unit": "TON/HR", "normal_min": 105, "normal_max": 125},
        "TI_PACKING1": {"desc": "一級填料溫度", "unit": "°C", "normal_min": 35, "normal_max": 55},
        "TI_PACKING2": {"desc": "二級填料溫度", "unit": "°C", "normal_min": 40, "normal_max": 62},
    },
    "COMP-101C": {
        "ZI_AXIAL_A": {"desc": "軸向位移 A", "unit": "MIL", "normal_min": -9.5, "normal_max": -3.0},
        "ZI_AXIAL_B": {"desc": "軸向位移 B", "unit": "MIL", "normal_min": -9.5, "normal_max": -3.0},
        "XI_VIB_C": {"desc": "振動 C（mil p-p）", "unit": "MIL p-p", "normal_min": 0.3, "normal_max": 0.8},
        "XI_VIB_D": {"desc": "振動 D（mil p-p）", "unit": "MIL p-p", "normal_min": 0.3, "normal_max": 0.8},
        "XI_VIB_E": {"desc": "振動 E（mil p-p）", "unit": "MIL p-p", "normal_min": 0.6, "normal_max": 1.3},
        "XI_VIB_G": {"desc": "振動 G（mil p-p）", "unit": "MIL p-p", "normal_min": 0.3, "normal_max": 0.8},
        "TI_TEMP_1": {"desc": "壓縮機 T1 溫度", "unit": "°C", "normal_min": 56, "normal_max": 72},
        "TI_TEMP_5": {"desc": "壓縮機 T5 溫度（高壓段）", "unit": "°C", "normal_min": 90, "normal_max": 100},
        "STX_SPEED": {"desc": "渦輪轉速", "unit": "RPM", "normal_min": 10500, "normal_max": 12200},
        "FIC_FLOW_1": {"desc": "一段吸入流量", "unit": "TON/HR", "normal_min": 13, "normal_max": 22},
    },
    "REACT-201": {
        "REACT_TEMP_IN": {"desc": "進料溫度（入口）", "unit": "°C", "normal_min": 340, "normal_max": 400},
        "REACT_TEMP_OUT": {"desc": "出料溫度（出口）", "unit": "°C", "normal_min": 355, "normal_max": 420},
        "REACT_DELTA_T": {"desc": "反應溫升 ΔT", "unit": "°C", "normal_min": 12, "normal_max": 25},
        "WHSV": {"desc": "重量空間速度", "unit": "hr⁻¹", "normal_min": 1.0, "normal_max": 2.5},
        "CONVERSION": {"desc": "進料轉化率", "unit": "%", "normal_min": 88, "normal_max": 96},
        "SELECTIVITY": {"desc": "產品選擇性", "unit": "%", "normal_min": 82, "normal_max": 92},
        "PRODUCT_QUAL": {"desc": "產品品質指標（API）", "unit": "API°", "normal_min": 38, "normal_max": 46},
    },
}
(OUT / "sensor_tags.json").write_text(
    json.dumps(tags, ensure_ascii=False, indent=2), encoding="utf-8"
)
print("✓ sensor_tags.json")


# ── 3. hpi_history.json ───────────────────────────────────────────────────────

def make_hpi_curve(start_hpi, weeks, drift_start_week, drift_per_week, noise_std=0.8):
    """Generate weekly HPI values."""
    result = []
    for i, d in enumerate(weekly_dates(START, TODAY)):
        if i < drift_start_week:
            hpi = noisy(start_hpi, noise_std)
        else:
            decay = drift_per_week * (i - drift_start_week)
            hpi = noisy(start_hpi - decay, noise_std)
        hpi = round(max(20, min(100, hpi)), 1)
        status = "normal" if hpi >= 70 else ("warning" if hpi >= 50 else "alarm")
        result.append({"date": d.isoformat(), "hpi": hpi, "status": status})
    return result

hpi = {
    "warning_threshold": 70,
    "alarm_threshold": 50,
    "equipment": {
        "COMP-102R-A": {
            "name": "往復式壓縮機 A台",
            "history": make_hpi_curve(87.5, 20, 99, 0),    # flat / healthy
        },
        "COMP-102R-B": {
            "name": "往復式壓縮機 B台",
            "history": make_hpi_curve(88.2, 20, 6, 2.1),   # declines from week 6
        },
        "COMP-101C": {
            "name": "離心式壓縮機",
            "history": make_hpi_curve(89.1, 20, 99, 0),
        },
    },
}
(OUT / "hpi_history.json").write_text(
    json.dumps(hpi, ensure_ascii=False, indent=2), encoding="utf-8"
)
print("✓ hpi_history.json")


# ── 4. sensor_trends.json ─────────────────────────────────────────────────────

def make_tag_weekly(base, drift_start_week, drift_per_week, noise_std):
    records = []
    for i, d in enumerate(weekly_dates(START, TODAY)):
        if i < drift_start_week:
            mean = noisy(base, noise_std)
        else:
            mean = noisy(base + drift_per_week * (i - drift_start_week), noise_std)
        records.append({
            "week_start": d.isoformat(),
            "mean": round(mean, 2),
            "max": round(mean + random.uniform(0.3, 0.8), 2),
            "min": round(mean - random.uniform(0.3, 0.8), 2),
        })
    return records

def trend_summary(records):
    if len(records) < 2:
        return "stable"
    delta = records[-1]["mean"] - records[-4]["mean"] if len(records) >= 4 else records[-1]["mean"] - records[0]["mean"]
    if delta > 1.5:
        return "↑ 上升"
    elif delta < -1.5:
        return "↓ 下降"
    return "→ 穩定"

trends = {}
# COMP-102R-B (deteriorating)
b_tags = {
    "TI2_OUTLET":  {"base": 141.0, "drift_start": 6, "drift_pw": 0.7, "noise": 0.4},
    "PI2_OUTLET":  {"base": 16.4,  "drift_start": 8, "drift_pw": -0.08, "noise": 0.05},
    "II_CURRENT":  {"base": 158.0, "drift_start": 7, "drift_pw": 0.6, "noise": 0.8},
    "TI_PACKING2": {"base": 48.0,  "drift_start": 9, "drift_pw": 0.5, "noise": 0.3},
    "FI_FLOW":     {"base": 116.0, "drift_start": 9, "drift_pw": -0.4, "noise": 0.6},
    "TI2_INLET":   {"base": 36.5,  "drift_start": 99, "drift_pw": 0, "noise": 0.3},
    "PI1_OUTLET":  {"base": 3.85,  "drift_start": 99, "drift_pw": 0, "noise": 0.03},
}
eq_b = {}
for tag, cfg in b_tags.items():
    recs = make_tag_weekly(cfg["base"], cfg["drift_start"], cfg["drift_pw"], cfg["noise"])
    eq_b[tag] = {
        "description": tags["COMP-102R"][tag]["desc"],
        "unit": tags["COMP-102R"][tag]["unit"],
        "normal_range": [tags["COMP-102R"][tag]["normal_min"], tags["COMP-102R"][tag]["normal_max"]],
        "current_value": recs[-1]["mean"],
        "trend_4w": trend_summary(recs),
        "weekly_history": recs,
    }
trends["COMP-102R-B"] = eq_b

# COMP-102R-A (healthy, same base but no drift)
eq_a = {}
for tag, cfg in b_tags.items():
    recs = make_tag_weekly(cfg["base"], 99, 0, cfg["noise"])
    eq_a[tag] = {
        "description": tags["COMP-102R"][tag]["desc"],
        "unit": tags["COMP-102R"][tag]["unit"],
        "normal_range": [tags["COMP-102R"][tag]["normal_min"], tags["COMP-102R"][tag]["normal_max"]],
        "current_value": recs[-1]["mean"],
        "trend_4w": trend_summary(recs),
        "weekly_history": recs,
    }
trends["COMP-102R-A"] = eq_a

# COMP-101C (healthy)
c_tags = {
    "XI_VIB_E":  {"base": 0.95, "drift_start": 99, "drift_pw": 0, "noise": 0.04},
    "XI_VIB_C":  {"base": 0.50, "drift_start": 99, "drift_pw": 0, "noise": 0.02},
    "STX_SPEED": {"base": 11480, "drift_start": 99, "drift_pw": 0, "noise": 30},
    "TI_TEMP_5": {"base": 94.8, "drift_start": 99, "drift_pw": 0, "noise": 0.4},
}
eq_c = {}
for tag, cfg in c_tags.items():
    recs = make_tag_weekly(cfg["base"], cfg["drift_start"], cfg["drift_pw"], cfg["noise"])
    eq_c[tag] = {
        "description": tags["COMP-101C"][tag]["desc"],
        "unit": tags["COMP-101C"][tag]["unit"],
        "normal_range": [tags["COMP-101C"][tag]["normal_min"], tags["COMP-101C"][tag]["normal_max"]],
        "current_value": recs[-1]["mean"],
        "trend_4w": trend_summary(recs),
        "weekly_history": recs,
    }
trends["COMP-101C"] = eq_c

(OUT / "sensor_trends.json").write_text(
    json.dumps(trends, ensure_ascii=False, indent=2), encoding="utf-8"
)
print("✓ sensor_trends.json")


# ── 5. failure_case_library.json — 老師傅知識庫 ──────────────────────────────

cases = [
    {
        "case_id": "CASE-001",
        "equipment_type": "reciprocating_compressor",
        "fault_type": "二級活塞桿磨損/斷裂",
        "severity": "高",
        "lead_time_weeks": "3-6 週",
        "signature_tags": ["TI2_OUTLET", "II_CURRENT", "PI2_OUTLET", "TI_PACKING2"],
        "pattern": {
            "TI2_OUTLET": "緩慢上升 +3~+8°C，歷時 3~5 週",
            "II_CURRENT": "上升 +5~+12A（氣缸內洩增加，壓縮效率下降）",
            "PI2_OUTLET": "下降 -0.3~-0.8 kg/cm²（二級壓縮比降低）",
            "TI_PACKING2": "上升 +5~+15°C（活塞桿摩擦熱增加）",
            "FI_FLOW":    "輕微下降，後期加速",
        },
        "historical_events": [
            {"date": "2024-12-30", "equipment": "COMP-102R-B", "action": "二級活塞桿檢修更換"},
            {"date": "2025-03-12", "equipment": "COMP-102R-A", "action": "二級活塞桿檢修更換"},
            {"date": "2024-07-23", "equipment": "COMP-102R-A", "action": "壓縮機全面檢修"},
        ],
        "root_cause": "活塞桿表面硬度下降、偏心磨損，導致活塞環失去密封性，氣缸內氣體洩漏",
        "recommended_action": "安排停機檢修，更換二級活塞桿、騎環（Rider Ring）與填料（Packing）",
        "urgency_rule": "HPI < 65 且 TI2_OUTLET 持續上升超過 4 週 → 建議 2 週內安排停機",
    },
    {
        "case_id": "CASE-002",
        "equipment_type": "reciprocating_compressor",
        "fault_type": "騎環（Rider Ring）破損",
        "severity": "高",
        "lead_time_weeks": "1-3 週",
        "signature_tags": ["FI_FLOW", "II_CURRENT", "TI2_OUTLET"],
        "pattern": {
            "FI_FLOW":    "突然下降 -10~-25%（氣體洩漏嚴重）",
            "II_CURRENT": "電流波動加大，平均上升",
            "TI2_OUTLET": "快速上升 +8~+20°C",
        },
        "historical_events": [
            {"date": "2024-08-27", "equipment": "COMP-102R-B", "action": "壓縮機檢修拆裝"},
            {"date": "2025-05-20", "equipment": "COMP-102R-S", "action": "1&2級活塞環與閥座檢修"},
        ],
        "root_cause": "騎環長期磨耗達到設計壽命，或因異物進入造成提前破損",
        "recommended_action": "立即安排停機，更換騎環、活塞環，檢查閥座",
        "urgency_rule": "FI_FLOW 在 48h 內下降 > 15% → 緊急停機",
    },
    {
        "case_id": "CASE-003",
        "equipment_type": "reciprocating_compressor",
        "fault_type": "出口閥座洩漏",
        "severity": "中",
        "lead_time_weeks": "2-8 週",
        "signature_tags": ["PI1_OUTLET", "FI_FLOW", "TI1_OUTLET"],
        "pattern": {
            "PI1_OUTLET": "一級出口壓力微降 -0.1~-0.4 kg/cm²",
            "FI_FLOW":    "緩慢下降 -5~-15%",
            "TI1_OUTLET": "輕微上升",
        },
        "historical_events": [
            {"date": "2024-05-13", "equipment": "COMP-102R-B", "action": "閥座洩漏拆裝"},
            {"date": "2025-06-19", "equipment": "COMP-102R-B", "action": "一級進出口閥加鎖工作"},
            {"date": "2025-06-20", "equipment": "COMP-102R-B", "action": "一級出口閥更換"},
        ],
        "root_cause": "閥座密封面因高壓衝擊疲勞，出現微裂紋或侵蝕坑洞",
        "recommended_action": "計劃性停機更換出口閥，可安排在下次定期保養時執行",
        "urgency_rule": "PI1_OUTLET 持續下降超過 4 週且下降 > 0.3 kg/cm² → 列入月保養計畫",
    },
    {
        "case_id": "CASE-004",
        "equipment_type": "centrifugal_compressor",
        "fault_type": "LP 壓縮機葉輪震動（軸承磨損）",
        "severity": "高",
        "lead_time_weeks": "4-10 週",
        "signature_tags": ["XI_VIB_E", "XI_VIB_C", "STX_SPEED"],
        "pattern": {
            "XI_VIB_E": "LP 段徑向振動從 ~0.95 mil 緩升至 > 1.4 mil",
            "XI_VIB_C": "伴隨上升，幅度較小",
            "STX_SPEED": "轉速波動加大（正常 ±30 RPM，異常 ±80 RPM）",
        },
        "historical_events": [
            {
                "date": "2016-06-27",
                "equipment": "空壓機膨脹機",
                "action": "第一段高振動葉輪斷裂損壞",
                "note": "PRiSM 於 2016-05-05 提前 52 天預測出異常，主要測點 YIX10748（X向振動）、YIY10728（Y向振動）",
            }
        ],
        "root_cause": "葉片表面孔蝕（腐蝕因素）→ 應力集中 → 疲勞裂紋 → 斷裂",
        "recommended_action": "振動超過 1.4 mil 時立即降負載，安排渦輪葉輪拆檢，確認葉片完整性",
        "urgency_rule": "XI_VIB 任一測點超過 1.4 mil p-p → 立即通知轉機組",
    },
]
(OUT / "failure_case_library.json").write_text(
    json.dumps(cases, ensure_ascii=False, indent=2), encoding="utf-8"
)
print("✓ failure_case_library.json")


# ── 6. maintenance_history.json ───────────────────────────────────────────────

maintenance = [
    {"date": "2026-03-13", "equipment": "COMP-102R-A", "type": "計劃性檢修", "content": "二級活塞桿檢修", "prism_tracked": True, "downtime_days": 2},
    {"date": "2025-12-31", "equipment": "COMP-102R-B", "type": "計劃性檢修", "content": "二級活塞桿回裝檢修", "prism_tracked": True, "downtime_days": 1},
    {"date": "2025-12-30", "equipment": "COMP-102R-B", "type": "計劃性檢修", "content": "二級活塞桿檢修", "prism_tracked": True, "downtime_days": 1},
    {"date": "2025-12-25", "equipment": "COMP-102R-S", "type": "計劃性檢修", "content": "一&二級活塞桿檢修", "prism_tracked": True, "downtime_days": 2},
    {"date": "2025-05-20", "equipment": "COMP-102R-S", "type": "故障維修", "content": "1&2級活塞環與閥座檢修", "prism_tracked": True, "downtime_days": 2},
    {"date": "2025-05-13", "equipment": "COMP-102R-B", "type": "故障維修", "content": "閥座洩漏拆裝", "prism_tracked": True, "downtime_days": 1},
    {"date": "2025-04-11", "equipment": "COMP-102R-A", "type": "計劃性檢修", "content": "二級活塞桿檢修", "prism_tracked": True, "downtime_days": 1},
    {"date": "2025-03-12", "equipment": "COMP-102R-A", "type": "計劃性檢修", "content": "二級活塞桿檢修", "prism_tracked": True, "downtime_days": 1},
    {"date": "2024-12-31", "equipment": "COMP-102R-B", "type": "計劃性檢修", "content": "二級活塞桿回裝", "prism_tracked": True, "downtime_days": 1},
    {"date": "2024-12-30", "equipment": "COMP-102R-B", "type": "計劃性檢修", "content": "二級活塞桿檢修", "prism_tracked": True, "downtime_days": 1},
    {"date": "2024-08-28", "equipment": "COMP-102R-B", "type": "故障維修",   "content": "壓縮機檢修拆裝（騎環磨損）", "prism_tracked": True, "downtime_days": 2},
    {"date": "2024-07-24", "equipment": "COMP-102R-A", "type": "計劃性檢修", "content": "壓縮機檢修回裝", "prism_tracked": True, "downtime_days": 1},
    {"date": "2024-07-23", "equipment": "COMP-102R-A", "type": "計劃性檢修", "content": "壓縮機檢修拆裝", "prism_tracked": True, "downtime_days": 1},
    {"date": "2024-05-13", "equipment": "COMP-102R-B", "type": "故障維修",   "content": "閥座洩漏拆裝", "prism_tracked": True, "downtime_days": 1},
]
(OUT / "maintenance_history.json").write_text(
    json.dumps(maintenance, ensure_ascii=False, indent=2), encoding="utf-8"
)
print("✓ maintenance_history.json")


# ── 7. heartbeat_snapshot.json ────────────────────────────────────────────────

# Simulates the output of the last heartbeat run (e.g., this morning)
snapshot = {
    "generated_at": f"{TODAY.isoformat()} 06:00",
    "scan_period_days": 30,
    "summary": {
        "total_equipment": 4,
        "alarm": 0,
        "warning": 1,
        "normal": 3,
    },
    "equipment_status": [
        {
            "equipment_id": "COMP-102R-B",
            "name": "往復式壓縮機 B台",
            "hpi": 61.1,
            "status": "warning",
            "top_contributors": [
                {"tag": "TI2_OUTLET", "desc": "二級出口溫度", "current": 147.3, "baseline": 141.0, "deviation_pct": 4.5, "trend": "↑ 持續上升 5 週"},
                {"tag": "II_CURRENT", "desc": "電動機電流",   "current": 166.2, "baseline": 158.0, "deviation_pct": 5.2, "trend": "↑ 持續上升 4 週"},
                {"tag": "PI2_OUTLET", "desc": "二級出口壓力", "current": 15.82, "baseline": 16.40, "deviation_pct": -3.5, "trend": "↓ 持續下降 3 週"},
            ],
            "alert_message": "⚠️ HPI 持續低於警戒值 70，主要偏差測點為二級出口溫度與電流，建議查閱診斷報告",
        },
        {
            "equipment_id": "COMP-102R-A",
            "name": "往復式壓縮機 A台",
            "hpi": 87.3,
            "status": "normal",
            "top_contributors": [],
            "alert_message": None,
        },
        {
            "equipment_id": "COMP-101C",
            "name": "離心式壓縮機",
            "hpi": 89.1,
            "status": "normal",
            "top_contributors": [],
            "alert_message": None,
        },
        {
            "equipment_id": "REACT-201",
            "name": "加氫裂解觸媒反應器",
            "hpi": None,
            "catalyst_activity": 62.3,
            "status": "normal",
            "alert_message": "ℹ️ 觸媒活性 62.3，距離換觸媒警戒值（55）尚有約 3 個月，請查閱觸媒活性預測報告",
        },
    ],
}
(OUT / "heartbeat_snapshot.json").write_text(
    json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8"
)
print("✓ heartbeat_snapshot.json")


# ── 8. catalyst/catalyst_activity_history.json ────────────────────────────────

# Catalyst loaded 2025-01-15, NOW is 2026-05-24 (16.3 months in)
# Exponential decay model: activity = 100 * exp(-k * t)
# Design life 24 months → activity at 24 months ≈ 42 (below alarm threshold 48)
# k = -ln(42/100) / 24 = 0.03666

cat_start = date(2025, 1, 15)
k = 0.03666
cat_history = []
d = cat_start
while d <= TODAY:
    t_months = (d - cat_start).days / 30.44
    base_activity = 100 * math.exp(-k * t_months)
    activity = round(noisy(base_activity, 0.4), 1)
    # Operator compensates by raising inlet temp (REACT_TEMP_IN)
    inlet_temp = round(noisy(355 + t_months * 2.1, 0.5), 1)
    conversion = round(noisy(max(88, 95 - t_months * 0.25), 0.3), 1)
    selectivity = round(noisy(max(82, 91 - t_months * 0.18), 0.2), 1)
    cat_history.append({
        "date": d.isoformat(),
        "catalyst_activity": activity,
        "REACT_TEMP_IN": inlet_temp,
        "CONVERSION": conversion,
        "SELECTIVITY": selectivity,
    })
    d += timedelta(days=7)  # weekly

# Future projection (next 8 months)
projections = []
for months_ahead in range(1, 9):
    proj_date = date(2026, 5, 24) + timedelta(days=int(months_ahead * 30.44))
    t_months = (proj_date - cat_start).days / 30.44
    activity = round(100 * math.exp(-k * t_months), 1)
    status = "normal" if activity >= 55 else ("warning" if activity >= 48 else "alarm")
    projections.append({
        "date": proj_date.isoformat(),
        "projected_activity": activity,
        "status": status,
    })

cat_data = {
    "reactor_id": "REACT-201",
    "catalyst_type": "Ni-Mo / Al₂O₃ 加氫裂解催化劑",
    "load_date": "2025-01-15",
    "warning_threshold": 55,
    "alarm_threshold": 48,
    "replacement_cost_ntd": 32_000_000,
    "design_life_months": 24,
    "current_activity": 62.3,
    "current_months_in_service": 16.3,
    "history": cat_history,
    "projections": projections,
    "optimal_replacement_window": {
        "start": "2026-08-01",
        "end": "2026-09-30",
        "rationale": "活性 55 預計在 2026-08 左右，此時更換可避免品質惡化，且不過早浪費剩餘活性",
    },
}
(OUT / "catalyst" / "catalyst_activity_history.json").write_text(
    json.dumps(cat_data, ensure_ascii=False, indent=2), encoding="utf-8"
)
print("✓ catalyst/catalyst_activity_history.json")


# ── 9. catalyst/catalyst_sop.json ─────────────────────────────────────────────

cat_sop = {
    "sop_id": "SOP-CAT-001",
    "title": "加氫裂解觸媒更換作業程序（REACT-201）",
    "version": "v2.3",
    "last_updated": "2024-03-01",
    "warning_threshold_activity": 55,
    "alarm_threshold_activity": 48,
    "steps": [
        "1. 確認觸媒活性指標連續 3 週低於警戒值 55，且進料溫度補償已達上限（420°C）",
        "2. 向製程部提交換觸媒申請，取得生產排程許可",
        "3. 計劃停機前 2 週通知觸媒供應商，確認備料到位（前置時間約 6-8 週，需提前訂購）",
        "4. 按 LOTO 程序停機，洩壓、沖洗反應器",
        "5. 確認溫度降至 < 80°C 後，開始卸載舊觸媒",
        "6. 依觸媒裝填程序填裝新觸媒，確認堆積密度符合規格",
        "7. 閉器、升壓、升溫，按預硫化（Presulfiding）程序活化觸媒",
        "8. 逐步升負荷至設計值，監測轉化率達標",
        "9. 記錄新觸媒裝填日期、批號，更新 PRiSM 模型基準線",
    ],
    "cost_note": "觸媒採購費用約 NT$32,000,000。更換時機過早（活性 > 60）每月浪費約 NT$1,800,000 剩餘價值；過晚（活性 < 48）每月因品質損失約 NT$3,500,000。",
    "procurement_lead_weeks": 6,
}
(OUT / "catalyst" / "catalyst_sop.json").write_text(
    json.dumps(cat_sop, ensure_ascii=False, indent=2), encoding="utf-8"
)
print("✓ catalyst/catalyst_sop.json")

print("\n✅ 所有假資料生成完成，輸出目錄：", OUT)
