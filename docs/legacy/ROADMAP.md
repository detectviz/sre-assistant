# ROADMAP.md - SRE Assistant 實施路線圖

**版本**: 2.0.0
**狀態**: 生效中 (Active)
**關聯架構**: [ARCHITECTURE.md](ARCHITECTURE.md)

## 總體目標

本路線圖旨在引導 SRE Assistant 從一個功能強大的後端服務（MVP），逐步演進為一個與 Grafana 深度整合的無縫體驗平台，並最終實現[架構文檔](ARCHITECTURE.md)中描述的、由多個專業化代理組成的聯邦化生態系統。

---

## Phase 0: 基礎與願景對齊 (Foundation & Vision Alignment)

- **時間**: 已完成
- **主題**: 確立統一的技術願景和架構藍圖。
- **主要成果**:
    - ✅ **統一架構**: 完成 `ARCHITECTURE.md` 的撰寫，融合了聯邦化（長期）和 Grafana 中心化（短期）的雙重願景。
    - ✅ **技術棧確認**: 明確了以 Google ADK、Python、LGTM Stack 和容器化為核心的技術棧。
    - ✅ **核心原則確立**: 就 Grafana 中心化、BaaS/FaaP、ADK 原生擴展、漸進式演進等核心原則達成共識。

---

## Phase 0: 優先技術債修正 (Priority Tech-Debt Remediation)

- **時間**: 1-2 週
- **主題**: 根據 ADK 首席架構師的審查 (`review.md`)，立即修正對系統穩定性和安全性影響最高的 P0 級技術債，確保專案建立在穩固的基礎之上。
- **主要成果**:
    - ✅ **AuthManager 重構**: 將有狀態的 `AuthManager` 重構為符合 ADK 規範的無狀態 `AuthenticationTool`，以提高可測試性和可靠性。
    - ✅ **標準化 HITL**: 使用 ADK 的 `LongRunningFunctionTool` 重新實現「人類介入」審批流程，確保與框架的無縫整合。
    - ✅ **結構化輸出**: 為核心的 `DiagnosticAgent` 實現 Pydantic `output_schema`，確保輸出格式的穩定性和可靠性。

---

## 風險評估 (Risk Assessment)

| 階段 (Phase) | 風險 (Risk) | 可能性 (Likelihood) | 影響 (Impact) | 緩解策略 (Mitigation) |
| :--- | :--- | :--- | :--- | :--- |
| Phase 1 | ADK 框架的學習曲線可能比預期陡峭 | 中 (Medium) | 中 (Medium) | 安排專門的學習時間，建立內部知識庫，尋求 Google 團隊的支援 |
| Phase 1 | 數據庫整合 (Postgres/Weaviate) 的複雜度被低估 | 高 (High) | 高 (High) | 優先進行 PoC 驗證，使用 ORM 簡化操作，確保數據庫專家參與早期設計 |
| Phase 2 | Grafana 插件的自定義 UI 開發比預期耗時 | 高 (High) | 中 (Medium) | 優先實現核心功能，複雜的 UI 組件延後，重用 Grafana 原生組件 |
| Phase 2 | Grafana 插件與後端之間的 WebSocket 通訊不穩定 | 中 (Medium) | 高 (High) | 實現心跳機制和自動重連，設計備用的 RESTful API 作為降級方案 |
| Phase 3 | A2A (gRPC) 通訊協議的設計與實現複雜 | 高 (High) | 高 (High) | 參考業界成熟的服務網格方案，從簡單的點對點通訊開始，逐步擴展 |

---

## Phase 1: MVP - 後端優先與核心能力建設 (Backend First & Core Capabilities)

- **預計時間**: 2-3 個月
- **主題**: 專注於後端 SRE Assistant Agent 的核心能力建設，並透過官方 ADK 工具進行快速驗證。
- **關鍵目標**: 打造一個功能強大、邏輯可靠的 SRE 後端服務。
- **使用者互動介面**: **官方 ADK Web UI**。

