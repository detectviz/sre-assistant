#!/bin/bash

# ==============================================================================
# SRE Assistant 依賴項本地安裝腳本 (Best-Effort)
# ==============================================================================
#
# 警告：這是一個盡力而為的腳本，不保證在所有環境中都能成功執行或保持冪等性。
# 本腳本假設執行環境為 Debian/Ubuntu 系統，並擁有 sudo 權限。
# 執行過程中可能需要手動介入。
#
# 架構師：Jules
# ==============================================================================

set -e  # 若有任何指令失敗，立即中止腳本

# --- 0. 系統更新與基礎工具 ---
echo ">>> [步驟 0/8] 更新系統套件..."
sudo apt-get update
sudo apt-get install -y wget curl gnupg software-properties-common ca-certificates

# --- 1. PostgreSQL 資料庫 ---
echo ">>> [步驟 1/8] 安裝 PostgreSQL..."
sudo apt-get install -y postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
echo "--- PostgreSQL 已安裝。請手動建立資料庫與使用者：---"
echo "  sudo -u postgres psql -c \"CREATE DATABASE sre_dev;\""
echo "  sudo -u postgres psql -c \"CREATE USER postgres WITH PASSWORD 'postgres';\""
echo "  sudo -u postgres psql -c \"GRANT ALL PRIVILEGES ON DATABASE sre_dev TO postgres;\""

# --- 2. Redis 快取 ---
echo ">>> [步驟 2/8] 安裝 Redis..."
sudo apt-get install -y redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
echo "--- Redis 已安裝並啟動。---"

# --- 3. Grafana 儀表板 ---
echo ">>> [步驟 3/8] 安裝 Grafana..."
sudo mkdir -p /etc/apt/keyrings/
wget -q -O - https://apt.grafana.com/gpg.key | gpg --dearmor | sudo tee /etc/apt/keyrings/grafana.gpg > /dev/null
echo "deb [signed-by=/etc/apt/keyrings/grafana.gpg] https://apt.grafana.com stable main" | sudo tee /etc/apt/sources.list.d/grafana.list
sudo apt-get update
sudo apt-get install -y grafana
sudo systemctl start grafana-server
sudo systemctl enable grafana-server
echo "--- Grafana 已安裝。請至 http://localhost:3000 訪問。---"

# --- 4. ChromaDB 向量資料庫 ---
echo ">>> [步驟 4/8] 安裝 ChromaDB..."
# ChromaDB 是一個 Python 套件，使用 pip 進行安裝
sudo apt-get install -y python3-pip
pip install chromadb
echo "--- ChromaDB 已透過 pip 安裝。若需啟動伺服器，請執行: 'chroma run --path /path/to/db' ---"

# --- 5. VictoriaMetrics 時序資料庫 ---
echo ">>> [步驟 5/8] 安裝 VictoriaMetrics..."
# VictoriaMetrics 以二進位檔形式發布
VM_VERSION="v1.99.0"
VM_ARCH="amd64" # 假設為 amd64 硬體架構
wget https://github.com/VictoriaMetrics/VictoriaMetrics/releases/download/${VM_VERSION}/victoria-metrics-${VM_ARCH}-${VM_VERSION}.tar.gz
tar -xvzf victoria-metrics-${VM_ARCH}-${VM_VERSION}.tar.gz
sudo mv victoria-metrics-prod /usr/local/bin/victoria-metrics
rm victoria-metrics-${VM_ARCH}-${VM_VERSION}.tar.gz
# 建立基礎的 systemd 服務
cat <<EOF | sudo tee /etc/systemd/system/victoria-metrics.service
[Unit]
Description=VictoriaMetrics
Wants=network-online.target
After=network-online.target

[Service]
User=root
ExecStart=/usr/local/bin/victoria-metrics \
    -storageDataPath="/var/lib/victoria-metrics-data" \
    -http.listenAddr=":8428"
Restart=always

[Install]
WantedBy=multi-user.target
EOF
sudo mkdir -p /var/lib/victoria-metrics-data
sudo systemctl daemon-reload
sudo systemctl start victoria-metrics
sudo systemctl enable victoria-metrics
echo "--- VictoriaMetrics 已安裝並啟動。---"

# --- 6. vmagent 數據採集器 ---
echo ">>> [步驟 6/8] 安裝 vmagent..."
VMAGENT_VERSION="v1.99.0"
VMAGENT_ARCH="amd64"
wget https://github.com/VictoriaMetrics/VictoriaMetrics/releases/download/${VMAGENT_VERSION}/vmagent-${VMAGENT_ARCH}-${VMAGENT_VERSION}.tar.gz
tar -xvzf vmagent-${VMAGENT_ARCH}-${VMAGENT_VERSION}.tar.gz
sudo mv vmagent-prod /usr/local/bin/vmagent
rm vmagent-${VMAGENT_ARCH}-${VMAGENT_VERSION}.tar.gz
# 注意：vmagent 需要手動設定採集目標
sudo mkdir -p /etc/vmagent
echo "--- vmagent 已安裝。請手動建立設定檔 /etc/vmagent/prometheus.yml 再啟動服務。---"

# --- 7. snmp_exporter 數據採集器 ---
echo ">>> [步驟 7/8] 安裝 snmp_exporter..."
SNMP_EXPORTER_VERSION="0.26.0"
SNMP_EXPORTER_ARCH="linux-amd64"
wget https://github.com/prometheus/snmp_exporter/releases/download/v${SNMP_EXPORTER_VERSION}/snmp_exporter-${SNMP_EXPORTER_VERSION}.${SNMP_EXPORTER_ARCH}.tar.gz
tar -xvzf snmp_exporter-${SNMP_EXPORTER_VERSION}.${SNMP_EXPORTER_ARCH}.tar.gz
sudo mv snmp_exporter-${SNMP_EXPORTER_VERSION}.${SNMP_EXPORTER_ARCH}/snmp_exporter /usr/local/bin/
rm -rf snmp_exporter*
echo "--- snmp_exporter 已安裝。需要手動設定與建立服務。---"

# --- 8. Keycloak 身份驗證服務 ---
echo ">>> [步驟 8/8] 安裝 Keycloak..."
# Keycloak 需要 Java 執行環境
sudo apt-get install -y default-jdk
KC_VERSION="25.0.0"
wget https://github.com/keycloak/keycloak/releases/download/${KC_VERSION}/keycloak-${KC_VERSION}.tar.gz
tar -xvzf keycloak-${KC_VERSION}.tar.gz
sudo mv keycloak-${KC_VERSION} /opt/keycloak
echo "--- Keycloak 已安裝至 /opt/keycloak。需要手動建立服務。---"
echo "--- 可使用 '/opt/keycloak/bin/kc.sh start-dev' 以開發模式啟動。---"

echo "=============================================================================="
echo "本地環境安裝腳本執行完畢。請檢查上方是否有錯誤訊息。"
echo "提醒：部分元件需要手動進行後續設定。"
echo "=============================================================================="
