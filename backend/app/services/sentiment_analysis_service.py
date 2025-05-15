from app.core.clients import sentiment_pipeline

class SentimentAnalysisService:
    @staticmethod
    def analyze(text: str):
        result = sentiment_pipeline(text[0])
        return result['label'], result['score']