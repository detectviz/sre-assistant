這與 **TASK-P1-CORE-03** 直接相關！讓我詳細說明如何實現 Keycloak 整合，並提供 AI 協作 Coding 的最佳實踐。

## 🔐 Keycloak OAuth 整合任務分析

### **相關任務：TASK-P1-CORE-03**

## 🎯 Keycloak 與 SRE Assistant OAuth 整合完整方案

### 📋 **任務定位：TASK-P1-CORE-03 - 實現 AuthProvider (OAuth 2.0)**

這個任務的目標是讓 SRE Assistant 能夠：
1. 與 Control Plane 共用 Keycloak 作為身份提供者
2. 實現單點登錄 (SSO)
3. 支援基於角色的訪問控制 (RBAC)

## 🔧 實作步驟與 AI 協作策略

### **步驟 1：建立 Keycloak 整合的 AuthProvider**

```python
# src/sre_assistant/auth/keycloak_provider.py
"""
Keycloak OAuth 2.0/OIDC Provider for SRE Assistant
實現與 Control Plane 共用的認證系統
"""

from typing import Dict, Optional, Any
import httpx
from datetime import datetime, timedelta
from ..config.config_manager import AuthConfig

class KeycloakAuthProvider:
    """
    Keycloak 認證提供者
    支援 OAuth 2.0 Authorization Code Flow 和 Client Credentials Flow
    """
    
    def __init__(self, config: AuthConfig):
        self.config = config
        self.keycloak_url = config.oidc_issuer  # e.g., "https://keycloak.example.com/auth/realms/control-plane"
        self.client_id = config.client_id
        self.client_secret = config.client_secret
        self.redirect_uri = config.redirect_uri
        
        # 自動發現 OIDC 端點
        self.discovery_url = f"{self.keycloak_url}/.well-known/openid-configuration"
        self._discover_endpoints()
    
    def _discover_endpoints(self):
        """從 Keycloak 的 OIDC 發現端點獲取配置"""
        response = httpx.get(self.discovery_url)
        discovery = response.json()
        
        self.auth_endpoint = discovery["authorization_endpoint"]
        self.token_endpoint = discovery["token_endpoint"]
        self.userinfo_endpoint = discovery["userinfo_endpoint"]
        self.jwks_uri = discovery["jwks_uri"]
    
    def get_authorization_url(self, state: str) -> str:
        """生成授權 URL，用於重定向用戶到 Keycloak 登錄"""
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "scope": "openid profile email roles",
            "state": state
        }
        return f"{self.auth_endpoint}?" + "&".join(f"{k}={v}" for k, v in params.items())
    
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """用授權碼交換訪問令牌"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.token_endpoint,
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "redirect_uri": self.redirect_uri
                }
            )
            return response.json()
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """從 Keycloak 獲取用戶信息和角色"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.userinfo_endpoint,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            user_info = response.json()
            
            # 解析 Keycloak 角色
            # Keycloak 通常在 realm_access 或 resource_access 中提供角色
            if "realm_access" in user_info:
                user_info["roles"] = user_info["realm_access"].get("roles", [])
            
            return user_info
```

### **步驟 2：整合到 ADK 框架**

```python
# src/sre_assistant/auth/adk_auth_integration.py
"""
將 Keycloak Provider 整合到 ADK 的 AuthProvider 協議
"""

from google.adk.auth.auth_schemes import OpenIdConnectWithConfig
from google.adk.auth.auth_credential import AuthCredential, OAuth2Auth
from google.adk.tools import ToolContext

class ADKKeycloakAuthProvider:
    """符合 ADK AuthProvider 協議的 Keycloak 提供者"""
    
    def __init__(self, keycloak_provider: KeycloakAuthProvider):
        self.keycloak = keycloak_provider
        
        # 創建 ADK 認證方案
        self.auth_scheme = OpenIdConnectWithConfig(
            authorization_endpoint=self.keycloak.auth_endpoint,
            token_endpoint=self.keycloak.token_endpoint,
            scopes=['openid', 'profile', 'email', 'roles']
        )
        
        # 創建認證憑證
        self.auth_credential = AuthCredential(
            auth_type=AuthCredentialTypes.OPEN_ID_CONNECT,
            oauth2=OAuth2Auth(
                client_id=self.keycloak.client_id,
                client_secret=self.keycloak.client_secret,
            )
        )
    
    async def authenticate_tool_context(self, tool_context: ToolContext) -> bool:
        """在工具執行前驗證和授權"""
        # 檢查 session 中是否有有效的 token
        if "access_token" not in tool_context.session.state:
            return False
        
        access_token = tool_context.session.state["access_token"]
        
        # 驗證 token 是否過期
        if self._is_token_expired(access_token):
            # 嘗試刷新 token
            refresh_token = tool_context.session.state.get("refresh_token")
            if refresh_token:
                new_tokens = await self._refresh_token(refresh_token)
                tool_context.session.state.update(new_tokens)
                return True
            return False
        
        return True
```

### **步驟 3：與 Control Plane 共用配置**

```yaml
# src/sre_assistant/config/environments/production.yaml
auth:
  provider: "keycloak"
  oidc_issuer: "https://keycloak.control-plane.example.com/auth/realms/sre"
  client_id: "sre-assistant"
  client_secret: "${KEYCLOAK_CLIENT_SECRET}"  # 從環境變數讀取
  redirect_uri: "https://sre-assistant.example.com/auth/callback"
  enable_rbac: true
  
  # 角色映射 - 與 Control Plane 保持一致
  role_mappings:
    super_admin: ["admin", "sre-operator", "viewer"]
    team_manager: ["sre-operator", "viewer"]
    team_member: ["viewer"]
```

