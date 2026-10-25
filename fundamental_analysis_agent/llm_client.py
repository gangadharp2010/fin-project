"""One reusable OpenAI client, bounded timeout, and SDK retries."""
import os
from functools import lru_cache
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

SYSTEM_RULES = """Use only supplied evidence. Never invent facts, financial values, dates,
news, peer metrics, or citations. For missing facts, write exactly:
'Cannot be confirmed from available information.' Separate reported facts from assumptions.
Educational research only, not personalized financial advice."""

@lru_cache(maxsize=1)
def get_client() -> OpenAI:
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY is not configured in .env")
    timeout = float(os.getenv("OPENAI_TIMEOUT_SECONDS", "45"))
    retries = int(os.getenv("OPENAI_MAX_RETRIES", "2"))
    return OpenAI(api_key=key, timeout=timeout, max_retries=retries)

def ask_llm(task: str, payload: str, *, model: str | None = None) -> str:
    client = get_client()
    response = client.responses.create(
        model=model or os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        input=[
            {"role": "system", "content": SYSTEM_RULES + "\n" + task},
            {"role": "user", "content": payload},
        ],
    )
    return response.output_text
