import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(Path(__file__).resolve().parent / ".env")

MODEL = os.getenv("OPENAI_MODEL", "").strip()

if not MODEL:
    raise RuntimeError("請設定 OPENAI_MODEL")

client = OpenAI()

VECTOR_STORE_ID = os.getenv("VECTOR_STORE_ID", "").strip()