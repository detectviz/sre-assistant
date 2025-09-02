# 架構文件: SRE Assistant 整合架構

**文件版本：** 3.0.0
**狀態**: 生效中 (Active)
**核心理念**: 以 `control-plane` 為指揮中心，`sre-assistant` 為專家代理的後端驅動架構。

## 1. 總體架構 (Overall Architecture)

本架構定義了 `control-plane` 與 `sre-assistant` 之間的整合模式。在此模式下，`control-plane` 作為使用者介面和核心指揮官，負責接收使用者指令，並將其轉化為對 `sre-assistant` 的 API 呼叫。`sre-assistant` 則作為一個無介面的 (headless) 專家代理，專注於執行複雜的診斷、分析與修復任務。

此架構取代了原有的以 Grafana 為中心的模型，旨在提供一個更統一、可擴展性更強的自動化運維平台。

```mermaid
graph TD
    subgraph "使用者層"
        User([使用者])
    end

    subgraph "指揮中心 (Control Plane)"
        ControlPlaneUI[Control Plane UI<br/>(HTMX, Go Backend)]
    end

    subgraph "專家代理 (SRE Assistant)"
        SREAssistantAPI[SRE Assistant API<br/>(Python, Google ADK)]
    end

    subgraph "外部系統"
        Observability[可觀測性平台<br/>(Prometheus, Loki)]
        AuditLogs[Control Plane Audit API]
    end

    %% Connections
    User --> ControlPlaneUI
    ControlPlaneUI -- API 請求 (攜帶使用者 JWT) --> SREAssistantAPI

    SREAssistantAPI -- 執行工具 --> Observability
    SREAssistantAPI -- 查詢變更歷史 --> AuditLogs
```

## 2. 組件職責 (Component Roles)

### 2.1 Control Plane
- **角色**: **指揮官 (Commander) / 協調器 (Orchestrator)**
- **職責**:
    - 提供統一的使用者操作介面。
    - 管理應用程式生命週期（部署、設定等）。
    - 將使用者的操作（如「診斷部署失敗」）轉換為對 `sre-assistant` 的標準化 API 請求。
    - 透過自身的 `/api/v1/audit-logs` 端點，為 `sre-assistant` 提供必要的上下文資訊（如變更歷史）。
    - 處理使用者身份驗證，並將使用者的身份資訊（透過 JWT）安全地傳遞給 `sre-assistant`。

### 2.2 SRE Assistant
- **角色**: **專家代理 (Specialist Agent)**
- **職責**:
    - 作為一個無介面的後端服務運行。
    - 接收來自 `control-plane` 的 API 請求。
    - 執行核心的診斷與分析邏輯，利用其工具集（如查詢指標、日誌）與外部系統互動。
    - 在需要時，回頭呼叫 `control-plane` 的 API 以獲取更多上下文。
    - 驗證傳入的 JWT，以確保請求來自合法的 `control-plane` 服務，並可根據需要執行基於使用者身份的細粒度權限控制。

## 3. API 契約 (API Contract)

`control-plane` 與 `sre-assistant` 之間的互動，嚴格遵循 `control-plane` 專案中定義的 `openapi.yaml` 文件。該文件是兩個服務之間 API 的「唯一真實來源」。

- **主要端點**:
    - `POST /diagnostics/deployment`: 用於觸發部署健康度診斷。
    - `POST /diagnostics/alerts`: 用於觸發告警事件分析。
    - `POST /execute`: 用於執行通用的、臨機的查詢。

## 4. 認證與授權 (Authentication & Authorization)

為了確保服務間通訊的安全性，本架構採用基於 **Keycloak** 的 OAuth 2.0 流程。

- **核心流程**: **Client Credentials Flow** (用於服務對服務 M2M 通訊)。
- **流程說明**:
    1. `control-plane` 使用其在 Keycloak 註冊的 `Client ID` 和 `Client Secret`，向 Keycloak 請求一個 Access Token。
    2. 在呼叫 `sre-assistant` 的 API 時，`control-plane` 會在 HTTP 的 `Authorization` 標頭中，以 `Bearer` 形式附上此 Token。
    3. `sre-assistant` 的 API 入口處會有一個中介軟體，負責攔截並驗證此 JWT 的有效性（簽名、過期時間等）。
- **詳細設定**: 關於如何在 Keycloak 中註冊客戶端、以及如何在 `sre-assistant` 中配置驗證中介軟體的具體步驟，請參閱 **`keycloak.md`** 文件。

## 5. 數據流範例：部署失敗診斷

1. **觸發**: 使用者在 `control-plane` 的 UI 上點擊一個部署失敗的服務，並選擇「開始診斷」。
2. **指揮**: `control-plane` 的後端服務，向 `sre-assistant` 的 `POST /diagnostics/deployment` 端點發起 API 請求。請求的 Body 中包含必要的上下文，如 `{ "deployment_id": "deploy-xyz-12345", "service_name": "payment-api" }`。此請求的 Header 中攜帶著從 Keycloak 獲取的 M2M Access Token。
3. **執行**: `sre-assistant` 驗證 Token，接收請求，並啟動其內部的診斷工作流 (Workflow)。
4. **分析**: `sre-assistant` 的代理開始執行其工具：
    - 呼叫 Prometheus API 查詢該服務的指標。
    - 呼叫 Loki API 查詢相關的日誌。
    - **回頭呼叫** `control-plane` 的 `GET /api/v1/audit-logs` API，查詢在問題發生時間點前後的部署或設定變更。
5. **回覆**: `sre-assistant` 綜合所有資訊，生成一份診斷報告，並將結果回傳給 `control-plane`。
6. **呈現**: `control-plane` 在 UI 上向使用者展示這份診斷報告。
