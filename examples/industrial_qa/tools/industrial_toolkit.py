import json
import pathlib

from neurforge.tools.base import AsyncBaseToolkit
from neurforge.tools.utils import register_tool

DATA_DIR = pathlib.Path(__file__).parent.parent / "mock_data"


def _load(filename: str) -> list | dict:
    with open(DATA_DIR / filename, encoding="utf-8") as f:
        return json.load(f)


class IndustrialQAToolkit(AsyncBaseToolkit):
    """Mock industrial data toolkit for NeurForge scenario demos.

    Tools:
        - get_equipment_info(equipment_id)
        - query_work_orders(equipment_id, status)
        - get_anomaly_records(equipment_id, resolved)
        - search_sop(keyword)
        - get_process_params(facility_type)
        - predict_cement_quality(rpm, water_ratio_pct, mixing_time_min)
        - get_stenter_setting(fabric_code)
        - get_power_plant_trend(months)
    """

    @register_tool
    def get_equipment_info(self, equipment_id: str) -> str:
        """查詢設備基本資料，包含位置、製造商、負責團隊與上次保養日期。

        Args:
            equipment_id: 設備編號，例如 EQ-001
        """
        registry = _load("equipment_registry.json")
        matches = [e for e in registry if e["equipment_id"] == equipment_id]
        if not matches:
            return json.dumps({"error": f"找不到設備 {equipment_id}"}, ensure_ascii=False)
        return json.dumps(matches[0], ensure_ascii=False, indent=2)

    @register_tool
    def query_work_orders(self, equipment_id: str = "", status: str = "") -> str:
        """查詢工單紀錄。可依設備編號與狀態篩選。

        Args:
            equipment_id: 設備編號，留空代表不篩選
            status: 工單狀態，可選「已完成」「進行中」「待處理」，留空代表全部
        """
        orders = _load("work_orders.json")
        result = orders
        if equipment_id:
            result = [o for o in result if o["equipment_id"] == equipment_id]
        if status:
            result = [o for o in result if o["status"] == status]
        if not result:
            return json.dumps({"message": "無符合條件的工單"}, ensure_ascii=False)
        return json.dumps(result, ensure_ascii=False, indent=2)

    @register_tool
    def get_anomaly_records(self, equipment_id: str = "", resolved: str = "") -> str:
        """查詢設備異常紀錄。

        Args:
            equipment_id: 設備編號，留空代表全部設備
            resolved: 是否已解決，填「true」或「false」，留空代表全部
        """
        records = _load("anomaly_records.json")
        result = records
        if equipment_id:
            result = [r for r in result if r["equipment_id"] == equipment_id]
        if resolved != "":
            flag = resolved.lower() == "true"
            result = [r for r in result if r["resolved"] == flag]
        if not result:
            return json.dumps({"message": "無符合條件的異常紀錄"}, ensure_ascii=False)
        return json.dumps(result, ensure_ascii=False, indent=2)

    @register_tool
    def search_sop(self, keyword: str) -> str:
        """依關鍵字搜尋 SOP 作業程序文件。

        Args:
            keyword: 搜尋關鍵字，例如「葉片」「溫度」「熱電偶」
        """
        sops = _load("sop_library.json")
        kw = keyword.lower()
        matched = []
        for sop in sops:
            searchable = (
                sop["title"] + sop["sop_id"] + sop.get("warning", "") +
                " ".join(sop.get("steps", []))
            ).lower()
            if kw in searchable:
                matched.append(sop)
        if not matched:
            return json.dumps({"message": f"未找到含「{keyword}」的 SOP"}, ensure_ascii=False)
        return json.dumps(matched, ensure_ascii=False, indent=2)

    @register_tool
    def get_process_params(self, facility_type: str) -> str:
        """取得製程參數資料表。

        Args:
            facility_type: 設施類型，可選「cement」（水泥攪拌）、「textile」（紡織定型機）、「power_plant」（電廠效率）
        """
        mapping = {
            "cement": "process_params/cement_mixing.json",
            "textile": "process_params/textile_stenter.json",
            "power_plant": "process_params/power_plant.json",
        }
        filename = mapping.get(facility_type.lower())
        if not filename:
            available = list(mapping.keys())
            return json.dumps({"error": f"不支援的類型：{facility_type}，可選：{available}"}, ensure_ascii=False)
        data = _load(filename)
        return json.dumps(data, ensure_ascii=False, indent=2)

    @register_tool
    def predict_cement_quality(self, rpm: float, water_ratio_pct: float, mixing_time_min: float) -> str:
        """根據攪拌轉速、加水率與攪拌時間，預測水泥坍度與 28 天抗壓強度，並判斷是否符合品質標準。
        加水率由 YOLO 視覺系統量測。

        Args:
            rpm: 攪拌轉速（轉/分鐘）
            water_ratio_pct: 加水率百分比（%）
            mixing_time_min: 攪拌時間（分鐘）
        """
        data = _load("process_params/cement_mixing.json")
        spec = data["quality_spec"]

        # 線性回歸近似（由歷史批次資料擬合）
        slump = round(18.5 + 1.0 * (water_ratio_pct - 38.0) - 0.2 * (rpm - 145) - 0.5 * (mixing_time_min - 4.5), 1)
        strength = round(42.0 - 1.2 * (water_ratio_pct - 38.0) + 0.3 * (rpm - 145) + 0.8 * (mixing_time_min - 4.5), 1)

        slump_pass = spec["slump_min_cm"] <= slump <= spec["slump_max_cm"]
        strength_pass = strength >= spec["strength_28d_min_mpa"]
        overall_pass = slump_pass and strength_pass

        result = {
            "input": {"rpm": rpm, "water_ratio_pct": water_ratio_pct, "mixing_time_min": mixing_time_min},
            "predicted_slump_cm": slump,
            "predicted_strength_28d_mpa": strength,
            "quality_spec": spec,
            "slump_pass": slump_pass,
            "strength_pass": strength_pass,
            "overall_pass": overall_pass,
            "recommendation": (
                "製程參數在規格範圍內，可正常出貨。" if overall_pass else
                ("坍度超標，請降低加水率或提升轉速。" if not slump_pass else "強度預測不足，請降低加水率並確認攪拌時間。")
            )
        }
        return json.dumps(result, ensure_ascii=False, indent=2)

    @register_tool
    def get_stenter_setting(self, fabric_code: str) -> str:
        """查詢特定布料規格的定型機溫度與速度建議設定。

        Args:
            fabric_code: 布料代碼，例如 PET-150D、NYLON-70D、COTTON-32S、TC-65-35
        """
        data = _load("process_params/textile_stenter.json")
        fc = fabric_code.upper()
        matched = [p for p in data["products"] if p["fabric_code"] == fc]
        if not matched:
            available = [p["fabric_code"] for p in data["products"]]
            return json.dumps({"error": f"找不到布料代碼 {fabric_code}，可用代碼：{available}"}, ensure_ascii=False)
        result = {
            "facility": data["facility"],
            "equipment": data["equipment"],
            "zones": data["zones"],
            "setting": matched[0]
        }
        return json.dumps(result, ensure_ascii=False, indent=2)

    @register_tool
    def get_power_plant_trend(self, months: int = 6) -> str:
        """查詢電廠最近 N 個月的熱耗率、鍋爐效率與發電量趨勢。

        Args:
            months: 要查詢的最近月份數，預設 6
        """
        data = _load("process_params/power_plant.json")
        records = data["monthly_records"][-months:]
        result = {
            "facility": data["facility"],
            "benchmarks": data["benchmarks"],
            "records": records,
            "trend_note": (
                "熱耗率上升或鍋爐效率下滑代表設備狀況惡化，建議對照保養紀錄分析原因。"
            )
        }
        return json.dumps(result, ensure_ascii=False, indent=2)