### 主要交付物 (Key Deliverables):
- **1.1. 基礎設施即代碼 (Infrastructure as Code)**:
    - ✅ 📦 提供 `docker-compose.yml` 文件，用於啟動可觀測性服務 (Grafana, Prometheus, Loki)。核心服務 (PostgreSQL, Redis) 則直接在本地運行，以提高穩定性。
- **1.2. SRE Assistant 後端服務 v0.1**:
    - ✅ 🤖 實現基於 Google ADK 的核心 Agent 服務 (已完成服務骨架)。
    - 🛠️ 整合基本的診斷工具（如：Prometheus 查詢、日誌關鍵字搜索）。
    - ✅ 🧠 **(已實現)** 實現了基於 `MemoryProvider` 的 RAG 檢索能力，後端使用 `ChromaDB`。
- **1.3. 核心服務實現**:
    - ✅ 🔐 **認證框架**: 實現了基於 `AuthProvider` 的可插拔認證框架，並整合至 API 層。預設使用 `none` 提供者，為後續實現 OAuth 2.0 奠定基礎。
    - ✅ 📝 **持久化會話**: 實現了基於 `session_service_builder` 的持久化會話管理，後端使用 PostgreSQL。
- **1.4. 功能驗證**:
    - 🎯 可透過 **ADK Web UI** 提交查詢，執行基本的事件診斷流程，並獲得包含 RAG 引用來源的答案。

### 成功指標 (Success Metrics):
- 診斷準確率 > 85%
- 工具執行成功率 > 95%

---

## Phase 2: Grafana 原生體驗 (The Grafana-Native Experience)

- **預計時間**: 3-4 個月
- **主題**: 將 SRE Assistant 的強大能力無縫嵌入到 SRE 的日常工作平台 Grafana 中，提供類似 Gemini Cloud Assist 的整合式、對話式體驗。
- **關鍵目標**: 開發自定義 Grafana 插件，提供一站式的 ChatOps 和自動化體驗。
- **使用者互動介面**: **SRE Assistant Grafana Plugin**。

### 主要交付物 (Key Deliverables):
- **2.1. SRE Assistant Grafana 插件 v1.0**:
    - 💬 開發一個 Grafana App Plugin，包含一個可嵌入儀表板的 ChatOps 面板。
    - 🔌 實現插件與 SRE Assistant 後端之間的 WebSocket / RESTful 通訊。
- **2.2. 深度整合能力**:
    - 📈 **圖表嵌入**: 支援在聊天中透過命令查詢並直接渲染 Grafana 圖表。
    - ✍️ **註解創建**: 支援透過聊天命令為 Grafana 圖表創建事件註解。
    - 🤫 **告警靜音**: 提供快速靜音指定告警的命令。
- **2.3. 使用者體驗遷移**:
    - ✨ 開始引導使用者從 ADK Web UI 過渡到使用 Grafana 插件進行日常操作。

### 成功指標 (Success Metrics):
- 用戶採用率 > 60%
- Grafana 插件穩定性 > 99%

---

## Phase 2.5: Agent 可觀測性與評估 (Agent Observability & Evaluation)
- **預計時間**: 1-2 個月
- **主題**: 為 SRE Assistant 自身建立深度可觀測性與系統化的評估框架，確保其決策過程透明、可追蹤且品質可控。
- **理論基礎**: 此階段的設計與實踐，應深度參考 **`docs/agents-companion-v2-zh-tw.md`** 中關於「代理人評估 (Agent Evaluation)」的章節。開發團隊應將其中闡述的最佳實踐，如**軌跡評估 (Trajectory Evaluation)**、**最終回應評估 (Final Response Evaluation)** 和**人在環路評估 (Human-in-the-Loop Evaluation)**，作為設計評估框架的核心指導原則。
- **關鍵目標**: 實現 `SPEC.md` 中定義的 LLM 可觀測性規格，並建立初步的自動化評估管線。
- **主要交付物**:
    - **2.5.1. 端到端追蹤**:
        - 📦 實現對 `SREWorkflow` 的 OpenTelemetry 自動化埋點。
        - 🔍 確保每次工具調用、LLM 請求都被捕獲為追蹤中的一個跨度 (Span)。
    - **2.5.2. 可觀測性儀表板**:
        - 📊 建立一個 Grafana 儀表板，用於視覺化 Agent 的執行流程、延遲和成本（Token 使用量）。
    - **2.5.3. 自動化評估框架 v1 (基於 ADK Eval)**:
        - 📝 **整合 ADK 評估框架**: 根據 `review.md` 的建議，採用官方的 `google.adk.eval.EvaluationFramework` 來建立評估管線。
        - 🧪 定義一組黃金測試案例 (`test_cases`)。
        - 📈 追蹤核心指標，如準確性 (`accuracy`)、延遲 (`latency`) 和成本 (`cost`)。
