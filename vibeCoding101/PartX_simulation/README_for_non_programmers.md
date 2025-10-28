## 簡要說明（非程式人員可讀）

這個資料夾：`vibeCoding101/PartX_simulation` 包含一些小工具和結果檔，用來示範如何從公共巴士 API 取得站點的到站資訊（ETA），並用簡單的模擬來估計乘客候車與上車情況。下面用最少術語、一步步說明每個檔案的用途與如何解讀結果。

---

主要檔案與說明（路徑請以專案根目錄為起點）

- `vibeCoding101/PartX_simulation/use_notebook_data.py`  
  功能：讀入站點清單（`kmb_stations.json`），向 KMB 的公開 API 詢問每個站的到站資料，並把回傳結果整理成兩個檔案：`kmb_extracted.json`（機器用）與一個時間戳的 CSV（例如 `kmb_extracted_20251028_044934.csv`）。
  非程式人員理解：把線上每個站目前的「哪班車、何時會到」資訊抓下來並存成表格，方便後續分析。

- `vibeCoding101/PartX_simulation/kmb_stations.json`  
  功能：站點清單，列出此專案希望查詢的站與其 stop id（識別碼）。

- `vibeCoding101/PartX_simulation/kmb_extracted.json`  
  功能：`use_notebook_data.py` 執行後產出的 JSON 格式資料（每筆包含路線、ETA、時間戳與對應站名）。

- `vibeCoding101/PartX_simulation/kmb_extracted_20251028_044934.csv`  
  功能：供人閱讀的表格（CSV），每一列代表一筆 ETA 記錄，可用 Excel 或 Google Sheets 開啟檢視。

- `vibeCoding101/PartX_simulation/sim_from_extracted.py`  
  功能：讀取 `kmb_extracted.json`（或 CSV 轉成的資料），把未來一段時間（預設 120 分鐘）內的 ETA 轉成「到站事件」，再用簡單的模擬器模擬乘客到站與巴士上車行為，最後輸出簡單統計（Total boarded、Remaining queue、Average wait、Median wait）。
  非程式人員理解：這個程式會回答「接下來一小時內，這個站可能會有多少人上車？還會剩多少人在等？平均等多久？」等問題。

- `vibeCoding101/PartX_simulation/sim_kmb_stops.py`  
  功能：一個更完整的腳本，可以直接向線上 API 查詢（透過站名或 stop id），並即時執行模擬。`sim_from_extracted.py` 則是讓你以已抓好的資料離線（不用再重抓 API）執行模擬。

- `vibeCoding101/PartX_simulation/requirements.txt`  
  功能：列出上述程式所需的 Python 套件（若要自己在電腦上執行，需要先安裝這些套件）。

---

CSV（`kmb_extracted_20251028_044934.csv`）欄位解釋

- `stop_id`：站點識別碼（機器用的 ID），對應到某個實體站牌。
- `route`：路線號碼（例如 272A、74D 等）。
- `direction`：方向代碼（例如 O 或 I，代表 Outbound/Inbound 系統代碼）。
- `eta`：預計到站時間（例如 `2025-10-28T12:52:20+08:00`），若為空白表示沒有當時的即時 ETA。
- `eta_seq`：同一路線的第幾個預計班次（第 1、2 班…）。
- `data_timestamp`：API 回傳資料的時間（告訴你這筆 ETA 是何時被提供的）。
- `station`：人類可讀的站名（例如 `St. Martin`）。

例子（一列示範）
- `3F24CFF9046300D9,272A,O,2025-10-28T12:52:20+08:00,1,2025-10-28T12:49:16+08:00,St. Martin`  
  讀法：在 `St. Martin` 站，272A 路線的第 1 班預計在 2025-10-28 12:52 到站；該資訊在 12:49:16 從 API 拿到。

---

如何重現（最少技術步驟）
1. 如果你只想看資料（不用跑程式）：用 Excel 或 Google Sheets 打開 `vibeCoding101/PartX_simulation/kmb_extracted_20251028_044934.csv`。
2. 如果想重新抓一次最新資料（需要能上網的環境，並請技術人員協助執行）：

```bash
python3 vibeCoding101/PartX_simulation/use_notebook_data.py
```

3. 如果想用抽出的資料跑模擬（已在專案中準備好）：

```bash
python3 vibeCoding101/PartX_simulation/sim_from_extracted.py --stations "St. Martin" "CHONG SAN ROAD" --horizon 60 --rate 0.8 --capacity 50
```

上面範例會模擬下一 60 分鐘，乘客到達率假設為 0.8 人/分鐘（大約每 1.25 分鐘來一人），巴士座位容量 50；輸出會是簡短的統計數字，例如總共上了多少人、還剩多少人在排隊、平均等多久。

---

讀到的注意事項（給非程式人員的提醒）
- 許多資料列的 `eta` 欄位是空白：表示當時 API 沒提供該路線的即時到站資料，模擬會忽略那些空白的列。
- CSV 有時會出現重複的記錄（相同路線與相同 ETA 多次出現）：這可能是 API 回傳的原始資料本身包含重複，或因為我們在不同 stop id 上抓到相同班次而產生重複。重複會讓模擬把一班車模擬成多次到站——如果需要更精確的結果，建議先做「去重」處理（技術人員可用路線+ETA 去重）。
- API 依賴網路：若執行 `use_notebook_data.py` 時出現錯誤，可能是網路連線或 API 服務本身暫時不可用，請稍候再試或提供截圖錯誤訊息給技術人員。

---

建議的下一步（非程式人員可決定）
1. 若想要更穩定的模擬結果：請技術人員幫忙在產生 `kmb_extracted.csv` 時做去重（例如：同一路線同一 ETA 只保留一筆），然後再跑模擬。  
2. 若想比較不同情境（例如不同到達率或不同巴士容量），可請技術人員使用 `sim_from_extracted.py` 調整 `--rate` 與 `--capacity`，並把結果寫成表格供比較。  
3. 若要把 Citybus（`003736`）的即時 ETA 也整合進來，請告訴我，我可以嘗試用 route-level 的 Citybus API 呼叫並把結果合併。

---

如果需要，我可以把這份說明再簡化為一頁 A4 的「操作步驟」，或製作一個簡單的說明影片腳本（指示用戶點選哪個檔案、如何開 Excel 檢視）。

需要我把這個說明 commit 到 Git 並幫您推上遠端嗎？（我可以協助，但先前嘗試推送時發現 repo 處於 detached HEAD 或需要設定 upstream — 我可以在您允許下幫忙處理。）

---

檔案最後更新：2025-10-28（與專案內產出時間同步）

作者：自動產生的專案說明（已由系統檢查並整理成非技術文件）
