from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import duckdb

from data_layer.schemas import (
    AIAssurance,
    ClaimsPayout,
    CustomerContext,
    DigitalTwinState,
    ExternalRiskSignal,
    GuardianAction,
    LivingRiskScore,
    PolicyCoverage,
    RiskObjectTwin,
)

try:
    from fastmcp import FastMCP
except Exception:  # pragma: no cover - fallback for constrained environments
    class FastMCP:  # type: ignore[no-redef]
        def __init__(self, name: str):
            self.name = name


def utc_now() -> datetime:
    return datetime.now(UTC)


def ensure_trace_id(trace_id: str | None = None) -> str:
    return trace_id if trace_id else str(uuid4())


def mask_pii_value(key: str, value: Any) -> Any:
    if value is None:
        return value
    if key == "email" and isinstance(value, str) and "@" in value:
        local, domain = value.split("@", 1)
        return f"{local[:1]}***@{domain}"
    if key in {"first_name", "last_name"} and isinstance(value, str):
        return value[:1] + "***"
    return value


def mask_pii(record: dict[str, Any]) -> dict[str, Any]:
    return {key: mask_pii_value(key, value) for key, value in record.items()}


class UDP2Tooling:
    def __init__(self) -> None:
        self.mcp = FastMCP("Insurance-UDP-2.0-Engine")
        self.conn = duckdb.connect(database=":memory:")
        self._create_tables()
        self._seed_baseline_data()

    def _create_tables(self) -> None:
        ddls = [
            """
            CREATE TABLE IF NOT EXISTS customer_context (
                customer_id VARCHAR PRIMARY KEY,
                first_name VARCHAR NOT NULL,
                last_name VARCHAR NOT NULL,
                email VARCHAR NOT NULL,
                consent_status VARCHAR NOT NULL,
                risk_tolerance VARCHAR NOT NULL,
                created_ts TIMESTAMP NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS policy_coverage (
                policy_id VARCHAR PRIMARY KEY,
                customer_id VARCHAR NOT NULL,
                policy_type VARCHAR NOT NULL,
                coverage_limit DOUBLE NOT NULL,
                deductible DOUBLE NOT NULL,
                parametric_threshold DOUBLE NOT NULL,
                status VARCHAR NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS risk_object_twin (
                risk_object_id VARCHAR PRIMARY KEY,
                policy_id VARCHAR NOT NULL,
                location_id VARCHAR NOT NULL,
                object_type VARCHAR NOT NULL,
                exposure_profile VARCHAR NOT NULL,
                insured_value DOUBLE NOT NULL,
                twin_status VARCHAR NOT NULL,
                valid_from_ts TIMESTAMP NOT NULL,
                valid_to_ts TIMESTAMP,
                is_current BOOLEAN NOT NULL,
                created_ts TIMESTAMP NOT NULL,
                modified_ts TIMESTAMP NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS external_risk_signal (
                signal_id VARCHAR PRIMARY KEY,
                location_id VARCHAR NOT NULL,
                signal_type VARCHAR NOT NULL,
                source_system_code VARCHAR NOT NULL,
                severity_score DOUBLE NOT NULL,
                event_ts TIMESTAMP NOT NULL,
                created_ts TIMESTAMP NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS digital_twin_state (
                twin_state_id VARCHAR PRIMARY KEY,
                risk_object_id VARCHAR NOT NULL,
                signal_id VARCHAR NOT NULL,
                state_snapshot_ts TIMESTAMP NOT NULL,
                exposure_state VARCHAR NOT NULL,
                confidence_score DOUBLE NOT NULL,
                trace_id VARCHAR NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS living_risk_score (
                risk_score_id VARCHAR PRIMARY KEY,
                twin_state_id VARCHAR NOT NULL,
                model_id VARCHAR NOT NULL,
                model_version VARCHAR NOT NULL,
                risk_score DOUBLE NOT NULL,
                predicted_loss DOUBLE NOT NULL,
                score_reason VARCHAR NOT NULL,
                scored_ts TIMESTAMP NOT NULL,
                trace_id VARCHAR NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS guardian_action (
                action_id VARCHAR PRIMARY KEY,
                customer_id VARCHAR NOT NULL,
                risk_score_id VARCHAR NOT NULL,
                action_type VARCHAR NOT NULL,
                action_priority VARCHAR NOT NULL,
                review_status VARCHAR NOT NULL,
                created_ts TIMESTAMP NOT NULL,
                modified_ts TIMESTAMP NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS claims_payout (
                payout_id VARCHAR PRIMARY KEY,
                policy_id VARCHAR NOT NULL,
                signal_id VARCHAR NOT NULL,
                payout_amount DOUBLE NOT NULL,
                payout_status VARCHAR NOT NULL,
                triggered_ts TIMESTAMP NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS ai_assurance (
                assurance_id VARCHAR PRIMARY KEY,
                trace_id VARCHAR NOT NULL,
                agent_name VARCHAR NOT NULL,
                model_version VARCHAR NOT NULL,
                prompt_hash VARCHAR NOT NULL,
                safety_score DOUBLE NOT NULL,
                execution_status VARCHAR NOT NULL,
                created_ts TIMESTAMP NOT NULL
            )
            """,
        ]
        for ddl in ddls:
            self.conn.execute(ddl)

    def _seed_baseline_data(self) -> None:
        customer = CustomerContext(
            first_name="Alex",
            last_name="Morgan",
            email="alex.morgan@example.com",
            consent_status="granted",
            risk_tolerance="balanced",
        )
        policy = PolicyCoverage(
            customer_id=customer.customer_id,
            policy_type="home",
            coverage_limit=450000.0,
            deductible=2500.0,
            parametric_threshold=0.7,
            status="active",
        )
        twin = RiskObjectTwin(
            policy_id=policy.policy_id,
            location_id="LOC-BASELINE-001",
            object_type="property",
            exposure_profile=json.dumps({"roof_type": "asphalt", "year_built": 2008}),
            insured_value=450000.0,
            twin_status="active",
        )
        self.conn.execute(
            """
            INSERT INTO customer_context
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                str(customer.customer_id),
                customer.first_name,
                customer.last_name,
                customer.email,
                customer.consent_status,
                customer.risk_tolerance,
                customer.created_ts,
            ],
        )
        self.conn.execute(
            """
            INSERT INTO policy_coverage
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                str(policy.policy_id),
                str(policy.customer_id),
                policy.policy_type,
                policy.coverage_limit,
                policy.deductible,
                policy.parametric_threshold,
                policy.status,
            ],
        )
        self.conn.execute(
            """
            INSERT INTO risk_object_twin
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                str(twin.risk_object_id),
                str(twin.policy_id),
                twin.location_id,
                twin.object_type,
                twin.exposure_profile,
                twin.insured_value,
                twin.twin_status,
                twin.valid_from_ts,
                twin.valid_to_ts,
                twin.is_current,
                twin.created_ts,
                twin.modified_ts,
            ],
        )

    def prefill_property_twin(
        self, location_id: str, first_name: str, last_name: str, email: str, trace_id: str | None = None
    ) -> dict[str, Any]:
        trace = ensure_trace_id(trace_id)
        customer = CustomerContext(
            first_name=first_name,
            last_name=last_name,
            email=email,
            consent_status="granted",
            risk_tolerance="balanced",
        )
        policy = PolicyCoverage(
            customer_id=customer.customer_id,
            policy_type="home",
            coverage_limit=500000.0,
            deductible=2000.0,
            parametric_threshold=0.75,
            status="active",
        )
        exposure_profile = {
            "attom_property_score": 0.72,
            "planet_roof_wear_index": 0.34,
            "vegetation_proximity": "medium",
        }
        twin = RiskObjectTwin(
            policy_id=policy.policy_id,
            location_id=location_id,
            object_type="property",
            exposure_profile=json.dumps(exposure_profile),
            insured_value=500000.0,
            twin_status="active",
        )
        self.conn.execute(
            "INSERT INTO customer_context VALUES (?, ?, ?, ?, ?, ?, ?)",
            [
                str(customer.customer_id),
                customer.first_name,
                customer.last_name,
                customer.email,
                customer.consent_status,
                customer.risk_tolerance,
                customer.created_ts,
            ],
        )
        self.conn.execute(
            "INSERT INTO policy_coverage VALUES (?, ?, ?, ?, ?, ?, ?)",
            [
                str(policy.policy_id),
                str(policy.customer_id),
                policy.policy_type,
                policy.coverage_limit,
                policy.deductible,
                policy.parametric_threshold,
                policy.status,
            ],
        )
        self.conn.execute(
            "INSERT INTO risk_object_twin VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                str(twin.risk_object_id),
                str(twin.policy_id),
                twin.location_id,
                twin.object_type,
                twin.exposure_profile,
                twin.insured_value,
                twin.twin_status,
                twin.valid_from_ts,
                twin.valid_to_ts,
                twin.is_current,
                twin.created_ts,
                twin.modified_ts,
            ],
        )
        return {
            "trace_id": trace,
            "customer": mask_pii(customer.model_dump(mode="json")),
            "policy_id": str(policy.policy_id),
            "risk_object_id": str(twin.risk_object_id),
            "prefill_sources": ["ATTOM", "PlanetLabs"],
            "exposure_profile": exposure_profile,
        }

    def _calculate_severity(self, signal_type: str, payload: dict[str, Any]) -> float:
        if signal_type == "openweather":
            wind = float(payload.get("wind_mph", 0.0))
            hail = float(payload.get("hail_inches", 0.0))
            return min(1.0, (wind / 120.0) + (hail / 2.0))
        if signal_type == "usgs":
            magnitude = float(payload.get("magnitude", 0.0))
            depth_factor = 1.0 if float(payload.get("depth_km", 10.0)) <= 30 else 0.8
            return min(1.0, (magnitude / 10.0) * depth_factor)
        if signal_type == "iot_valve":
            pressure = float(payload.get("line_pressure", 0.0))
            leak_prob = float(payload.get("leak_probability", 0.0))
            return min(1.0, (pressure / 200.0) + leak_prob)
        return min(1.0, float(payload.get("severity_score", 0.0)))

    def update_twin_and_score(
        self,
        location_id: str,
        signal_type: str,
        source_system_code: str,
        telemetry: dict[str, Any],
        trace_id: str | None = None,
    ) -> dict[str, Any]:
        trace = ensure_trace_id(trace_id)
        severity = self._calculate_severity(signal_type, telemetry)

        signal = ExternalRiskSignal(
            location_id=location_id,
            signal_type=signal_type,
            source_system_code=source_system_code,
            severity_score=severity,
        )
        self.conn.execute(
            "INSERT INTO external_risk_signal VALUES (?, ?, ?, ?, ?, ?, ?)",
            [
                str(signal.signal_id),
                signal.location_id,
                signal.signal_type,
                signal.source_system_code,
                signal.severity_score,
                signal.event_ts,
                signal.created_ts,
            ],
        )
        twin_row = self.conn.execute(
            """
            SELECT rot.risk_object_id, rot.insured_value, rot.policy_id, pc.customer_id
            FROM risk_object_twin rot
            JOIN policy_coverage pc ON pc.policy_id = rot.policy_id
            WHERE rot.location_id = ? AND rot.is_current = ?
            ORDER BY rot.created_ts DESC
            LIMIT 1
            """,
            [location_id, True],
        ).fetchone()
        if not twin_row:
            raise ValueError(f"No active twin for location_id={location_id}")
        risk_object_id, insured_value, policy_id, customer_id = twin_row
        risk_score_value = min(1.0, severity * 1.2)
        state = DigitalTwinState(
            risk_object_id=risk_object_id,
            signal_id=signal.signal_id,
            exposure_state="elevated" if risk_score_value >= 0.5 else "normal",
            confidence_score=max(0.3, min(0.99, severity)),
            trace_id=trace,
        )
        score = LivingRiskScore(
            twin_state_id=state.twin_state_id,
            model_id="living-risk-engine",
            model_version="2.0.0",
            risk_score=risk_score_value,
            predicted_loss=float(insured_value) * risk_score_value * 0.1,
            score_reason=f"Derived from {signal_type} severity={severity:.3f}",
            trace_id=trace,
        )
        self.conn.execute(
            "INSERT INTO digital_twin_state VALUES (?, ?, ?, ?, ?, ?, ?)",
            [
                str(state.twin_state_id),
                str(state.risk_object_id),
                str(state.signal_id),
                state.state_snapshot_ts,
                state.exposure_state,
                state.confidence_score,
                state.trace_id,
            ],
        )
        self.conn.execute(
            "INSERT INTO living_risk_score VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                str(score.risk_score_id),
                str(score.twin_state_id),
                score.model_id,
                score.model_version,
                score.risk_score,
                score.predicted_loss,
                score.score_reason,
                score.scored_ts,
                score.trace_id,
            ],
        )
        return {
            "trace_id": trace,
            "signal_id": str(signal.signal_id),
            "policy_id": policy_id,
            "customer_id": customer_id,
            "risk_score_id": str(score.risk_score_id),
            "risk_score": score.risk_score,
            "severity_score": severity,
        }

    def trigger_guardian_action(
        self, customer_id: str, risk_score_id: str, risk_score: float, trace_id: str | None = None
    ) -> dict[str, Any]:
        trace = ensure_trace_id(trace_id)
        if risk_score < 0.5:
            return {"trace_id": trace, "triggered": False}
        action = GuardianAction(
            customer_id=customer_id,
            risk_score_id=risk_score_id,
            action_type="SHUT_OFF_VALVE",
            action_priority="high",
            review_status="open",
        )
        self.conn.execute(
            "INSERT INTO guardian_action VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            [
                str(action.action_id),
                str(action.customer_id),
                str(action.risk_score_id),
                action.action_type,
                action.action_priority,
                action.review_status,
                action.created_ts,
                action.modified_ts,
            ],
        )
        return {
            "trace_id": trace,
            "triggered": True,
            "action_id": str(action.action_id),
            "iot_command": {"command": "VALVE_SHUTOFF", "priority": "urgent"},
        }

    def evaluate_parametric_payout(
        self, policy_id: str, signal_id: str, severity_score: float, trace_id: str | None = None
    ) -> dict[str, Any]:
        trace = ensure_trace_id(trace_id)
        policy = self.conn.execute(
            """
            SELECT coverage_limit, parametric_threshold
            FROM policy_coverage
            WHERE policy_id = ?
            LIMIT 1
            """,
            [policy_id],
        ).fetchone()
        if not policy:
            return {"trace_id": trace, "triggered": False}
        coverage_limit, threshold = policy
        if severity_score < float(threshold):
            return {"trace_id": trace, "triggered": False}
        payout = ClaimsPayout(
            policy_id=policy_id,
            signal_id=signal_id,
            payout_amount=float(coverage_limit) * 0.2,
            payout_status="approved",
        )
        self.conn.execute(
            "INSERT INTO claims_payout VALUES (?, ?, ?, ?, ?, ?)",
            [
                str(payout.payout_id),
                str(payout.policy_id),
                str(payout.signal_id),
                payout.payout_amount,
                payout.payout_status,
                payout.triggered_ts,
            ],
        )
        return {
            "trace_id": trace,
            "triggered": True,
            "payout_id": str(payout.payout_id),
            "payout_amount": payout.payout_amount,
        }

    def recommend_contextual_coverage(self, location_id: str, trace_id: str | None = None) -> dict[str, Any]:
        trace = ensure_trace_id(trace_id)
        result = self.conn.execute(
            """
            SELECT lrs.risk_score
            FROM living_risk_score lrs
            JOIN digital_twin_state dts ON dts.twin_state_id = lrs.twin_state_id
            JOIN risk_object_twin rot ON rot.risk_object_id = dts.risk_object_id
            WHERE rot.location_id = ?
            ORDER BY lrs.scored_ts DESC
            LIMIT 1
            """,
            [location_id],
        ).fetchone()
        if not result:
            return {"trace_id": trace, "recommendations": []}
        risk_score = float(result[0])
        recommendations = []
        if risk_score >= 0.7:
            recommendations.append(
                {
                    "rider": "SevereWeather-72h",
                    "coverage_limit": 100000,
                    "estimated_premium": 79.0,
                }
            )
        elif risk_score >= 0.4:
            recommendations.append(
                {
                    "rider": "PropertyProtection-Weekend",
                    "coverage_limit": 50000,
                    "estimated_premium": 29.0,
                }
            )
        return {"trace_id": trace, "recommendations": recommendations}

    def log_ai_assurance(
        self,
        trace_id: str,
        agent_name: str,
        model_version: str,
        prompt_payload: dict[str, Any],
        safety_score: float,
        execution_status: str,
    ) -> dict[str, Any]:
        prompt_hash = hashlib.sha256(json.dumps(prompt_payload, sort_keys=True).encode("utf-8")).hexdigest()
        assurance = AIAssurance(
            trace_id=trace_id,
            agent_name=agent_name,
            model_version=model_version,
            prompt_hash=prompt_hash,
            safety_score=safety_score,
            execution_status=execution_status,
        )
        self.conn.execute(
            "INSERT INTO ai_assurance VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            [
                str(assurance.assurance_id),
                assurance.trace_id,
                assurance.agent_name,
                assurance.model_version,
                assurance.prompt_hash,
                assurance.safety_score,
                assurance.execution_status,
                assurance.created_ts,
            ],
        )
        return {"trace_id": trace_id, "assurance_id": str(assurance.assurance_id), "prompt_hash": prompt_hash}

    def get_twin_state(self, location_id: str) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            """
            SELECT
                rot.location_id,
                dts.state_snapshot_ts,
                dts.exposure_state,
                lrs.risk_score,
                lrs.predicted_loss,
                lrs.trace_id
            FROM risk_object_twin rot
            JOIN digital_twin_state dts ON dts.risk_object_id = rot.risk_object_id
            JOIN living_risk_score lrs ON lrs.twin_state_id = dts.twin_state_id
            WHERE rot.location_id = ?
            ORDER BY dts.state_snapshot_ts DESC
            LIMIT 10
            """,
            [location_id],
        ).fetchall()
        return [
            {
                "location_id": row[0],
                "state_snapshot_ts": row[1].isoformat(),
                "exposure_state": row[2],
                "risk_score": float(row[3]),
                "predicted_loss": float(row[4]),
                "trace_id": row[5],
            }
            for row in rows
        ]

    def get_active_actions(self) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            """
            SELECT ga.action_id, ga.action_type, ga.action_priority, ga.review_status, cc.first_name, cc.last_name, cc.email
            FROM guardian_action ga
            JOIN customer_context cc ON cc.customer_id = ga.customer_id
            WHERE ga.review_status = ?
            ORDER BY ga.created_ts DESC
            """,
            ["open"],
        ).fetchall()
        return [
            mask_pii(
                {
                    "action_id": row[0],
                    "action_type": row[1],
                    "action_priority": row[2],
                    "review_status": row[3],
                    "first_name": row[4],
                    "last_name": row[5],
                    "email": row[6],
                }
            )
            for row in rows
        ]

    def health(self) -> dict[str, Any]:
        return {"status": "ok", "mcp_server": self.mcp.name, "timestamp": utc_now().isoformat()}

