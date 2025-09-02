# src/sre_assistant/tools/prometheus_tool.py
"""
此工具用於與 Prometheus 進行互動，以查詢指標數據。
"""
import httpx
from typing import Dict, Any, Optional

from ..contracts import ToolResult, ToolError
from ..config.config_manager import config_manager

class PrometheusQueryTool:
    """
    一個用於執行 PromQL 查詢的工具。
    """
    def __init__(self):
        self.config = config_manager.get_prometheus_config()
        if not self.config or not self.config.base_url:
            raise ValueError("Prometheus configuration with base_url is required.")
        self.base_url = self.config.base_url
        self.timeout = self.config.timeout_seconds or 15

    async def execute_query(
        self,
        promql_query: str,
        time: Optional[str] = None
    ) -> ToolResult:
        """
        執行一個 PromQL 查詢。

        Args:
            promql_query: 要執行的 PromQL 查詢字串。
            time: (可選) 執行查詢的時間戳。如果留空，則使用當前時間。

        Returns:
            一個 ToolResult 物件，其中包含查詢結果或一個錯誤。
        """
        params = {"query": promql_query}
        if time:
            params["time"] = time

        url = f"{self.base_url}/api/v1/query"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=self.timeout)
                response.raise_for_status()

            query_result = response.json()
            if query_result.get("status") == "success":
                return ToolResult(success=True, data=query_result.get("data", {}))
            else:
                error_message = query_result.get("error", "Unknown Prometheus error")
                return ToolResult(
                    success=False,
                    error=ToolError(code="PROMETHEUS_QUERY_FAILED", message=error_message)
                )

        except httpx.HTTPStatusError as e:
            error_code = f"HTTP_{e.response.status_code}"
            error_message = f"Failed to query Prometheus: {e.response.text}"
            return ToolResult(
                success=False,
                error=ToolError(code=error_code, message=error_message)
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=ToolError(code="INTERNAL_TOOL_ERROR", message=str(e))
            )
