import math

def estimate_narration_time(text: str) -> int:
    """Estimate narration duration in seconds based on word count (≈150 WPM)."""
    words = len(text.split())
    seconds = words / 2.5  # ~150 words per minute
    return math.ceil(seconds)
