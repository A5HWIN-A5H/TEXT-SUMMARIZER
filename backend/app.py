from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from schemas import SummarizeRequest, SummarizeResponse
from summarizer import get_summarizer
from validators import validate_text, validate_lengths, ValidationError

app = FastAPI(
    title="AI Text Summarizer",
    description="BART-powered text summarization API with multiple styles",
    version="1.1.0"
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
    return {"status": "ok", "service": "AI Text Summarizer", "version": "1.1.0"}


@app.post("/summarize", response_model=SummarizeResponse)
def summarize(request: SummarizeRequest):
    try:
        validate_text(request.text)
        validate_lengths(request.min_length, request.max_length)

        summarizer = get_summarizer()
        summary_text = summarizer.summarize(
            request.text,
            max_length=request.max_length,
            min_length=request.min_length,
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