def suggestion_prompt_template(review_text: str, examples_block: str) -> str:
    return f"""
    You are an expert in evaluating product reviews.
    Follow these rules strictly:
    - Do NOT invent facts; use ONLY the user's draft and the APPROVED EXAMPLES provided.
    - If information is missing in the draft, ask the user to include it (in the feedback).
    - Output MUST be a single valid JSON object (no markdown fences, no extra text).

    Acceptance Criteria:
    - Clear, specific, useful for other buyers.
    - At least 20 words.
    - Describes a specific experience with the product.

    Rejection Criteria:
    - Too short, generic, or uninformative.
    - Fewer than 20 words or vague terms like "good", "bad", "nice".

    USER DRAFT:
    ---
    {review_text}
    ---

    APPROVED EXAMPLES (from my database):
    {examples_block}

    TASK:
    1) Classify as "Accepted" or "Rejected" with a short reason.
    2) If rejected, list what is missing (bullets) and provide an improved suggestion WITHOUT adding facts not present in the draft.
    3) Cite the example IDs you leveraged (if any).

    Respond ONLY with JSON in this shape:
    {{
      "status": "Accepted" or "Rejected",
      "feedback": "Short and clear message to the user",
      "suggestion": "Improved rewrite if rejected, else empty string",
      "examples_used": ["75","62"]  // IDs you relied on; empty if none
    }}
    """