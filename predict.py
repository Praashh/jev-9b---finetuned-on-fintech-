#!/usr/bin/env python3
"""
FinTech Transaction Guardian - Live Model Predictor
Run inference directly against your fine-tuned Endor model: 'default/jev-9b-v1'

Usage:
  python3 predict.py               # Runs interactive scenario test
  python3 predict.py --fraud       # Tests a fraud attack (SIM swap / Mule)
  python3 predict.py --legit       # Tests a verified grocery UPI transaction
  python3 predict.py --all         # Runs through all test scenarios
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timezone

# 1. Load API key from .env if present
env_file = Path(".env")
if env_file.exists():
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line.startswith("ENDOR_API_KEY=") and not line.startswith("#"):
            val = line.split("=", 1)[1].strip().strip('"').strip("'")
            if val:
                os.environ["ENDOR_API_KEY"] = val

if not os.environ.get("ENDOR_API_KEY"):
    print("❌ ENDOR_API_KEY is not set. Please add it to .env or export it.")
    sys.exit(1)

import endor

MODEL_NAME = "default/jev-9b-v1"

QUESTIONS_SCHEMA = {
    "is_fraud": {
        "type": "noul",
        "instructions": "Is this fintech transaction fraudulent, abusive, or indicative of financial crime?"
    },
    "fintech_category": {
        "type": "choice",
        "instructions": "What fintech transaction flow best describes this event?",
        "criteria": {
            "p2p_transfer": "Peer-to-peer payments, instant wallet transfers, split bills",
            "card_spend": "Debit/credit card e-commerce, POS swipes, consumer retail",
            "saas_payroll": "B2B SaaS subscriptions, cloud infra, salary & vendor payouts",
            "wealth_invest": "Brokerage deposits, mutual fund SIP mandates, crypto funding",
            "loan_bnpl": "Buy-now-pay-later installments, credit line drawdowns, EMI debits",
            "cross_border": "International remittances, SWIFT wires, FX conversion",
            "cash_atm": "ATM cash withdrawals, cardless ATM payouts, agent cashouts"
        }
    },
    "risk_level": {
        "type": "choice",
        "instructions": "Assess the risk level of this transaction for real-time policy routing.",
        "criteria": {
            "low": "Verified baseline, consistent with normal user financial behavior",
            "medium": "Mild anomaly such as unusual time or slightly elevated ticket size",
            "high": "Multiple risk markers requiring step-up verification or manual triage",
            "critical": "Severe fraud pattern, account takeover, card testing, or mule activity"
        }
    },
    "action": {
        "type": "choice",
        "instructions": "What policy enforcement action should the transaction engine take?",
        "criteria": {
            "auto_approve": "Approve instantly via straight-through processing",
            "step_up_2fa": "Prompt cardholder with mandatory biometric/OTP challenge",
            "manual_review": "Hold transaction for compliance and fraud analyst review",
            "hard_block": "Decline transaction immediately and freeze payment instrument"
        }
    },
    "aml_flag": {
        "type": "noul",
        "instructions": "Does this transaction exhibit anti-money laundering (AML) structuring or suspicious layering?"
    }
}

TEST_CASES = [
    {
        "title": "🛒 Safe UPI Grocery Payment (Bangalore)",
        "state": {
            "transaction_id": "tx_legit_001",
            "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "timezone": "UTC",
            "amount": 845.0,
            "currency": "INR",
            "counterparty": "Blinkit Instant Commerce #821",
            "payment_rail": "mobile_sdk",
            "device_fingerprint": {
                "device_model": "iPhone 15 Pro",
                "is_device_trusted": True,
                "ip_country": "IN",
                "biometric_authenticated": True
            },
            "location": {"city": "Bangalore", "country": "IN", "distance_from_registered_address_km": 1.2}
        }
    },
    {
        "title": "🚨 Mule Layering into Crypto OTC",
        "state": {
            "transaction_id": "tx_mule_992",
            "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "timezone": "UTC",
            "amount": 98500.0,
            "currency": "INR",
            "counterparty": "Unregulated Crypto OTC Desk (Instant USDT Conversion)",
            "payment_rail": "mobile_sdk",
            "flow_type": "mule_layering_drain",
            "device_fingerprint": {
                "device_model": "Linux Kali Headless Tor Client",
                "is_device_trusted": False,
                "ip_country": "SC"
            },
            "location": {"city": "Victoria", "country": "SC", "distance_from_registered_address_km": 4200.0}
        }
    },
    {
        "title": "📱 SIM-Swap Wire Drain",
        "state": {
            "transaction_id": "tx_sim_441",
            "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "timezone": "UTC",
            "amount": 18500.0,
            "currency": "USD",
            "counterparty": "Offshore SWIFT Wire: Panamanian Shell Entity Ltd",
            "payment_rail": "swift_sepa_remittance",
            "flow_type": "sim_swap_wire_drain",
            "device_fingerprint": {
                "device_model": "Motorola Moto G (Fresh IMSI / SIM Change 45 mins ago)",
                "is_device_trusted": False,
                "ip_country": "NG"
            },
            "location": {"city": "Lagos", "country": "NG", "distance_from_registered_address_km": 8800.0}
        }
    },
    {
        "title": "⚖️ AML Structuring Smurf",
        "state": {
            "transaction_id": "tx_smurf_882",
            "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "timezone": "UTC",
            "amount": 49200.0,
            "currency": "INR",
            "counterparty": "P2P Structuring Node: multiple fast payouts",
            "payment_rail": "mobile_sdk",
            "flow_type": "aml_smurfing_structuring",
            "device_fingerprint": {
                "device_model": "Windows 10 Chrome (Residential Proxy Network)",
                "is_device_trusted": False,
                "ip_country": "IN"
            },
            "location": {"city": "Mumbai", "country": "IN", "distance_from_registered_address_km": 4.5}
        }
    }
]

def run_decision(client, model_name: str, test_case: dict):
    print("\n" + "=" * 65)
    print(f"📌 Scenario: {test_case['title']}")
    state = test_case["state"]
    amt_str = f"₹{state['amount']:,.0f}" if state.get("currency") == "INR" else f"${state['amount']:,.2f}"
    print(f"   Amount: {amt_str} | Counterparty: {state.get('counterparty')}")
    print(f"   Calling fine-tuned model: '{model_name}'...")
    print("-" * 65)

    try:
        res = client.system_one(
            state=state,
            questions=QUESTIONS_SCHEMA,
            model=model_name
        )

        fraud_prob = res.nouls["is_fraud"].noul
        action = res.choices["action"].choice
        action_probs = res.choices["action"].probabilities
        category = res.choices["fintech_category"].choice
        cat_probs = res.choices["fintech_category"].probabilities
        risk = res.choices["risk_level"].choice
        aml_prob = res.nouls["aml_flag"].noul

        # Formatted output
        print(f"\n🎯 DECISION VERDICT:")
        if action == "hard_block":
            print(f"   Action:        🚨 DECLINE & HARD BLOCK")
        elif action == "manual_review":
            print(f"   Action:        ⚠️  HOLD FOR MANUAL REVIEW")
        elif action == "step_up_2fa":
            print(f"   Action:        🔒 STEP-UP 2FA / BIOMETRIC CHALLENGE")
        else:
            print(f"   Action:        ✅ AUTO-APPROVE")

        print(f"   Risk Tier:     {risk.upper()}")
        print(f"   Fraud Prob:    {fraud_prob * 100:.1f}%")
        print(f"   Category:      {category} (P={cat_probs.get(category, 0.0) * 100:.1f}%)")
        print(f"   AML Red Flag:  {aml_prob * 100:.1f}%\n")

        print("   Action Probabilities Distribution:")
        for act, p in sorted(action_probs.items(), key=lambda x: x[1], reverse=True):
            bar = "█" * int(p * 25)
            print(f"      {act:<14} {p * 100:5.1f}% | {bar}")

        if hasattr(res, "usage") and res.usage:
            print(f"\n   Tokens Billed: {res.usage.input_tokens} tokens (~${res.usage.input_tokens * 0.00000002:.6f})")

    except Exception as err:
        print(f"❌ Decision call failed: {err}")

def main():
    parser = argparse.ArgumentParser(description="Query your fine-tuned Endor model")
    parser.add_argument("--model", default=MODEL_NAME, help=f"Model ID (default: {MODEL_NAME})")
    parser.add_argument("--fraud", action="store_true", help="Test fraud scenarios")
    parser.add_argument("--legit", action="store_true", help="Test legitimate scenario")
    parser.add_argument("--all", action="store_true", help="Run all test scenarios")

    args = parser.parse_args()

    client = endor.EndorClient()

    if args.legit:
        run_decision(client, args.model, TEST_CASES[0])
    elif args.fraud:
        run_decision(client, args.model, TEST_CASES[1])
        run_decision(client, args.model, TEST_CASES[2])
    elif args.all:
        for tc in TEST_CASES:
            run_decision(client, args.model, tc)
    else:
        # Default: test 1 legit and 1 fraud scenario
        run_decision(client, args.model, TEST_CASES[0])
        run_decision(client, args.model, TEST_CASES[1])

    print("\n" + "=" * 65)
    print("💡 To use this model in your own app:")
    print(f'   res = client.system_one(transaction, questions, model="{args.model}")')
    print("=" * 65)

if __name__ == "__main__":
    main()
