# app/core/config.py
import os
from dotenv import load_dotenv
from pathlib import Path

# Force .env to load from the root directory
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path)

ANTHROPIC_KEY = os.getenv("ANTHROPIC_KEY")

if ANTHROPIC_KEY is None:
    raise ValueError("❌ ANTHROPIC_KEY is not set in .env or environment variables!")