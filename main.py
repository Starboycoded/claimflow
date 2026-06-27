"""
ClaimFlow — Autopilot Agent for Claims Processing
Track 4: Autopilot Agent — Global AI Hackathon with Qwen Cloud
Entry point: python main.py --demo | --process <file> | --dashboard-only
"""
import argparse, json, sys, os, uuid
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import config
from agent.orchestrator import ClaimOrchestrator


SAMPLE_CLAIMS = [
    {
        "text": "My MacBook Pro screen cracked during shipping. I ordered it 2 days ago and it arrived like this. I need a replacement immediately.",
        "source": "web",
        "images": [],
    },
    {
        "text": "The car bumper I received has a huge dent on the left side. This is unacceptable — I paid $800 for this part.",
        "source": "web",
        "images": [],
    },
    {
        "text": "Bonjour, le telephone que j'ai recu ne s'allume pas du tout. L'ecran reste noir meme apres chargement.",
        "source": "web",
        "images": [],
    },
    {
        "text": "My package arrived but the box was completely crushed and the appliance inside is bent. I want a full refund.",
        "source": "api",
        "images": [],
    },
    {
        "text": "Just checking — what's your return policy for opened electronics? I bought a laptop but changed my mind.",
        "source": "web",
        "images": [],
    },
]


def run_demo():
    """Process 5 sample claims through the full pipeline."""
    print("=" * 60)
    print("  ClaimFlow Autopilot Agent — Demo Mode")
    print("  Track 4: Autopilot Agent | Qwen Cloud Hackathon")
    print("=" * 60)

    orchestrator = ClaimOrchestrator()

    for i, raw in enumerate(SAMPLE_CLAIMS, 1):
        print(f"\n{'─' * 50}")
        print(f"  Claim #{i}: {raw['text'][:80]}...")
        print(f"{'─' * 50}")

        result = orchestrator.process(raw)
        _print_result(result, i)

    print(f"\n{'=' * 60}")
    print("  Demo complete. 5 claims processed.")
    print("  Dashboard available at http://localhost:{}/".format(config.dashboard_port))
    print("=" * 60)


def run_single(filepath):
    """Process a single claim from a JSON file."""
    with open(filepath, "r") as f:
        raw = json.load(f)

    orchestrator = ClaimOrchestrator()
    result = orchestrator.process(raw)
    _print_result(result, 1)
    return result


def _print_result(result, idx):
    """Pretty-print pipeline result."""
    c = result.get("classification", {})
    v = result.get("verification", {})
    f = result.get("fraud", {})
    d = result.get("decision", {})

    print(f"  Claim ID:    {result.get('claim_id', 'N/A')}")
    print(f"  Type:        {c.get('claim_type', '?')} | Object: {c.get('object_type', '?')}")
    print(f"  Urgency:     {c.get('urgency', '?')} | Sentiment: {c.get('sentiment', '?')}")
    print(f"  Evidence:    {'Met' if v.get('evidence_met') else 'Not Met'} (conf: {v.get('confidence', 0):.0%})")
    print(f"  Fraud Risk:  {f.get('overall_risk', 'none').upper()} | Flags: {f.get('risk_flags', 'none')}")
    print(f"  Decision:    {d.get('action', '?').upper()} -> {d.get('resolution', d.get('reason_code', '?'))}")


def run_dashboard():
    """Start the human-in-the-loop Flask dashboard."""
    from web.dashboard import create_app
    app = create_app()
    print(f"\n  ClaimFlow Dashboard running at http://localhost:{config.dashboard_port}/")
    print("  Press Ctrl+C to stop.\n")
    app.run(host="0.0.0.0", port=config.dashboard_port, debug=False)


def main():
    parser = argparse.ArgumentParser(description="ClaimFlow Autopilot Agent")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--demo", action="store_true", help="Run demo with 5 sample claims")
    group.add_argument("--process", type=str, metavar="FILE", help="Process single claim from JSON file")
    group.add_argument("--dashboard-only", action="store_true", help="Start dashboard only")
    args = parser.parse_args()

    if args.demo:
        run_demo()
    elif args.process:
        run_single(args.process)
    elif args.dashboard_only:
        run_dashboard()
    else:
        print("Usage: python main.py --demo | --process <file.json> | --dashboard-only")
        sys.exit(1)


if __name__ == "__main__":
    main()
