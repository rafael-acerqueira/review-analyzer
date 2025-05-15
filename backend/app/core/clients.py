from pyexpat.errors import messages

from transformers import pipeline
import openai
import os

sentiment_pipeline = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

openai.api_key = os.getenv("OPENAI_API_KEY")

def call_llm(prompt: str) -> str:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an expert in evaluating reviews."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=150,
        temperature=0.3
    )
    return response['choices'][0]['message']['content']