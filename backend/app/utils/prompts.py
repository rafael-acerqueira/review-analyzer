def suggestion_prompt_template(review_text: str) -> str:
    return f"""
You are an expert in evaluating product reviews.

Your task is to analyze the text of a review written by a user and classify whether it should be accepted or rejected, following the criteria below:

Criteria for Accepting:
- The review is clear, specific, and useful for other buyers.
- Contains at least 20 words.
- Describes a specific experience with the product.

Criteria for Rejecting:
- It is too short, generic, or uninformative.
- Contains fewer than 20 words or vague terms such as "good", "bad", "nice".

Respond ONLY with a valid JSON object like this — no labels, no markdown, no explanations:

{{
  "status": "Accepted" or "Rejected",
  "feedback": "Short and clear message to the user",
  "suggestion": "Suggestion on how to improve the review, if applicable. If the review is accepted, leave this field as an empty string."
}}

Example expected response:

{{
  "status": "Rejected",
  "feedback": "Your review is too generic. Please provide more details.",
  "suggestion": "Explain what exactly you didn't like and how the product could be improved."
}}

DO NOT include the word "json", do NOT wrap the output in triple backticks, and do NOT explain anything.

Now rate the following review:

\"\"\"{review_text}\"\"\"
"""