## 💡 AI 協作 Coding 最佳實踐

### **1. 提供清晰的上下文**

當要求 AI 協助實現此功能時，使用以下提示模板：

```markdown
我正在實現 SRE Assistant 的 OAuth 2.0 認證功能 (TASK-P1-CORE-03)。

**背景**：
- 我們需要與另一個專案 Control Plane 共用 Keycloak 作為身份提供者
- 使用 Google ADK 框架
- 需要支援 SSO 和 RBAC

**已有資源**：
- Control Plane 的 Keycloak 配置（見 control-plane.md）
- ADK 認證範例（見 headless_agent_auth）
- 現有的無狀態 auth/tools.py

**需求**：
1. 實現 KeycloakAuthProvider 類
2. 支援 OAuth 2.0 Authorization Code Flow
3. 能夠從 Keycloak 獲取用戶角色
4. 與 ADK 的 AuthProvider 協議相容

請幫我實現 [具體功能]，並確保遵循 ADK 最佳實踐。
```

### **2. 分步驟開發**

將任務分解為小步驟，每次只專注一個功能：

```python
# 第一步：先實現基本的 OIDC 發現
async def test_oidc_discovery():
    """測試能否成功連接到 Keycloak 並獲取端點"""
    provider = KeycloakAuthProvider(config)
    assert provider.auth_endpoint is not None
    assert provider.token_endpoint is not None
    print("✅ OIDC Discovery successful")

# 第二步：實現授權碼交換
async def test_code_exchange():
    """測試授權碼交換流程"""
    # 使用 mock 或測試環境的授權碼
    mock_code = "test-auth-code"
    tokens = await provider.exchange_code_for_token(mock_code)
    assert "access_token" in tokens
    print("✅ Code exchange successful")

# 第三步：整合到 ADK
async def test_adk_integration():
    """測試與 ADK 框架的整合"""
    adk_provider = ADKKeycloakAuthProvider(provider)
    # 測試工具上下文認證
    # ...
```

### **3. 使用測試驅動開發 (TDD)**

```python
# tests/test_keycloak_auth.py
import pytest
from unittest.mock import AsyncMock, MagicMock

@pytest.mark.asyncio
async def test_keycloak_user_authentication():
    """測試完整的用戶認證流程"""
    # 準備
    mock_httpx = AsyncMock()
    mock_httpx.post.return_value.json.return_value = {
        "access_token": "mock-token",
        "refresh_token": "mock-refresh",
        "expires_in": 3600
    }
    
    # 執行
    provider = KeycloakAuthProvider(test_config)
    provider._http_client = mock_httpx
    
    tokens = await provider.exchange_code_for_token("test-code")
    
    # 驗證
    assert tokens["access_token"] == "mock-token"
    mock_httpx.post.assert_called_once()
```

### **4. AI 協作的具體技巧**

#### **技巧 1：提供範例代碼**
```markdown
這是 Control Plane 的 Keycloak 配置方式：
[貼上 control-plane.md 的相關部分]

這是 ADK 的認證範例：
[貼上 headless_agent_auth 的關鍵代碼]

請參考這些範例，幫我實現類似的功能。
```

#### **技巧 2：請求代碼審查**
```markdown
這是我實現的 KeycloakAuthProvider：
[貼上你的代碼]

請幫我審查：
1. 是否有安全漏洞？
2. 是否遵循 ADK 最佳實踐？
3. 錯誤處理是否完善？
4. 有什麼可以改進的地方？
```

#### **技巧 3：除錯協助**
```markdown
我在實現 Keycloak 整合時遇到這個錯誤：
```
Error: Invalid redirect_uri
```

相關代碼：
[貼上相關代碼]

Keycloak 配置：
[貼上配置]

請幫我分析可能的原因和解決方案。
```

## 🚀 實施計劃

### **第一週：基礎實現**
1. Day 1-2: 實現 KeycloakAuthProvider 基礎類
2. Day 3-4: 完成 OAuth 2.0 流程
3. Day 5: 單元測試和整合測試

### **第二週：ADK 整合**
1. Day 1-2: 實現 ADK AuthProvider 適配器
2. Day 3-4: 整合到 workflow.py
3. Day 5: 端到端測試

### **第三週：與 Control Plane 聯調**
1. Day 1-2: 配置共用 Keycloak realm
2. Day 3-4: 測試 SSO 和角色同步
3. Day 5: 文檔和部署

## 📝 驗收標準檢查清單

- [ ] 成功連接到 Keycloak OIDC 端點
- [ ] 完成 OAuth 2.0 Authorization Code Flow
- [ ] 能夠獲取並解析用戶角色
- [ ] Token 自動刷新機制運作正常
- [ ] 與 ADK 框架完全相容
- [ ] 通過所有單元測試（覆蓋率 > 80%）
- [ ] 與 Control Plane 成功實現 SSO
- [ ] RBAC 正確執行（根據角色限制功能）
- [ ] 安全審計通過（無明顯漏洞）
- [ ] 完整的錯誤處理和日誌記錄

這個整合將使 SRE Assistant 和 Control Plane 形成一個統一的、安全的智能維運平台！