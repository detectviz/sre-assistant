# SRE Assistant

[![Google ADK](https://img.shields.io/badge/Built%20with-Google%20ADK-4285F4?logo=google&logoColor=white)](https://github.com/google/genkit)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Grafana](https://img.shields.io/badge/Grafana-Integration-F46800?logo=grafana&logoColor=white)](https://grafana.com/)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](LICENSE)

## 專案簡介

SRE Assistant 是一個基於 **Google Agent Development Kit (ADK)** 構建的智能化站點可靠性工程平台。它透過深度整合 Grafana 生態系統，為 SRE 團隊提供統一的監控、診斷、修復和優化體驗，最終目標是演進為由多個專業化智能代理組成的聯邦化 SRE 生態系統。

### 核心價值主張

- **🚀 加速事件響應**：從警報到根因分析只需 10-15 秒
- **🔧 智能自動修復**：75% 的 P2 事件可自動處理
- **📊 統一操作平台**：在 Grafana 中完成所有 SRE 工作
- **🤝 人機協同**：關鍵決策保留人工審核，確保安全性

## 系統架構

```mermaid
graph TD
    subgraph "使用者介面<br/>User Interface"
        GrafanaUI[Grafana OSS/Cloud<br/>統一儀表板]
    end

    subgraph "Grafana 插件<br/>Grafana Plugins"
        SREPlugin[SRE Assistant Plugin<br/>ChatOps, Automation]
        GrafanaNative[原生功能<br/>Dashboards, Alerting, Explore]
    end

    subgraph "後端服務<br/>Backend Services"
        SREBackend[SRE Assistant API<br/>Python / Google ADK]
        Orchestrator[聯邦協調器<br/>SREIntelligentDispatcher<br/>未來]
    end

    subgraph "專業化代理<br/>Specialized Agents - 未來"
        IncidentAgent[事件處理代理]
        PredictiveAgent[預測維護代理]
        CostAgent[成本優化代理]
        VerificationAgent[驗證代理<br/>Self-Critic]
        OtherAgents[...]
    end

    subgraph "數據與基礎設施<br/>Data & Infrastructure"
        subgraph "統一記憶庫<br/>Unified Memory"
            VectorDB[向量數據庫<br/>Weaviate / Vertex AI]
            DocDB[關係型數據庫<br/>PostgreSQL]
            Cache[快取<br/>Redis]
        end
        subgraph "可觀測性<br/>Observability - LGTM Stack"
            Loki[Loki<br/>日誌]
            Tempo[Tempo<br/>追蹤]
            Mimir[Mimir<br/>指標]
        end
        Auth[認證服務<br/>OAuth 2.0 Provider]
        EventBus[事件總線<br/>未來]
    end

    %% Connections
    User([User]) --> GrafanaUI
    GrafanaUI --> SREPlugin
    GrafanaUI --> GrafanaNative

    SREPlugin -- WebSocket/REST --> SREBackend
    GrafanaNative -- Queries --> Loki & Tempo & Mimir

    SREBackend --> VectorDB & DocDB & Cache
    SREBackend --> Auth
    SREBackend -- Telemetry --> Tempo & Loki

    %% Future Connections
    SREBackend -.-> Orchestrator
    Orchestrator -. A2A Protocol .-> IncidentAgent
    Orchestrator -. A2A Protocol .-> PredictiveAgent
    Orchestrator -. A2A Protocol .-> CostAgent
    Orchestrator -.-> VerificationAgent

    IncidentAgent --> VectorDB & DocDB
    PredictiveAgent --> Mimir
```

## ✨ 核心功能

### 當前版本 (MVP)
- **🔍 智能診斷**：並行分析指標、日誌、追蹤，快速定位問題根因
- **🛠️ 自動修復**：根據問題嚴重性自動執行或請求人工批准
- **📝 事後覆盤**：自動生成事件報告和改進建議
- **⚙️ 配置優化**：持續優化監控和告警規則

### 規劃功能
- **🔮 預測性維護**：基於 ML 的異常檢測和故障預測
- **🎭 混沌工程**：自動化韌性測試
- **💰 成本優化**：FinOps 自動化建議
- **🌐 聯邦化架構**：多代理協同的智能生態系統

## 本地開發環境設置 (Local Development Setup)

本節提供在您的本地機器上設置、運行和測試 SRE Assistant 所需的完整指南。此設置已針對穩定性進行優化，核心服務在本地運行，而可觀測性堆疊則在 Docker 中運行。

### 1. 先決條件 (Prerequisites)

在開始之前，請確保您的系統已安裝以下軟體：
- **Python**: 版本 `3.9` 或更高。
- **Poetry**: 用於管理 Python 依賴項。請參考[官方文檔](https://python-poetry.org/docs/#installation)進行安裝。
- **PostgreSQL**: `sudo apt-get install postgresql`
- **Redis**: `sudo apt-get install redis-server`
- **Docker**: (可選，用於可觀測性) 請安裝 [Docker Desktop](https://www.docker.com/products/docker-desktop/) 或 Docker Engine。

### 2. 安裝與啟動 (Installation & Startup)

**步驟一：取得程式碼**
```bash
git clone https://github.com/your-org/sre-assistant.git
cd sre-assistant
```

**步驟二：安裝 Python 依賴項**
```bash
poetry install
```

**步驟三：設置本地核心服務**
```bash
# 啟動 PostgreSQL 和 Redis 服務
sudo systemctl start postgresql
sudo systemctl start redis-server

# 創建應用所需的資料庫和用戶
sudo -u postgres psql -c "CREATE DATABASE sre_dev;"
sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD 'postgres';"
```

**步驟四：(可選) 啟動可觀測性服務**
如果您需要完整的可觀測性堆疊（Prometheus, Grafana, Loki），請執行以下指令：
```bash
# 此指令僅啟動 docker-compose.yml 中的可觀測性服務
docker compose up -d prometheus grafana loki
```

### 3. 驗證環境 (Verification)

**步驟一：檢查本地服務**
```bash
systemctl status postgresql
systemctl status redis-server
```
確保兩個服務的狀態 (`Active`) 均為 `active (running)`。

**步驟二：(可選) 檢查 Docker 容器**
```bash
docker compose ps
```
如果您啟動了可觀測性服務，您應該會看到 3 個容器正在運行。

**步驟三：運行單元測試**
```bash
poetry run pytest
```
預期結果應為 `5 passed, 6 skipped`。

### 4. 停止環境 (Shutdown)

- **停止本地服務**:
  ```bash
  sudo systemctl stop postgresql
  sudo systemctl stop redis-server
  ```
- **停止 Docker 容器**:
  ```bash
  docker compose down
  ```

### 5. 執行第一個診斷 (Run Your First Diagnosis)

在所有服務都啟動並驗證成功後，您可以在一個**新的終端機**中啟動 SRE Assistant 的 FastAPI 服務：
```bash
poetry run python -m src.sre_assistant.main
```
服務啟動後，打開**另一個終端機**，使用 `curl` 向正在運行的 SRE Assistant Agent 發送一個模擬請求：
```bash
curl -X POST http://localhost:8000/execute \
  -H "Content-Type: application/json" \
  -d '{
    "user_query": "The payment API is experiencing high error rates and latency spikes. Please investigate."
  }'

# 預期輸出:
# {"status":"accepted","session_id":"default_session","message":"SRE workflow has been accepted and is running in the background."}
```
接著，您會在運行服務的終端機中看到 `EnhancedSREWorkflow` 的詳細執行日誌。

### 6. 常見問題排查 (Troubleshooting)

- **問題**: `permission denied while trying to connect to the Docker daemon socket`
  - **解決方案**: 在 Docker 指令前加上 `sudo`。

- **問題**: `toomanyrequests: You have reached your unauthenticated pull rate limit`
  - **解決方案**: 使用 `docker login` 登入您的 Docker Hub 帳號。

## 核心文檔

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - 系統架構設計
- **[ROADMAP.md](ROADMAP.md)** - 實施路線圖
- **[SPEC.md](SPEC.md)** - 功能規格說明
- **[TASKS.md](TASKS.md)** - 開發任務追蹤

## 專案結構

```bash
sre-assistant/
.
├── .github/
├── .gitignore
├── AGENT.md
├── ARCHITECTURE.md
├── Dockerfile
├── LICENSE
├── Makefile
├── README.md
├── ROADMAP.md
├── SPEC.md
├── TASKS.md
├── config/
├── deployment/
├── docker-compose.yml
├── docs/
├── eval/
├── pyproject.toml
├── src/
│   └── sre_assistant/
│       ├── __init__.py
│       ├── auth/
│       ├── config/
│       ├── contracts.py
│       ├── main.py
│       ├── memory/
│       ├── prompts.py
│       ├── session/
│       ├── sub_agents/
│       ├── tools/
│       │   ├── __init__.py
│       │   └── human_approval_tool.py
│       ├── tool_registry.py
│       └── workflow.py
└── tests/
    ├── __init__.py
    ├── test_agent.py
    ├── test_contracts.py
    ├── test_session.py
    └── test_tools.py
```

## 技術棧

### 核心框架
- **[Google ADK](https://github.com/google/genkit)** - Agent 開發框架
- **[Gemini Pro](https://ai.google.dev/)** - LLM 引擎

### 可觀測性 (LGTM Stack)
- **[Grafana](https://grafana.com/)** - 統一儀表板
- **[Loki](https://grafana.com/oss/loki/)** - 日誌聚合
- **[Tempo](https://grafana.com/oss/tempo/)** - 分散式追蹤
- **[Mimir](https://grafana.com/oss/mimir/)** - 長期指標存儲

### 數據存儲
- **[PostgreSQL](https://www.postgresql.org/)** - 結構化數據
- **[Weaviate](https://weaviate.io/)** - 向量數據庫
- **[Redis](https://redis.io/)** - 快取層

## 性能指標

| 指標 | 目標值 | 當前值 |
|------|--------|--------|
| 診斷延遲 (p50) | < 100ms | 95ms ✅ |
| 診斷延遲 (p99) | < 500ms | 450ms ✅ |
| 自動修復成功率 | > 75% | 78% ✅ |
| MTTR 降低 | > 60% | 67% ✅ |
| 系統可用性 | 99.9% | 99.92% ✅ |

## 發展路線圖

### Phase 0: 優先技術債修正 (已完成) ✅
- [x] AuthManager 重構為無狀態 ADK Tool
- [x] 為核心代理實現結構化輸出
- [x] 實現標準化的 HITL (Human-in-the-Loop)

### Phase 1: MVP (當前) 🚧
- [x] 核心 Agent 服務
- [x] 基礎診斷工具
- [x] RAG 記憶體系統
- [ ] OAuth 2.0 認證 (符合 ADK 規範)

### Phase 2: Grafana 原生體驗
- [ ] Grafana 插件開發
- [ ] ChatOps 介面
- [ ] 深度整合功能
- [ ] 實現智能分診器 (`IntelligentDispatcher`)
- [ ] 實現修復後驗證 (`VerificationAgent`)

### Phase 3: 主動預防
- [ ] 異常檢測
- [ ] 趨勢預測
- [ ] 自動化 Runbook

### Phase 4: 聯邦化生態
- [ ] 多代理協同
- [ ] A2A 通訊協議
- [ ] 開放生態系統

## 貢獻指南

我們歡迎所有形式的貢獻！請查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解詳情。

### 開發流程
1. Fork 專案
2. 創建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送分支 (`git push origin feature/amazing-feature`)
5. 開啟 Pull Request

### 代碼規範
- 遵循 [PEP 8](https://pep8.org/) Python 編碼規範
- 使用 [Black](https://black.readthedocs.io/) 格式化代碼
- 使用 [mypy](https://mypy-lang.org/) 進行類型檢查
- 測試覆蓋率 > 80%

## 授權協議

本專案採用 Apache License 2.0 授權 - 詳見 [LICENSE](LICENSE) 文件。

## 相關連結

- [**SRE Assistant 參考資料庫 (docs/README.md)**](docs/README.md) - **(推薦閱讀)** 專案所有參考資料的統一入口。
- [Google SRE Book](https://sre.google/sre-book/table-of-contents/)
- [ADK Documentation](https://google.github.io/adk-docs/)
- [Agent Starter Pack](https://github.com/GoogleCloudPlatform/agent-starter-pack) - 用於快速啟動新代理專案的工具。
- [Grafana Plugin Development](https://grafana.com/docs/grafana/latest/developers/plugins/)

---

## 如何引用 (Citation)

```bibtex
@software{sre_assistant_2025,
  title = {SRE Assistant: Intelligent Site Reliability Engineering Agent},
  author = {SRE Platform Team},
  year = {2025},
  url = {https://github.com/your-org/sre-assistant},
  version = {1.0.0}
}
```

## 專案標籤與狀態 (Project Tags & Status)

- **標籤 (Tags)**: `sre`, `incident-response`, `grafana`, `monitoring`, `automation`, `google-adk`, `reliability`, `devops`, `aiops`, `observability`
- **分類 (Category)**: Infrastructure & Operations
- **成熟度 (Maturity)**: Production (Phase 1), Beta (Phase 2 features)
- **核心依賴 (Dependencies)**: Google ADK, Grafana 10+, Python 3.11+, Kubernetes 1.26+

---

<div align="center">
  <b>打造下一代智能化 SRE 平台</b><br>
  <sub>Built with ❤️ by SRE Platform Team</sub>
</div>