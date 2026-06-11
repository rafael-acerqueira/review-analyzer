from app.services.sentiment_analysis_service import SentimentAnalysisService

def test_sentiment_negative(mocker):
    mocker.patch(
        "app.services.sentiment_analysis_service.get_sentiment_pipeline",
        return_value=lambda text: [{"label": "NEGATIVE", "score": 0.99}],
    )

    sentiment, score = SentimentAnalysisService.analyze("The delivery delayed one hour and the food was cold!")
    assert sentiment == "NEGATIVE"
    assert 0.0 <= score <= 1.0

def test_sentiment_positive(mocker):
    mocker.patch(
        "app.services.sentiment_analysis_service.get_sentiment_pipeline",
        return_value=lambda text: [{"label": "POSITIVE", "score": 0.98}],
    )

    sentiment, score = SentimentAnalysisService.analyze("I bought this product two years ago, gave it to my mom, and am now buying another one. It seems to work forever!")
    assert sentiment == "POSITIVE"
    assert 0.0 <= score <= 1.0
