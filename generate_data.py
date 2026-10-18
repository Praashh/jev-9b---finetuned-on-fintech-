#!/usr/bin/env python3
"""
FinTech Transaction Guardian - Dataset Generator
Specifically tailored for FinTech Neobanks, Card Issuers, Wallets, and Payment Gateways.

Generates realistic FinTech transaction records covering:
  - Neobanking & Wallets (UPI, P2P, split-bills, salary direct deposits)
  - BNPL & Lending (affirm/simpl installments, micro-credit drawdowns, EMI autopay)
  - Corporate Expense Cards (AWS/GCP cloud billing, SaaS subscriptions, vendor wires)
  - WealthTech & Investments (Brokerage deposits, Mutual fund SIPs, Crypto on/off ramp)
  - FinTech-Specific Fraud Vectors:
      * Mule Account Layering (rapid P2P in -> crypto/cash out)
      * Card Testing Attack (bot-driven micro-authorizations)
      * SIM-Swap / Account Hijacking (biometric change followed by instant max wire)
      * Synthetic Identity Bustout (maxing out newly issued credit line)
      * AML Structuring / Smurfing (transfers just under ₹50k or $10k thresholds)
      * Remote Access / Refund Social Engineering scam

Compatible with Endor's jev-9b and kev-9b decision models.
"""

import json
import os
import random
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Tuple

random.seed(42)

os.makedirs("data", exist_ok=True)

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

FINTECH_PROFILES = [
    {"user_id": "usr_retail_01", "tier": "consumer", "currency": "INR", "country": "IN", "city": "Bangalore", "avg_monthly_vol": 65000, "trusted_device": "iPhone 15 Pro", "primary_channel": "mobile_app"},
    {"user_id": "usr_retail_02", "tier": "consumer", "currency": "INR", "country": "IN", "city": "Mumbai", "avg_monthly_vol": 95000, "trusted_device": "Samsung Galaxy S24", "primary_channel": "mobile_app"},
    {"user_id": "usr_retail_03", "tier": "consumer", "currency": "INR", "country": "IN", "city": "Delhi", "avg_monthly_vol": 45000, "trusted_device": "OnePlus 12", "primary_channel": "mobile_app"},
    {"user_id": "usr_smb_01", "tier": "corporate_smb", "currency": "USD", "country": "US", "city": "San Francisco", "avg_monthly_vol": 42000, "trusted_device": "MacBook Pro M3", "primary_channel": "web_dashboard"},
    {"user_id": "usr_smb_02", "tier": "corporate_smb", "currency": "USD", "country": "US", "city": "New York", "avg_monthly_vol": 85000, "trusted_device": "MacBook Air M2", "primary_channel": "api_integration"},
    {"user_id": "usr_freelance_01", "tier": "freelancer", "currency": "USD", "country": "IN", "city": "Hyderabad", "avg_monthly_vol": 4500, "trusted_device": "ThinkPad X1 Carbon", "primary_channel": "web_dashboard"},
    {"user_id": "usr_hni_01", "tier": "wealth_hni", "currency": "USD", "country": "GB", "city": "London", "avg_monthly_vol": 120000, "trusted_device": "iPhone 15 Pro Max", "primary_channel": "mobile_app"},
    {"user_id": "usr_neo_01", "tier": "neobank_genz", "currency": "INR", "country": "IN", "city": "Pune", "avg_monthly_vol": 28000, "trusted_device": "Pixel 8", "primary_channel": "mobile_app"}
]

