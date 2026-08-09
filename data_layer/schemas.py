from __future__ import annotations

from datetime import UTC, datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(UTC)


class CustomerContext(BaseModel):
    customer_id: UUID = Field(default_factory=uuid4)
    first_name: str
    last_name: str
    email: str
    consent_status: str
    risk_tolerance: str
    created_ts: datetime = Field(default_factory=utc_now)


class PolicyCoverage(BaseModel):
    policy_id: UUID = Field(default_factory=uuid4)
    customer_id: UUID
    policy_type: str
    coverage_limit: float
    deductible: float
    parametric_threshold: float
    status: str


class RiskObjectTwin(BaseModel):
    risk_object_id: UUID = Field(default_factory=uuid4)
    policy_id: UUID
    location_id: str
    object_type: str
    exposure_profile: str
    insured_value: float
    twin_status: str
    valid_from_ts: datetime = Field(default_factory=utc_now)
    valid_to_ts: Optional[datetime] = None
    is_current: bool = True
    created_ts: datetime = Field(default_factory=utc_now)
    modified_ts: datetime = Field(default_factory=utc_now)


class ExternalRiskSignal(BaseModel):
    signal_id: UUID = Field(default_factory=uuid4)
    location_id: str
    signal_type: str
    source_system_code: str
    severity_score: float
    event_ts: datetime = Field(default_factory=utc_now)
    created_ts: datetime = Field(default_factory=utc_now)


class DigitalTwinState(BaseModel):
    twin_state_id: UUID = Field(default_factory=uuid4)
    risk_object_id: UUID
    signal_id: UUID
    state_snapshot_ts: datetime = Field(default_factory=utc_now)
    exposure_state: str
    confidence_score: float
    trace_id: str


class LivingRiskScore(BaseModel):
    risk_score_id: UUID = Field(default_factory=uuid4)
    twin_state_id: UUID
    model_id: str
    model_version: str
    risk_score: float
    predicted_loss: float
    score_reason: str
    scored_ts: datetime = Field(default_factory=utc_now)
    trace_id: str


class GuardianAction(BaseModel):
    action_id: UUID = Field(default_factory=uuid4)
    customer_id: UUID
    risk_score_id: UUID
    action_type: str
    action_priority: str
    review_status: str
    created_ts: datetime = Field(default_factory=utc_now)
    modified_ts: datetime = Field(default_factory=utc_now)


class ClaimsPayout(BaseModel):
    payout_id: UUID = Field(default_factory=uuid4)
    policy_id: UUID
    signal_id: UUID
    payout_amount: float
    payout_status: str
    triggered_ts: datetime = Field(default_factory=utc_now)


class AIAssurance(BaseModel):
    assurance_id: UUID = Field(default_factory=uuid4)
    trace_id: str
    agent_name: str
    model_version: str
    prompt_hash: str
    safety_score: float
    execution_status: str
    created_ts: datetime = Field(default_factory=utc_now)

