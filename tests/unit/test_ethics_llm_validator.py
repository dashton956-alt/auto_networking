"""Tests for ANIF-722 LLM output validation — 4-stage pipeline."""

from __future__ import annotations

import hashlib
import uuid

import pytest

from anif_platform.ethics.llm_validator import (
    LLMOutputValidator,
    LLMValidationInput,
    Stage4SecurityIncidentError,
)


def _make_prompt_hash(prompt: str) -> str:
    return hashlib.sha256(prompt.encode()).hexdigest()


def _valid_input(
    *,
    confidence: float = 0.90,
    agent_tier: int = 2,
    prompt: str = "test prompt",
    schema_valid: bool = True,
    hallucination_free: bool = True,
    canonical_state_age: int = 120,
) -> LLMValidationInput:
    prompt_hash = _make_prompt_hash(prompt)
    return LLMValidationInput(
        agent_id=uuid.uuid4(),
        intent_id=uuid.uuid4(),
        agent_tier=agent_tier,
        output_schema_valid=schema_valid,
        factual_claims_consistent=hallucination_free,
        canonical_state_age_seconds=canonical_state_age,
        confidence_score=confidence,
        prompt_hash_recorded=prompt_hash,
        prompt_hash_submitted=prompt_hash,
    )


# ── Stage 1: Schema Check ──────────────────────────────────────────────────


def test_stage1_pass_when_schema_valid() -> None:
    """ANIF-722 §5.2: output passes stage 1 when schema is valid."""
    result = LLMOutputValidator().validate(_valid_input(schema_valid=True))
    assert result.stage1 == "pass"


def test_stage1_fail_blocks_pipeline() -> None:
    """ANIF-722 §5.4: schema failure blocks — result is blocked with manual_review."""
    result = LLMOutputValidator().validate(_valid_input(schema_valid=False))
    assert result.stage1 == "fail"
    assert result.blocked is True
    assert result.route_to == "manual_review"
    assert result.strike_incremented is True


# ── Stage 2: Hallucination Check ──────────────────────────────────────────


def test_stage2_fail_blocks_pipeline() -> None:
    """ANIF-722 §6.6: hallucination failure blocks and increments strike."""
    result = LLMOutputValidator().validate(
        _valid_input(schema_valid=True, hallucination_free=False)
    )
    assert result.stage2 == "fail"
    assert result.blocked is True
    assert result.strike_incremented is True


def test_stage2_stale_canonical_state_blocks() -> None:
    """ANIF-722 §6.2: canonical state older than 5 min (300s) MUST block stage 2."""
    result = LLMOutputValidator().validate(_valid_input(canonical_state_age=400))
    assert result.stage2 == "fail"
    assert result.blocked is True


# ── Stage 3: Confidence Check ──────────────────────────────────────────────


def test_stage3_pass_tier2_above_threshold() -> None:
    """ANIF-722 §7.3: tier 2 agent with confidence ≥ 0.65 passes stage 3."""
    result = LLMOutputValidator().validate(_valid_input(confidence=0.70, agent_tier=2))
    assert result.stage3 == "pass"
    assert result.blocked is False


def test_stage3_suppressed_tier2_below_threshold() -> None:
    """ANIF-722 §7.5: tier 2 agent with confidence < 0.65 is suppressed (not blocked via strike)."""
    result = LLMOutputValidator().validate(_valid_input(confidence=0.50, agent_tier=2))
    assert result.stage3 == "suppressed"
    assert result.blocked is True
    assert result.strike_incremented is False


def test_stage3_suppressed_tier3_below_threshold() -> None:
    """ANIF-722 §7.2: tier 3 threshold is 0.80."""
    result = LLMOutputValidator().validate(_valid_input(confidence=0.75, agent_tier=3))
    assert result.stage3 == "suppressed"
    assert result.blocked is True


# ── Stage 4: Prompt Integrity Hash ────────────────────────────────────────


def test_stage4_pass_when_hashes_match() -> None:
    """ANIF-722 §8.2: matching hashes pass stage 4."""
    result = LLMOutputValidator().validate(_valid_input())
    assert result.stage4 == "pass"


def test_stage4_hash_mismatch_raises_security_incident() -> None:
    """ANIF-722 §8.4: hash mismatch MUST raise Stage4SecurityIncidentError."""
    inp = _valid_input()
    inp.prompt_hash_submitted = "tampered_hash_value"
    with pytest.raises(Stage4SecurityIncidentError):
        LLMOutputValidator().validate(inp)


# ── All stages pass ────────────────────────────────────────────────────────


def test_all_stages_pass_returns_approved() -> None:
    """ANIF-722 §4: all stages passing returns approved output."""
    result = LLMOutputValidator().validate(_valid_input())
    assert result.blocked is False
    assert result.stage1 == "pass"
    assert result.stage2 == "pass"
    assert result.stage3 == "pass"
    assert result.stage4 == "pass"