def generate_legit_fintech_tx(seq_id: int) -> Dict[str, Any]:
    profile = random.choice(FINTECH_PROFILES)
    category = random.choices(
        ["p2p_transfer", "card_spend", "saas_payroll", "wealth_invest", "loan_bnpl", "cross_border", "cash_atm"],
        weights=[30, 25, 12, 12, 10, 7, 4]
    )[0]
    
    curr = profile["currency"]
    mult = 83.0 if curr == "INR" else 1.0
    
    if category == "p2p_transfer":
        if curr == "INR":
            merchant = random.choice(["UPI: rahul_sharma@okaxis", "UPI: priya.patel@okhdfcbank", "PhonePe Split Bill #482", "Google Pay P2P Transfer", "Paytm Money Request"])
            amount = round(random.uniform(150, 4500), 0)
        else:
            merchant = random.choice(["Venmo: @alex-miller-21", "Zelle: payment to Sarah Jenkins", "Cash App: $dave_designs", "Revolut P2P Vault Split"])
            amount = round(random.uniform(15, 250), 2)
        channel = "mobile_sdk"
        flow_type = "instant_debit"

    elif category == "card_spend":
        if curr == "INR":
            merchant = random.choice(["Blinkit Instant Commerce #821", "Swiggy Food Gourmet", "Zepto Groceries Koramangala", "Flipkart Wholesale Pvt Ltd", "Myntra Fashion E-retail"])
            amount = round(random.uniform(250, 6500), 0)
        else:
            merchant = random.choice(["Amazon Business Prime", "Target Stores #0881", "Trader Joe's Supermarket", "Uber Technologies Inc", "DoorDash Food Delivery"])
            amount = round(random.uniform(18, 220), 2)
        channel = "card_not_present_3ds"
        flow_type = "merchant_authorization"

    elif category == "saas_payroll":
        if curr == "INR":
            merchant = random.choice(["RazorpayX Payroll Direct Credit", "AWS Cloud Services India", "Google Workspace India Billing", "Zoho One Annual Enterprise", "Slack Technologies UK"])
            amount = round(random.uniform(12000, 185000), 0)
        else:
            merchant = random.choice(["Amazon Web Services (AWS.com)", "Google Cloud Platform Services", "GitHub Enterprise Seats", "Stripe Billing Recurring Fee", "Datadog Cloud Monitoring"])
            amount = round(random.uniform(250, 4800), 2)
        channel = "ach_automated_clearing"
        flow_type = "corporate_b2b"

    elif category == "wealth_invest":
        if curr == "INR":
            merchant = random.choice(["Zerodha Broking Limited (Funds Deposit)", "Groww Mutual Fund Auto-SIP Mandate", "CoinDCX Compliant Crypto On-ramp", "HDFC Mid-Cap Opportunities SIP", "CRED Mint P2P Lending Investment"])
            amount = round(random.uniform(2000, 45000), 0)
        else:
            merchant = random.choice(["Robinhood Financial Margin Deposit", "Vanguard Total Stock Index Auto-Invest", "Interactive Brokers Wire Inbound", "Fidelity Institutional Sweep"])
            amount = round(random.uniform(200, 5000), 2)
        channel = "nach_direct_debit" if curr == "INR" else "fedwire_deposit"
        flow_type = "securities_funding"

    elif category == "loan_bnpl":
        if curr == "INR":
            merchant = random.choice(["Simpl PayLater 15-Day Auto-Repayment", "LazyPay BNPL Installment 2/3", "Slice Credit Card Repayment via UPI", "Bajaj Finserv Consumer EMI Mandate"])
            amount = round(random.uniform(950, 18500), 0)
        else:
            merchant = random.choice(["Affirm Monthly Installment (Peloton)", "Klarna Pay-in-4 Settlement", "Afterpay Auto-debit Installment 3", "Upstart Personal Loan EMI"])
            amount = round(random.uniform(45, 380), 2)
        channel = "recurring_standing_order"
        flow_type = "credit_repayment"

    elif category == "cross_border":
        if curr == "INR":
            merchant = random.choice(["Wise Inward Remittance (Client Invoice)", "Remitly US-to-India Family Support", "Western Union Digital Payout", "Payoneer Freelance USD to INR Settlement"])
            amount = round(random.uniform(15000, 120000), 0)
        else:
            merchant = random.choice(["Wise Cross-Border Wire to UK", "SWIFT Wire: Supplier Payment Germany", "OFX Global Currency Exchange", "Mercury Treasury FX Transfer"])
            amount = round(random.uniform(850, 9500), 2)
        channel = "swift_sepa_remittance"
        flow_type = "cross_border_fx"

    else:  # cash_atm
        if curr == "INR":
            merchant = random.choice(["HDFC Bank ATM Indiranagar (Biometric PIN)", "ICICI Bank ATM Bandra West", "State Bank of India ATM (EMV Chip)", "Kotak Mahindra ATM Koramangala"])
            amount = round(random.uniform(1000, 10000), 0)
        else:
            merchant = random.choice(["Chase Bank ATM #482 (Cardless Apple Pay)", "Bank of America Branch ATM", "Wells Fargo Downtown ATM"])
            amount = round(random.uniform(40, 400), 2)
        channel = "card_present_emv_chip"
        flow_type = "atm_withdrawal"

    # Generate realistic UTC timestamp within the past 7 days
    base_utc = datetime.now(timezone.utc) - timedelta(
        days=random.randint(0, 7),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
        seconds=random.randint(0, 59)
    )
    timestamp_utc_str = base_utc.strftime("%Y-%m-%dT%H:%M:%SZ")

    # Realistic risk variation for normal transactions
    is_slightly_large = amount > (profile["avg_monthly_vol"] * 0.4)
    risk = "medium" if is_slightly_large else "low"
    action = "step_up_2fa" if (is_slightly_large and category in ["cross_border", "p2p_transfer"]) else "auto_approve"

    state = {
        "transaction_id": f"tx_fintech_{seq_id:06d}",
        "timestamp_utc": timestamp_utc_str,
        "timezone": "UTC",
        "user_id": profile["user_id"],
        "user_segment": profile["tier"],
        "amount": amount,
        "currency": curr,
        "counterparty": merchant,
        "payment_rail": channel,
        "flow_type": flow_type,
        "device_fingerprint": {
            "device_model": profile["trusted_device"],
            "is_device_trusted": True,
            "ip_country": profile["country"],
            "device_ip_match": True,
            "biometric_authenticated": True if channel in ["mobile_sdk", "card_present_emv_chip"] else False
        },
        "location": {
            "city": profile["city"],
            "country": profile["country"],
            "distance_from_registered_address_km": round(random.uniform(0.5, 4.5), 1)
        },
        "kyc_aml_status": {
            "kyc_level": "full_verified",
            "account_tenure_days": random.randint(180, 1200),
            "past_30d_velocity_count": random.randint(14, 65),
            "sanctions_watchlist_match": False
        }
    }

    return {
        "id": f"ft-row-{seq_id:05d}",
        "state": state,
        "questions": QUESTIONS_SCHEMA,
        "labels": {
            "is_fraud": False,
            "fintech_category": category,
            "risk_level": risk,
            "action": action,
            "aml_flag": False
        }
    }

