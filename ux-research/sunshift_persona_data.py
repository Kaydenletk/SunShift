#!/usr/bin/env python3
"""
SunShift — Data-driven persona generation based on RESEARCH_SYNTHESIS.md
Feeds Tampa Bay SMB user data into PersonaGenerator
"""

import sys
import json
sys.path.insert(0, "/Users/khanhle/.claude/skills/ux-researcher-designer/scripts")
from persona_generator import PersonaGenerator

# ─────────────────────────────────────────────
# Segment 1: "Dr. Worried" — Healthcare / Dental
# ─────────────────────────────────────────────
dr_worried_data = [
    {
        "user_id": f"hw_{i}",
        "age": 38 + (i % 20),  # 38-57, established practitioners
        "usage_frequency": "daily",
        "features_used": [
            "hurricane_shield", "auto_backup", "hipaa_audit_log",
            "disaster_recovery", "data_encryption", "compliance_dashboard"
        ],
        "primary_device": "desktop",
        "usage_context": "work",
        "tech_proficiency": 3 + (i % 3),  # 3-5, low-to-mid tech
        "location_type": "suburban",
        "pain_points": [
            "HIPAA compliance fear",
            "data loss during hurricane",
            "expensive IT consultants",
            "no time to manage servers",
            "insurance doesn't cover data loss"
        ][: (i % 5) + 1],
    }
    for i in range(25)
]

dr_worried_interviews = [
    {
        "quotes": [
            "After Milton, I couldn't access patient records for 12 days. We lost $85,000 in revenue.",
            "My IT guy charges $150/hour and I still don't know if my backups actually work.",
            "If I get a HIPAA fine because of a hurricane, my practice is done.",
        ],
        "motivations": [
            "Protect patient data",
            "HIPAA compliance peace of mind",
            "Business continuity after storms",
            "Reduce dependency on IT consultants",
        ],
        "values": [
            "Patient safety",
            "Regulatory compliance",
            "Business survival",
            "Simplicity",
        ],
        "goals": [
            "Zero data loss during hurricanes",
            "Automated HIPAA-compliant backups",
            "One-click disaster recovery",
        ],
        "needs": [
            "HIPAA BAA agreement",
            "Audit trail for all data transfers",
            "AES-256 encryption",
            "Simple dashboard — not IT jargon",
        ],
    }
]

# ─────────────────────────────────────────────
# Segment 2: "Attorney Always-On" — Law Firms
# ─────────────────────────────────────────────
attorney_data = [
    {
        "user_id": f"law_{i}",
        "age": 35 + (i % 25),  # 35-59
        "usage_frequency": "daily",
        "features_used": [
            "hurricane_shield", "auto_backup", "file_server_migration",
            "zero_downtime", "encrypted_sync", "energy_dashboard"
        ],
        "primary_device": "desktop",
        "usage_context": "work",
        "tech_proficiency": 4 + (i % 3),  # 4-6, mid tech
        "location_type": "urban",
        "pain_points": [
            "court deadlines missed due to power outage",
            "client confidentiality at risk",
            "file server inaccessible during storms",
            "high electricity bills for server room",
            "no DR plan but know they need one"
        ][: (i % 5) + 1],
    }
    for i in range(20)
]

attorney_interviews = [
    {
        "quotes": [
            "Missing a court filing deadline because of a hurricane is malpractice. Period.",
            "I have 15 years of case files on a server under my desk. That terrifies me.",
            "We pay $400/month in electricity just for our server closet. In summer it's worse.",
        ],
        "motivations": [
            "Never miss a court deadline",
            "Protect client confidentiality",
            "Reduce electricity costs",
            "Professional reputation",
        ],
        "values": [
            "Client trust",
            "Professional reliability",
            "Cost efficiency",
            "Data security",
        ],
        "goals": [
            "Access case files from anywhere during emergencies",
            "Reduce server electricity costs by 30%+",
            "Automated failover — no IT knowledge needed",
        ],
        "needs": [
            "End-to-end encryption for client data",
            "Remote access during evacuations",
            "Energy cost tracking dashboard",
            "Seamless file server migration",
        ],
    }
]

# ─────────────────────────────────────────────
# Segment 3: "Number Cruncher" — Accounting/Finance
# ─────────────────────────────────────────────
accountant_data = [
    {
        "user_id": f"acc_{i}",
        "age": 33 + (i % 25),  # 33-57
        "usage_frequency": ["daily", "daily", "weekly"][i % 3],  # heavier during tax season
        "features_used": [
            "hurricane_shield", "auto_backup", "seasonal_scaling",
            "energy_arbitrage", "compliance_logging", "cost_dashboard"
        ],
        "primary_device": "desktop",
        "usage_context": "work",
        "tech_proficiency": 5 + (i % 3),  # 5-7, mid-high tech
        "location_type": "suburban",
        "pain_points": [
            "tax season server overload",
            "data loss = client lawsuits",
            "electricity spikes during tax season",
            "manual backup process unreliable",
            "SOX compliance complexity"
        ][: (i % 5) + 1],
    }
    for i in range(15)
]

accountant_interviews = [
    {
        "quotes": [
            "During tax season, our server runs at 100% and our electricity bill doubles.",
            "If we lose client financial records, we lose our license. It's that simple.",
            "I know I should have a disaster plan but between January and April I can't think about anything else.",
        ],
        "motivations": [
            "Protect client financial data",
            "Handle tax season workload spikes",
            "Reduce operational costs",
            "SOX/regulatory compliance",
        ],
        "values": [
            "Accuracy",
            "Reliability",
            "Cost consciousness",
            "Client trust",
        ],
        "goals": [
            "Scale compute during tax season without buying hardware",
            "Automated backup with compliance audit trail",
            "Reduce electricity costs year-round",
        ],
        "needs": [
            "Seasonal auto-scaling to cloud",
            "Financial data encryption",
            "Cost savings dashboard with ROI tracking",
            "Integration with accounting software",
        ],
    }
]


def main():
    generator = PersonaGenerator()

    segments = [
        ("Dr. Worried — Healthcare/Dental Practice Owner", dr_worried_data, dr_worried_interviews),
        ("Attorney Always-On — Law Firm Partner", attorney_data, attorney_interviews),
        ("Number Cruncher — Accounting Firm Owner", accountant_data, accountant_interviews),
    ]

    all_personas = []

    for segment_name, data, interviews in segments:
        persona = generator.generate_persona_from_data(data, interviews)
        # Override with SunShift-specific naming
        persona["segment_name"] = segment_name
        all_personas.append(persona)

        print(f"\n{'='*60}")
        print(f"SEGMENT: {segment_name}")
        print(f"{'='*60}")
        print(generator.format_persona_output(persona))
        print()

    # Also output JSON for further processing
    if len(sys.argv) > 1 and sys.argv[1] == "json":
        print("\n\n--- JSON OUTPUT ---")
        print(json.dumps(all_personas, indent=2, default=str))


if __name__ == "__main__":
    main()
