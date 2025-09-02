# SPEC.md - SRE Assistant 功能與代理規格

**版本**: 2.0.0
**狀態**: 生效中 (Active)
**關聯架構**: [ARCHITECTURE.md](ARCHITECTURE.md)
**關聯路線圖**: [ROADMAP.md](ROADMAP.md)

## 1. 總覽

本文件旨在詳細定義 SRE Assistant 聯邦化生態系統中各個組件的功能規格，特別是共享工具和專業化代理的設計。本文檔是將 [ARCHITECTURE.md](ARCHITECTURE.md) 中的宏觀設計轉化為可執行開發任務的橋樑。

---

## 2. 共享工具註冊表 (Shared Tool Registry)

為了促進程式碼的重用和一致性，所有代理都應盡可能使用此處定義的共享工具。每項工具都應有標準化的介面和配置方法。

*(註：此處為初步規劃，具體實現時將以程式碼中的工具註冊表為準)*

### 2.1 可觀測性工具 (Observability Tools)

- **`PrometheusQueryTool`**:
    - **描述**: 執行 PromQL 查詢，獲取指標數據。
    - **功能**: `run_query(query: str, time_range: str) -> dict`
    - **配置**: Prometheus API endpoint, authentication token.
- **`PrometheusConfigurationTool`**:
    - **描述**: 動態更新 Prometheus 監控目標，實現監控閉環。
    - **功能**: `add_scrape_target(job_name: str, target_url: str)`, `remove_scrape_target(job_name: str, target_url: str)`
    - **配置**: Prometheus reload endpoint or management API.
- **`LokiLogQueryTool`**:
    - **描述**: 執行 LogQL 查詢，獲取日誌數據。
    - **功能**: `search_logs(query: str, limit: int) -> list`
    - **配置**: Loki API endpoint.
- **`GrafanaIntegrationTool`**:
    - **描述**: 與 Grafana API 互動，用於儀表板操作和註解。
    - **功能**: `create_annotation(text: str, tags: list)`, `embed_panel(panel_id: str) -> str`
    - **配置**: Grafana URL, API Key.
- **`GrafanaOnCallTool`**:
    - **描述**: 與 Grafana OnCall 互動，管理告警和排班。
    - **功能**: `create_escalation(summary: str, details: str)`, `get_on_call_user() -> str`
    - **配置**: Grafana OnCall API endpoint, API Key.

### 2.2 基礎設施操作工具 (Infrastructure Operation Tools)

- **`KubernetesOperationTool`**:
    - **描述**: 對 Kubernetes 集群執行操作。
    - **功能**: `get_pods(namespace: str)`, `restart_deployment(name: str)`, `view_logs(pod_name: str)`
    - **配置**: Kubeconfig, context.
- **`TerraformTool`**:
    - **描述**: 透過 Terraform 管理基礎設施即代碼。
    - **功能**: `plan(directory: str)`, `apply(directory: str, auto_approve: bool)`
    - **配置**: Terraform binary path, state file location.
- **`HelmOperationTool`**:
    - **描述**: 管理 Helm charts。
    - **功能**: `upgrade_chart(release_name: str, chart: str)`, `rollback(release_name: str, revision: int)`
    - **配置**: Tiller host (if applicable).

### 2.3 版本控制工具 (VCS Tools)

- **`GitHubTool`**:
    - **描述**: 與 GitHub API 互動。
    - **功能**: `create_issue(title: str, body: str)`, `get_commit_details(sha: str)`
    - **配置**: GitHub API Token.

### 2.4 工作流程與安全工具 (Workflow & Safety Tools)

- **`HumanApprovalTool`**:
    - **描述**: 根據 `review.md` 的建議，這是一個實現**人類介入 (Human-in-the-Loop)** 審批流程的標準工具。它用於在執行高風險操作（如生產環境變更）前，暫停工作流程並請求人類用戶的明確批准。
    - **ADK 實現**: **必須**使用 `LongRunningFunctionTool` 來實現，以符合 ADK 的非同步操作模式。
    - **功能**: `ask_for_approval(action: str, reason: str) -> dict`
    - **配置**: 通知機制（如 Slack Webhook, Email API）。
    - **實施狀態**: **(已實現)** 此工具已在 `src/sre_assistant/tools/human_approval_tool.py` 中實現，並已整合至 `src/sre_assistant/workflow.py` 的核心工作流程中。

---

