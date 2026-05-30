"""CaseDetectiveAgent (案件偵探) toolkit — telecom customer service tools."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from neurforge.tools.base import AsyncBaseToolkit
from neurforge.tools.utils import register_tool

_DATA = Path(__file__).parent.parent / "mock_data"


def _load(path: Path) -> Any:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


class CaseDetectiveToolkit(AsyncBaseToolkit):
    """案件偵探電信客服 toolkit — billing, SLA, speed, construction, follow-up."""

    def __init__(self, config=None) -> None:
        super().__init__(config)

    @register_tool
    def get_customer_profile(self, customer_id: str) -> str:
        """查詢客戶基本資料、訂閱方案、合約期間與 VIP 等級。

        Args:
            customer_id: 客戶編號，例如 C-10001
        """
        data = _load(_DATA / "customer_profiles.json")
        matches = [c for c in data if c["customer_id"] == customer_id]
        if not matches:
            return json.dumps({"error": f"找不到客戶 {customer_id}"}, ensure_ascii=False)
        return json.dumps(matches[0], ensure_ascii=False)

    @register_tool
    def search_customer_by_name(self, name: str) -> str:
        """以客戶姓名搜尋客戶資料（支援部分比對）。

        Args:
            name: 客戶姓名或部分姓名，例如 "陳怡君" 或 "陳"
        """
        data = _load(_DATA / "customer_profiles.json")
        matches = [c for c in data if name in c["name"]]
        if not matches:
            return json.dumps({"error": f"找不到姓名包含 '{name}' 的客戶"}, ensure_ascii=False)
        return json.dumps(matches, ensure_ascii=False)

    @register_tool
    def get_billing_history(self, customer_id: str, months: int = 6) -> str:
        """查詢客戶最近 N 個月的帳單記錄，包含基本費、額外費用與繳費狀態。

        Args:
            customer_id: 客戶編號
            months: 查詢月份數（預設 6）
        """
        data = _load(_DATA / "billing_history.json")
        records = [r for r in data if r["customer_id"] == customer_id]
        records = sorted(records, key=lambda x: x["billing_month"])[-months:]
        if not records:
            return json.dumps({"error": f"找不到客戶 {customer_id} 的帳單資料"}, ensure_ascii=False)
        return json.dumps({"customer_id": customer_id, "total": len(records), "records": records}, ensure_ascii=False)

    @register_tool
    def get_complaint_cases(self, customer_id: str) -> str:
        """查詢指定客戶的所有申訴案件記錄（含歷史已結案與進行中案件）。

        Args:
            customer_id: 客戶編號
        """
        data = _load(_DATA / "complaint_cases.json")
        cases = [c for c in data if c["customer_id"] == customer_id]
        cases = sorted(cases, key=lambda x: x["opened_date"])
        if not cases:
            return json.dumps({"message": f"客戶 {customer_id} 無申訴紀錄", "total": 0}, ensure_ascii=False)
        return json.dumps({"customer_id": customer_id, "total": len(cases), "cases": cases}, ensure_ascii=False)

    @register_tool
    def get_case_detail(self, case_id: str) -> str:
        """查詢單一申訴案件的完整細節。

        Args:
            case_id: 案件編號，例如 CASE-2026-0518
        """
        data = _load(_DATA / "complaint_cases.json")
        matches = [c for c in data if c["case_id"] == case_id]
        if not matches:
            return json.dumps({"error": f"找不到案件 {case_id}"}, ensure_ascii=False)
        return json.dumps(matches[0], ensure_ascii=False)

    @register_tool
    def get_sla_records(self, customer_id: str, months: int = 6) -> str:
        """查詢客戶最近 N 個月的 SLA 達成狀況，包含可用率、延遲、封包遺失率。

        Args:
            customer_id: 客戶編號
            months: 查詢月份數（預設 6）
        """
        data = _load(_DATA / "sla_records.json")
        records = [r for r in data if r["customer_id"] == customer_id]
        records = sorted(records, key=lambda x: x["month"])[-months:]
        if not records:
            return json.dumps({"error": f"找不到客戶 {customer_id} 的 SLA 記錄"}, ensure_ascii=False)
        violations = [r for r in records if not r["met_sla"]]
        return json.dumps({
            "customer_id": customer_id,
            "months_checked": len(records),
            "sla_violations": len(violations),
            "records": records,
        }, ensure_ascii=False)

    @register_tool
    def get_speed_test_logs(self, customer_id: str) -> str:
        """查詢客戶的歷史測速紀錄，用於判斷網速是否持續低於合約保證值。

        Args:
            customer_id: 客戶編號
        """
        data = _load(_DATA / "speed_test_logs.json")
        logs = [r for r in data if r["customer_id"] == customer_id]
        logs = sorted(logs, key=lambda x: x["test_datetime"])
        if not logs:
            return json.dumps({"message": f"客戶 {customer_id} 無測速紀錄", "total": 0}, ensure_ascii=False)
        below_count = sum(1 for r in logs if r["below_guarantee"])
        return json.dumps({
            "customer_id": customer_id,
            "total_tests": len(logs),
            "below_guarantee_count": below_count,
            "logs": logs,
        }, ensure_ascii=False)

    @register_tool
    def lookup_construction(self, district: str) -> str:
        """查詢指定行政區附近的施工工程，確認是否有影響電信服務的施工。

        Args:
            district: 行政區名稱，例如 "新北市板橋區" 或 "台北市信義區"
        """
        data = _load(_DATA / "construction_lookup.json")
        matches = [c for c in data if district in c["district"] or c["district"] in district]
        if not matches:
            return json.dumps({"message": f"'{district}' 附近無在案施工紀錄", "total": 0}, ensure_ascii=False)
        return json.dumps({"district": district, "total": len(matches), "projects": matches}, ensure_ascii=False)

    @register_tool
    def get_followup_tasks(self, customer_id: str = "", case_id: str = "") -> str:
        """查詢待處理的後續追蹤任務。可依客戶編號或案件編號篩選。

        Args:
            customer_id: 客戶編號（選填）
            case_id: 案件編號（選填）
        """
        data = _load(_DATA / "followup_tasks.json")
        results = data
        if customer_id:
            results = [t for t in results if t.get("customer_id") == customer_id]
        if case_id:
            results = [t for t in results if t.get("case_id") == case_id]
        overdue = [t for t in results if t["status"] == "overdue"]
        return json.dumps({
            "total": len(results),
            "overdue_count": len(overdue),
            "tasks": results,
        }, ensure_ascii=False)

    @register_tool
    def search_knowledge_base(self, keywords: str) -> str:
        """搜尋客服知識庫，查詢帳單處理、SLA 補償、升級規則等標準作業說明。

        Args:
            keywords: 搜尋關鍵字，以空格分隔，例如 "SLA 補償 企業"
        """
        data = _load(_DATA / "knowledge_base.json")
        kws = keywords.lower().split()
        results = []
        for article in data:
            text = json.dumps(article, ensure_ascii=False).lower()
            if any(kw in text for kw in kws):
                results.append(article)
        if not results:
            return json.dumps({"message": "知識庫中無符合條件的文章", "total": 0}, ensure_ascii=False)
        return json.dumps({"total": len(results), "articles": results}, ensure_ascii=False)
