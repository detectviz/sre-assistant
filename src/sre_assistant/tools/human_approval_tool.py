# src/sre_assistant/tools/human_approval_tool.py
"""
實現標準化的人類介入 (Human-in-the-Loop) 工具。
"""
import httpx
import uuid
from typing import Dict, Any, AsyncIterator
from google.adk.tools import LongRunningFunctionTool, ToolEvent
from ..config.config_manager import config_manager

class HumanApprovalTool(LongRunningFunctionTool):
    """
    使用 ADK 的長時間運行工具實現 HITL，並與 Control Plane 對接。

    此工具會暫停工作流程，透過向 Control Plane 發送 API 請求來觸發一個人工審批流程，
    然後等待 Control Plane 透過一個回呼 (Callback) URL 傳回批准或拒絕的結果。
    """
    def __init__(self, name: str):
        super().__init__(name=name)
        self.control_plane_config = config_manager.get_control_plane_config()
        self.sre_assistant_config = config_manager.get_sre_assistant_config()

        if not self.control_plane_config or not self.control_plane_config.base_url:
            raise ValueError("Control Plane configuration with base_url is required for HumanApprovalTool.")
        if not self.sre_assistant_config or not self.sre_assistant_config.base_url:
            raise ValueError("SRE Assistant's own base_url is required for callback.")

    async def run(self, request: Dict[str, Any]) -> AsyncIterator[ToolEvent]:
        """
        執行工具的核心邏輯：向 Control Plane 發送審批請求並等待回呼。

        Args:
            request: 一個包含需要批准的操作細節的字典。
                     例如: `{'action': 'restart_deployment', 'details': '...`}`
        """
        request_id = str(uuid.uuid4())

        # 步驟 1: 構造回呼 URL，Control Plane 將透過此 URL 回覆審批結果
        # 注意: 這需要在 sre-assistant 的 API 中實現一個對應的端點來接收回呼
        callback_url = f"{self.sre_assistant_config.base_url}/v1/callbacks/approval/{request_id}"

        # 步驟 2: 構造向 Control Plane 發送的請求內容
        payload = {
            "request_id": request_id,
            "action": request.get("action"),
            "details": request.get("details"),
            "requester": "SRE Assistant",
            "callback_url": callback_url
        }

        # 假設 Control Plane 提供了一個接收審批請求的端點
        approval_endpoint = f"{self.control_plane_config.base_url}/api/v1/approval-requests"

        try:
            # 步驟 3: 向 Control Plane 發送非同步 API 請求
            async with httpx.AsyncClient() as client:
                response = await client.post(approval_endpoint, json=payload, timeout=10)
                response.raise_for_status()

            print(f"Successfully sent approval request {request_id} to Control Plane for action: {request.get('action')}")

            # 步驟 4: 產生一個 "pending" 事件，通知 ADK Runner 工作流程正在等待外部輸入。
            # Runner 會在此處暫停，直到 Control Plane 呼叫 callback_url，
            # 觸發一個包含 FunctionResponse 的 `runner.run_async` 調用。
            yield ToolEvent(
                type="pending",
                data={"request_id": request_id, "message": "Waiting for human approval via Control Plane."}
            )

        except Exception as e:
            # 如果連發送請求都失敗了，直接產生一個 "completed" 事件並附上錯誤
            print(f"Failed to send approval request to Control Plane: {e}")
            yield ToolEvent(
                type="completed",
                data={"status": "error", "reason": f"Failed to contact Control Plane: {e}"}
            )