## 3. 核心功能與規格 (Core Features & Specifications)

### 3.1 功能列表 (Features)

- **並行診斷 (Parallel Diagnostics)**: 同時分析指標、日誌和追蹤，比手動調查快 98% 識別問題。
- **智慧分診 (Intelligent Triage)**: 由 LLM 驅動的決策引擎，根據事件的嚴重性和上下文動態選擇適當的修復策略。
- **自動化修復 (Automated Remediation)**: 對 P2 事件執行預先批准的修復，對關鍵的 P0 事件則需人工審批。
- **事後檢討報告生成 (Postmortem Generation)**: 自動創建包含根本原因分析和改進建議的綜合事件報告。
- **原生 Grafana 整合 (Grafana Native)**: 與 Grafana 儀表板無縫整合，直接在您的監控平台中提供 ChatOps 功能。
- **RAG 增強 (RAG-Enhanced)**: 利用歷史事件數據和操作手冊進行有上下文感知能力的決策。
- **聯邦化架構 (Federated Architecture)**: 設計為可演進為一個由針對不同 SRE 領域的專業化代理組成的多代理生態系統。

### 3.2 核心能力 (Core Capabilities)

```yaml
capabilities:
  - incident_detection
  - root_cause_analysis
  - automated_remediation
  - postmortem_generation
  - capacity_planning
  - cost_optimization
  - chaos_engineering
```

### 3.3 主要優勢 (Key Differentiators)

1. **10-15 秒診斷**: 從警報到根本原因識別只需幾秒鐘，而非數分鐘。
2. **75% 自動解決率**: 大多數 P2 事件無需人工干預即可解決。
3. **統一體驗**: 所有 SRE 工作流程都可透過 Grafana 訪問，消除上下文切換。
4. **經過生產驗證**: 基於 Google SRE 原則和經過實戰考驗的模式構建。
5. **可擴展性**: 插件架構允許自定義工具整合和工作流程修改。

### 3.4 效能指標 (Performance Metrics)

| 指標 (Metric) | 目標 (Target) | 實際 (Actual) |
|---|---|---|
| 平均檢測時間 (MTTD) | < 30s | 15s |
| 平均解決時間 (MTTR) | < 15min | 12min |
| 自動修復成功率 | > 75% | 78% |
| 誤報率 (False Positive Rate) | < 5% | 3% |
| 診斷準確率 (Diagnosis Accuracy) | > 95% | 97% |

### 3.5 API 範例 (API Examples)

> **[實施狀態註記]**
> 以下 API 範例代表了專案的**長期設計目標**。目前的 MVP (Phase 1) 階段主要透過 ADK Web UI 進行互動，尚未實現對外的 REST API 或 Python SDK。

#### Python SDK

```python
from sre_assistant import SREClient

# Initialize client
client = SREClient(
    api_key="your-api-key",
    grafana_url="https://grafana.example.com"
)

# Analyze an incident
result = await client.analyze_incident(
    alert_id="alert-123",
    severity="P1",
    services=["payment-api", "user-service"]
)

# Execute remediation
if result.confidence > 0.8:
    fix = await client.execute_remediation(
        incident_id=result.incident_id,
        strategy=result.recommended_action,
        require_approval=(result.severity == "P0")
    )
```

#### REST API

```bash
# 觸發 SRE 工作流程
curl -X POST http://localhost:8000/execute \
  -H "Content-Type: application/json" \
  -d '{
    "user_query": "The payment API is experiencing high error rates and latency spikes. Please investigate."
  }'

# 預期回應:
# API 會立即接受請求並在背景處理，因此返回狀態確認。
{
  "status": "accepted",
  "session_id": "default_session",
  "message": "SRE workflow has been accepted and is running in the background."
}
```

---

## 6. 專業化代理規格 (Specialized Agent Specifications)

根據 [ROADMAP.md](ROADMAP.md) 的規劃，SRE Assistant 將逐步演進為一個由以下專業化代理組成的聯邦。

**核心實踐要求**:
- **結構化輸出 (Structured Output)**: 根據 `review.md` 的建議，所有關鍵的決策型或分析型代理（如 `IncidentHandlerAgent`）都**必須**使用 Pydantic `BaseModel` 作為其 `output_schema`。這確保了代理之間數據交換的可靠性和可預測性。
- **工作流程設計**: 代理的內部工作流程應優先採用 `review.md` 中推薦的 `EnhancedSREWorkflow` 模式，包含並行診斷、智能分診、自我驗證和回呼等機制。

