class InvalidReview(Exception):
    pass

class Forbidden(Exception):
    pass

class ReviewNotFound(Exception):
    pass

__all__ = ["InvalidReview", "Forbidden", "ReviewNotFound"]
