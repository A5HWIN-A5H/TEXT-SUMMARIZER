# TEXT-SUMMARIZER Engineering Project Report

## Preliminary Pages

### Cover Page

**Project Title:** Text Summarizer

**Student Name:** [Your Name]

**Supervisor:** [Supervisor Name]

**Department:** [Department Name]

**Institution:** [Institution Name]

**Date:** [Submission Date]

---

### Title Page

**Title:** Text Summarizer

**Subtitle:** A Full-Stack Web Application for AI-Powered Text Summarization

**Author:** [Your Name]

**Course:** [Course Name]

**Institution:** [Institution Name]

**Supervisor:** [Supervisor Name]

**Date:** [Submission Date]

---

### Certificate

This is to certify that the project titled **"Text Summarizer"** has been carried out by **[Your Name]** under my supervision. This work is original and has not been submitted earlier for any degree or diploma.

**Supervisor Name:** [Supervisor Name]

**Signature:** ____________________

**Date:** [Submission Date]

---

### Declaration

I hereby declare that this project titled **"Text Summarizer"** is my original work. All sources used in the preparation of this report have been acknowledged.

**Student Name:** [Your Name]

**Signature:** ____________________

**Date:** [Submission Date]

---

### Acknowledgement

I would like to express my sincere gratitude to my project guide, **[Supervisor Name]**, for providing valuable guidance, support, and encouragement throughout this project.

I also thank my department and all faculty members for their support. Finally, I thank my family and friends for their encouragement and support during this project.

---

### Abstract

The **Text Summarizer** project develops a full-stack application that transforms long text into concise, readable summaries using advanced natural language processing. The backend uses a FastAPI service integrated with the Hugging Face BART model for summarization, while the frontend provides a React-based user interface for input, style selection, and results display.

The system supports multiple summary styles including concise, detailed, bullet points, executive, academic, and context-preserving summaries. Input validation ensures source text quality, while backend logic adjusts output length and formats results according to the selected style. The implementation also includes text cleanup, hallucination filtering, and multi-step chunk summarization for longer inputs.

This project demonstrates the integration of modern AI tools with web technologies, delivering a practical summarization tool for academic and professional use.

---

### Table of Contents

1. Introduction
2. Literature Review
3. System Design
4. Implementation
5. Results and Discussion
6. Conclusion and Future Scope
7. References
8. Appendices

---

### List of Figures

- Figure 1: System Architecture Diagram
- Figure 2: Application Flow Diagram
- Figure 3: User Interface Screenshots

### List of Tables

- Table 1: Summary Style Definitions
- Table 2: Validation Rules
- Table 3: Backend Dependencies

### List of Abbreviations

- API: Application Programming Interface
- BART: Bidirectional and Auto-Regressive Transformers
- CPU: Central Processing Unit
- UI: User Interface
- NLP: Natural Language Processing
- JSON: JavaScript Object Notation
- REST: Representational State Transfer

---

## Chapter 1: Introduction

### Background

Text summarization is a natural language processing task in which a long document is reduced to a shorter version while preserving key information. Summarization tools are useful for processing articles, reports, academic papers, and business documents.

This project applies modern AI summarization to build a user-friendly web application that can produce multiple summary styles, helping users convert long text into concise and readable outputs.

### Problem Statement

Many users need to extract essential meaning from long documents quickly. Manual summarization is time-consuming, and generic keyword-based summarizers often fail to preserve context and readability.

The goal is to build an application that produces high-quality summaries in different styles while validating input length and handling longer documents efficiently.

### Objectives

- Develop a backend API for AI-based summarization.
- Support multiple summary styles.
- Provide an intuitive frontend interface for text input and output display.
- Validate user input and manage long text with chunked summarization.
- Clean and format summary output to reduce repetition and hallucination.

### Scope

The project covers:

- Backend implementation with FastAPI and Hugging Face Transformers.
- Frontend implementation with React.
- Support for six summary styles.
- Input validation and length normalization.
- Output formatting and quality improvement.

The project does not cover:

- Real-time collaborative summarization.
- Multi-user authentication.
- Cloud deployment or server scaling.

### Methodology Overview

The system is implemented using a combination of web development and machine learning components:

- The frontend collects input text, style selection, and summary length preferences.
- The backend validates input, computes token-based length bounds, and summarizes text using the BART model.
- Long documents are chunked and summarized iteratively.
- The backend cleans and formats the output before returning it.

### Report Organization

- Chapter 2 reviews related summarization systems and gaps.
- Chapter 3 describes system design and architecture.
- Chapter 4 provides implementation details for backend and frontend modules.
- Chapter 5 presents result analysis and discussion.
- Chapter 6 concludes and describes future enhancements.

---

## Chapter 2: Literature Review

### Existing Systems

Existing summarization systems often use extractive or abstractive strategies. Extractive systems select important sentences directly from the source text, while abstractive systems generate new sentences using language models.

Common approaches include:

- Rule-based summarizers using sentence ranking and term frequency.
- Extractive summarizers such as TextRank.
- Transformer-based models like BERT and BART for abstractive summarization.

### Research Gap

Many generic summarizers do not support multiple summarization styles or provide readable, polished output. They also struggle with longer text and may generate repetitive or hallucinated content.

This project addresses the gap by combining an abstractive transformer model with application-specific formatting, cleanup, and style options.

### Comparative Analysis

Compared to simple extractive summarizers, the project’s approach can produce natural-sounding, paraphrased summaries. Compared to off-the-shelf models without formatting, this application adds:

- multi-style output
- length normalization
- hallucination filtering
- chunked summarization for long text

This makes the system more useful for practical user-facing summarization tasks.

---

## Chapter 3: System Design

### Architecture Diagram

The system follows a client-server architecture.

- The React frontend sends requests to the FastAPI backend.
- The backend runs model inference using Hugging Face Transformers.
- The backend returns structured summary responses.

(Figure 1: System Architecture Diagram)

### Block Diagram

The system consists of three main blocks:

1. Frontend UI
2. API Layer
3. Summarization Engine

(Figure 2: Block Diagram)

### Flowcharts

The summarization flow includes:

- User inputs text and style.
- Frontend validates basic input.
- Backend validates text length and style.
- Backend computes token-based lengths.
- Backend summarizes text in one or more passes.
- Backend cleans and formats output.
- Frontend displays the summary.

(Figure 3: Application Flowchart)

### UML Diagrams (if applicable)

A class diagram would include:

- `SummarizerService`
- `KeyFactExtractor`
- `SummarizeRequest`
- `SummarizeResponse`
- `useSummarizer`

### Hardware and Software Requirements

Hardware:

- A modern CPU, preferably with at least 8 GB RAM
- Enough storage for Python packages and model weights

Software:

- Python 3.11+
- Node.js 18+ and npm
- FastAPI
- Uvicorn
- Transformers
- PyTorch
- React

---

## Chapter 4: Implementation

### Modules

The project is implemented in two parts:

- Backend modules:
  - `app.py`
  - `schemas.py`
  - `validators.py`
  - `summarizer.py`
- Frontend modules:
  - `App.jsx`
  - `useSummarizer.js`
  - `api.js`
  - `TextInput.jsx`
  - `SummaryOutput.jsx`
  - `Header.jsx`
  - `LoadingSpinner.jsx`

### Algorithms

#### Input Validation

- Reject empty input.
- Require 50–2000 words.
- Ensure minimum summary length is less than maximum length.

#### Chunked Summarization

For long documents (>400 words), the backend:

- Splits input into ~300-word chunks.
- Summarizes each chunk.
- Combines chunk summaries.
- Optionally summarizes the combined text.

#### Style Formatting

Each summary style uses a dedicated formatter:

- `concise`: short sentence count
- `detailed`: longer explanation
- `bullets`: bullet list output
- `executive`: summary with key takeaway
- `academic`: metadata-rich academic tone
- `context_preserve`: summary plus extracted key facts

#### Output Cleanup

The backend cleans the raw model output by:

- removing prompt fragments
- deduplicating similar sentences
- fixing spacing and punctuation
- filtering low-supported statements

### Database Design

No database is used in the current version of the project. The application is stateless and processes each request independently.

### Implementation Details

#### Backend