- **參考**:
    - [Datadog LLM Observability](https://docs.datadoghq.com/llm_observability/)
    - `docs/agents-companion-v2-zh-tw.md`

---

## Phase 3: 邁向聯邦化 - 主動與自動 (Towards Federation - Proactive & Automated)

- **預計時間**: 3-6 個月
- **主題**: 從被動響應工具進化為主動預防的智能助手，並開始向聯邦化架構演進。
- **關鍵目標**: 孵化第一個專業化代理，並實現主動型（Proactive）SRE 能力。

### 主要交付物 (Key Deliverables):
- **3.1. 主動式事件感知 (Proactive Incident Awareness)**:
    - 🌐 **整合 Personalized Service Health**: 實現 `GoogleCloudHealthTool`，使 Assistant 能夠主動查詢並告知使用者是否存在影響其專案的 Google Cloud 平台事件。
- **3.2. 第一個專業化代理**:
    - 📄 將後端服務中的**覆盤報告生成 (Postmortem Generation)** 功能重構為一個獨立的、可單獨部署的 `PostmortemAgent`。
- **3.3. A2A 通訊協議 v1**:
    - 📡 實現 `ARCHITECTURE.md` 中定義的 gRPC Agent-to-Agent (A2A) 通訊協議。
    - 🔗 SRE Assistant 主服務將作為協調器（Orchestrator），透過 A2A 協議調用新的 `PostmortemAgent` 來完成覆盤報告任務。
- **3.4. 主動預防能力**:
    - 🔮 在主服務中整合基於機器學習的**異常檢測**和**趨勢預測**能力，用於主動發現潛在問題。
- **3.5. 進階自動化**:
    - 📜 實現更複雜的、跨多個工具的多步驟**自動化修復工作流 (Runbooks)**。

### 成功指標 (Success Metrics):
- **主動預防**: 成功預測並預防的事件佔總事件的 10%。
- **A2A 通訊延遲**: p99 延遲 < 50ms。
- **覆盤報告自動化率**: 80% 的 P3/P4 事件可自動生成覆盤報告初稿。

---

## Phase 4: 聯邦化生態系統 (The Federated Ecosystem)

- **預計時間**: 12 個月以上
- **主題**: 全面實現 `ARCHITECTURE.md` 中描述的、由多個自治代理協同工作的聯邦化生態系統。
- **關鍵目標**: 建立一個開放、可擴展、自學習的 SRE 智能平台。

### 主要交付物 (Key Deliverables):
- **4.1. 聯邦協調器 (SRE Orchestrator)**:
    - 🚀 實現一個功能完備的、獨立的聯邦協調器服務，負責任務分解、代理路由和結果匯總。
- **4.2. 專業化代理矩陣**:
    - 💰 開發並部署更多的專業化代理，如 `CostOptimizationAgent`、`CapacityPlanningAgent`、`ChaosEngineeringAgent`。
- **4.3. 服務發現與註冊**:
    - 🗺️ 建立成熟的代理註冊中心和服務發現機制，允許代理動態加入和退出聯邦。
- **4.4. 平台開放性**:
    - 🤝 定義第三方代理的開發規範和接入標準，鼓勵社區貢獻和生態擴展。
    - 🧠 為代理引入自學習和自我優化能力。

### 成功指標 (Success Metrics):
- **生態擴展**: 至少有 2 個由第三方開發的專業化代理成功接入聯邦。
- **自學習能力**: 自動化建議的採納率 > 40%。
- **系統總擁有成本 (TCO)**: 相比前一年度，SRE 操作的總成本降低 15%。