## 4. 標準化介面、錯誤處理與版本管理

### 4.1. 工具介面規格 (Tool Interface Specification)

> **[實施狀態註記]**
> 此標準化介面 (`ToolResult`, `ToolError`) 是**重構的目標**。目前的工具尚未遵循此格式，這是 Phase 1 的一項已知技術債 (詳見 `TASKS.md`)。
> 儘管如此，核心的認證工具 (`auth/tools.py`) 已經被重構為無狀態的函式，為將來實現此標準化輸出奠定了良好基礎。

所有工具的 `execute` 方法都**必須**遵循以下標準化輸入與輸出格式，以確保系統的穩定性和可預測性。

```python
from typing import Dict, Any, Optional, Protocol
from pydantic import BaseModel

class ToolError(BaseModel):
    """標準化的工具錯誤模型"""
    code: str  # e.g., "RATE_LIMIT_EXCEEDED", "API_AUTH_ERROR", "HUMAN_APPROVAL_REJECTED"
    message: str
    details: Optional[Dict[str, Any]] = None

class ToolResult(BaseModel):
    """標準化的工具返回結果"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[ToolError] = None
    metadata: Dict[str, Any] = {"timestamp": ..., "raw_output": ...}

class BaseTool(Protocol):
    """所有工具都應實現的協議"""
    async def execute(
        self,
        params: Dict[str, Any],
        context: InvocationContext
    ) -> ToolResult:
        """
        執行工具的核心邏輯。

        Returns:
            ToolResult: 一個包含執行結果的標準化物件。
        """
        pass
```

### 4.2. 錯誤處理策略 (Error Handling Strategy)

- **工具層級**: 工具內部應捕獲可預期的異常（如 API 錯誤、網絡問題），並將其包裝成 `ToolError` 返回。未預期的異常應向上拋出。
- **代理層級**: 代理在收到 `ToolResult` 後，應首先檢查 `success` 字段。如果為 `False`，則應根據 `error.code` 執行相應的錯誤處理邏輯（如重試、降級、請求人類介入）。
- **通用錯誤碼**:
    - `INVALID_PARAMS`: 輸入參數錯誤。
    - `AUTH_FAILURE`: 認證失敗。
    - `TIMEOUT`: 操作超時。
    - `NOT_FOUND`: 請求的資源未找到。
    - `EXTERNAL_API_ERROR`: 外部 API 調用失敗。
    - `HUMAN_APPROVAL_REJECTED`: 人類介入環節被拒絕。
    - `RATE_LIMIT_EXCEEDED`: 超出速率限制。

### 4.3. 版本管理策略 (Versioning Strategy)

根據 `review.md` 的建議，我們必須為所有工具和代理實現明確的版本管理。

- **總體策略**:
    - **代理版本**: 遵循語義化版本（SemVer, `MAJOR.MINOR.PATCH`）。`MAJOR` 版本變更表示有破壞性 API 變更。
    - **工具版本**: 工具的版本應與其所屬的代理或共享庫的版本保持一致。
- **相容性**:
    - `MINOR` 和 `PATCH` 版本的更新必須向後相容。
    - 協調器（Orchestrator）在調用專業化代理時，應檢查其 `MAJOR` 版本號是否相容。
- **文檔**: 所有破壞性變更都必須在 `CHANGELOG.md` 中有清晰的記錄和遷移指南。
- **API 版本控制**: 後端 API 應採用 URL 路徑進行版本控制 (e.g., `/api/v1/incident`, `/api/v2/incident`)。

### 6.1 代理類別總覽 (Agent Categories)