def generate_fraud_fintech_tx(seq_id: int) -> Dict[str, Any]:
    profile = random.choice(FINTECH_PROFILES)
    fraud_pattern = random.choice([
        "mule_layering_drain",
        "card_testing_botnet",
        "sim_swap_wire_drain",
        "synthetic_id_bustout",
        "aml_smurfing_structuring",
        "remote_access_scam"
    ])

    curr = profile["currency"]
    # Generate realistic UTC timestamp within the past 48 hours for fraud alerts
    base_utc = datetime.now(timezone.utc) - timedelta(
        days=random.randint(0, 2),
        hours=random.choice([0, 1, 2, 3, 4, 23]), # night-time UTC attack spikes
        minutes=random.randint(0, 59),
        seconds=random.randint(0, 59)
    )
    timestamp_utc_str = base_utc.strftime("%Y-%m-%dT%H:%M:%SZ")

    if fraud_pattern == "mule_layering_drain":
        category = "wealth_invest" if random.random() > 0.5 else "p2p_transfer"
        counterparty = "Unregulated Crypto OTC Desk (Instant USDT Conversion)"
        amount = 98500.0 if curr == "INR" else 4850.0
        risk = "critical"
        action = "hard_block"
        aml = True
        device = "Linux Kali Headless Tor Client"
        ip_country = "SC" # Seychelles
        notes = "Rapid P2P fan-in from 12 distinct UPI IDs in 30 mins, immediately routed to crypto liquidity pool"

    elif fraud_pattern == "card_testing_botnet":
        category = "card_spend"
        counterparty = "Merchant Gateway #9910 Micro-Auth (Card Testing Probe)"
        amount = 75.0 if curr == "INR" else 1.25
        risk = "critical"
        action = "hard_block"
        aml = False
        device = "Automated Python Requests Bot / Scraping Node"
        ip_country = "VN"
        notes = "45 micro-auth attempts in 120 seconds across sequential CVVs"

    elif fraud_pattern == "sim_swap_wire_drain":
        category = "cross_border"
        counterparty = "Offshore SWIFT Wire: Panamanian Shell Entity Ltd"
        amount = 450000.0 if curr == "INR" else 18500.0
        risk = "critical"
        action = "hard_block"
        aml = True
        device = "Motorola Moto G (Fresh IMSI / SIM Change 45 mins ago)"
        ip_country = "NG"
        notes = "SIM swapped 45 minutes prior to max credit line wire withdrawal"

    elif fraud_pattern == "synthetic_id_bustout":
        category = "loan_bnpl"
        counterparty = "High-End Electronics BNPL Merchant (Instant Cashout)"
        amount = 145000.0 if curr == "INR" else 3500.0
        risk = "high"
        action = "manual_review"
        aml = False
        device = "Samsung Galaxy S20 (Factory Reset Detected)"
        ip_country = profile["country"]
        notes = "Newly approved line exhausted within 6 hours of account creation"

    elif fraud_pattern == "aml_smurfing_structuring":
        category = "p2p_transfer"
        # Structuring right below regulatory reporting limit (₹50,000 in India, $10,000 in US)
        counterparty = "P2P Structuring Node: multiple fast payouts"
        amount = 49200.0 if curr == "INR" else 9800.0
        risk = "critical"
        action = "manual_review"
        aml = True
        device = "Windows 10 Chrome (Residential Proxy Network)"
        ip_country = profile["country"]
        notes = "3rd transaction in 24 hours pegged just $200 below mandatory AML cash reporting threshold"

    else:  # remote_access_scam
        category = "p2p_transfer"
        counterparty = "Fraudulent VPA / Remote Screen Drain (helpdesk_support@vpa)"
        amount = 75000.0 if curr == "INR" else 1800.0
        risk = "critical"
        action = "hard_block"
        aml = False
        device = "Android Device running TeamViewer QuickSupport / AnyDesk"
        ip_country = profile["country"]
        notes = "Active screen-sharing accessibility service running during transaction PIN input"

    state = {
        "transaction_id": f"tx_fintech_alert_{seq_id:06d}",
        "timestamp_utc": timestamp_utc_str,
        "timezone": "UTC",
        "user_id": profile["user_id"],
        "user_segment": profile["tier"],
        "amount": amount,
        "currency": curr,
        "counterparty": counterparty,
        "payment_rail": "api_integration" if "Bot" in device else "mobile_sdk",
        "flow_type": fraud_pattern,
        "device_fingerprint": {
            "device_model": device,
            "is_device_trusted": False,
            "ip_country": ip_country,
            "device_ip_match": False,
            "biometric_authenticated": False,
            "suspicious_indicators": [fraud_pattern, notes]
        },
        "location": {
            "city": "Unknown / Proxied",
            "country": ip_country,
            "distance_from_registered_address_km": 8500.0
        },
        "kyc_aml_status": {
            "kyc_level": "tier_1_restricted" if fraud_pattern == "synthetic_id_bustout" else "full_verified",
            "account_tenure_days": 4 if fraud_pattern == "synthetic_id_bustout" else random.randint(30, 450),
            "past_30d_velocity_count": 89 if "botnet" in fraud_pattern else 5,
            "sanctions_watchlist_match": False
        }
    }

    return {
        "id": f"ft-row-{seq_id:05d}",
        "state": state,
        "questions": QUESTIONS_SCHEMA,
        "labels": {
            "is_fraud": True,
            "fintech_category": category,
            "risk_level": risk,
            "action": action,
            "aml_flag": aml
        }
    }

