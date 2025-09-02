# src/sre_assistant/tools/loki_tool.py
"""
此工具用於與 Grafana Loki 進行互動，以查詢日誌數據。
"""
import httpx
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from ..contracts import ToolResult, ToolError
from ..config.config_manager import config_manager

class LokiLogQueryTool:
    """
    一個用於執行 LogQL 查詢的工具。
    """
    def __init__(self):
        self.config = config_manager.get_loki_config()
        if not self.config or not self.config.base_url:
            raise ValueError("Loki configuration with base_url is required.")
        self.base_url = self.config.base_url
        self.timeout = self.config.timeout_seconds or 20

    async def execute_query_range(
        self,
        logql_query: str,
        limit: int = 100,
        minutes_ago: int = 60
    ) -> ToolResult:
        """
        執行一個 LogQL 範圍查詢 (query_range)。

        Args:
            logql_query: 要執行的 LogQL 查詢字串。
            limit: 返回的最大日誌行數。
            minutes_ago: 從多少分鐘前開始查詢。

        Returns:
            一個 ToolResult 物件，其中包含查詢結果或一個錯誤。
        """
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=minutes_ago)

        params = {
            "query": logql_query,
            "limit": limit,
            "start": start_time.timestamp(),
            "end": end_time.timestamp()
        }

        url = f"{self.base_url}/loki/api/v1/query_range"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=self.timeout)
                response.raise_for_status()

            query_result = response.json()
            if query_result.get("status") == "success":
                return ToolResult(success=True, data=query_result.get("data", {}))
            else:
                error_message = query_result.get("error", "Unknown Loki error")
                return ToolResult(
                    success=False,
                    error=ToolError(code="LOKI_QUERY_FAILED", message=error_message)
                )

        except httpx.HTTPStatusError as e:
            error_code = f"HTTP_{e.response.status_code}"
            error_message = f"Failed to query Loki: {e.response.text}"
            return ToolResult(
                success=False,
                error=ToolError(code=error_code, message=error_message)
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=ToolError(code="INTERNAL_TOOL_ERROR", message=str(e))
            )
