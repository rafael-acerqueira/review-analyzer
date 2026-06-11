from app.services.suggestion_service import SuggestionService
from unittest.mock import patch

@patch("app.services.suggestion_service.call_llm")
def test_review_reject(mock_call_llm):
    mock_call_llm.return_value = '''
    {
      "status": "Rejected",
      "feedback": "Too vague.",
      "suggestion": "Add more details."
    }
    '''

    svc = SuggestionService()
    result = svc.evaluate(text="Bad")
    assert result["status"] == "Rejected"
    assert result["feedback"]
    assert result["suggestion"]

@patch("app.services.suggestion_service.call_llm")
def test_review_accepted(mock_call_llm):
    mock_call_llm.return_value = '''
    {
      "status": "Accepted",
      "feedback": "Thanks for your review!",
      "suggestion": ""
    }
    '''
    svc = SuggestionService()

    result = svc.evaluate(text="Amazing product, battery lasted 3 days.")
    assert result["status"] == "Accepted"
    assert result["suggestion"] == ""

@patch("app.services.suggestion_service.call_llm")
def test_review_parses_json_inside_markdown_block(mock_call_llm):
    mock_call_llm.return_value = '''
    Here is the evaluation:

    ```json
    {
      "status": "Rejected",
      "feedback": "Add details about the product experience.",
      "suggestion": "The phone battery drained quickly during my workday."
    }
    ```
    '''

    svc = SuggestionService()
    result = svc.evaluate(text="Battery bad")

    assert result["status"] == "Rejected"
    assert result["feedback"] == "Add details about the product experience."
    assert result["suggestion"] == "The phone battery drained quickly during my workday."

@patch("app.services.suggestion_service.call_llm")
def test_review_normalizes_llm_status(mock_call_llm):
    mock_call_llm.return_value = '''
    {
      "status": "accepted",
      "feedback": "Clear and specific.",
      "suggestion": ""
    }
    '''

    svc = SuggestionService()
    result = svc.evaluate(text="The battery lasted all day and the screen remained bright outdoors.")

    assert result["status"] == "Accepted"
    assert result["suggestion"] == ""

@patch("app.services.suggestion_service.call_llm")
def test_review_normalizes_llm_text_fields(mock_call_llm):
    long_feedback = "x" * 250
    mock_call_llm.return_value = f'''
    {{
      "status": "Rejected",
      "feedback": "{long_feedback}",
      "suggestion": {{"text": "Add details about battery life."}}
    }}
    '''

    svc = SuggestionService()
    result = svc.evaluate(text="Battery bad")

    assert result["status"] == "Rejected"
    assert len(result["feedback"]) == 200
    assert result["suggestion"] == '{"text": "Add details about battery life."}'
