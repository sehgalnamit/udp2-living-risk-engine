from __future__ import annotations

from typing import Any

from mcp_tools.tools import UDP2Tooling


class LivingRiskOrchestrator:
    def __init__(self, tooling: UDP2Tooling) -> None:
        self.tooling = tooling

    def execute_signal_dag(self, payload: dict[str, Any], trace_id: str) -> dict[str, Any]:
        location_id = str(payload["location_id"])
        signal_type = str(payload["signal_type"])
        source_system_code = str(payload.get("source_system_code", signal_type.upper()))
        telemetry = payload.get("telemetry", {})
        update_result = self.tooling.update_twin_and_score(
            location_id=location_id,
            signal_type=signal_type,
            source_system_code=source_system_code,
            telemetry=telemetry,
            trace_id=trace_id,
        )
        guardian_result = self.tooling.trigger_guardian_action(
            customer_id=update_result["customer_id"],
            risk_score_id=update_result["risk_score_id"],
            risk_score=float(update_result["risk_score"]),
            trace_id=trace_id,
        )
        payout_result = self.tooling.evaluate_parametric_payout(
            policy_id=update_result["policy_id"],
            signal_id=update_result["signal_id"],
            severity_score=float(update_result["severity_score"]),
            trace_id=trace_id,
        )
        coverage_result = self.tooling.recommend_contextual_coverage(location_id=location_id, trace_id=trace_id)
        assurance_result = self.tooling.log_ai_assurance(
            trace_id=trace_id,
            agent_name="LivingRiskOrchestrator",
            model_version="2.0.0",
            prompt_payload=payload,
            safety_score=0.99,
            execution_status="success",
        )
        return {
            "trace_id": trace_id,
            "signal_ingestion": {"location_id": location_id, "signal_type": signal_type},
            "twin_state_and_score": update_result,
            "guardian_action_check": guardian_result,
            "parametric_payout_check": payout_result,
            "contextual_rider_check": coverage_result,
            "ai_assurance_logging": assurance_result,
        }

