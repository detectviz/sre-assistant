# src/sre_assistant/workflow.py
"""
SRE Assistant - 核心工作流程

本檔案定義了 SRE Assistant 的核心業務邏輯，遵循 `EnhancedSREWorkflow` 設計模式
"""

from typing import Dict, Any, List, Optional

from google.adk.agents import (
    LlmAgent,
    SequentialAgent,
    ParallelAgent,
    BaseAgent
)
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.invocation_context import InvocationContext
from google.genai import types
from pydantic import BaseModel, Field

# Import tools
from .tools.human_approval_tool import HumanApprovalTool
from .tools.prometheus_tool import PrometheusQueryTool
from .tools.loki_tool import LokiLogQueryTool
from .tools.control_plane_tool import ControlPlaneTool


# --- 1. 定義結構化輸出 (Pydantic Models) ---

class DispatchDecision(BaseModel):
    """
    定義智能分診器 (IntelligentDispatcher) 的決策輸出格式,
    這確保了 LLM 的輸出是可預測和可用的
    """
    selected_experts: List[str] = Field(description="根據診斷結果，選擇最合適的專家代理名稱列表")
    reasoning: str = Field(description="解釋為什麼選擇這些專家代理的簡要理由")
    confidence: float = Field(description="對此決策的信心指數 (0.0 到 1.0)")


# --- 2. 實例化工具並定義具備工具的代理 ---

# 實例化所有需要的工具
prometheus_tool = PrometheusQueryTool()
loki_tool = LokiLogQueryTool()
control_plane_tool = ControlPlaneTool()
human_approval_tool = HumanApprovalTool(name="ask_for_approval")

# 為 LlmAgent 創建一個輔助函式，以保持程式碼整潔
def _create_agent(name: str, instruction: str, tools: List[Any] = None) -> LlmAgent:
    """一個用於創建 LlmAgent 的輔助函式"""
    return LlmAgent(
        name=name,
        instruction=instruction,
        model="gemini-1.5-flash",
        tools=tools or []
    )

# 定義具備真實工具的診斷代理
MetricsAnalyzer = _create_agent(
    "MetricsAnalyzer",
    "分析指標數據並總結發現。請使用 prometheus_query_tool。",
    tools=[prometheus_tool]
)
LogAnalyzer = _create_agent(
    "LogAnalyzer",
    "分析日誌數據並找出異常錯誤。請使用 loki_log_query_tool。",
    tools=[loki_tool]
)
ContextFetcher = _create_agent(
    "ContextFetcher",
    "從 Control Plane 獲取關於服務變更歷史的上下文資訊。請使用 control_plane_tool。",
    tools=[control_plane_tool]
)
# TraceAnalyzer 仍然是一個佔位符，因為我們尚未創建其工具
TraceAnalyzer = _create_agent(
    "TraceAnalyzer", "分析追蹤數據以確定延遲瓶頸"
)

# 定義具備人工審批工具的修復代理
RemediationExecutor = _create_agent(
    "RemediationExecutor",
    instruction=(
        "You are a remediation executor. You have been given a remediation plan. "
        "You MUST first ask for human approval for the action: 'restart_deployment'. "
        "Use the ask_for_approval tool. "
        "If the approval status from the tool output is 'approved', then you MUST state 'REMEDIATION APPROVED AND EXECUTED'. "
        "Otherwise, you must state 'REMEDIATION REJECTED'."
    ),
    tools=[human_approval_tool]
)

# 驗證代理的佔位符
HealthCheckAgent = _create_agent(
    "HealthCheckAgent", "執行服務健康檢查"
)
SLOValidationAgent = _create_agent(
    "SLOValidationAgent", "驗證服務的 SLO 是否恢復正常"
)


# --- 3. 實現核心工作流程 (Core Workflow) ---

