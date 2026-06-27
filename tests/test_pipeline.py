"""
Basic pipeline tests — validates the agent processes claims correctly.
Run: python -m pytest tests/ -v
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

def test_intake_valid_message():
    from intake.receiver import IntakeReceiver
    receiver = IntakeReceiver()
    result = receiver.process({"text": "My laptop is broken", "source": "web"})
    assert result["rejected"] == False
    assert result["clean_text"] == "My laptop is broken"

def test_intake_empty_message():
    from intake.receiver import IntakeReceiver
    receiver = IntakeReceiver()
    result = receiver.process({"text": "", "source": "web"})
    assert result["rejected"] == True

def test_fraud_detector_clean():
    from fraud.detector import FraudDetector
    detector = FraudDetector()
    result = detector.assess(
        verification={"wrong_object": False, "possible_manipulation": False},
        classification={},
        user_history={"prior_claims": 1, "prior_fraud_flags": 0},
        images=[]
    )
    assert result["overall_risk"] == "none"

def test_fraud_detector_suspicious():
    from fraud.detector import FraudDetector
    detector = FraudDetector()
    result = detector.assess(
        verification={"wrong_object": True, "possible_manipulation": True},
        classification={},
        user_history={"prior_claims": 3, "prior_fraud_flags": 1},
        images=[]
    )
    assert result["manual_review_required"] == True
    assert result["overall_risk"] in ("medium", "high")

def test_decision_auto_approve():
    from decision.engine import DecisionEngine
    engine = DecisionEngine()
    result = engine.evaluate(
        classification={"claim_type": "damage_claim", "urgency": "low"},
        verification={"evidence_met": True, "confidence": 0.9, "evidence_reason": "Damage clearly visible"},
        fraud={"overall_risk": "none", "manual_review_required": False},
        user="test_user",
        user_history={"prior_claims": 3, "prior_fraud_flags": 0}
    )
    assert result["action"] == "auto_resolved"

def test_decision_escalate_fraud():
    from decision.engine import DecisionEngine
    engine = DecisionEngine()
    result = engine.evaluate(
        classification={"claim_type": "damage_claim", "urgency": "low"},
        verification={"evidence_met": True, "confidence": 0.9},
        fraud={"overall_risk": "high", "manual_review_required": True, "risk_flags": "wrong_object,possible_manipulation"},
        user="test_user",
        user_history={"prior_claims": 1}
    )
    assert result["action"] == "escalated"
