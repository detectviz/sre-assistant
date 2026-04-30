# SRE Assistant

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](LICENSE)

## 1. 專案簡介 (Project Overview)

SRE Assistant 是一個基於 **Hermes Agent** 構建的、無介面的 (headless) 智能化站點可靠性工程 (SRE) 代理。

## 執行摘要

過去系統缺乏透明度，難以快速定位服務異常。本次投資旨在建立**集中式數據中心**，以一次性基礎設施投入，換取全球服務的統一、高效維運能力，並為導入 AI 自動化排障奠定基礎。

---

## 投資效益

| 面向 | 改善成果 |
|:---|:---|
| **成本優化** | 快速定位服務異常，顯著降低全球擴張的硬體與人力成本。 |
| **風險控管** | 提供秒級全鏈路日誌調閱，加速釐清問題；完整保存業務操作軌跡，以滿足合規與稽核需求。 |
| **組織升級** | 導入 AI 進行第一線告警處理，減輕夜間值班負擔；建立統一戰情室，打破跨部門資訊孤島；系統化沉澱維運知識庫。 |

**AI 事件治理閉環流程**：

```
Grafana 偵測告警
     ↓
Telegram 通知 + Hermes Agent 自動喚醒
     ↓
AI 自動提取歷史趨勢圖、關聯底層錯誤日誌，並檢索知識庫 SOP
     ↓
AI 彙整初步根因分析 (RCA)，並推播至 Telegram
     ↓
【Human-in-the-Loop】SRE 確認後點擊「批准修復」
     ↓
系統自動執行修復腳本，並將結果回報至 Telegram
     ↓
AI 自動生成事後 RCA 報告，存入知識庫
```


在新架構下，本專案扮演 **專家代理 (Specialist Agent)** 的角色，負責接收來自上層 **指揮官 (Commander)** (例如 [control-plane](https://github.com/detectviz/control-plane)) 的 API 命令，並執行複雜的診斷、分析與自動化修復任務。

**重要提示**: 本專案不再以 Grafana 為主要操作介面。關於 `control-plane` 與 `sre-assistant` 如何協同工作的詳細技術藍圖，請參閱我們的核心架構文件：

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - **(推薦閱讀)** 描述了系統的整合架構、API 契約和數據流。

## 2. 本地開發與測試 (Local Development & Testing)

開發者可以獨立運行和測試本代理的核心功能。

### 2.1 環境設置 (Prerequisites)

- **Python**: 版本 `3.9` 或更高。
- **Poetry**: 用於管理 Python 依賴項。
- **Docker**: 用於運行資料庫等依賴項。

### 2.2 啟動服務 (Running the Service)

1.  **安裝依賴**:
    ```bash
    poetry install
    ```
2.  **啟動後端 API 服務**:
    ```bash
    poetry run python -m src.sre_assistant.main
    ```
    服務將默認在 `http://localhost:8000` 啟動。

### 2.3 執行測試 (Running Tests)

在提交任何變更前，請務必運行完整的測試套件：
```bash
pytest
```

## 3. 核心文件與連結

- **[ARCHITECTURE.md](ARCHITECTURE.md)**: 系統的整合架構設計。
- **[keycloak.md](keycloak.md)**: 身份驗證機制的詳細設定指南。
- **[openapi.yaml](openapi.yaml)**: 本服務提供的 API 端點規格。
- **`docs/legacy/`**: 包含所有舊版、以 Grafana 為中心的架構文件存檔。