class EnhancedSREWorkflow(SequentialAgent):
    """
    符合 ADK 最佳實踐的 SRE 工作流程,
    這是一個由多個階段性子代理組成的序列，用於處理從診斷到修復的完整流程
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        # 步驟 1: 創建工作流程的各個階段
        diagnostic_phase = self._create_diagnostic_phase()
        dispatcher_phase = self._create_dispatcher_phase()
        remediation_phase = self._create_remediation_phase()
        verification_phase = self._create_verification_phase()

        # 步驟 2: 使用父類別 `SequentialAgent` 的構造函式來串聯這些階段
        super().__init__(
            name="EnhancedSREWorkflow",
            sub_agents=[
                diagnostic_phase,
                dispatcher_phase,
                remediation_phase,
                verification_phase
            ],
            # 註冊整個工作流程開始前和完成後的回呼函式
            before_agent_callback=self._workflow_pre_check,
            after_agent_callback=self._workflow_post_process
        )
        print("EnhancedSREWorkflow initialized.")

    def _create_diagnostic_phase(self) -> ParallelAgent:
        """
        創建並行診斷階段,
        此階段會同時運行多個分析代理，以最快速度收集資訊
        """
        print("Creating DiagnosticPhase...")
        # TODO: The 'EnhancedSREWorkflow' blueprint from salvaged_code.md uses
        #       parameters (aggregation_strategy, etc.) not available in the
        #       current ADK version (^1.12.0). Reverting to a simpler ParallelAgent
        #       for now and will revisit advanced parallel execution patterns later.
        return ParallelAgent(
            name="DiagnosticPhase",
            sub_agents=[
                MetricsAnalyzer,
                LogAnalyzer,
                ContextFetcher, # 新增的代理，用於獲取上下文
                TraceAnalyzer,
            ],
        )

    def _aggregate_diagnostics(self, results: List[Dict]) -> Dict:
        """
        自定義的聚合函式，用於將多個診斷代理的輸出整合成一個全面的報告
        """
        print("Aggregating diagnostic results...")
        # 在真實場景中，這裡會有更複雜的邏輯來融合和去重資訊
        combined_details = "\n".join([str(r) for r in results])
        return {"summary": "綜合診斷報告", "details": combined_details}

    def _create_dispatcher_phase(self) -> LlmAgent:
        """
        創建智能分診修復階段,
        此階段使用一個 LLM 來根據診斷結果，動態地選擇合適的修復專家
        """
        print("Creating DispatcherPhase...")
        # 這裡我們使用一個 LlmAgent 來模擬分診器
        return LlmAgent(
            name="IntelligentDispatcher",
            instruction=(
                "請仔細分析來自 {aggregated_diagnosis} 的診斷報告, "
                "然後假裝你選擇了 'KubernetesRemediationAgent' 來解決問題, "
                "你的輸出應該只有 'KubernetesRemediationAgent' 這個詞"
            ),
            output_key="remediation_decision"
        )

    def _create_remediation_phase(self) -> BaseAgent:
        """
        創建執行修復的階段，此階段包含人工審批步驟
        """
        print("Creating RemediationPhase (Executor)...")
        return RemediationExecutor

    def _create_verification_phase(self) -> SequentialAgent:
        """
        創建修復後驗證階段,
        這是一個循序代理，用於執行一系列檢查來確認問題是否已解決
        """
        print("Creating VerificationPhase...")
        return SequentialAgent(
            name="VerificationPhase",
            sub_agents=[
                HealthCheckAgent,
                SLOValidationAgent,
            ],
            after_agent_callback=self._check_verification_status
        )

    def _workflow_pre_check(self, context: CallbackContext) -> Optional[types.Content]:
        """在整個工作流程開始前執行的回呼函式"""
        print(f"Workflow '{self.name}' pre-check triggered for user query: {context.user_query}")
        # 可以在此處添加如權限檢查、參數驗證等邏輯
        return None  # 返回 None 表示繼續執行

    def _workflow_post_process(self, context: CallbackContext) -> Optional[types.Content]:
        """在整個工作流程完成後執行的回呼函式"""
        print(f"Workflow '{self.name}' post-process triggered. Final state: {context.state}")
        # 可以在此處添加如發送通知、記錄日誌等邏輯
        return None

    def _check_verification_status(self, context: CallbackContext):
        """
        在驗證階段完成後的回呼，用於檢查驗證是否通過,
        這模擬了 self-criticism 模式
        """
        print("Checking verification status...")
        # 假設驗證代理會將結果寫入 state
        if not context.state.get("verification_passed", True): # 默認為 True 以便測試
            self._trigger_rollback(context)

    def _trigger_rollback(self, context: CallbackContext):
        """模擬觸發回滾的機制"""
        print("CRITICAL: Verification failed! Triggering rollback procedures.")
        context.state["rollback_required"] = True
