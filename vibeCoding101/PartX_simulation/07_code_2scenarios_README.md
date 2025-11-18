**07_code_2scenarios.ipynb — Notebook 說明**

此檔案說明 `vibeCoding101/PartX_simulation/07_code_2scenarios.ipynb` 的目的、執行流程、每個程式格的功能、輸入/輸出，以及執行與除錯建議。

**目的**:
- 使用 eTBus（KMB）即時 ETA 資料推估路線頻率，並以 SimPy 建模公車到站、乘客到達與上車流程，評估乘客等待時間、巴士排隊時間與停靠（dwell）行為。
- 比較兩種主要情境：Scenario 1（Baseline）與 Scenario 2（路線分配/合併後）。

**如何執行**:
- 在 VS Code 中開啟 `vibeCoding101/PartX_simulation/07_code_2scenarios.ipynb`，啟動 kernel（預設 .venv），然後執行所有儲存格。
- 或在終端機執行 notebook 的片段化腳本（若已抽成 .py），或直接在 notebook 中改參數後執行。

**主要輸入來源**:
- eTBus API: `https://data.etabus.gov.hk/v1/transport/kmb/stop-eta/{stop_id}`（用以取得各站 ETA 清單）。

**主要輸出檔案（會產生於工作目錄）**:
- `simulation_results_baseline_stop_{stop_id}_morning_peak1.csv`：Scenario 1 每個 stop 的模擬結果（若該 stop 有有效 route 資料）。
- `simulation_results_allocated_stop_{stop_id}_morning_peak1.csv`：Scenario 2 的模擬結果。
- Notebook 內會產生多張視覺化圖像（bar、violin、hist、png 檔）。

**程式格（Cell-by-Cell）摘要（以 Cell 編號 1..11 表示）**
- Cell 1 — 取得站位資訊
  - 對多個 stop_id 呼叫 stop 資訊 API，列出站名與經緯度，並產生 Google Maps 連結。

- Cell 2 — St. Martin 的 ETA 擷取與篩選
  - 對 St. Martin 之 4 個 stop_id 呼叫 ETA API，將落在 `now + 5 min` 到 `now + 65 min` 的 ETA 篩出並列印。

- Cell 3 — CHONG SAN ROAD 的 ETA 擷取與篩選
  - 與 Cell 2 相同流程，但針對 CHONG SAN ROAD 的 4 個 stop_id。

- Cell 4 — 安裝註解
  - 只有註解 `#pip install simpy`，未執行安裝動作。

- Cell 5 — Scenario 1：Baseline 模擬
  - 定義模擬參數（SIM_TIME、BOARDING_TIME、BERTHS_PER_STOP、PASSENGER_RATE、NUM_SIMULATIONS 等）。
  - `get_real_time_routes(stop_id)`：用 ETA 計算每路線頻率（freq = 60 / mean(interval)）。
  - SimPy 元件：`passenger_generator`、`bus_generator`、`bus_process`、`run_simulation`。
  - 主迴圈會對每個 stop 跑 NUM_SIMULATIONS 次模擬並寫出 CSV 檔。

- Cell 6 — Scenario 2：路線分配與模擬
  - 在收集所有 stop 的 route 資料後，呼叫 `allocate_routes` 對共享路線做簡單分配（奇偶頻率或獨佔性），再對分配結果跑相同 SimPy 模擬流程。

- Cell 7 — 情境比較長條圖
  - 使用範例數據產生 Scenario 1 vs Scenario 2 的 bar charts（等待時間與排隊時間比較）。

- Cell 8 — Violin plot（合成資料）
  - 以常態分配生成合成模擬資料，畫出 violin plots（乘客等待與排隊時間）。

- Cell 9 — Violin plot（Poisson / Exponential，需 SciPy）
  - 使用 `scipy.stats.expon` 與 `poisson` 生成資料；此格在未安裝 `scipy` 時會失敗（Notebook 中曾報錯）。

- Cell 10 — Histogram 比較
  - 使用範例數據繪製等待與排隊時間的直方圖，分 Scenario 顯示。

- Cell 11 — Route-specific 分析
  - 讀取前述產生的 CSV（若存在），將 `routes` 欄位解析成 list，並為每條 route 繪製 route-by-route 的 violin 圖；若某些 CSV 不存在會被跳過並印出提示。

**可調整參數（常見）**
- `SIM_TIME`（模擬秒數，預設 3600）
- `NUM_SIMULATIONS`（重覆次數，示範中預設 100，可改為 200 以符合你的 KPI 表）
- `BOARDING_TIME` / `CLEARANCE_TIME` / `BERTHS_PER_STOP` / `PASSENGER_RATE`

**已知限制與注意事項**
- ETA → 頻率 的估算依賴足夠的 ETA 點。若某路線 ETA 數量太少，freq 計算會不穩定。
- 模擬為每個 stop 獨立執行（未建模路線/車輛間的網路互動或延遲傳播）。若需更精細的車輛流動，需改成 network-level 模型。
- `scipy` 未安裝會造成使用 `expon`/`poisson` 的儲存格失敗（解法：在 kernel 中 `%pip install scipy` 或使用 `notebook_install_packages`）。

**建議的後續操作**
- 若要與你提供的 KPI 表完全對齊，將 `NUM_SIMULATIONS` 改為 200 並重新執行 Scenario 1 & 2，接著由生成的 CSV 計算 avg/median/p90、mean_boarded 等指標（我可以代為執行）。
- 若要更忠實還原觀察到的到站模式，可把 ETA 清單直接做 schedule-driven simulation（把 ETA 轉為 env 事件），我可以示範如何改寫。

**聯絡點（在 repo 中）**
- Notebook 檔案：`vibeCoding101/PartX_simulation/07_code_2scenarios.ipynb`
- 本說明檔：`vibeCoding101/PartX_simulation/07_code_2scenarios_README.md`（此檔）
- KPI 視覺化腳本（示例）：`presentation/simulation/plot_kpi_comparison.py`

---
最後，如果你要我把 `NUM_SIMULATIONS` 改為 200 並執行整個 notebook（產生符合你 KPI 表的模擬結果），或把模擬改為 schedule-driven，請回覆你想要的選項，我會接著操作。
