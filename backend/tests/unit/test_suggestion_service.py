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

    result = SuggestionService.evaluate_review("Bad")
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
    result = SuggestionService.evaluate_review("Amazing product, battery lasted 3 days.")
    assert result["status"] == "Accepted"
    assert result["suggestion"] == ""