"""
Four Rs Fraud Detection — adapted for the ClaimFlow Autopilot Agent.

R1 RECOGNIZE: Separate claim from visible findings
R2 REJECT: Flag wrong objects/parts
R3 REVEAL: Detect manipulation, text instructions
R4 ROUTE: Check user history, escalate suspicious patterns
"""
from dataclasses import dataclass, field

@dataclass
class FraudAssessment:
    wrong_object: bool = False
    wrong_object_part: bool = False
    non_original_image: bool = False
    possible_manipulation: bool = False
    text_instruction_present: bool = False
    user_history_risk: bool = False
    manual_review_required: bool = False
    risk_flags: list = field(default_factory=list)
    overall_risk: str = "none"

class FraudDetector:
    def assess(self, verification, classification, user_history, images):
        fa = FraudAssessment()

        fa.wrong_object = verification.get("wrong_object", False)
        fa.wrong_object_part = verification.get("wrong_object_part", False)
        fa.possible_manipulation = verification.get("possible_manipulation", False)
        fa.text_instruction_present = verification.get("text_instruction_found", False)

        prior_flags = user_history.get("prior_fraud_flags", 0)
        prior_claims = user_history.get("prior_claims", 0)
        if prior_flags >= 2 or prior_claims >= 5:
            fa.user_history_risk = True

        if fa.wrong_object: fa.risk_flags.append("wrong_object")
        if fa.wrong_object_part: fa.risk_flags.append("wrong_object_part")
        if fa.possible_manipulation: fa.risk_flags.append("possible_manipulation")
        if fa.text_instruction_present: fa.risk_flags.append("text_instruction_present")
        if fa.user_history_risk: fa.risk_flags.append("user_history_risk")

        serious = sum([fa.wrong_object, fa.possible_manipulation, fa.text_instruction_present])
        if serious >= 2 or fa.user_history_risk:
            fa.manual_review_required = True
            fa.risk_flags.append("manual_review_required")

        count = len(fa.risk_flags)
        fa.overall_risk = "none" if count==0 else "low" if count<=1 else "medium" if count<=3 else "high"

        return {
            "wrong_object": fa.wrong_object,
            "possible_manipulation": fa.possible_manipulation,
            "text_instruction_present": fa.text_instruction_present,
            "user_history_risk": fa.user_history_risk,
            "manual_review_required": fa.manual_review_required,
            "risk_flags": ",".join(fa.risk_flags) if fa.risk_flags else "none",
            "overall_risk": fa.overall_risk
        }
