"""
Decision engine — auto-resolve, request more info, or escalate to human.
"""
from config import config

class DecisionEngine:
    def evaluate(self, classification, verification, fraud, user, user_history):
        confidence = verification.get("confidence", 0.5)
        fraud_risk = fraud.get("overall_risk", "none")
        urgency = classification.get("urgency", "medium")

        if fraud.get("manual_review_required"):
            return self._escalate("fraud_detected",
                f"Fraud risk: {fraud_risk}. Flags: {fraud.get('risk_flags','none')}")

        if fraud_risk == "high":
            return self._escalate("high_fraud_risk",
                "Multiple fraud indicators detected")

        if urgency == "critical":
            return self._escalate("critical_urgency",
                "Critical urgency claim requires human review")

        if user_history.get("prior_claims", 0) == 0:
            return self._request_info("first_claim",
                "First claim from this user — requesting additional verification")

        if confidence >= config.auto_resolve_threshold and fraud_risk in ("none", "low"):
            if verification.get("evidence_met"):
                return self._auto_approve(confidence, verification)
            else:
                return self._auto_deny(confidence, verification)

        if confidence >= config.human_escalation_threshold:
            return self._request_info("medium_confidence",
                f"Confidence {confidence:.0%} — requesting additional evidence")

        return self._escalate("low_confidence",
            f"Confidence {confidence:.0%} below threshold")

    def _auto_approve(self, confidence, verification):
        return {
            "action": "auto_resolved",
            "resolution": "approved",
            "confidence": confidence,
            "reason": verification.get("evidence_reason", ""),
            "requires_human": False
        }

    def _auto_deny(self, confidence, verification):
        return {
            "action": "auto_resolved",
            "resolution": "denied",
            "confidence": confidence,
            "reason": verification.get("evidence_reason", ""),
            "requires_human": False
        }

    def _request_info(self, reason_code, detail):
        return {
            "action": "info_requested",
            "reason_code": reason_code,
            "detail": detail,
            "requires_human": False,
            "follow_up_questions": [
                "Can you provide additional photos from a different angle?",
                "Please confirm the date the damage occurred."
            ]
        }

    def _escalate(self, reason_code, detail):
        return {
            "action": "escalated",
            "reason_code": reason_code,
            "detail": detail,
            "requires_human": True,
            "priority": "high" if reason_code in ("fraud_detected","high_fraud_risk") else "normal"
        }
