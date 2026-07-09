# TEXT-SUMMARIZER

## Overview

`TEXT-SUMMARIZER` is a full-stack web application for generating natural-language summaries from long text. It includes:

- A Python FastAPI backend that runs a Hugging Face BART summarization model.
- A React frontend that gathers user input, selects summary options, and displays the generated output.

The backend performs text validation, length normalization, chunking for long documents, and multi-style output formatting. The frontend uses a clean interface to make summarization accessible to non-technical users.

---

## Repository structure

```
backend/
  app.py
  requirements.txt
  schemas.py
  summarizer.py
  validators.py
frontend/
  package.json
  README.md
  public/
    index.html
  src/
    App.jsx
    App.module.css
    index.css
    index.js
    components/
      Header/
      LoadingSpinner/
      SummaryOutput/
      TextInput/
    hooks/
      useSummarizer.js
    services/
      api.js
    utils/
      helpers.js
```

---

## Backend

### `backend/app.py`

This is the FastAPI application entry point.

- Starts the FastAPI app with metadata and documentation.
- Adds CORS middleware to allow frontend access from any origin.
- Defines two endpoints:
  - `GET /` health check
  - `POST /summarize` summarization API
- Handles validation and error responses.

The backend converts word-based min/max length values into token counts before summarization, and then returns a structured response containing the summary, original text length, summary length, and selected style.

### `backend/schemas.py`

Defines Pydantic models used by the backend:

- `SummaryStyle` enum: `concise`, `detailed`, `bullets`, `executive`, `academic`, `context_preserve`
- `SummarizeRequest`: request body with `text`, `max_length`, `min_length`, and `style`
- `SummarizeResponse`: response body with `summary`, `original_length`, `summary_length`, and `style`

### `backend/validators.py`

Contains validation logic for user input:

- `validate_text(text)`: ensures text is not empty, and word count is between 50 and 2000.
- `validate_lengths(min_length, max_length)`: ensures minimum length is strictly less than maximum length.
- `ValidationError`: custom exception type used by the backend.

### `backend/summarizer.py`

This module contains the summarization service and text-processing helpers.

#### Model and service

- Uses Hugging Face `transformers.pipeline` with `facebook/bart-large-cnn`.
- Loads the model once using a singleton pattern in `get_summarizer()`.
- Summarizer methods:
  - `_summarize_pass()` performs a single BART summarization pass.
  - `_chunk_text()` splits long input into chunks around 300 words.
  - `summarize()` chooses between single-pass summarization and chunked summarization depending on input size.

#### Style-aware formatting

The backend supports six output styles.

- `concise`: short summary, few sentences.
- `detailed`: longer summary with more context.
- `bullets`: bullet-style summary list.
- `executive`: business-style executive summary with key takeaway.
- `academic`: formal style with year/source metadata when available.
- `context_preserve`: summary plus extracted key facts from the original text.

Each style is implemented with a formatting helper in `FORMAT_FUNCS`.

#### Summary cleanup and quality control

The summarizer also includes enhancement logic:

- `_clean_summary()`: removes prompt artifacts, fixes common tokenization errors, removes near-duplicate sentences, and eliminates obvious hallucinations.
- `_filter_hallucinations()`: removes sentences not well-supported by the original text.
- `_enforce_length()`: ensures summary stays within sentence count bounds.
- `_format_bullets()`, `_format_executive()`, `_format_academic()`, `_format_context_preserve()`: apply style-specific transformations.
- `KeyFactExtractor`: extracts dates, metrics, money values, percentages, ratios, and quotations from the original input text.

### `backend/requirements.txt`

Python dependencies for the backend:

- `numpy==1.26.4`
- `fastapi==0.104.1`
- `uvicorn==0.24.0`
- `pydantic==2.5.0`
- `transformers==4.35.2`
- `torch==2.1.1`
- `python-multipart==0.0.6`

---

## Frontend

The frontend is a Create React App with a simple UX for entering text and viewing summaries.

### `frontend/package.json`

- React app dependencies: `react`, `react-dom`, `react-scripts`
- Proxy configuration points to `http://localhost:8000` for backend API requests during development.

### `frontend/src/App.jsx`

Root component that composes:

- `Header`
- `TextInput`
- `SummaryOutput`
- `LoadingSpinner`

It retrieves summary state and actions from `useSummarizer()`.

### `frontend/src/hooks/useSummarizer.js`

Custom hook that manages frontend state and API interaction:

- `summary`, `isLoading`, `error`
- `originalLength`, `summaryLength`, `style`
- `generateSummary()` sends text to backend and stores response.
- `clearSummary()` resets results.

It also performs local validation for text length before sending the request.

### `frontend/src/services/api.js`

Backend API wrapper that sends POST requests to `/summarize`.

- Uses `fetch` with JSON payload.
- Adds a 60-second timeout.
- Handles errors and aborts gracefully.
- Uses `REACT_APP_API_URL` when available or defaults to `http://localhost:8000`.

### Frontend components

#### `Header`

Displays the app title, icon, and subtitle.

#### `TextInput`

User input form with:

- A large textarea for text input.
- Word count display and validation state.
- Style selection buttons.
- Min and max summary length sliders.
- Submit and clear controls.

Validation enforces:

- Minimum 50 words
- Maximum 2000 words
- Sliders: min 20–150, max 50–400

#### `SummaryOutput`

Displays the generated summary and metadata:

- Summary style label
- Original text length and summary length
- Compression ratio
- Copy and download buttons
- Reset button for a new summary

#### `LoadingSpinner`

Overlay shown while the summary request is pending.

### `frontend/src/utils/helpers.js`

Utility functions used by frontend components, such as clipboard copy and file download helpers.

---

## API Contract

### `GET /`

Health-check endpoint.

Response example:

```json
{
  "status": "ok",
  "service": "AI Text Summarizer",
  "version": "1.2.0"
}
```

### `POST /summarize`

Request body:

```json
{
  "text": "...",
  "max_length": 150,
  "min_length": 30,
  "style": "concise"
}
```

Response body:

```json
{
  "summary": "...",
  "original_length": 320,
  "summary_length": 80,
  "style": "concise"
}
```

Validation errors return HTTP 400 with a `detail` message.

---

## Usage

### Backend

1. Create and activate a Python virtual environment.
2. Install dependencies:

```bash
pip install -r backend/requirements.txt
```

3. Run the backend server:

```bash
python backend/app.py
```

or with Uvicorn:

```bash
uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

1. Install npm dependencies:

```bash
cd frontend
npm install
```

2. Start the frontend:

```bash
npm start
```

3. Open the app at `http://localhost:3000`.

The frontend will proxy requests to `http://localhost:8000`.

---

## Important details

- The backend uses CPU mode (`device=-1`) for the BART model, so summary generation may be slow on large text inputs.
- The backend and frontend both enforce the same text length range of 50 to 2000 words.
- Summary length settings are normalized internally before model inference.
- Large texts are chunked and summarized in stages to improve performance and stability.

---

## Extension ideas

- Add Docker support for both backend and frontend.
- Add authentication or usage logging.
- Add a persistent history for past summaries.
- Replace CPU-only BART inference with a GPU-enabled model when available.
- Add tests for backend validation, summary style formatting, and frontend hook behavior.