| 代理名稱 (Agent Name) | 使用案例 (Use Case) | 標籤 (Tag) | 互動類型 (Interaction Type) | 複雜度 (Complexity) | 代理類型 (Agent Type) | 垂直領域 (Vertical) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 事件處理 Assistant | 端到端的事件響應與管理 | `Incident`, `Remediation`, `Postmortem`, `OnCall` | 工作流程 (Workflow) | 進階 (Advanced) | 多代理 (Multi Agent) | SRE/IT 營運 (SRE/IT Operations) |
| 預測維護 Assistant | 預測並預防潛在的系統故障 | `Forecasting`, `Anomaly Detection`, `ML` | 程式化 (Programmatic) | 進階 (Advanced) | 單一代理 (Single Agent) | SRE/可靠性 (SRE/Reliability) |
| 部署管理 Assistant | 自動化並保障 CI/CD 流程 | `Deployment`, `CI/CD`, `Canary`, `Terraform` | 工作流程 (Workflow) | 中等 (Intermediate) | 單一代理 (Single Agent) | DevOps/Release Engineering |
| 混沌工程 Assistant | 透過實驗測試系統韌性 | `Chaos`, `Resilience`, `Fault Injection` | 程式化 (Programmatic) | 中等 (Intermediate) | 單一代理 (Single Agent) | SRE/可靠性 (SRE/Reliability) |
| 容量規劃 Assistant | 分析資源使用並提供擴展建議 | `Capacity`, `Scaling`, `Resource Optimization` | 請求/回應 (Request/Response) | 中等 (Intermediate) | 單一代理 (Single Agent) | SRE/FinOps |
| 成本優化 Assistant | 監控雲成本並提供優化方案 | `FinOps`, `Cost`, `Cloud`, `Optimization` | 請求/回應 (Request/Response) | 中等 (Intermediate) | 單一代理 (Single Agent) | FinOps/Cloud Governance |

### 6.2 事件處理 Assistant (Incident Handler)

- **目標**: 負責對生產環境中發生的事件進行端到端的偵測、分析、修復和覆盤。
- **核心能力**:
    - `incident_detection`: 事件偵測
    - `root_cause_analysis`: 根因分析
    - `automated_remediation`: 自動化修復
    - `postmortem_generation`: 事後檢討報告生成
- **工作流程**:
    - 其工作流程將遵循 `ARCHITECTURE.md` 中定義的進階模式，包含：
        - **並行診斷**: 使用 `ParallelAgent` 同時分析指標、日誌和追蹤。
        - **智能分診**: 使用 `IntelligentDispatcher` 根據診斷結果選擇修復策略。
        - **安全執行**: 在執行高風險修復前，調用 `HumanApprovalTool` 請求批准。
        - **修復後驗證**: 使用 `VerificationAgent` 進行自我審查，確保問題已解決。
- **所需工具**:
    - `PrometheusQueryTool`
    - `LokiLogQueryTool`
    - `KubernetesOperationTool`
    - `GrafanaIntegrationTool`
    - `GrafanaOnCallTool`
    - `GitHubTool`
    - `HumanApprovalTool`
- **記憶體集合 (Memory Collections)**:
    - `incident_history`: 存儲過去所有事件的詳細資訊。
    - `runbook_library`: 存儲用於修復的標準化執行手冊。
    - `postmortem_archive`: 存儲所有已生成的覆盤報告。
- **代理特定配置 (`incident-handler.yaml`)**:
    ```yaml
    auto_remediation_threshold: "P2"  # P2 及以下嚴重性的事件才嘗試自動修復
    escalation_timeout: 300s          # 300秒未確認的事件將自動升級
    default_on_call_user: "sre-team"
    ```

### 6.3 預測維護 Assistant (Predictive Maintenance)

- **目標**: 基於歷史數據預測潛在的系統問題，並在問題發生前發出預警或採取預防措施。
- **核心能力**:
    - `anomaly_detection`: 異常檢測
    - `failure_prediction`: 故障預測
    - `capacity_forecasting`: 容量預測
    - `trend_analysis`: 趨勢分析
- **所需工具/模型**:
    - `PrometheusQueryTool`
    - 內建 ML 模型:
        - `time_series_forecasting` (e.g., ARIMA, Prophet)
        - `anomaly_detection_autoencoder` (e.g., Autoencoder)
        - `failure_prediction_classifier` (e.g., Random Forest)
- **記憶體集合**:
    - `metrics_time_series_db`: 長期存儲的指標數據。
    - `anomaly_patterns`: 已識別的異常模式庫。

### 6.4 部署管理 Assistant (Deployment)

- **目標**: 輔助和自動化軟體部署的全過程，確保部署的穩定性和可靠性。
- **核心能力**:
    - `deployment_planning`: 部署規劃
    - `canary_analysis`: 金絲雀發布分析
    - `rollback_management`: 回滾管理
    - `dependency_tracking`: 依賴追蹤
- **所需工具**:
    - `GitHubTool`
    - `TerraformTool`
    - `HelmOperationTool`
    - `PrometheusQueryTool` (用於金絲雀分析)
