# Building ClaimFlow: An AI Autopilot Agent That Processes Insurance Claims End-to-End

**By Joshua Damilola Ajisafe (CodedLabs) — June 2026**

---

I spent the last week building an AI agent that automates the entire claims processing workflow — from intake to resolution — using two Qwen Cloud models and a human-in-the-loop dashboard. Here's how it went.

## The Problem

Claims processing is a $40B+ industry where 70%+ of the work is still manual. A customer sends a message (WhatsApp, web form, email), attaches photos as evidence, and then waits days for a human adjuster to review everything. Most claims are straightforward — the damage is visible, the evidence checks out — but they still sit in a queue behind edge cases and fraud investigations.

I wanted to build something that auto-resolves the 80% of claims that are clear-cut, flags the suspicious ones, and only escalates the genuinely tricky cases to a human.

## What ClaimFlow Does

ClaimFlow is a 6-stage Autopilot Agent built for Track 4 of the Global AI Hackathon with Qwen Cloud:

1. **Intake** — Normalizes messages from any channel (WhatsApp, web, API), detects language, validates input
2. **Classify** — Qwen 3.7 Max categorizes the claim (damage/warranty/return/refund), identifies the object, assesses urgency
3. **Verify** — Qwen Vision Max inspects submitted images against the claim text, checking evidence requirements
4. **Fraud Detection** — A Four Rs framework (Recognize → Reject → Reveal → Route) flags wrong objects, manipulated images, and suspicious user patterns
5. **Decide** — Auto-approves high-confidence claims, requests more info for medium-confidence, escalates low-confidence or fraudulent ones
6. **Respond** — Auto-replies in the user's language (English, French, Spanish, Arabic) or creates a human case file

## Why Qwen Cloud

I picked Qwen Cloud for two reasons:

**First, the free tier is generous.** 1,000,000 tokens with no payment method required. For a solo hacker building over a weekend, not worrying about burning through API credits while debugging is a real advantage.

**Second, the dual-model strategy.** Qwen 3.7 Max handles text classification with strong reasoning — it correctly identified a French-language phone warranty claim and a frustrated customer's refund request from context alone. Qwen Vision Max handles image inspection, comparing what's actually visible in photos against what the user claims.

The Anthropic-compatible endpoint made integration straightforward. If you've used the Anthropic SDK before, Qwen Cloud is a drop-in replacement — just change the `base_url`. The only quirk I hit was that Qwen returns a `ThinkingBlock` before the `TextBlock` in responses. Once you filter for only `type='text'` blocks, everything works smoothly.

## What I Learned

**The hard part isn't the AI — it's the pipeline design.** Getting Qwen to classify a claim is one API call. Building a system that handles 6 stages, with decisions cascading from one stage to the next, while keeping a human in the loop — that's where the real engineering happens.

**Fraud detection needs vision + context.** A photo can show damage, but the same photo submitted by a user with 5 prior claims and 2 fraud flags tells a different story. The Four Rs framework combines image analysis with user history to catch patterns that either alone would miss.

**Multi-language support is a small detail that makes a big difference.** The agent detects the user's language at intake and responds in it. That French customer with the broken phone gets a reply in French, not a generic English template.

## Try It Yourself

The code is open source (MIT) at [github.com/Starboycoded/claimflow](https://github.com/Starboycoded/claimflow).

```bash
git clone https://github.com/Starboycoded/claimflow.git
cd claimflow
pip install -r requirements.txt
export QWEN_API_KEY="your-key-here"
python main.py --demo
```

---

*Built for the Global AI Hackathon Series with Qwen Cloud. Track 4: Autopilot Agent.*
