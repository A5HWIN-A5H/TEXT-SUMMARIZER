const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export async function summarizeText(text, maxLength = 150, minLength = 30, style = 'concise', signal) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 60000);
  const abortSignal = signal || controller.signal;

  try {
    const response = await fetch(`${API_BASE_URL}/summarize`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text,
        max_length: maxLength,
        min_length: minLength,
        style,
      }),
      signal: abortSignal,
    });

    clearTimeout(timeoutId);
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || `Server error: ${response.status}`);
    }

    return data;
  } catch (err) {
    clearTimeout(timeoutId);
    if (err.name === 'AbortError') {
      throw new Error('Request timed out. The model may still be loading.');
    }
    throw err;
  }
}