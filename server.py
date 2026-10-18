#!/usr/bin/env python3
"""
FinTech Transaction Guardian - Local HTTP & API Server
Serves the interactive web dashboard and provides JSON endpoints for decision routing,
real-time stream simulation, and benchmark leaderboard data.
"""

import os
import sys
import json
import random
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timezone

# Load .env if present
env_file = Path(".env")
if env_file.exists():
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line.startswith("ENDOR_API_KEY=") and not line.startswith("#"):
            os.environ["ENDOR_API_KEY"] = line.split("=", 1)[1].strip().strip('"').strip("'")

from guardian import TransactionGuardian
import generate_data

guardian = TransactionGuardian()

SAMPLES = [
    {
        "id": "sample_upi_blinkit",
        "title": "🛒 Blinkit Grocery UPI (Bangalore)",
        "type": "legitimate",
        "data": {
            "transaction_id": "tx_upi_88412",
            "timestamp_utc": "2026-10-16T14:32:00Z",
            "timezone": "UTC",
            "user_id": "usr_retail_01",
            "user_segment": "consumer",
            "amount": 845.0,
            "currency": "INR",
            "counterparty": "Blinkit Instant Commerce #821",
            "payment_rail": "mobile_sdk",
            "flow_type": "merchant_authorization",
            "device_fingerprint": {
                "device_model": "iPhone 15 Pro",
                "is_device_trusted": True,
                "ip_country": "IN",
                "device_ip_match": True,
                "biometric_authenticated": True
            },
            "location": {
                "city": "Bangalore",
                "country": "IN",
                "distance_from_registered_address_km": 1.2
            },
            "kyc_aml_status": {
                "kyc_level": "full_verified",
                "account_tenure_days": 430,
                "past_30d_velocity_count": 28,
                "sanctions_watchlist_match": False
            }
        }
    },
    {
        "id": "sample_mule_crypto",
        "title": "🚨 Mule Layering into Crypto OTC",
        "type": "fraud",
        "data": {
            "transaction_id": "tx_mule_99201",
            "timestamp_utc": "2026-10-16T02:18:45Z",
            "timezone": "UTC",
            "user_id": "usr_neo_01",
            "user_segment": "neobank_genz",
            "amount": 98500.0,
            "currency": "INR",
            "counterparty": "Unregulated Crypto OTC Desk (Instant USDT Conversion)",
            "payment_rail": "mobile_sdk",
            "flow_type": "mule_layering_drain",
            "device_fingerprint": {
                "device_model": "Linux Kali Headless Tor Client",
                "is_device_trusted": False,
                "ip_country": "SC",
                "device_ip_match": False,
                "biometric_authenticated": False,
                "suspicious_indicators": ["mule_layering_drain", "Rapid P2P fan-in from 12 distinct UPI IDs in 30 mins"]
            },
            "location": {
                "city": "Victoria",
                "country": "SC",
                "distance_from_registered_address_km": 4200.0
            },
            "kyc_aml_status": {
                "kyc_level": "full_verified",
                "account_tenure_days": 32,
                "past_30d_velocity_count": 48,
                "sanctions_watchlist_match": False
            }
        }
    },
    {
        "id": "sample_saas_aws",
        "title": "☁️ Corporate AWS Cloud Infrastructure",
        "type": "legitimate",
        "data": {
            "transaction_id": "tx_corp_44910",
            "timestamp_utc": "2026-10-16T08:00:00Z",
            "timezone": "UTC",
            "user_id": "usr_smb_01",
            "user_segment": "corporate_smb",
            "amount": 1420.50,
            "currency": "USD",
            "counterparty": "Amazon Web Services (AWS.com)",
            "payment_rail": "ach_automated_clearing",
            "flow_type": "corporate_b2b",
            "device_fingerprint": {
                "device_model": "MacBook Pro M3",
                "is_device_trusted": True,
                "ip_country": "US",
                "device_ip_match": True,
                "biometric_authenticated": True
            },
            "location": {
                "city": "San Francisco",
                "country": "US",
                "distance_from_registered_address_km": 0.4
            },
            "kyc_aml_status": {
                "kyc_level": "full_verified",
                "account_tenure_days": 780,
                "past_30d_velocity_count": 52,
                "sanctions_watchlist_match": False
            }
        }
    },
    {
        "id": "sample_card_testing",
        "title": "🤖 Botnet Card Testing Attack ($1.25)",
        "type": "fraud",
        "data": {
            "transaction_id": "tx_probe_77189",
            "timestamp_utc": "2026-10-16T03:44:12Z",
            "timezone": "UTC",
            "user_id": "usr_retail_03",
            "user_segment": "consumer",
            "amount": 1.25,
            "currency": "USD",
            "counterparty": "Merchant Gateway #9910 Micro-Auth (Card Testing Probe)",
            "payment_rail": "api_integration",
            "flow_type": "card_testing_botnet",
            "device_fingerprint": {
                "device_model": "Automated Python Requests Bot / Scraping Node",
                "is_device_trusted": False,
                "ip_country": "VN",
                "device_ip_match": False,
                "biometric_authenticated": False,
                "suspicious_indicators": ["card_testing_botnet", "45 micro-auth attempts in 120 seconds"]
            },
            "location": {
                "city": "Hanoi",
                "country": "VN",
                "distance_from_registered_address_km": 9200.0
            },
            "kyc_aml_status": {
                "kyc_level": "full_verified",
                "account_tenure_days": 120,
                "past_30d_velocity_count": 89,
                "sanctions_watchlist_match": False
            }
        }
    },
    {
        "id": "sample_sim_swap",
        "title": "📱 SIM-Swap Wire Drain ($18,500)",
        "type": "fraud",
        "data": {
            "transaction_id": "tx_wire_91823",
            "timestamp_utc": "2026-10-16T01:12:09Z",
            "timezone": "UTC",
            "user_id": "usr_smb_02",
            "user_segment": "corporate_smb",
            "amount": 18500.0,
            "currency": "USD",
            "counterparty": "Offshore SWIFT Wire: Panamanian Shell Entity Ltd",
            "payment_rail": "swift_sepa_remittance",
            "flow_type": "sim_swap_wire_drain",
            "device_fingerprint": {
                "device_model": "Motorola Moto G (Fresh IMSI / SIM Change 45 mins ago)",
                "is_device_trusted": False,
                "ip_country": "NG",
                "device_ip_match": False,
                "biometric_authenticated": False,
                "suspicious_indicators": ["sim_swap_wire_drain", "SIM swapped 45 minutes prior to max credit line wire withdrawal"]
            },
            "location": {
                "city": "Lagos",
                "country": "NG",
                "distance_from_registered_address_km": 8800.0
            },
            "kyc_aml_status": {
                "kyc_level": "full_verified",
                "account_tenure_days": 540,
                "past_30d_velocity_count": 15,
                "sanctions_watchlist_match": False
            }
        }
    },
    {
        "id": "sample_aml_structuring",
        "title": "⚖️ AML Structuring Smurf (₹49,200)",
        "type": "aml",
        "data": {
            "transaction_id": "tx_smurf_33890",
            "timestamp_utc": "2026-10-16T19:22:15Z",
            "timezone": "UTC",
            "user_id": "usr_retail_02",
            "user_segment": "consumer",
            "amount": 49200.0,
            "currency": "INR",
            "counterparty": "P2P Structuring Node: multiple fast payouts",
            "payment_rail": "mobile_sdk",
            "flow_type": "aml_smurfing_structuring",
            "device_fingerprint": {
                "device_model": "Windows 10 Chrome (Residential Proxy Network)",
                "is_device_trusted": False,
                "ip_country": "IN",
                "device_ip_match": False,
                "biometric_authenticated": False,
                "suspicious_indicators": ["aml_smurfing_structuring", "3rd transaction in 24 hours pegged just below ₹50,000 AML threshold"]
            },
            "location": {
                "city": "Mumbai",
                "country": "IN",
                "distance_from_registered_address_km": 4.5
            },
            "kyc_aml_status": {
                "kyc_level": "full_verified",
                "account_tenure_days": 180,
                "past_30d_velocity_count": 22,
                "sanctions_watchlist_match": False
            }
        }
    }
]

class GuardianServerHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/status":
            self._handle_status()
        elif path == "/api/samples":
            self._send_json(SAMPLES)
        elif path == "/api/benchmarks":
            self._handle_benchmarks()
        elif path == "/api/stream":
            self._handle_stream()
        else:
            # Default to index.html if root requested
            if path == "/" or path == "":
                self.path = "/index.html"
            return super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/analyze":
            self._handle_analyze()
        elif path == "/api/model-select":
            self._handle_model_select()
        else:
            self.send_error(404, "Endpoint not found")

    def _handle_status(self):
        train_path = Path("data/train.jsonl")
        eval_path = Path("data/eval.jsonl")
        
        train_count = 0
        eval_count = 0
        if train_path.exists():
            with open(train_path, "r", encoding="utf-8") as f:
                train_count = sum(1 for _ in f)
        if eval_path.exists():
            with open(eval_path, "r", encoding="utf-8") as f:
                eval_count = sum(1 for _ in f)

        has_api_key = bool(os.environ.get("ENDOR_API_KEY"))

        status = {
            "project": "fintech-guardian",
            "status": "online",
            "active_model": guardian.model_name,
            "has_endor_api_key": has_api_key,
            "connected_to_endor": guardian.endor_client is not None,
            "base_models": ["jev-9b", "kev-9b"],
            "dataset": {
                "train_rows": train_count,
                "eval_rows": eval_count,
                "schema_questions": 5
            },
            "timestamp_utc": datetime.now(timezone.utc).isoformat()
        }
        self._send_json(status)

    def _handle_benchmarks(self):
        b_path = Path("benchmarks.json")
        if b_path.exists():
            try:
                with open(b_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._send_json(data)
                return
            except Exception:
                pass
        self._send_json({"error": "Benchmarks not yet available."})

    def _handle_stream(self):
        """Simulates one live transaction entering the payment gateway with decision."""
        sample = random.choice(SAMPLES)
        state = dict(sample["data"])
        # Give fresh transaction ID and current UTC timestamp
        seq = random.randint(100000, 999999)
        state["transaction_id"] = f"tx_live_{seq}"
        state["timestamp_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        
        decision = guardian.evaluate(state)
        self._send_json(decision)

    def _handle_analyze(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        try:
            payload = json.loads(body.decode("utf-8"))
            state = payload.get("state", payload)
            result = guardian.evaluate(state)
            self._send_json(result)
        except Exception as e:
            self._send_json({"error": f"Invalid request payload: {str(e)}"}, status=400)

    def _handle_model_select(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        try:
            payload = json.loads(body.decode("utf-8"))
            new_model = payload.get("model", "fintech-guardian/jev-9b-v1")
            guardian.model_name = new_model
            self._send_json({"success": True, "active_model": new_model})
        except Exception as e:
            self._send_json({"error": str(e)}, status=400)

    def _send_json(self, data, status=200):
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

def run(port: int = 8080):
    server_address = ("", port)
    httpd = HTTPServer(server_address, GuardianServerHandler)
    print("=" * 60)
    print("🛡️  FinTech Transaction Guardian - Web Server Running")
    print(f"👉 Local UI: http://localhost:{port}")
    print(f"👉 API Endpoints: /api/status, /api/analyze, /api/benchmarks, /api/stream")
    print("=" * 60)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
        httpd.server_close()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run(port)
