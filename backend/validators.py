class ValidationError(Exception):
    pass


def validate_text(text: str) -> None:
    if not text or not text.strip():
        raise ValidationError("Text cannot be empty")
    
    word_count = len(text.split())
    if word_count < 20:
        raise ValidationError(f"Text too short. Minimum 20 words, got {word_count}.")
    
    if word_count > 2000:
        raise ValidationError(f"Text too long. Maximum 2000 words, got {word_count}.")


def validate_lengths(min_length: int, max_length: int) -> None:
    if min_length >= max_length:
        raise ValidationError("min_length must be less than max_length")