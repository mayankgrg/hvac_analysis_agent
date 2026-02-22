from __future__ import annotations

import json
from typing import Any


def build_reasoning_prompt(project_name: str, evidence: dict[str, Any]) -> str:
    return (
        "You are an HVAC margin rescue analyst. Use evidence and return strict JSON with keys: "
        "root_cause, contributing_factors, recovery_actions, recoverable_amount, confidence, evidence_refs. "
        f"Project: {project_name}. Evidence: {json.dumps(evidence)}"
    )
