"""
Response generator — creates customer replies or human case files.
"""
import json
from config import config

RESPONSE_PROMPT = """You are a customer service agent. Generate a professional, empathetic response to the user.

Context: {case_summary}
Decision: {decision}
Language: {language}

Rules:
- Be warm but professional
- If approved: confirm the decision and next steps
- If denied: explain clearly and politely why
- If more info needed: ask specifically for what's missing
- Never make promises about timelines or amounts
- Keep under 3 sentences when possible
"""

class Responder:
    def generate(self, decision, case, user_language="en"):
        action = decision.get("action", "escalated")
        resolution = decision.get("resolution", "")

        if action == "auto_resolved" and resolution == "approved":
            return self._build_reply(case, decision, user_language, template="approved")
        elif action == "auto_resolved" and resolution == "denied":
            return self._build_reply(case, decision, user_language, template="denied")
        elif action == "info_requested":
            return self._build_reply(case, decision, user_language, template="info_requested")
        else:
            return self._build_escalation(case, decision)

    def _build_reply(self, case, decision, language, template):
        claim_id = case["claim_id"]
        templates = {
            "approved": {
                "en": f"Thank you for your claim (ref: {claim_id}). After reviewing your evidence, your claim has been approved. You'll receive confirmation within 24 hours.",
                "es": f"Gracias por su reclamo (ref: {claim_id}). Tras revisar la evidencia, su reclamo ha sido aprobado. Recibira confirmacion en 24 horas.",
                "fr": f"Merci pour votre reclamation (ref: {claim_id}). Apres examen, votre reclamation est approuvee. Vous recevrez une confirmation sous 24h.",
                "ar": f"Shukran ala mutalibatika (ref: {claim_id}). Baada murajaat al-adilla, tamma al-muwafaqa ala mutalibatika. satatalaqqa ta'keedan khilal 24 sa'a."
            },
            "denied": {
                "en": f"Regarding your claim (ref: {claim_id}), we were unable to verify the reported damage from the submitted images. You may resubmit with additional evidence.",
            },
            "info_requested": {
                "en": f"Thank you for your claim (ref: {claim_id}). To proceed, we need additional information. {decision.get('follow_up_questions',['Please provide more details.'])[0]}",
            }
        }
        msgs = templates.get(template, templates["info_requested"])
        return {
            "type": "auto_reply",
            "message": msgs.get(language, msgs["en"]),
            "language": language,
            "channel": case.get("source", "whatsapp")
        }

    def _build_escalation(self, case, decision):
        return {
            "type": "human_escalation",
            "case_file": {
                "claim_id": case["claim_id"],
                "reason": decision.get("detail", ""),
                "priority": decision.get("priority", "normal"),
                "summary": case.get("classification", {}).get("summary", ""),
                "fraud_flags": case.get("fraud", {}).get("risk_flags", "none"),
                "verification": case.get("verification", {}),
            },
            "customer_message": {
                "en": f"Your claim (ref: {case['claim_id']}) requires additional review. A specialist will contact you shortly."
            }
        }
