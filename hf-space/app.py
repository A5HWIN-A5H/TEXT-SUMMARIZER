import os
import re
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from enum import Enum
from transformers import pipeline

app = FastAPI(title="AI Text Summarizer API", version="1.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SummaryStyle(str, Enum):
    CONCISE = "concise"
    DETAILED = "detailed"
    BULLET_POINTS = "bullets"
    EXECUTIVE = "executive"
    ACADEMIC = "academic"

class SummarizeRequest(BaseModel):
    text: str = Field(..., min_length=50, max_length=10000)
    max_length: int = Field(default=150, ge=50, le=500)
    min_length: int = Field(default=30, ge=10, le=200)
    style: SummaryStyle = Field(default=SummaryStyle.CONCISE)

class SummarizeResponse(BaseModel):
    summary: str
    original_length: int
    summary_length: int
    style: str

STYLE_PROMPTS = {
    "concise": "Summarize the following text in a brief, focused paragraph. Include only the most essential facts and main conclusion:",
    "detailed": "Provide a comprehensive summary of the following text. Include key details, important context, supporting evidence, and main implications:",
    "bullets": "Extract the key points from the following text. Focus on distinct, standalone facts and findings:",
    "executive": "Summarize the following text for executive decision-making. Highlight business impact, strategic importance, actionable outcomes, and key metrics:",
    "academic": "Summarize the following academic text. Preserve the research question, methodology, key findings, and significant citations or dates:",
}

def _format_bullets(text: str) -> str:
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if len(s.strip()) > 10]
    bullets = []
    for sent in sentences:
        clauses = [c.strip() for c in sent.split(', ') if len(c.strip()) > 15]
        if len(clauses) > 1 and len(sent) > 100:
            bullets.extend(clauses)
        else:
            bullets.append(sent)
    return '\n'.join(f'• {b.rstrip(".")}.' for b in bullets if b)

def _format_executive(text: str) -> str:
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
    takeaway = sentences[0] if sentences else "Review full document for details."
    return f"Executive Summary\n\n{text}\n\nKey Takeaway: {takeaway}"

def _format_academic(text: str, original: str) -> str:
    years = sorted(set(re.findall(r'\b(19|20)\d{2}\b', original)))
    header = "Academic Summary"
    if years:
        header += f"\nPeriod: {years[0]}{f'–{years[-1]}' if len(years) > 1 else ''}"
    return f"{header}\n\n{text}"

FORMAT_FUNCS = {
    "concise": lambda t, _: t,
    "detailed": lambda t, _: t,
    "bullets": lambda t, _: _format_bullets(t),
    "executive": lambda t, _: _format_executive(t),
    "academic": lambda t, o: _format_academic(t, o),
}

print("Loading BART model...")
model = pipeline("summarization", model="facebook/bart-large-cnn", device=-1)
print("Model loaded!")

def chunk_text(text: str, max_words: int = 350) -> list:
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    chunks, current_chunk, current_words = [], [], 0
    for sent in sentences:
        w = len(sent.split())
        if current_words + w > max_words and current_chunk:
            chunks.append(' '.join(current_chunk))
            current_chunk, current_words = [sent], w
        else:
            current_chunk.append(sent)
            current_words += w
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    return chunks

def summarize_pass(text: str, max_len: int, min_len: int, prompt: str) -> str:
    styled = f"{prompt}\n\n{text}" if len(text) > 100 else text
    result = model(
        styled,
        max_length=max_len,
        min_length=min_len,
        do_sample=False,
        num_beams=4,
        early_stopping=True,
        truncation=True,
    )
    return result[0]["summary_text"].strip()

@app.get("/")
def health_check():
    return {"status": "ok", "service": "AI Text Summarizer API", "version": "1.1.0"}

@app.post("/summarize", response_model=SummarizeResponse)
def summarize(request: SummarizeRequest):
    try:
        word_count = len(request.text.split())
        if word_count < 20:
            return JSONResponse(status_code=400, content={"detail": "Text too short. Minimum 20 words."})
        if word_count > 2000:
            return JSONResponse(status_code=400, content={"detail": "Text too long. Maximum 2000 words."})
        if request.min_length >= request.max_length:
            return JSONResponse(status_code=400, content={"detail": "min_length must be less than max_length"})

        config = STYLE_PROMPTS.get(request.style.value, STYLE_PROMPTS["concise"])
        formatter = FORMAT_FUNCS.get(request.style.value, lambda t, _: t)

        if word_count <= 400:
            raw = summarize_pass(request.text, request.max_length, request.min_length, config)
            summary_text = formatter(raw, request.text)
        else:
            chunks = chunk_text(request.text)
            num_chunks = len(chunks)
            chunk_max = max(60, min(120, (request.max_length * 2) // num_chunks))
            chunk_min = max(25, request.min_length // num_chunks)
            
            chunk_summaries = []
            for chunk in chunks:
                summary = summarize_pass(chunk, chunk_max, chunk_min, config)
                chunk_summaries.append(summary)
            
            combined = ' '.join(chunk_summaries)
            final_max = request.max_length
            final_min = max(request.min_length, int(final_max * 0.3))
            
            if len(combined.split()) > request.max_length * 0.8:
                final = summarize_pass(combined, final_max, final_min, config)
            else:
                final = combined
            
            summary_text = formatter(final, request.text)

        return SummarizeResponse(
            summary=summary_text,
            original_length=word_count,
            summary_length=len(summary_text.split()),
            style=request.style.value
        )

    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"Summarization failed: {str(e)}"})