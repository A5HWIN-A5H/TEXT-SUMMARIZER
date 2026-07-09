from transformers import pipeline
import re


class KeyFactExtractor:
    """Extract key facts from text using regex patterns."""
    
    PATTERNS = {
        'dates': r'\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}|(?:19|20)\d{2})\b',
        'metrics': r'\b\d+(?:,\d{3})*(?:\.\d+)?\s*(?:percent|million|billion|trillion|thousand|km|miles|kg|tons?|GB|TB|MB|MHz|GHz|%\b)',
        'money': r'\$\d+(?:,\d{3})*(?:\.\d+)?(?:\s*(?:million|billion|trillion))?',
        'percentages': r'\b\d+(?:\.\d+)?%\b',
        'ratios': r'\b\d+\s*(?:to|[:])\s*\d+\b',
        'quotations': r'"[^"]{20,200}"',
    }
    
    STOP_WORDS = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need', 'dare', 'ought', 'used', 'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from', 'as', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'between', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just', 'and', 'but', 'if', 'or', 'because', 'until', 'while', 'about', 'against', 'up', 'down', 'out', 'off', 'over', 'it', 'its', 'this', 'that', 'these', 'those', 'they', 'them', 'their'}
    
    def extract(self, text: str, max_facts: int = 10) -> list:
        facts = []
        seen = set()
        
        for category, pattern in self.PATTERNS.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                fact = match.group().strip()
                if self._is_valid_fact(fact) and fact.lower() not in seen:
                    position_score = 1 - (match.start() / len(text))
                    score = position_score + self._category_weight(category)
                    facts.append({'text': fact, 'score': score})
                    seen.add(fact.lower())
        
        facts.sort(key=lambda x: x['score'], reverse=True)
        return [f['text'] for f in facts[:max_facts]]
    
    def _is_valid_fact(self, fact: str) -> bool:
        if len(fact) < 4:
            return False
        skip = {'the', 'this', 'that', 'these', 'those', 'they', 'them', 'their', 'there', 'then', 'than'}
        return fact.lower() not in skip
    
    def _category_weight(self, category: str) -> float:
        weights = {'dates': 0.3, 'metrics': 0.4, 'money': 0.4, 'percentages': 0.35, 'ratios': 0.3, 'quotations': 0.2}
        return weights.get(category, 0.1)


STYLE_CONFIGS = {
    "concise": {"target_ratio": 0.20, "min_sentences": 2, "max_sentences": 4},
    "detailed": {"target_ratio": 0.45, "min_sentences": 5, "max_sentences": 10},
    "bullets": {"target_ratio": 0.35, "min_sentences": 4, "max_sentences": 8},
    "executive": {"target_ratio": 0.30, "min_sentences": 3, "max_sentences": 6},
    "academic": {"target_ratio": 0.40, "min_sentences": 4, "max_sentences": 8},
    "context_preserve": {"target_ratio": 0.50, "min_sentences": 6, "max_sentences": 12},
}


