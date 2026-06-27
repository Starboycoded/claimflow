"""
Human-in-the-Loop Dashboard — Flask web interface for reviewing escalated claims.
Shows escalated claims with fraud flags, confidence scores, and action buttons.
"""
from flask import Flask, render_template_string, request, jsonify
from datetime import datetime

DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ClaimFlow — Human-in-the-Loop Dashboard</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: system-ui, -apple-system, sans-serif; background: #0f172a; color: #e2e8f0; min-height: 100vh; }
        .header { background: #1e293b; border-bottom: 2px solid #3b82f6; padding: 20px 32px; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { font-size: 1.5rem; color: #3b82f6; }
        .header .badge { background: #3b82f6; color: white; padding: 4px 12px; border-radius: 12px; font-size: 0.75rem; }
        .stats { display: flex; gap: 20px; padding: 20px 32px; }
        .stat-card { background: #1e293b; border-radius: 8px; padding: 16px 24px; flex: 1; text-align: center; border: 1px solid #334155; }
        .stat-card .num { font-size: 2rem; font-weight: 700; }
        .stat-card .label { font-size: 0.8rem; color: #94a3b8; margin-top: 4px; }
        .stat-card.critical .num { color: #ef4444; }
        .stat-card.warning .num { color: #f59e0b; }
        .stat-card.ok .num { color: #22c55e; }
        .container { padding: 0 32px 32px; }
        table { width: 100%; border-collapse: collapse; background: #1e293b; border-radius: 8px; overflow: hidden; border: 1px solid #334155; }
        th { background: #334155; padding: 12px 16px; text-align: left; font-size: 0.8rem; text-transform: uppercase; color: #94a3b8; }
        td { padding: 12px 16px; border-top: 1px solid #334155; font-size: 0.9rem; }
        tr:hover { background: #283448; }
        .risk-high { color: #ef4444; font-weight: 600; }
        .risk-medium { color: #f59e0b; font-weight: 600; }
        .risk-low { color: #22c55e; }
        .risk-none { color: #64748b; }
        .btn { padding: 6px 16px; border-radius: 6px; border: none; cursor: pointer; font-size: 0.8rem; font-weight: 500; }
        .btn-approve { background: #22c55e; color: white; }
        .btn-deny { background: #ef4444; color: white; }
        .btn-info { background: #3b82f6; color: white; }
        .btn:hover { opacity: 0.85; }
        .empty { text-align: center; padding: 48px; color: #64748b; }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>ClaimFlow Dashboard</h1>
            <span style="font-size:0.8rem;color:#94a3b8;">Track 4: Autopilot Agent — Human-in-the-Loop Review</span>
        </div>
        <div class="badge">Qwen Cloud</div>
    </div>

    <div class="stats">
        <div class="stat-card critical">
            <div class="num">{{ stats.high_risk }}</div>
            <div class="label">High Risk</div>
        </div>
        <div class="stat-card warning">
            <div class="num">{{ stats.escalated }}</div>
            <div class="label">Escalated</div>
        </div>
        <div class="stat-card ok">
            <div class="num">{{ stats.auto_resolved }}</div>
            <div class="label">Auto-Resolved</div>
        </div>
        <div class="stat-card" style="border-color:#64748b;">
            <div class="num" style="color:#94a3b8;">{{ stats.total }}</div>
            <div class="label">Total Claims</div>
        </div>
    </div>

    <div class="container">
        {% if claims %}
        <table>
            <thead>
                <tr>
                    <th>Claim ID</th>
                    <th>Type</th>
                    <th>Object</th>
                    <th>Urgency</th>
                    <th>Confidence</th>
                    <th>Fraud Risk</th>
                    <th>Decision</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {% for c in claims %}
                <tr>
                    <td><code>{{ c.claim_id }}</code></td>
                    <td>{{ c.classification.claim_type or '?' }}</td>
                    <td>{{ c.classification.object_type or '?' }}</td>
                    <td>{{ c.classification.urgency or '?' }}</td>
                    <td>{{ (c.verification.confidence * 100) | int if c.verification.confidence else 0 }}%</td>
                    <td><span class="risk-{{ c.fraud.overall_risk }}">{{ c.fraud.overall_risk | upper }}</span></td>
                    <td>{{ c.decision.action | upper }}</td>
                    <td>
                        {% if c.decision.requires_human %}
                        <button class="btn btn-approve" onclick="review('{{ c.claim_id }}', 'approved')">Approve</button>
                        <button class="btn btn-deny" onclick="review('{{ c.claim_id }}', 'denied')">Deny</button>
                        <button class="btn btn-info" onclick="review('{{ c.claim_id }}', 'request_info')">Request Info</button>
                        {% else %}
                        <span style="color:#64748b;">—</span>
                        {% endif %}
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% else %}
        <div class="empty">
            <p style="font-size:1.2rem;">No escalated claims pending review</p>
            <p style="margin-top:8px;">All claims are being auto-resolved. Escalated claims will appear here.</p>
        </div>
        {% endif %}
    </div>

    <script>
        async function review(claimId, action) {
            try {
                const resp = await fetch('/api/review', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({claim_id: claimId, action: action})
                });
                if (resp.ok) location.reload();
            } catch(e) {
                alert('Error: ' + e.message);
            }
        }
    </script>
</body>
</html>
"""

_claims_store = []


def create_app():
    """Create and configure the Flask dashboard app."""
    app = Flask(__name__)

    @app.route("/")
    def index():
        escalated = [c for c in _claims_store if c.get("decision", {}).get("requires_human")]
        auto_resolved = [c for c in _claims_store if not c.get("decision", {}).get("requires_human") and not c.get("rejected")]
        high_risk = [c for c in _claims_store if c.get("fraud", {}).get("overall_risk") in ("high", "medium")]

        stats = {
            "total": len(_claims_store),
            "escalated": len(escalated),
            "auto_resolved": len(auto_resolved),
            "high_risk": len(high_risk),
        }
        return render_template_string(DASHBOARD_TEMPLATE, claims=_claims_store, stats=stats)

    @app.route("/api/review", methods=["POST"])
    def review():
        data = request.get_json()
        claim_id = data.get("claim_id")
        action = data.get("action")

        for claim in _claims_store:
            if claim["claim_id"] == claim_id:
                claim["decision"]["action"] = "reviewed"
                claim["decision"]["resolution"] = action
                claim["decision"]["requires_human"] = False
                claim["decision"]["reviewed_by"] = "human"
                claim["decision"]["reviewed_at"] = datetime.now().isoformat()
                return jsonify({"status": "ok", "claim_id": claim_id, "action": action})
        return jsonify({"status": "error", "message": "Claim not found"}), 404

    @app.route("/api/claims", methods=["GET"])
    def list_claims():
        return jsonify(_claims_store)

    @app.route("/api/claims", methods=["POST"])
    def add_claim():
        """Add a claim to the dashboard store (called by orchestrator)."""
        claim = request.get_json()
        _claims_store.append(claim)
        return jsonify({"status": "ok", "claim_id": claim.get("claim_id")})

    return app


def push_claim(claim_data: dict):
    """Called by the orchestrator to register a claim in the dashboard."""
    _claims_store.append(claim_data)
