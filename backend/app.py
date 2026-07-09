from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from schemas import SummarizeRequest, SummarizeResponse
from summarizer import get_summarizer
from validators import validate_text, validate_lengths, ValidationError

app = FastAPI(
    title="AI Text Summarizer",
    description="BART-powered text summarization API with multiple styles",
    version="1.2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    return {"status": "ok", "service": "AI Text Summarizer", "version": "1.2.0"}


@app.post("/summarize", response_model=SummarizeResponse)
def summarize(request: SummarizeRequest):
    try:
        validate_text(request.text)
        
        # Convert words to tokens for BART (1 word ≈ 1.33 tokens)
        token_max = int(request.max_length * 1.33)
        token_min = int(request.min_length * 1.33)
        
        # Ensure valid token ranges
        token_max = min(500, max(50, token_max))
        token_min = min(200, max(10, token_min))
        
        if token_min >= token_max:
            token_min = max(10, token_max - 20)
        
        validate_lengths(token_min, token_max)

        summarizer = get_summarizer()
        summary_text = summarizer.summarize(
            request.text,
            max_length=token_max,
            min_length=token_min,
            style=request.style.value
        )

        return SummarizeResponse(
            summary=summary_text,
            original_length=len(request.text.split()),
            summary_length=len(summary_text.split()),
            style=request.style.value
        )

    except ValidationError as e:
        return JSONResponse(status_code=400, content={"detail": str(e)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"Summarization failed: {str(e)}"})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)