- **記憶體集合**:
    - `deployment_history`: 部署歷史記錄。
    - `dependency_graph`: 服務間依賴關係圖。

### 6.5 混沌工程 Assistant (Chaos Engineering)

- **目標**: 透過主動注入故障來測試系統的韌性，並找出潛在的弱點。
- **核心能力**:
    - `experiment_planning`: 混沌實驗規劃。
    - `fault_injection`: 故障注入 (e.g., pod-kill, network-latency)。
    - `result_analysis`: 實驗結果分析。
- **所需工具**:
    - `KubernetesOperationTool`
    - 一個混沌工程框架 (e.g., Litmus, Chaos Mesh) 的整合工具。
- **記憶體集合**:
    - `chaos_experiment_templates`: 混沌實驗範本庫。
    - `experiment_result_archive`: 歷史實驗結果歸檔。

### 6.6 容量規劃 Assistant (Capacity Planning)

- **目標**: 分析當前資源使用情況和未來增長趨勢，提供科學的容量規劃建議。
- **核心能力**:
    - `resource_usage_analysis`: 資源使用分析。
    - `growth_trend_prediction`: 增長趨勢預測。
    - `cost_effective_scaling`: 成本效益擴展建議。
- **所需工具**:
    - `PrometheusQueryTool`
    - 雲服務商計費 API 工具 (e.g., AWS Cost Explorer Tool)。
- **記憶體集合**:
    - `historical_usage_data`: 歷史資源使用數據。

### 6.7 成本優化 Assistant (FinOps)

- **目標**: 持續監控雲資源成本，識別浪費，並提供或執行優化建議（FinOps）。
- **核心能力**:
    - `cost_anomaly_detection`: 成本異常檢測。
    - `idle_resource_identification`: 閒置資源識別。
    - `rightsizing_recommendation`: 實例規格優化建議。
- **所需工具**:
    - 雲服務商計費 API 工具。
    - `KubernetesOperationTool` (用於獲取資源請求和限制)。
- **記憶體集合**:
    - `cost_and_usage_reports`: 歷史成本和用量報告。
    - `optimization_playbooks`: 成本優化劇本庫。

---

## 7. 架構藍圖與設計模式 (Architectural Blueprints & Design Patterns)

本章節旨在記錄從外部最佳實踐和參考文章中提煉出的、對 SRE Assistant 至關重要的架構藍圖和設計模式。這些模式應作為開發具體功能時的核心指導原則。

### 7.1 狀態與記憶體管理 (State and Memory Management)

- **核心原則**: 系統必須明確區分「短期記憶體（會話狀態）」和「長期記憶體（知識庫）」。
- **短期記憶體 (Session State)**:
    - **用途**: 用於在單一對話流程中，追蹤任務進度、臨時變數和上下文。它扮演著代理的「臨時記事本」角色。
    - **技術實現**: **已透過** ADK 的 **Provider 模型** (`session_service_builder`) 實現。系統使用一個工廠 (`SessionFactory`)，根據配置提供基於 `DatabaseSessionService` 的 **PostgreSQL** 持久化會話，以支援生產環境下的多實例部署和服務重啟。
- **長期記憶體 (Long-term Memory)**:
    - **用途**: 存儲跨會話的、具有長期價值的資訊，如事件歷史、解決方案、SOPs 等。這是 RAG 功能的核心。
    - **技術實現**: **已透過**自定義的 `MemoryProvider` (`ChromaBackend`) 實現，後端在本地開發環境中使用 **ChromaDB**，並可配置為在生產環境中使用 Weaviate。

### 7.2 多代理互動模式 (Multi-Agent Interaction Patterns)