def _clean_summary(text: str) -> str:
    """Clean up BART artifacts and remove repetition."""
    # Fix common BART typos
    typo_fixes = {
        r'\bdonanenemab\b': 'donanemab',
        r'\bARia-H\b': 'ARIA-H',
        r'\bARia-E\b': 'ARIA-E',
        r'\balzheimer\'s\b': 'Alzheimer\'s',
    }
    for wrong, right in typo_fixes.items():
        text = re.sub(wrong, right, text, flags=re.IGNORECASE)
    
    # Remove leaked prompt fragments
    prompts_to_remove = [
        "summarize briefly:", "summarize in detail:", "list key points:",
        "executive summary:", "academic summary:", "comprehensive summary:",
        "summarize the following text", "focus only on", "be brief and direct",
        "be thorough", "be organized",
    ]
    for prompt in prompts_to_remove:
        text = re.sub(re.escape(prompt), '', text, flags=re.IGNORECASE)
    
    # Split into sentences and remove near-duplicates
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
    unique_sentences = []
    seen_signatures = []
    seen_openings = []
    
    for sent in sentences:
        words = re.findall(r'\b[a-z]+\b', sent.lower())
        key_words = [w for w in words if w not in KeyFactExtractor.STOP_WORDS]
        signature = ' '.join(sorted(key_words))
        opening = ' '.join(words[:3]) if len(words) >= 3 else ''
        
        is_duplicate = False
        
        # Check semantic similarity
        for seen in seen_signatures:
            if signature and seen:
                seen_words = set(seen.split())
                current_words = set(signature.split())
                if len(current_words) > 0:
                    overlap = len(current_words & seen_words)
                    similarity = overlap / len(current_words)
                    if similarity > 0.5:
                        is_duplicate = True
                        break
        
        # Check repeated openings
        if not is_duplicate and opening and len(opening) > 5:
            for existing_opening in seen_openings:
                if opening == existing_opening:
                    is_duplicate = True
                    break
        
        if not is_duplicate and len(sent) > 10:
            unique_sentences.append(sent)
            seen_signatures.append(signature)
            if opening:
                seen_openings.append(opening)
    
    text = ' '.join(unique_sentences)
    
    # Remove repeated words
    text = re.sub(r'(\b\w+\b)(?:\s+\1)+', r'\1', text, flags=re.IGNORECASE)
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'([a-zA-Z])\s*([.!?])\s*', r'\1\2 ', text)
    
    # Remove common hallucinations
    hallucinations = [
        r'also known as ["\']The Big Bang["\']?',
        r'also known as the Big Bang',
        r'is the origin of the solar system',
        r'is the origin of the universe',
        r'is the origin of the Milky Way',
        r'also known as ["\']the universe["\']?',
    ]
    for h in hallucinations:
        text = re.sub(h, '', text, flags=re.IGNORECASE)
    
    # Fix spacing around commas
    text = re.sub(r'\s*,\s*', ', ', text)
    
    # Clean up extra spaces from removals
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'\s+([.!?])', r'\1', text)
    
    return text.strip()


def _filter_hallucinations(summary: str, original: str) -> str:
    """Remove sentences with claims not supported by original text."""
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', summary) if s.strip()]
    original_lower = original.lower()
    
    filtered = []
    for sent in sentences:
        words = re.findall(r'\b[a-z]{4,}\b', sent.lower())
        key_phrases = [w for w in words if w not in KeyFactExtractor.STOP_WORDS]
        
        if not key_phrases:
            filtered.append(sent)
            continue
        
        matches = sum(1 for phrase in key_phrases if phrase in original_lower)
        match_ratio = matches / len(key_phrases)
        
        if match_ratio > 0.4:
            filtered.append(sent)
    
    return ' '.join(filtered) if filtered else summary


def _enforce_length(text: str, min_sentences: int, max_sentences: int) -> str:
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
    if len(sentences) < min_sentences:
        return text
    if len(sentences) > max_sentences:
        return ' '.join(sentences[:max_sentences])
    return text


def _format_bullets(text: str, min_items: int = 3) -> str:
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if len(s.strip()) > 15]
    bullets = []
    for sent in sentences:
        if len(sent) > 120 and ', ' in sent:
            parts = [p.strip() for p in sent.split(', ') if len(p.strip()) > 20]
            if len(parts) > 1:
                bullets.extend(parts)
                continue
        bullets.append(sent)
    result = '\n'.join(f'• {b.rstrip(".")}.' for b in bullets if b)
    return result if result else text


def _format_executive(text: str) -> str:
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
    # Pick last sentence as takeaway (often has conclusion)
    takeaway = sentences[-1] if len(sentences) > 2 else (sentences[0] if sentences else "Review full document for details.")
    return f"Executive Summary\n\n{text}\n\nKey Takeaway: {takeaway}"


def _format_academic(text: str, original: str) -> str:
    # Catch all year patterns including BCE/CE
    years = re.findall(r'\b(?:\d{1,4})\s*(?:BCE|CE|BC|AD)?\b', original, re.IGNORECASE)
    # Clean and sort years
    clean_years = []
    for y in years:
        num = re.search(r'\d+', y).group()
        suffix = re.search(r'(BCE|CE|BC|AD)', y, re.IGNORECASE)
        suffix = suffix.group().upper() if suffix else 'CE'
        clean_years.append(f"{num} {suffix}")
    clean_years = sorted(set(clean_years), key=lambda x: int(re.search(r'\d+', x).group()))
    
    # Extract journal names properly
    journals = re.findall(r'(?:published in|from|in)\s+([A-Z][\w\s]+?(?:Journal|Medicine|Review|Proceedings|Letters|Reports|Nature|Science|Cell|Lancet|BMJ|JAMA))', original)
    
    header = "Academic Summary"
    if clean_years:
        header += f"\nPeriod: {clean_years[0]}{f'–{clean_years[-1]}' if len(clean_years) > 1 else ''}"
    
    footer = ""
    if journals:
        footer = f"\n\nSources: {', '.join(set(journals[:2]))}"
    elif clean_years:
        footer = f"\n\nKey dates: {', '.join(clean_years[:3])}"
    
    return f"{header}\n\n{text}{footer}"


