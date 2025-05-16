from dotenv import load_dotenv
from transformers import pipeline
from huggingface_hub import InferenceClient
from functools import lru_cache
import os

load_dotenv()

sentiment_pipeline = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

HF_TOKEN = os.getenv("HF_TOKEN")
HF_MODEL = "microsoft/phi-4"



client = InferenceClient(
    provider="hf-inference",
    api_key=HF_TOKEN,
)

@lru_cache(maxsize=128)
def call_llm(user_prompt: str) -> str:
    try:
        completion = client.chat.completions.create(
            model=HF_MODEL,
            messages=[{"role": "user", "content": user_prompt}],
            temperature=0.3,
            max_tokens=150,
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"[LLM ERROR] {e}")
        return '{"status": "Rejected", "feedback": "AI error", "suggestion": ""}'