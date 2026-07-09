class ValidationError(Exception):
    pass


def validate_text(text: str) -> None:
    if not text or not text.strip():
        raise ValidationError("Text cannot be empty")
    
    word_count = len(text.split())
    if word_count < 50:
        raise ValidationError(f"Text too short. Minimum 50 words required for reliable summarization. Current: {word_count}.")
    
    if word_count > 2000:
        raise ValidationError(f"Text too long. Maximum 2000 words. Current: {word_count}.")


def validate_lengths(min_length: int, max_length: int) -> None:
    if min_length >= max_length:
        raise ValidationError("Min words must be less than max words")