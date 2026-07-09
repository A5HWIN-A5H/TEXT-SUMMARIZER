from pydantic import BaseModel, Field
from enum import Enum


class SummaryStyle(str, Enum):
    CONCISE = "concise"
    DETAILED = "detailed"
    BULLET_POINTS = "bullets"
    EXECUTIVE = "executive"
    ACADEMIC = "academic"
    CONTEXT_PRESERVE = "context_preserve"


class SummarizeRequest(BaseModel):
    text: str = Field(..., min_length=50, max_length=10000, description="Text to summarize")
    max_length: int = Field(default=150, ge=50, le=400, description="Maximum summary length in words")
    min_length: int = Field(default=30, ge=20, le=150, description="Minimum summary length in words")
    style: SummaryStyle = Field(default=SummaryStyle.CONCISE, description="Summary writing style")


class SummarizeResponse(BaseModel):
    summary: str
    original_length: int
    summary_length: int
    style: str