def generate_fintech_dataset(total_rows: int = 300, fraud_ratio: float = 0.22) -> Tuple[List[Dict], List[Dict]]:
    n_fraud = int(total_rows * fraud_ratio)
    n_legit = total_rows - n_fraud
    
    rows = []
    for i in range(1, n_legit + 1):
        rows.append(generate_legit_fintech_tx(i))
    for i in range(n_legit + 1, total_rows + 1):
        rows.append(generate_fraud_fintech_tx(i))
        
    random.shuffle(rows)
    split_point = int(total_rows * 0.8) # 240 train, 60 eval
    return rows[:split_point], rows[split_point:]

def main():
    print("🏦 Generating Specialized FinTech Guardian Dataset...")
    train_rows, eval_rows = generate_fintech_dataset(300, 0.22)
    
    train_file = "data/train.jsonl"
    eval_file = "data/eval.jsonl"
    
    with open(train_file, "w", encoding="utf-8") as f:
        for r in train_rows:
            f.write(json.dumps(r) + "\n")
            
    with open(eval_file, "w", encoding="utf-8") as f:
        for r in eval_rows:
            f.write(json.dumps(r) + "\n")
            
    print(f"✨ Written {len(train_rows)} FinTech training rows to {train_file}")
    print(f"✨ Written {len(eval_rows)} FinTech evaluation rows to {eval_file}")

if __name__ == "__main__":
    main()
