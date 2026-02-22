from __future__ import annotations

from typing import Any


def generate_reasoning_from_evidence(evidence: dict[str, Any]) -> dict[str, Any]:
    trigger_type = evidence.get("trigger_type", "UNKNOWN")
    cos = evidence.get("change_orders", [])
    open_rfis = [r for r in evidence.get("rfis", []) if r.get("status") != "Closed"]

    root = {
        "LINE_OVERRUN": "Labor/material execution exceeded bid assumptions on affected SOV line.",
        "PENDING_CO_EXPOSURE": "Revenue risk from unresolved change orders is accumulating against current costs.",
        "BILLING_LAG": "Earned work is not being billed/approved fast enough, creating cash and margin pressure.",
        "ORPHAN_RFI": "Cost-impact RFIs are not translating into formal change recovery.",
    }.get(trigger_type, "Mixed cost and execution pressure.")

    factors = [
        f"Recent CO count: {len(cos)}",
        f"Open RFI count in sampled set: {len(open_rfis)}",
        f"Labor sample size: {len(evidence.get('labor_samples', []))}",
    ]
    actions = [
        {"action": "Escalate unresolved COs with 72-hour owner response deadline", "owner": "PM", "amount": 250000},
        {"action": "Freeze overtime on non-critical paths and re-sequence crews", "owner": "Superintendent", "amount": 120000},
        {"action": "Weekly bill-vs-earned review with finance", "owner": "Project Controls", "amount": 80000},
    ]
    return {
        "root_cause": root,
        "contributing_factors": factors,
        "recovery_actions": actions,
        "recoverable_amount": sum(a["amount"] for a in actions),
        "confidence": 0.72,
        "evidence_refs": {
            "field_note_ids": [n.get("note_id") for n in evidence.get("field_notes", [])[:3]],
            "co_numbers": [c.get("co_number") for c in cos[:3]],
            "rfi_numbers": [r.get("rfi_number") for r in evidence.get("rfis", [])[:3]],
        },
    }
