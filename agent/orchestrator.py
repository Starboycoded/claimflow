"""
Claim orchestrator — coordinates the 6-stage Autopilot Agent pipeline.

Stage 1: Intake    -> Normalize message from any channel
Stage 2: Classify  -> Qwen 3.7 Max: claim type, object, urgency
Stage 3: Verify    -> Qwen Vision Max: inspect image evidence
Stage 4: Fraud     -> Four Rs: Recognize -> Reject -> Reveal -> Route
Stage 5: Decide    -> Auto-approve / request-info / escalate
Stage 6: Respond   -> Auto-reply or create human case file
"""
import uuid
from datetime import datetime

from config import config
from intake.receiver import IntakeReceiver
from agent.classifier import ClaimClassifier
from verification.verifier import EvidenceVerifier
from fraud.detector import FraudDetector
from decision.engine import DecisionEngine
from agent.responder import Responder


class ClaimOrchestrator:
    """6-stage Autopilot Agent pipeline for claim processing."""

    def __init__(self):
        self.intake = IntakeReceiver()
        self.classifier = ClaimClassifier()
        self.verifier = EvidenceVerifier()
        self.fraud = FraudDetector()
        self.decider = DecisionEngine()
        self.responder = Responder()

    def process(self, raw_message: dict, user_id: str = None) -> dict:
        """
        Run a claim through the full 6-stage pipeline.
        Returns the complete case record with all stage outputs.
        """
        claim_id = raw_message.get("claim_id", str(uuid.uuid4())[:8])
        user_id = user_id or raw_message.get("user_id", "anonymous")
        images = raw_message.get("images", [])

        # Stage 1: Intake
        intake = self.intake.process(raw_message)
        if intake.get("rejected"):
            return {
                "claim_id": claim_id,
                "rejected": True,
                "reason": intake.get("reason", "Unknown"),
                "timestamp": datetime.now().isoformat(),
            }

        # Stage 2: Classify
        user_history = raw_message.get("user_history", {"prior_claims": 0, "prior_fraud_flags": 0})
        classification = self.classifier.classify(
            text=intake.get("clean_text", ""),
            images=images,
            user_history=user_history,
        )

        # Stage 3: Verify
        evidence_requirements = self._build_evidence_requirements(classification)
        verification = self.verifier.verify(
            claim_text=intake.get("clean_text", ""),
            claim_object=classification.get("object_type", "other"),
            claim_type=classification.get("claim_type", "general_inquiry"),
            images=images,
            evidence_requirements=evidence_requirements,
        )

        # Stage 4: Fraud Detection
        fraud = self.fraud.assess(
            verification=verification,
            classification=classification,
            user_history=user_history,
            images=images,
        )

        # Stage 5: Decision
        decision = self.decider.evaluate(
            classification=classification,
            verification=verification,
            fraud=fraud,
            user=user_id,
            user_history=user_history,
        )

        # Stage 6: Respond
        response = self.responder.generate(
            decision=decision,
            case={
                "claim_id": claim_id,
                "classification": classification,
                "verification": verification,
                "fraud": fraud,
                "source": raw_message.get("source", "web"),
            },
            user_language=classification.get("language", intake.get("language", "en")),
        )

        return {
            "claim_id": claim_id,
            "user_id": user_id,
            "rejected": False,
            "timestamp": datetime.now().isoformat(),
            "intake": intake,
            "classification": classification,
            "verification": verification,
            "fraud": fraud,
            "decision": decision,
            "response": response,
        }

    def _build_evidence_requirements(self, classification: dict) -> list:
        """Build evidence requirements based on claim type and object."""
        claim_type = classification.get("claim_type", "")
        requirements = []

        if claim_type == "damage_claim":
            requirements = [
                "Clear photo of the damaged area",
                "Photo showing the full item for context",
                "Photo of any packaging if shipping damage",
            ]
        elif claim_type == "warranty_claim":
            requirements = [
                "Photo of the defective part",
                "Photo of serial number / model label",
                "Proof of purchase (receipt or order number)",
            ]
        elif claim_type == "return_request":
            requirements = [
                "Photo of the item in current condition",
                "Photo of all accessories and packaging",
            ]
        elif claim_type == "refund_request":
            requirements = [
                "Photo of the issue / defect",
                "Photo of the full product",
                "Order confirmation or receipt",
            ]
        else:
            requirements = ["Relevant photo or screenshot of the issue"]

        return requirements
