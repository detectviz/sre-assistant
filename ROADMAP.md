# ROADMAP.md - SRE Assistant 實施路線圖 (v3)

**版本**: 3.0.0
**狀態**: 生效中 (Active)
**關聯架構**: [ARCHITECTURE.md](ARCHITECTURE.md)

## 總體目標

本路線圖旨在引導 SRE Assistant 完成其核心戰略轉型：從一個與 Grafana 整合的工具，演進為一個由 **`control-plane` 指揮的、無介面的 (headless) 專家代理**。我們的首要任務是實現與 `control-plane` 的無縫對接，並在此基礎上，逐步擴展其作為後端核心大腦的自動化能力。

---

## Phase 1: Control-Plane 核心整合 (Core Integration)

- **預計時間**: 1-2 個月
- **主題**: 專注於完成 `sre-assistant` 與 `control-plane` 之間的所有技術對接工作，確保兩者能夠安全、可靠地協同工作。
- **關鍵目標**: 實現一個可由 `control-plane` 觸發並完成端到端診斷流程的最小可行產品 (MVP)。

### 主要交付物 (Key Deliverables):

- **1.1. API 契約符合性 (API Contract Compliance)**:
    - 🎯 **任務**: 確保 `sre-assistant` 的 FastAPI 服務嚴格遵守 `control-plane/openapi.yaml` 中定義的所有端點、請求格式和回應格式。
    - **驗收標準**: `sre-assistant` 能夠成功接收並解析來自 `control-plane` 的所有 API 請求。

- **1.2. 服務對服務認證 (M2M Authentication)**:
    - 🔐 **任務**: 根據新 `ARCHITECTURE.md` 的定義，完整實現基於 Keycloak 和 Client Credentials Flow 的 `AuthProvider`。
    - **驗收標準**: `sre-assistant` 的 API 端點能夠成功驗證來自 `control-plane` 的 JWT，並拒絕無效請求。

- **1.3. 開發 `ControlPlaneTool`**:
    - 🛠️ **任務**: 開發一個新的工具，專門用於回頭呼叫 `control-plane` 的 API，以獲取必要的上下文資訊。
    - **驗收標準**:
        - `ControlPlaneTool` 能夠成功呼叫 `control-plane` 的 `GET /api/v1/audit-logs` 端點。
        - 該工具能夠處理認證，將自身的 M2M Token 用於 API 請求。

- **1.4. 端到端流程測試**:
    - 🔗 **任務**: 建立一個整合測試，模擬從 `control-plane` 觸發一個部署診斷，到 `sre-assistant` 執行、回調 `control-plane` API，並最終返回結果的完整流程。
    - **驗收標準**: 整合測試通過，證明核心對接流程已打通。

---

## Phase 2: 功能擴展與遷移 (Feature Expansion & Migration)

- **預計時間**: 2-3 個月
- **主題**: 在完成核心整合的基礎上，將舊架構中有價值的核心功能，遷移並適應到新的 `control-plane` 指揮模式下。
- **關鍵目標**: 豐富 `sre-assistant` 的診斷與分析能力，使其能夠處理更多元的任務。

### 主要交付物 (Key Deliverables):

- **2.1. 增強診斷能力**:
    - 🩺 **任務**: 完善 `deployment` 和 `alert` 診斷流程的內部邏輯，確保其能夠利用 `ControlPlaneTool` 獲取上下文，並結合觀測工具（Prometheus, Loki）進行深入分析。

- **2.2. 結構化報告生成**:
    - 📝 **任務**: 重構覆盤報告 (Postmortem) 的生成功能，使其能夠根據 `control-plane` 傳遞的事件 ID，自動生成結構化的分析報告。

- **2.3. 人類介入流程 (Human-in-the-Loop)**:
    - 🧑‍💻 **任務**: 改造 `HumanApprovalTool`。當需要人工審批時，應透過 `control-plane` 的通知系統（如果存在）或一個回呼 (Callback) URL，將審批請求導向 `control-plane` 的 UI 介面，而不是依賴於 Grafana。

---

## Phase 3: 聯邦化與主動預防 (Federation & Proactive Prevention)

- **預計時間**: 3-6 個月
- **主題**: 此階段的目標與舊路線圖類似，專注於 `sre-assistant` 自身的長期演進，使其變得更加智能和主動。
- **關鍵目標**: 將 `sre-assistant` 從單一代理演進為多代理協同的聯邦化系統，並具備預測性維護能力。

### 主要交付物 (Key Deliverables):

- **3.1. 第一個專業化子代理**:
    - 🤖 **任務**: 將一項核心功能（如覆盤報告生成）重構為一個獨立的、可透過 A2A (Agent-to-Agent) 協議呼叫的 `PostmortemAgent`。

- **3.2. 主動預防能力**:
    - 🔮 **任務**: 整合機器學習模型，用於異常檢測和趨勢預測，實現從「被動響應」到「主動預防」的轉變。

- **3.3. 代理可觀測性**:
    - 📊 **任務**: 建立一個完善的 LLM 可觀測性儀表板，用於追蹤代理的決策過程、成本和性能，確保系統的可靠性和可維護性。
