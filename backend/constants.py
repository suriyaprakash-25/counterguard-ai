"""
Application-wide constants.
"""

MAX_CROSS_QUERIES = 5
ESCALATION_THRESHOLD = 70.0


# Investigation Weights
class RiskWeights:
    VERY_LOW_PRICE = 40
    POOR_SELLER = 25
    MISSING_WARRANTY = 10
    POOR_LISTING_QUALITY = 10
    SUSPICIOUS_BRAND = 15


# Core Settings
class Thresholds:
    PRICE_MIN = 10.0
    SELLER_RATING_MIN = 3.0
    MIN_IMAGES = 2
    MIN_DESCRIPTION_LENGTH = 50
    KEYWORD_STUFFING_RATIO = 0.4
    KEYWORD_STUFFING_MIN_WORDS = 20
    VISUAL_SIMILARITY_MIN = 75.0
    VISUAL_SEVERITY_HIGH_MAX = 50.0


# Risk Levels
class RiskLevels:
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


# Risk Scores
class RiskScoreThresholds:
    LOW_MAX = 30
    MEDIUM_MAX = 60
    HIGH_MIN = 80
