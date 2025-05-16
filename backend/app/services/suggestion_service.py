from app.utils.prompts import suggestion_prompt_template
from app.core.clients import call_llm
import json
import re


class SuggestionService:
    @staticmethod
    def evaluate_review(text: str):
        prompt = suggestion_prompt_template(text)
        response = call_llm(prompt)

        try:
            cleaned_response = re.sub("```|json", "", response)
            return json.loads(cleaned_response)
        except json.JSONDecodeError:
            return {
                "status": "Reject",
                "feedback": "Unexpected response from AI. Check your review"
            }