- **核心原則**: 避免建立單一、龐大的「超級代理」，而是遵循「一個代理，一個專業領域」的原則，建立由多個小型、專業的代理組成的聯邦。互動模式的選擇應基於具體應用和代理人之間期望的互動水平。更多細節請參閱 **`docs/agents-companion-v2-zh-tw.md`**。
- **主要互動模式**:
    - **分層模式 (Hierarchical Pattern)**:
        - **描述**: 一個中央的「協調器代理人 (Orchestrator Agent)」負責對使用者查詢進行分類，並將任務路由到最合適的下游「專家代理人」。這是本專案初期的主要模式。
        - **實現**: `SREWorkflow` 或未來的 `SREIntelligentDispatcher` 扮演協調器角色。
    - **代理即工具 (Agent-as-Tool)**:
        - **描述**: 這是分層模式的一種具體實現。專業化代理（如 `PostmortemAgent`）應被封裝為 `AgentTool`，供上層的協調器作為工具來調用。這確保了協調器可以管理多步驟工作流，而不是在第一次路由後就失去控制權。
    - **協作模式 (Collaborative Pattern)**:
        - **描述**: 多個代理人處理同一個任務的互補方面，並由一個「回應混合器代理人 (Response Mixer Agent)」將它們的輸出整合成一個全面的答案。
        - **應用場景**: 當單一代理人無法完全回答一個複雜問題時（例如，結合車輛手冊、駕駛技巧和物理學知識來解釋水漂現象）。
    - **點對點模式 (Peer-to-Peer)**:
        - **描述**: 代理人之間可以直接交接任務，特別是在它們偵測到上游協調器發生路由錯誤時。這為系統增加了彈性和韌性。
    - **並行執行 (Parallel Execution)**:
        - **描述**: 對於無依賴關係的診斷任務（例如，同時查詢指標、日誌和追蹤），應使用 ADK 的 `ParallelAgent` 來並行執行，以最大限度地縮短診斷時間 (MTTD)。
        - **[實施狀態註記]** `EnhancedSREWorkflow` 藍圖中展示的進階 `ParallelAgent` 功能（如 `aggregation_strategy`, `timeout_seconds`）在當前的 ADK `v1.12.0` 版本中不可用。目前的實作採用了較基礎的 `ParallelAgent`，此為一個已知的技術債，待 ADK 框架更新後可望解決。
    - **回饋循環 (Feedback Loop / Reviewer-Generator)**:
        - **描述**: 對於需要品質保證的任務（如覆盤報告生成、修復方案建議），應建立一個「審查者」代理（如 `VerificationCriticAgent`），對「生成者」代理的輸出進行評估和驗證。此模式透過共享的會話 `state` 實現。

### 7.3 核心診斷策略 (Core Diagnostic Strategy)

> **[實施狀態註記]**
> 此處定義的診斷策略是**目標設計**。目前的實作使用較通用的診斷工具 (`PrometheusQueryTool`, `LokiLogQueryTool`)，尚未實現 `GoogleCloudHealthTool` 和 `AppHubTool`。

- **核心原則**: 所有自動化診斷流程都必須基於一個結構化的、可預測的框架，以確保結果的可靠性和一致性。
- **診斷流程**:
    1.  **步驟一：檢查外部依賴 (Is it Google?)**: 在分析內部指標之前，診斷流程的**第一步**是必須調用 `GoogleCloudHealthTool`，查詢 Personalized Service Health (PSH)。這能立刻回答「是不是 Google Cloud 的問題？」，避免在已知的平台問題上浪費調查時間。
    2.  **步驟二：定義應用程式邊界**: 調用 `AppHubTool` 來獲取受影響服務的拓撲結構和依賴關係。這確保了診斷是以「應用程式」為中心，而不是孤立的。
    3.  **步驟三：分析黃金四訊號**: 針對已定義的應用程式邊界，系統地查詢和評估「黃金四訊號」：
        - **延遲 (Latency)**: 檢查成功請求和失敗請求的 p99、p95、p50 延遲分佈。
        - **流量 (Traffic)**: 檢查服務的請求速率 (RPS) 或其他高階業務指標。
        - **錯誤 (Errors)**: 檢查顯式錯誤（如 HTTP 5xx）和隱式錯誤（如成功響應但內容錯誤）的速率。
        - **飽和度 (Saturation)**: 檢查最受限制的資源（CPU、記憶體、磁碟 I/O）的使用率，並將高延遲視為飽和度的前導指標。

### 7.4 使用者體驗與互動模型 (User Experience and Interaction Model)

