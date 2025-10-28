
# Team 6 Bus Stop Merge — API Reference and Data Request (Citybus)

本節整理自 Citybus Open Data API 規格（https://www.citybus.com.hk/datagovhk/bus_eta_api_specifications.pdf），供團隊技術討論與資料查詢信參考：

## 1. Bus Stop API
- Endpoint 範例：`/v1/transport/bus-stop`
- 主要欄位：`stop_id`, `name_tc`, `name_en`, `lat`, `long`, `location_type`, `accessible`（如有）
- 說明：回傳所有巴士站的唯一 ID、中英文名稱、座標。若能提供無障礙設施（如斜道、觸覺鋪面）欄位更佳。

## 2. Route API
- Endpoint 範例：`/v1/transport/route`
- 主要欄位：`route`, `service_type`, `bound`, `orig_tc`, `orig_en`, `dest_tc`, `dest_en`, `stops`（依序 stop_id）
- 說明：回傳所有路線、方向、每條路線的站序、服務類型、起訖站名稱。

## 3. API 回應格式範例
- 範例：`GET https://rt.data.gov.hk/v1/transport/bus-stop`
- 回應（JSON）：
	```json
	{
		"data": [
			{"stop_id": "001234", "name_tc": "中環碼頭", "name_en": "Central Ferry Piers", "lat": 22.287, "long": 114.158, "location_type": "bus", "accessible": true},
			...
		]
	}
	```
- 可接受 JSON、CSV 或 GTFS 格式。

如無法直接 API 存取，也可請對方一次性匯出（CSV/JSON/Excel）上述欄位。
