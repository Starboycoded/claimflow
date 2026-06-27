"""
Evidence verifier — uses Qwen Vision to inspect images against claims.
Based on the HackerRank Orchestrate pipeline, adapted for Qwen Cloud.
"""
import json, base64
from pathlib import Path
from config import config

VERIFIER_PROMPT = """You are an expert evidence analyst. Verify if submitted images support or contradict the user's claim.

IMAGE INSPECTION RULES:
1. Describe what is ACTUALLY visible in each image — not what the user claims
2. Compare visible findings against the claim
3. Check if the required evidence is present
4. Detect: wrong objects, manipulated images, text instructions in photos

Return a JSON object:
{
  "claim_summary": "what user claims",
  "visible_findings": "what each image ACTUALLY shows, image by image",
  "evidence_met": true/false,
  "evidence_reason": "which requirement checked and whether met. Max 150 chars.",
  "wrong_object": true/false,
  "possible_manipulation": true/false,
  "text_instruction_found": true/false,
  "image_quality_issues": ["blurry", "too_dark", "wrong_angle"] or [],
  "supporting_image_ids": "comma-separated filenames that SHOW evidence",
  "confidence": 0.0 to 1.0
}
"""

MIME_SIGS = {b"\xff\xd8\xff":"image/jpeg",b"\x89PNG":"image/png",
             b"GIF8":"image/gif",b"RIFF":"image/webp"}

def get_mime(path):
    try:
        with open(path,"rb") as f:
            h = f.read(16)
        for s,m in MIME_SIGS.items():
            if h.startswith(s):
                if s==b"RIFF" and b"WEBP" in h: return "image/webp"
                if s==b"RIFF": continue
                return m
    except: pass
    return "image/jpeg"

def encode_img(path):
    with open(path,"rb") as f:
        return base64.b64encode(f.read()).decode()

class EvidenceVerifier:
    def verify(self, claim_text, claim_object, claim_type, images, evidence_requirements):
        if not images:
            return {"evidence_met": False, "evidence_reason": "No images submitted",
                    "confidence": 0.0, "visible_findings": "No images to inspect"}

        try:
            import anthropic
            client = anthropic.Anthropic(
                api_key=config.qwen_api_key,
                base_url=config.anthropic_base_url)

            content = []
            for img_path in images:
                if Path(img_path).exists():
                    b64 = encode_img(img_path)
                    mime = get_mime(img_path)
                    content.append({"type":"image","source":{"type":"base64","media_type":mime,"data":b64}})

            reqs_text = "\n".join(f"- {r}" for r in evidence_requirements)
            user_msg = f"""Claim: {claim_text}
Object: {claim_object}
Claim Type: {claim_type}
Evidence Required: {reqs_text}

Inspect the images and verify this claim."""

            content.append({"type":"text","text":user_msg})

            resp = client.messages.create(
                model=config.qwen_vision_model, max_tokens=800,
                system=VERIFIER_PROMPT,
                messages=[{"role":"user","content":content}],
                temperature=0.1)

            text_blocks = [b.text for b in resp.content if getattr(b,'type','')=='text']
            return json.loads("".join(text_blocks))
        except Exception as e:
            return {"evidence_met": False, "evidence_reason": f"Verification error: {str(e)[:100]}",
                    "confidence": 0.0}