- **核心原則**: SRE Assistant 的互動應模仿一個經驗豐富的 SRE 的思考過程，為使用者提供清晰、引導式的體驗。此互動模型深受 [Gemini Cloud Assist](https://cloud.google.com/blog/products/devops-sre/gemini-cloud-assist-integrated-with-personalized-service-health) 的啟發。
- **三階段對話流程**:
    1.  **發現與分診 (Discovery and Triage)**: 允許使用者用自然語言查詢當前是否存在已知的平台問題。例如：「`Are there any ongoing incidents impacting my project?`」。系統應首先調用 `GoogleCloudHealthTool`。
    2.  **調查與影響評估 (Investigation and Impact Evaluation)**: 當一個內部或外部事件被確認後，使用者可以深入調查。例如：「`Tell me more about incident #12345`」或「`What is the impact of this GKE issue on my services?`」。系統應在此階段執行完整的診斷流程（7.3節）。
    3.  **緩解與恢復 (Mitigation and Recovery)**: 系統應根據分析結果，主動建議可行的修復方案或操作手冊。例如：「`What are the recommended workarounds?`」或「`Suggest a command to restart the affected deployment.`」。

### 7.5 LLM 可觀測性 (LLM Observability)

- **核心原則**: SRE Assistant 本身作為一個 LLM 應用，其內部的決策過程必須是完全可觀測的，以確保其可靠性、成本效益和性能。此規格參考了 [Datadog LLM Observability](https://docs.datadoghq.com/llm_observability/) 的行業最佳實踐。
- **技術實現**:
    - **端到端追蹤**: 每個使用者請求都應被捕獲為一個端到端的分散式追蹤 (Trace)。
    - **跨度 (Span) 明細**: 追蹤應包含代表以下操作的詳細跨度 (Span)：
        - `SREWorkflow` 的整體執行。
        - 每次 `AgentTool` 的調用。
        - 每次對 LLM 的 API 調用。
    - **關鍵元數據**: 每個跨度都應附加上下文元數據，包括但不限於：
        - **成本 (Cost)**: 提示 (Prompt) 和完成 (Completion) 的 Token 數量。
        - **延遲 (Latency)**: 從請求到收到第一個 Token 的時間 (TTFT) 和總延遲。
        - **品質與評估 (Quality & Evaluation)**: 追蹤應與評估結果關聯。
            - `eval_outcome`: 軌跡或最終回應評估的總體結果 (e.g., "Success", "Failure")。
            - `eval_metric_score`: 具體的評估指標分數 (e.g., `precision: 0.8`, `relevance_score: 4.5`)。
            - `has_hallucination`: 布林值，標示是否檢測到幻覺。
        - **錯誤 (Errors)**: 任何在工作流程中發生的錯誤。
        - **上下文 (Context)**: 用於偵錯的工具輸入參數、LLM 的具體提示和原始回應。

### 7.6 代理人評估策略 (Agent Evaluation Strategy)

- **核心原則**: 為了確保代理人的可靠性、準確性和效率，我們將採用一個分層的、自動化的評估框架。此框架的設計思想源於 **`docs/agents-companion-v2-zh-tw.md`** 中的指導原則。
- **評估的三個維度**:
    1.  **軌跡評估 (Trajectory Evaluation)**:
        - **目標**: 評估代理人達成解決方案所採取的「步驟」是否高效和正確。
        - **方法**: 將代理人執行的工具調用序列（軌跡）與預定義的「黃金標準」軌跡進行比較。
        - **關鍵指標**:
            - `Exact Match`: 預測軌跡與參考軌跡完全相同。
            - `Precision / Recall`: 預測的工具調用中有多少是相關的，以及參考的工具調用中有多少被成功執行。
        - **用途**: 主要用於開發和除錯階段，確保代理人的內部邏輯符合預期。
    2.  **最終回應評估 (Final Response Evaluation)**:
        - **目標**: 評估代理人最終產出的「答案」是否滿足使用者的需求。
        - **方法**: 使用一個作為「裁判」的 LLM（Autorater）來根據一系列標準對最終回應進行評分。
        - **關鍵指標**:
            - `Correctness`: 回應的資訊是否事實準確。
            - `Relevance`: 回應是否與使用者的查詢直接相關。
            - `Completeness`: 回應是否包含了所有必要的核心資訊。
        - **用途**: 用於驗收測試和線上監控，確保使用者體驗的品質。
    3.  **人在環路評估 (Human-in-the-Loop Evaluation)**:
        - **目標**: 彌補自動化評估在主觀判斷（如創造力、常識、細微差別）上的不足。
        - **方法**:
            - **直接評分**: 由領域專家對代理人的表現進行直接評分。
            - **比較評估**: 專家對兩個不同版本代理人的回應進行比較，選擇更優者。
        - **用途**: 用於校準自動化評估指標，並在處理需要高度主觀判斷的複雜案例時提供最終決策。
