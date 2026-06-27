"""
Claim classifier — uses Qwen to categorize incoming claims.
"""
import json
from config import config

CLASSIFIER_PROMPT = """You are a claims classification agent. Analyze the user's message and classify it.

Return a JSON object:
{
  "claim_type": "damage_claim | warranty_claim | return_request | refund_request | general_inquiry",
  "object_type": "car | laptop | package | phone | appliance | other",
  "object_part": "specific part mentioned (e.g. screen, bumper, lid)",
  "issue_category": "dent | scratch | crack | missing_part | water_damage | broken | not_working | other",
  "urgency": "low | medium | high | critical",
  "summary": "one sentence summarizing the claim",
  "language": "detected language code",
  "sentiment": "neutral | frustrated | urgent | calm"
}

Rules:
- urgency=critical if safety issue or high value item
- Extract object_type even if vaguely described
- If unclear, use "other" and note ambiguity
"""

class ClaimClassifier:
    def classify(self, text, images, user_history):
        if not text:
            return {"claim_type": "general_inquiry", "object_type": "other",
                    "urgency": "low", "summary": "No claim text provided"}

        try:
            import anthropic
            client = anthropic.Anthropic(
                api_key=config.qwen_api_key,
                base_url=config.anthropic_base_url)

            user_msg = f"User message: {text}\nUser history: {json.dumps(user_history)}\n\nClassify this claim."

            resp = client.messages.create(
                model=config.qwen_model, max_tokens=300,
                system=CLASSIFIER_PROMPT,
                messages=[{"role":"user","content":user_msg}],
                temperature=0.0)

            text_blocks = [b.text for b in resp.content if getattr(b,'type','')=='text']
            result = json.loads("".join(text_blocks))
            return result
        except Exception as e:
            return {"claim_type": "general_inquiry", "object_type": "other",
                    "urgency": "medium", "summary": text[:100], "error": str(e)[:100]}
