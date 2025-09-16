from app.utils.prompts import suggestion_prompt_template
from app.core.clients import call_llm
from app.services.retriever import search_similar_reviews
import json
import re


def _render_examples_block(hits: list[dict]) -> str:
    lines = []
    for h in hits[:5]:
        snippet = (h.get("text") or "").replace("\n", " ").strip()[:400]
        lines.append(f'[ID={h["id"]} | score={h["score"]:.2f}]\n"{snippet}"')
    return "\n\n".join(lines) if lines else "EXAMPLE_NOT_FIND"

class SuggestionService:
    @staticmethod
    def evaluate_review(text: str, session, k: int=5, min_score: float=0.7):

        hits = search_similar_reviews(session=session, query_text=text, k=k, min_score=min_score)
        examples_block = _render_examples_block(hits)

        prompt = suggestion_prompt_template(review_text=text, examples_block=examples_block)
        response = call_llm(prompt)

        try:
            cleaned_response = re.sub("```|json", "", response, flags=re.IGNORECASE)
            return json.loads(cleaned_response)
        except json.JSONDecodeError:
            return {
                "status": "Reject",
                "feedback": "Unexpected response from AI. Check your review"
            }