def _format_context_preserve(text: str, original: str) -> str:
    extractor = KeyFactExtractor()
    facts = extractor.extract(original, max_facts=10)
    summary = _enforce_length(_clean_summary(text), 6, 12)
    
    if not facts:
        return summary
    
    summary_lower = summary.lower()
    unique_facts = [f for f in facts if f.lower() not in summary_lower]
    
    if not unique_facts:
        return summary
    
    facts_text = "\n".join(f"• {fact}" for fact in unique_facts[:8])
    return f"{summary}\n\n─── Key Context Preserved ───\n{facts_text}"


FORMAT_FUNCS = {
    "concise": lambda t, o: _enforce_length(_clean_summary(_filter_hallucinations(t, o)), 2, 4),
    "detailed": lambda t, o: _enforce_length(_clean_summary(_filter_hallucinations(t, o)), 5, 10),
    "bullets": lambda t, o: _format_bullets(_clean_summary(_filter_hallucinations(t, o)), 3),
    "executive": lambda t, o: _format_executive(_clean_summary(_filter_hallucinations(t, o))),
    "academic": lambda t, o: _format_academic(_clean_summary(_filter_hallucinations(t, o)), o),
    "context_preserve": lambda t, o: _format_context_preserve(_filter_hallucinations(t, o), o),
}


class SummarizerService:
    def __init__(self):
        print("Loading BART model... (this may take a minute)")
        self.model = pipeline("summarization", model="facebook/bart-large-cnn", device=-1)
        print("Model loaded successfully!")

    def _chunk_text(self, text: str, max_words: int = 300) -> list:
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

    def _summarize_pass(self, text: str, max_len: int, min_len: int) -> str:
        result = self.model(
            text,
            max_length=max_len,
            min_length=min_len,
            do_sample=False,
            num_beams=6,
            num_beam_groups=2,
            diversity_penalty=0.5,
            length_penalty=1.2,
            early_stopping=True,
            truncation=True,
            no_repeat_ngram_size=3,
        )
        return result[0]["summary_text"].strip()

    def summarize(self, text: str, max_length: int = 150, min_length: int = 30, style: str = "concise") -> str:
        config = STYLE_CONFIGS.get(style, STYLE_CONFIGS["concise"])
        word_count = len(text.split())
        
        target_words = max(min_length, int(word_count * config["target_ratio"]))
        target_words = min(target_words, max_length)
        
        token_max = int(max_length * 1.33)
        token_min = int(max(min_length, target_words * 0.7) * 1.33)
        
        if word_count <= 400:
            raw = self._summarize_pass(text, token_max, token_min)
            cleaned = _clean_summary(raw)
            return FORMAT_FUNCS[style](cleaned, text)
        
        chunks = self._chunk_text(text)
        num_chunks = len(chunks)
        chunk_max = max(60, min(120, (token_max * 2) // num_chunks))
        chunk_min = max(25, token_min // num_chunks)
        
        chunk_summaries = []
        for chunk in chunks:
            summary = self._summarize_pass(chunk, chunk_max, chunk_min)
            chunk_summaries.append(summary)
        
        combined = ' '.join(chunk_summaries)
        final_max = token_max
        final_min = max(token_min, int(final_max * 0.3))
        
        if len(combined.split()) > max_length * 0.8:
            final = self._summarize_pass(combined, final_max, final_min)
        else:
            final = combined
        
        cleaned = _clean_summary(final)
        return FORMAT_FUNCS[style](cleaned, text)


_summarizer = None

def get_summarizer() -> SummarizerService:
    global _summarizer
    if _summarizer is None:
        _summarizer = SummarizerService()
    return _summarizer