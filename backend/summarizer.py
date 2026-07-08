from transformers import pipeline
import re


STYLE_CONFIGS = {
    "concise": {
        "prompt": "Summarize the following text in a brief, focused paragraph. Include only the most essential facts and main conclusion:",
        "format": lambda text, _: text,
        "target_ratio": 0.20,
    },
    "detailed": {
        "prompt": "Provide a comprehensive summary of the following text. Include key details, important context, supporting evidence, and main implications:",
        "format": lambda text, _: text,
        "target_ratio": 0.40,
    },
    "bullets": {
        "prompt": "Extract the key points from the following text. Focus on distinct, standalone facts and findings:",
        "format": lambda text, _: _format_bullets(text),
        "target_ratio": 0.35,
    },
    "executive": {
        "prompt": "Summarize the following text for executive decision-making. Highlight business impact, strategic importance, actionable outcomes, and key metrics:",
        "format": lambda text, _: _format_executive(text),
        "target_ratio": 0.30,
    },
    "academic": {
        "prompt": "Summarize the following academic text. Preserve the research question, methodology, key findings, and significant citations or dates:",
        "format": lambda text, orig: _format_academic(text, orig),
        "target_ratio": 0.35,
    },
}


def _format_bullets(text: str) -> str:
    """Convert prose summary into clean bullet points."""
    print(f"[DEBUG] Formatting bullets. Input: {text[:80]}...")
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if len(s.strip()) > 10]
    bullets = []
    for sent in sentences:
        clauses = [c.strip() for c in sent.split(', ') if len(c.strip()) > 15]
        if len(clauses) > 1 and len(sent) > 100:
            bullets.extend(clauses)
        else:
            bullets.append(sent)
    result = '\n'.join(f'• {b.rstrip(".")}.' for b in bullets if b)
    print(f"[DEBUG] Bullets output: {result[:80]}...")
    return result


def _format_executive(text: str) -> str:
    """Add executive framing to summary."""
    print(f"[DEBUG] Formatting executive. Input: {text[:80]}...")
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
    takeaway = sentences[0] if sentences else "Review full document for details."
    result = f"Executive Summary\n\n{text}\n\nKey Takeaway: {takeaway}"
    print(f"[DEBUG] Executive output: {result[:80]}...")
    return result


def _format_academic(text: str, original: str) -> str:
    """Preserve academic markers and add citation context."""
    print(f"[DEBUG] Formatting academic. Input: {text[:80]}...")
    years = sorted(set(re.findall(r'\b(19|20)\d{2}\b', original)))
    journals = re.findall(r'(?:the\s+)?([A-Z][\w\s]+Journal\s+of\s+[\w\s]+|[A-Z][\w\s]+Proceedings)', original)
    
    header = "Academic Summary"
    if years:
        header += f"\nPeriod: {years[0]}{f'–{years[-1]}' if len(years) > 1 else ''}"
    
    footer = ""
    if journals:
        footer = f"\n\nSources: {', '.join(set(journals[:2]))}"
    elif years:
        footer = f"\n\nKey dates: {', '.join(years[:3])}"
    
    result = f"{header}\n\n{text}{footer}"
    print(f"[DEBUG] Academic output: {result[:80]}...")
    return result


class SummarizerService:
    def __init__(self):
        print("Loading BART model... (this may take a minute)")
        self.model = pipeline(
            "summarization",
            model="facebook/bart-large-cnn",
            device=-1
        )
        print("Model loaded successfully!")

    def _chunk_text(self, text: str, max_words: int = 350) -> list:
        """Split text at sentence boundaries into processable chunks."""
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

    def _summarize_pass(self, text: str, max_len: int, min_len: int, prompt: str) -> str:
        """Single BART summarization with style prompt prepended."""
        styled = f"{prompt}\n\n{text}" if len(text) > 100 else text
        result = self.model(
            styled,
            max_length=max_len,
            min_length=min_len,
            do_sample=False,
            num_beams=4,
            early_stopping=True,
            truncation=True,
        )
        return result[0]["summary_text"].strip()

    def summarize(self, text: str, max_length: int = 150, min_length: int = 30, style: str = "concise") -> str:
        """Multi-stage summarization with style-aware formatting."""
        print(f"[DEBUG] summarize() called with style={style}, max={max_length}, min={min_length}")
        
        config = STYLE_CONFIGS.get(style, STYLE_CONFIGS["concise"])
        print(f"[DEBUG] Config found: prompt={config['prompt'][:50]}...")
        
        word_count = len(text.split())
        print(f"[DEBUG] Word count: {word_count}")
        
        # Stage 1: For short texts, single pass
        if word_count <= 400:
            print("[DEBUG] Using single-pass (short text)")
            raw = self._summarize_pass(text, max_length, min_length, config["prompt"])
            print(f"[DEBUG] Raw BART output: {raw[:80]}...")
            formatted = config["format"](raw, text)
            print(f"[DEBUG] Final formatted output: {formatted[:80]}...")
            return formatted
        
        # Stage 2: Chunk summarization for medium texts
        print("[DEBUG] Using multi-pass (long text)")
        chunks = self._chunk_text(text)
        num_chunks = len(chunks)
        print(f"[DEBUG] Split into {num_chunks} chunks")
        
        chunk_max = max(60, min(120, (max_length * 2) // num_chunks))
        chunk_min = max(25, min_length // num_chunks)
        
        chunk_summaries = []
        for i, chunk in enumerate(chunks):
            print(f"[DEBUG] Summarizing chunk {i+1}/{num_chunks}")
            summary = self._summarize_pass(chunk, chunk_max, chunk_min, config["prompt"])
            chunk_summaries.append(summary)
        
        combined = ' '.join(chunk_summaries)
        print(f"[DEBUG] Combined length: {len(combined.split())} words")
        
        # Stage 3: Final refinement pass
        final_max = max_length
        final_min = max(min_length, int(final_max * 0.3))
        
        if len(combined.split()) > max_length * 0.8:
            print("[DEBUG] Running final refinement pass")
            final = self._summarize_pass(combined, final_max, final_min, config["prompt"])
        else:
            final = combined
        
        return config["format"](final, text)


_summarizer = None

def get_summarizer() -> SummarizerService:
    global _summarizer
    if _summarizer is None:
        _summarizer = SummarizerService()
    return _summarizer