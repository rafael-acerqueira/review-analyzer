from app.core.clients import get_sentiment_pipeline

class SentimentAnalysisService:
    @staticmethod
    def analyze(text: str):
        sentiment_pipeline = get_sentiment_pipeline()
        result = sentiment_pipeline(text)[0]
        return result['label'], result['score']
