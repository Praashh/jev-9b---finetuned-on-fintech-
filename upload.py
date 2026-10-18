import os
import sys
from pathlib import Path
import endor

# 1. Load API key from .env file if present (takes priority over stale shell variables)
env_file = Path(".env")
if env_file.exists():
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line.startswith("ENDOR_API_KEY=") and not line.startswith("#"):
            val = line.split("=", 1)[1].strip().strip('"').strip("'")
            if val:
                os.environ["ENDOR_API_KEY"] = val

# 2. Check active key
active_key = os.environ.get("ENDOR_API_KEY", "").strip()
if not active_key:
    print("\n⚠️  ENDOR_API_KEY is not set.")
    try:
        key = input("Enter your Endor API Key (starts with edk_): ").strip()
        if key:
            os.environ["ENDOR_API_KEY"] = key
            with open(".env", "w") as f:
                f.write(f'ENDOR_API_KEY="{key}"\n')
            active_key = key
            print("Saved to .env.\n")
        else:
            print("Error: API key is required.")
            sys.exit(1)
    except (EOFError, KeyboardInterrupt):
        print("\nAborted.")
        sys.exit(1)

masked = active_key[:8] + "..." + active_key[-4:] if len(active_key) > 12 else "***"
print(f"🔑 Authenticating with key: {masked}")

# Connect to Endor
client = endor.EndorClient()

# Get or create project with jev-9b and kev-9b base models
project = client.projects.get_or_create("default", base_models=["jev-9b", "kev-9b"])
print(f"Project: {project.name}")

# Upload training dataset
train_rows = endor.data.load_rows("data/train.jsonl")
info = project.datasets.upload("train", train_rows)
print(f"Uploaded 'train': {info.n_rows} rows | Question types: {info.question_types}")

# Upload held-out evaluation dataset
eval_rows = endor.data.load_rows("data/eval.jsonl")
eval_info = project.datasets.upload("eval", eval_rows)
print(f"Uploaded 'eval': {eval_info.n_rows} rows | Question types: {eval_info.question_types}")
