import { useState, useCallback } from 'react';
import { summarizeText } from '../services/api';

export function useSummarizer() {
  const [summary, setSummary] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [originalLength, setOriginalLength] = useState(0);
  const [summaryLength, setSummaryLength] = useState(0);
  const [style, setStyle] = useState('concise');

  const generateSummary = useCallback(async (text, maxLength, minLength, selectedStyle) => {
    const wordCount = text.trim().split(/\s+/).filter(Boolean).length;
    if (wordCount < 20) {
      setError(`Text too short. Minimum 20 words required. Current: ${wordCount}.`);
      return;
    }
    if (wordCount > 2000) {
      setError(`Text too long. Maximum 2000 words allowed. Current: ${wordCount}.`);
      return;
    }

    setIsLoading(true);
    setError(null);
    setSummary('');
    setStyle(selectedStyle);

    try {
      const result = await summarizeText(text, maxLength, minLength, selectedStyle);
      setSummary(result.summary);
      setOriginalLength(result.original_length);
      setSummaryLength(result.summary_length);
    } catch (err) {
      setError(err.message);
      setOriginalLength(0);
      setSummaryLength(0);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const clearSummary = useCallback(() => {
    setSummary('');
    setError(null);
    setOriginalLength(0);
    setSummaryLength(0);
  }, []);

  return {
    summary,
    isLoading,
    error,
    originalLength,
    summaryLength,
    style,
    generateSummary,
    clearSummary,
  };
}