- `app.py` defines routes and error handling.
- `schemas.py` defines request and response validation.
- `validators.py` enforces text length rules.
- `summarizer.py` loads the BART model and performs summarization with formatting.

The backend uses a singleton `get_summarizer()` to avoid repeated model load overhead.

#### Frontend

- `App.jsx` orchestrates the user interface.
- `useSummarizer.js` handles API requests and manages state.
- `api.js` sends POST requests with a timeout.
- `TextInput.jsx` accepts user text and style selections.
- `SummaryOutput.jsx` renders the summary and actions.
- `LoadingSpinner.jsx` displays progress during inference.

The frontend validates text length locally before sending requests.

---

## Chapter 5: Results and Discussion

### Experimental Results

The application successfully generates summary outputs in multiple styles. It produces cleaner and readable summaries for texts above the 50-word threshold.

Example results:

- `concise`: a short summary with only key sentences
- `detailed`: a more descriptive summary
- `bullets`: bullet-style output for quick scanning
- `executive`: executive summary with a takeaway

### Performance Analysis

- Short text inputs are summarized in a single pass.
- Long inputs are broken into chunks, which improves stability.
- CPU-based inference can be slower, especially for long documents.

### Screenshots

- Input form with style controls
- Generated summary output
- Loading state during model inference

### Graphs

- Graphs could show request latency vs document length.
- A performance comparison chart could compare single-pass vs chunked summarization.

### Discussion

The project demonstrates a working integration of AI summarization with a web UI. The style-based formatting and cleanup logic improve output quality beyond raw model responses.

The main challenge is model inference speed on CPU and the need to handle longer text gracefully. The chunking strategy addresses this by summarizing large inputs without overwhelming the model.

---

## Chapter 6: Conclusion and Future Scope

### Conclusion

The Text Summarizer project successfully builds a full-stack summarization tool. It uses state-of-the-art transformer models and provides a user-friendly interface with multiple summary styles.

The system validates input, manages long text, and formats output to improve usability.

### Limitations

- CPU-only model inference limits performance.
- No persistent storage or user accounts.
- The system is not deployed to a production environment.
- Some output may still contain minor repetition or style inconsistency.

### Future Enhancements

Potential future improvements:

- GPU acceleration for faster summarization.
- Deployment with Docker and cloud hosting.
- User authentication and summary history.
- Support for file uploads and PDF/text import.
- Additional summary styles and configurable prompts.
- Automated testing for backend and frontend components.

---

## References

1. Lewis, M., Liu, Y., Goyal, N., Ghazvininejad, M., Mohamed, A., &amp; Levy, O. (2020). BART: Denoising Sequence-to-Sequence Pre-training for Natural Language Generation, Translation, and Comprehension. arXiv.
2. FastAPI documentation. Available at: https://fastapi.tiangolo.com/
3. Hugging Face Transformers documentation. Available at: https://huggingface.co/docs/transformers/
4. React documentation. Available at: https://reactjs.org/

> References are formatted in IEEE style.

---

## Appendices

### Appendix A: Source Code

Key source files:

- `backend/app.py`
- `backend/schemas.py`
- `backend/validators.py`
- `backend/summarizer.py`
- `backend/requirements.txt`
- `frontend/package.json`
- `frontend/src/App.jsx`
- `frontend/src/hooks/useSummarizer.js`
- `frontend/src/services/api.js`
- `frontend/src/components/TextInput/TextInput.jsx`
- `frontend/src/components/SummaryOutput/SummaryOutput.jsx`
- `frontend/src/components/Header/Header.jsx`
- `frontend/src/components/LoadingSpinner/LoadingSpinner.jsx`

### Appendix B: User Manual

1. Start the backend server:

```bash
cd backend
python app.py
```

2. Start the frontend app:

```bash
cd frontend
npm install
npm start
```

3. Open the browser at `http://localhost:3000`.
4. Paste the text to summarize.
5. Choose a summary style.
6. Adjust min and max summary word lengths.
7. Click **Generate Summary**.
8. Copy or download the output.

### Appendix C: Datasheets

Not applicable for this software-only project.

### Appendix D: Additional Results

Additional test summaries and performance observations can be added here during testing and evaluation.
