"""SensorSageAgent (機況先知) toolkit — PdM tools for compressor + catalyst monitoring."""

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


class SensorSageToolkit(AsyncBaseToolkit):
    """機況先知 PdM toolkit — heartbeat, HPI, sensor trends, failure cases, maintenance."""

    def __init__(self, config=None) -> None:
        super().__init__(config)

    @register_tool
    def get_heartbeat_snapshot(self) -> str:
        """取得最新心跳掃描快照，顯示所有設備的目前 HPI 狀態與警示摘要。"""
        data = _load(_DATA / "heartbeat_snapshot.json")
        return json.dumps(data, ensure_ascii=False)

    @register_tool
    def get_equipment_list(self) -> str:
        """列出廠區所有設備的基本資料（設備ID、名稱、類型、規格、安裝日期）。"""
        data = _load(_DATA / "equipment_registry.json")
        return json.dumps(data, ensure_ascii=False)

    @register_tool
    def get_sensor_tags(self, equipment_id: str) -> str:
        """取得指定設備的 PI Tag 清單與正常操作範圍。

        Args:
            equipment_id: 設備編號，例如 COMP-102R-B
        """
        data = _load(_DATA / "sensor_tags.json")
        tags = [t for t in data if t.get("equipment_id") == equipment_id]
        if not tags:
            return json.dumps({"error": f"找不到設備 {equipment_id} 的感測器資料"}, ensure_ascii=False)
        return json.dumps(tags, ensure_ascii=False)

    @register_tool
    def get_hpi_history(self, equipment_id: str, weeks: int = 20) -> str:
        """取得指定設備的 HPI 歷史趨勢（最近 N 週）。

        Args:
            equipment_id: 設備編號，例如 COMP-102R-B
            weeks: 要查詢的週數（預設 20）
        """
        data = _load(_DATA / "hpi_history.json")
        records = [r for r in data if r.get("equipment_id") == equipment_id]
        records = sorted(records, key=lambda x: x["week_start"])[-weeks:]
        if not records:
            return json.dumps({"error": f"找不到設備 {equipment_id} 的 HPI 資料"}, ensure_ascii=False)
        return json.dumps(records, ensure_ascii=False)

    @register_tool
    def get_sensor_trends(self, equipment_id: str, weeks: int = 8) -> str:
        """取得指定設備最近 N 週各測點數值趨勢，用於識別偏差測點。

        Args:
            equipment_id: 設備編號，例如 COMP-102R-B
            weeks: 要查詢的週數（預設 8）
        """
        data = _load(_DATA / "sensor_trends.json")
        records = [r for r in data if r.get("equipment_id") == equipment_id]
        records = sorted(records, key=lambda x: x["week_start"])[-weeks:]
        if not records:
            return json.dumps({"error": f"找不到設備 {equipment_id} 的感測器趨勢資料"}, ensure_ascii=False)
        return json.dumps(records, ensure_ascii=False)

    @register_tool
    def search_failure_cases(self, symptom_keywords: str) -> str:
        """搜尋老師傅知識庫，根據症狀關鍵字找出歷史故障案例與診斷建議。

        Args:
            symptom_keywords: 症狀關鍵字，以空格分隔，例如 "出口溫度 電流 壓力下降"
        """
        data = _load(_DATA / "failure_case_library.json")
        keywords = symptom_keywords.lower().split()
        results = []
        for case in data:
            searchable = json.dumps(case, ensure_ascii=False).lower()
            if any(kw in searchable for kw in keywords):
                results.append(case)
        if not results:
            return json.dumps({"message": "未找到符合症狀的歷史案例", "total": 0}, ensure_ascii=False)
        return json.dumps({"total": len(results), "cases": results}, ensure_ascii=False)

    @register_tool
    def get_maintenance_history(self, equipment_id: str) -> str:
        """查詢指定設備的歷史維護工單紀錄（包含 PM、預測性維護、緊急搶修）。

        Args:
            equipment_id: 設備編號，例如 COMP-102R-B
        """
        data = _load(_DATA / "maintenance_history.json")
        records = [r for r in data if r.get("equipment_id") == equipment_id]
        records = sorted(records, key=lambda x: x["date"])
        if not records:
            return json.dumps({"message": f"設備 {equipment_id} 無維護紀錄", "total": 0}, ensure_ascii=False)
        return json.dumps({"equipment_id": equipment_id, "total": len(records), "records": records}, ensure_ascii=False)

    @register_tool
    def get_catalyst_status(self) -> str:
        """取得 REACT-201 觸媒反應器的目前活性指數、衰退趨勢與更換時程預測。"""
        history = _load(_DATA / "catalyst" / "catalyst_activity_history.json")
        # 最近一筆 + 摘要
        records = sorted(history, key=lambda x: x["month"])
        latest = records[-1] if records else {}
        summary = {
            "latest_record": latest,
            "total_months_tracked": len(records),
            "first_record": records[0] if records else {},
            "trend_note": "活性指數自 2025-01 起持續線性下降，平均每月降低約 2.1 個百分點",
        }
        return json.dumps(summary, ensure_ascii=False)

    @register_tool
    def get_catalyst_history(self, months: int = 18) -> str:
        """取得觸媒活性指數的歷史月度數據。

        Args:
            months: 要查詢的月份數（預設 18）
        """
        data = _load(_DATA / "catalyst" / "catalyst_activity_history.json")
        records = sorted(data, key=lambda x: x["month"])[-months:]
        return json.dumps(records, ensure_ascii=False)

    @register_tool
    def get_catalyst_replacement_sop(self) -> str:
        """取得觸媒更換 SOP，包含作業程序、安全注意事項與費用估算。"""
        data = _load(_DATA / "catalyst" / "catalyst_sop.json")
        return json.dumps(data, ensure_ascii=False)
