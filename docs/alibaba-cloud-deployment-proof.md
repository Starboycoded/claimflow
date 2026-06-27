# Alibaba Cloud Deployment Proof — ClaimFlow

## Qwen Cloud Integration

ClaimFlow uses **Qwen Cloud** (Alibaba Cloud's international AI platform) as its core AI engine via the DashScope International API.

### API Endpoint Configuration

```python
# config.py
qwen_api_key: str = os.getenv("QWEN_API_KEY", "")
qwen_model: str = "qwen3.7-max"
qwen_vision_model: str = "qwen-vl-max"
anthropic_base_url: str = "https://dashscope-intl.aliyuncs.com/apps/anthropic"
```

### Verified API Usage

**Endpoint:** `https://dashscope-intl.aliyuncs.com/apps/anthropic`  
**Protocol:** Anthropic-compatible SDK  
**Models Used:**
- `qwen3.7-max` — Text classification (Stages 2: Classify)
- `qwen-vl-max` — Vision evidence verification (Stage 3: Verify)

**API Key Source:** Generated at https://home.qwencloud.com/api-keys

### Live Demo Results (June 27, 2026)

Running `python main.py --demo` with QWEN_API_KEY set:

```
Claim #1: MacBook Pro screen cracked → classified as "damage_claim" / "laptop"
Claim #2: Car bumper dent → classified as "damage_claim" / "car" / "frustrated"  
Claim #3: French phone not working → classified as "warranty_claim" / "phone"
Claim #4: Crushed package → classified as "refund_request" / "appliance" / "frustrated"
Claim #5: Return policy question → classified as "return_request" / "laptop" / "low"

All 5 claims processed through full 6-stage pipeline successfully.
```

### Free Tier Usage

- **Plan:** Qwen Cloud Free Tier
- **Quota:** 1,000,000 tokens
- **No payment method required**
- **Access:** Immediate after account creation
- **Models available on free tier:** qwen3.7-max, qwen-vl-max

### Code That Calls Qwen Cloud

**Stage 2 — Classifier** (`agent/classifier.py`):
```python
import anthropic
client = anthropic.Anthropic(
    api_key=config.qwen_api_key,
    base_url=config.anthropic_base_url)

resp = client.messages.create(
    model=config.qwen_model,
    max_tokens=300,
    system=CLASSIFIER_PROMPT,
    messages=[{"role":"user","content":user_msg}])
```

**Stage 3 — Verifier** (`verification/verifier.py`):
```python
import anthropic
client = anthropic.Anthropic(
    api_key=config.qwen_api_key,
    base_url=config.anthropic_base_url)

resp = client.messages.create(
    model=config.qwen_vision_model,
    max_tokens=800,
    system=VERIFIER_PROMPT,
    messages=[{"role":"user","content":content}])
```

### Screenshot Instructions

To capture deployment proof for submission:
1. Log into https://home.qwencloud.com/api-keys
2. Screenshot the API Keys page showing an active key
3. Screenshot the demo output showing Qwen Cloud classification results
4. Include both in the Devpost submission
