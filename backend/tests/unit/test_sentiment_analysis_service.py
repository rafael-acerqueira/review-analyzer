from app.services.sentiment_analysis_service import SentimentAnalysisService

def test_sentiment_negative():
    sentiment, score = SentimentAnalysisService.analyze("The delivery delayed one hour and the food was cold!")
    assert sentiment == "NEGATIVE"
    assert 0.0 <= score <= 1.0

def test_sentiment_positive():
    sentiment, score = SentimentAnalysisService.analyze("I bought this product two years ago, gave it to my mom, and am now buying another one. It seems to work forever!")
    assert sentiment == "POSITIVE"
    assert 0.0 <= score <= 1.0