import React, { useState, useCallback, useRef, useMemo } from 'react';
import styles from './TextInput.module.css';

const STYLES = [
  { value: 'concise', label: 'Concise', desc: 'Short, just the facts' },
  { value: 'detailed', label: 'Detailed', desc: 'More context & examples' },
  { value: 'bullets', label: 'Bullet Points', desc: 'Key points as a list' },
  { value: 'executive', label: 'Executive', desc: 'Business-focused, actionable' },
  { value: 'academic', label: 'Academic', desc: 'Formal, preserves citations' },
];

function TextInput({ onSubmit, isLoading, onClear }) {
  const [text, setText] = useState('');
  const [maxLength, setMaxLength] = useState(150);
  const [minLength, setMinLength] = useState(30);
  const [style, setStyle] = useState('concise');
  const textareaRef = useRef(null);

  const wordCount = useMemo(() => text.trim().split(/\s+/).filter(Boolean).length, [text]);
  const charCount = text.length;
  const isTooShort = wordCount > 0 && wordCount < 20;
  const isTooLong = wordCount > 2000;
  const isValid = wordCount >= 20 && wordCount <= 2000;

  const handleSubmit = useCallback((e) => {
    e.preventDefault();
    if (!isValid || isLoading) return;
    onSubmit(text, maxLength, minLength, style);
  }, [text, maxLength, minLength, style, isValid, isLoading, onSubmit]);

  const handleClear = useCallback(() => {
    setText('');
    setStyle('concise');
    onClear();
    textareaRef.current?.focus();
  }, [onClear]);

  const handleMaxLengthChange = useCallback((e) => {
    const value = parseInt(e.target.value, 10);
    setMaxLength(value);
    if (value <= minLength) {
      setMinLength(Math.max(10, value - 20));
    }
  }, [minLength]);

  const handleMinLengthChange = useCallback((e) => {
    const value = parseInt(e.target.value, 10);
    setMinLength(Math.min(value, maxLength - 20));
  }, [maxLength]);

  return (
    <section className={styles.section}>
      <form onSubmit={handleSubmit} className={styles.form}>
        <div className={styles.textareaWrapper}>
          <label htmlFor="text-input" className={styles.label}>
            Input Text
          </label>
          <textarea
            ref={textareaRef}
            id="text-input"
            className={`${styles.textarea} ${isTooShort ? styles.invalid : ''} ${isTooLong ? styles.invalid : ''}`}
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Paste your article, report, or document here (minimum 20 words)..."
            rows={10}
            disabled={isLoading}
            aria-describedby="word-count-hint"
          />
          <div className={styles.metaRow}>
            <span 
              id="word-count-hint"
              className={`${styles.wordCount} ${isTooShort || isTooLong ? styles.invalid : ''}`}
            >
              {wordCount} words · {charCount} chars
              {isTooShort && ' (min 20)'}
              {isTooLong && ' (max 2000)'}
            </span>
            {text && (
              <button
                type="button"
                onClick={handleClear}
                className={styles.clearBtn}
                disabled={isLoading}
              >
                Clear
              </button>
            )}
          </div>
        </div>

        <div className={styles.styleGroup}>
          <label className={styles.label}>Summary Style</label>
          <div className={styles.styleGrid}>
            {STYLES.map((s) => (
              <button
                key={s.value}
                type="button"
                className={`${styles.styleBtn} ${style === s.value ? styles.active : ''}`}
                onClick={() => setStyle(s.value)}
                disabled={isLoading}
              >
                <span className={styles.styleLabel}>{s.label}</span>
                <span className={styles.styleDesc}>{s.desc}</span>
              </button>
            ))}
          </div>
        </div>

        <div className={styles.controls}>
          <div className={styles.sliderGroup}>
            <label htmlFor="min-length" className={styles.sliderLabel}>
              Min Length: <span className={styles.sliderValue}>{minLength}</span>
              <span className={styles.sliderHint}> tokens</span>
            </label>
            <input
              id="min-length"
              type="range"
              min={10}
              max={200}
              value={minLength}
              onChange={handleMinLengthChange}
              className={styles.slider}
              disabled={isLoading}
            />
          </div>

          <div className={styles.sliderGroup}>
            <label htmlFor="max-length" className={styles.sliderLabel}>
              Max Length: <span className={styles.sliderValue}>{maxLength}</span>
              <span className={styles.sliderHint}> tokens</span>
            </label>
            <input
              id="max-length"
              type="range"
              min={50}
              max={500}
              value={maxLength}
              onChange={handleMaxLengthChange}
              className={styles.slider}
              disabled={isLoading}
            />
          </div>
        </div>

        <div className={styles.hint}>
          <span className={styles.hintIcon}>ℹ</span>
          1 token ≈ 0.75 words. Adjust sliders for longer or shorter summaries.
        </div>

        <button
          type="submit"
          className={styles.submitBtn}
          disabled={!isValid || isLoading}
          aria-busy={isLoading}
        >
          {isLoading ? 'Summarizing...' : 'Generate Summary'}
        </button>
      </form>
    </section>
  );
}

export default React.memo(TextInput);