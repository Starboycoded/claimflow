"""
ClaimFlow Configuration — Qwen Cloud powered Autopilot Agent.
Track 4: Autopilot Agent — HackerRank-tested architecture, Qwen-powered.
"""
import os
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Config:
    # Qwen Cloud
    qwen_api_key: str = field(default_factory=lambda: os.getenv("QWEN_API_KEY", ""))
    qwen_model: str = "qwen3.7-max"
    qwen_vision_model: str = "qwen-vl-max"
    anthropic_base_url: str = "https://dashscope-intl.aliyuncs.com/apps/anthropic"

    # Agent settings
    auto_resolve_threshold: float = 0.85
    human_escalation_threshold: float = 0.60
    max_images_per_claim: int = 5
    supported_languages: list = field(default_factory=lambda: ["en", "fr", "es", "ar", "zh"])

    # Business workflow
    claim_categories: list = field(default_factory=lambda: [
        "damage_claim", "warranty_claim", "return_request",
        "refund_request", "general_inquiry"
    ])
    object_types: list = field(default_factory=lambda: [
        "car", "laptop", "package", "phone", "appliance", "other"
    ])

    # Human-in-the-loop
    dashboard_port: int = 5000
    require_human_approval_for: list = field(default_factory=lambda: [
        "high_value_claim", "fraud_suspected", "first_time_user"
    ])

    # Database (JSON file for demo, PostgreSQL for production)
    db_path: str = "claims_database.json"

config = Config()
