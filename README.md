# 🛡️ FinTech Transaction Guardian

> An intelligent transaction fraud detection, policy routing, and category triage engine fine-tuned on Endor's **`jev-9b`** (AutoTrust) and **`kev-9b`** (jaredpalmer) decision models.

---

## 🌟 Highlights

- **Specialized for FinTech**: Covers UPI/P2P instant transfers, B2B SaaS cloud billing, corporate expense cards, BNPL micro-loans, WealthTech/brokerage SIP mandates, cross-border remittances, and card-present ATM withdrawals.
- **Realistic Attack Vectors**: Mule account layering into crypto liquidity pools, automated botnet card testing, SIM-swap wire drains, AML structuring/smurfing under ₹50k / $10k reporting limits, and remote screen-sharing accessibility scams.
- **Endor Decision Models (`jev-9b` & `kev-9b`)**:
  - Calibrated probability outputs ($P(\text{fraud})$, $P(\text{auto\_approve})$, $P(\text{aml})$) for threshold-based policy routing.
  - Constrained JSON decision decoding: zero hallucinations, instant schema conformance.
  - Sub-150ms inference latency at $0.02 - $0.04 per 1M tokens (~50,000 decisions per $1).
- **Interactive Web Dashboard**:
  - **Transaction Inspector**: Instant payload editor with preset fintech scenarios and animated SVG probability gauges.
  - **Live Gateway Stream**: Real-time simulation of incoming payment gateway transactions with live statistics (Total, Auto-Approve %, Fraud Block %, Avg Latency).
  - **Model Benchmark Leaderboard**: Side-by-side comparison of `jev-9b` vs `kev-9b` accuracy, recall, precision, and latency before and after fine-tuning.

---

## 📁 Repository Structure

```text
├── data/
│   ├── train.jsonl          # 240 FinTech training records in Endor schema
│   └── eval.jsonl           # 60 held-out evaluation records in Endor schema
├── generate_data.py         # FinTech dataset generator (India + global rails, UTC timestamps)
├── upload.py                # Endor dataset uploader (train & eval registration)
├── predict.py               # Live CLI model query runner
├── api_server.py            # Dedicated FastAPI inference server (port 8000)
├── guardian.py              # Policy engine & decision router
├── index.html               # Modern dark-mode fintech dashboard
├── style.css                # Glassmorphic CSS styling & micro-animations
├── app.js                   # Reactive UI logic & gateway feed simulator
└── benchmarks.json          # Benchmark metrics comparing jev-9b and kev-9b
```

---

## 🚀 Quickstart

### 1. Launch the FastAPI Dedicated Inference Server
```bash
python3 api_server.py
```
- **API Server & Dashboard**: [http://localhost:8000](http://localhost:8000)
- **Interactive Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Documentation**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### 2. Test Model from the Command Line
```bash
python3 predict.py --all
```

### 2. Upload Data to Endor (with your $100 credit)
Export your Endor API key:
```bash
export ENDOR_API_KEY="your-endor-api-key"
python3 upload.py
```

### 3. Fine-Tune Decision Models on Endor's GPU
```bash
# Fine-tune jev-9b (AutoTrust 9B)
python3 train.py --model jev-9b --epochs 3 --batch-size 8 --rank 16

# Fine-tune kev-9b (jaredpalmer 9B)
python3 train.py --model kev-9b --epochs 3 --batch-size 8 --rank 16

# Benchmark both models sequentially
python3 train.py --all
```

---

## 🎯 Decision Model Schema

Every transaction decision answers 5 simultaneous questions:

| Question Name | Type | Options / Criteria | Purpose |
|---|---|---|---|
| `is_fraud` | `noul` | `true`, `false` | Primary fraud classification |
| `fintech_category` | `choice` | `p2p_transfer`, `card_spend`, `saas_payroll`, `wealth_invest`, `loan_bnpl`, `cross_border`, `cash_atm` | Spend analytics & transaction tagging |
| `risk_level` | `choice` | `low`, `medium`, `high`, `critical` | Risk tier escalation |
| `action` | `choice` | `auto_approve`, `step_up_2fa`, `manual_review`, `hard_block` | Real-time policy enforcement |
| `aml_flag` | `noul` | `true`, `false` | Anti-Money Laundering structuring alert |
