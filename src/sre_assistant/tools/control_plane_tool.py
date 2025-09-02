# src/sre_assistant/tools/control_plane_tool.py
"""
此工具用於與 Control Plane API 進行互動，以獲取額外的上下文資訊。
"""
import httpx
from typing import Dict, Any, Optional

from google.adk.agents.invocation_context import InvocationContext

from ..contracts import ToolResult, ToolError
from ..config.config_manager import config_manager

class ControlPlaneTool:
    """
    一個用於呼叫 Control Plane 後端 API 的工具。
    """
    def __init__(self):
        self.config = config_manager.get_control_plane_config()
        if not self.config or not self.config.base_url:
            raise ValueError("Control Plane configuration with base_url is required.")
        self.base_url = self.config.base_url
        self.timeout = self.config.timeout_seconds or 10

    async def get_audit_logs(
        self,
        ctx: InvocationContext,
        service_name: str,
        start_time: str,
        end_time: str
    ) -> ToolResult:
        """
        從 Control Plane 獲取指定服務在特定時間範圍內的審計日誌。

        Args:
            ctx: ADK 的調用上下文，用於獲取認證 Token。
            service_name: 要查詢的服務名稱。
            start_time: 查詢的開始時間 (ISO 8601 格式)。
            end_time: 查詢的結束時間 (ISO 8601 格式)。

        Returns:
            一個 ToolResult 物件，其中包含審計日誌列表或一個錯誤。
        """
        # 步驟 1: 從上下文中獲取 M2M 認證 Token
        # 假設在工作流程的早期，sre-assistant 已經為自己獲取了一個 M2M Token
        # 並將其儲存在會話狀態中，以供後續的工具使用。
        m2m_token = ctx.session.state.get("m2m_token")
        if not m2m_token:
            return ToolResult(
                success=False,
                error=ToolError(code="AUTH_ERROR", message="M2M token not found in session state.")
            )

        headers = {"Authorization": f"Bearer {m2m_token}"}
        params = {
            "service_name": service_name,
            "start_time": start_time,
            "end_time": end_time
        }
        url = f"{self.base_url}/api/v1/audit-logs"

        # 步驟 2: 執行非同步 HTTP 請求
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, headers=headers, timeout=self.timeout)
                response.raise_for_status()  # 如果狀態碼是 4xx 或 5xx，則會引發異常

            # 步驟 3: 處理成功的回應
            return ToolResult(success=True, data={"audit_logs": response.json()})

        except httpx.HTTPStatusError as e:
            # 處理已知的 HTTP 錯誤
            error_code = f"HTTP_{e.response.status_code}"
            error_message = f"Failed to fetch audit logs from Control Plane: {e.response.text}"
            return ToolResult(
                success=False,
                error=ToolError(code=error_code, message=error_message)
            )
        except Exception as e:
            # 處理其他未知錯誤 (例如網路問題)
            return ToolResult(
                success=False,
                error=ToolError(code="INTERNAL_TOOL_ERROR", message=str(e))
            )
