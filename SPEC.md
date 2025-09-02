# SPEC.md - SRE Assistant 功能規格 (v3)

**版本**: 3.0.0
**狀態**: 生效中 (Active)
**關聯架構**: [ARCHITECTURE.md](ARCHITECTURE.md)
**API 契約**: [openapi.yaml](openapi.yaml)

## 1. 總覽

本文件定義了 SRE Assistant 作為一個**無介面 (headless) 專家代理**的功能規格。所有功能都透過標準化的 REST API 端點暴露，供上層指揮官（如 `control-plane`）呼叫。本規格的核心是 API 契約，而非使用者介面。

---

## 2. API 驅動的核心能力

SRE Assistant 的核心能力圍繞其公開的 API 端點進行組織。

### 2.1 `POST /diagnostics/deployment`

- **功能**: 診斷指定部署的健康狀況。
- **目的**: 當一個部署未能成功或出現異常時，此端點將觸發一個端到端的工作流程，以找出潛在的根本原因。
- **輸入 (Input)**: 一個包含部署上下文的 JSON 物件，例如：
  ```json
  {
    "deployment_id": "deploy-xyz-12345",
    "service_name": "payment-api",
    "namespace": "production"
  }
  ```
- **核心工作流程**:
  1.  接收請求並驗證來自 `control-plane` 的 M2M Token。
  2.  啟動 `DeploymentDiagnosticsWorkflow`。
  3.  **並行執行**以下工具進行分析：
      - `PrometheusQueryTool`: 查詢該服務在部署時間點前後的「四大黃金訊號」（延遲、流量、錯誤、飽和度）。
      - `LokiLogQueryTool`: 查詢該服務的錯誤日誌或 Crash 日誌。
      - `ControlPlaneTool`: 回頭呼叫 `control-plane` 的 `/api/v1/audit-logs` 端點，檢查最近是否有相關的設定變更。
  4.  將收集到的所有資訊交給一個 LLM Agent 進行綜合分析，生成一份診斷摘要。
- **輸出 (Output)**: 一個結構化的 JSON 物件，包含診斷結果、信心分數和建議的下一步操作。
  ```json
  {
    "status": "COMPLETED",
    "summary": "診斷完成。初步發現 'payment-api' 的 CPU 使用率在部署後達到 100%，可能導致健康檢查失敗。",
    "findings": [
      { "source": "Prometheus", "data": { "cpu_usage": "100%" } },
      { "source": "Loki", "data": { "log_pattern": "OOMKilled" } }
    ],
    "recommended_action": "建議檢查部署的資源請求 (Resource Request) 與限制 (Limit)。"
  }
  ```

### 2.2 `POST /diagnostics/alerts`

- **功能**: 分析一或多個觸發的告警事件。
- **目的**: 當監控系統發出告警時，此端點用於自動化初步的調查，將多個告警關聯起來，並找出共同模式。
- **輸入 (Input)**: 一個包含告警事件 ID 的 JSON 物件。
  ```json
  {
    "incident_ids": [101, 102, 105],
    "service_name": "database-cluster"
  }
  ```
- **輸出 (Output)**: 一份綜合的事件報告初稿，同樣以結構化 JSON 格式返回。

### 2.3 `POST /execute`

- **功能**: 通用目的的臨機 (ad-hoc) 查詢與任務執行。
- **目的**: 提供最大的靈活性，允許 `control-plane` 將更開放式的自然語言查詢直接傳遞給 SRE Assistant。
- **核心工作流程**: 此端點背後的代理將更依賴 LLM 的能力來理解查詢意圖、動態規劃步驟並選擇合適的工具。
- **使用場景**: 用於 `control-plane` UI 中可能存在的「通用聊天」或「問答」功能。

---

## 3. 工具介面與版本管理

### 3.1 標準化工具介面

為了確保系統的穩定性和可預測性，所有由 SRE Assistant 使用的工具 (`Tool`)，其 `execute` 方法都**必須**遵循以下標準化輸出格式。

```python
from pydantic import BaseModel
from typing import Optional, Dict, Any

class ToolError(BaseModel):
    """標準化的工具錯誤模型"""
    code: str  # e.g., "API_AUTH_ERROR", "NOT_FOUND"
    message: str

class ToolResult(BaseModel):
    """標準化的工具返回結果"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[ToolError] = None
```
此設計確保了工作流程中的代理能夠以統一的方式處理工具的成功與失敗，並根據 `error.code` 執行相應的錯誤處理邏輯。

### 3.2 版本管理策略

- **API 版本**: 後端 API 應採用 URL 路徑進行版本控制 (e.g., `/api/v1/...`)，儘管當前 MVP 階段為 v1，但此為未來擴展的基礎。
- **代理版本**: 整個 SRE Assistant 應用程式遵循語義化版本（SemVer, `MAJOR.MINOR.PATCH`）。`MAJOR` 版本變更表示有破壞性的 API 變更。
- **文件同步**: 任何對 API 的修改都必須同步更新 `openapi.yaml` 和本 `SPEC.md` 文件。
