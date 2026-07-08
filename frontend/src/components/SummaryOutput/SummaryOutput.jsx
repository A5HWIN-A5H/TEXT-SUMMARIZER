import React, { useState, useCallback } from 'react';
import { copyToClipboard, downloadAsText } from '../../utils/helpers';
import styles from './SummaryOutput.module.css';

const STYLE_LABELS = {
  concise: 'Concise',
  detailed: 'Detailed',
  bullets: 'Bullet Points',
  executive: 'Executive',
  academic: 'Academic',
};

function SummaryOutput({ summary, originalLength, summaryLength, error, style, onClear }) {
  const [copyStatus, setCopyStatus] = useState('idle');

  const handleCopy = useCallback(async () => {
    const success = await copyToClipboard(summary);
    setCopyStatus(success ? 'success' : 'error');
    setTimeout(() => setCopyStatus('idle'), 2000);
  }, [summary]);

  const handleDownload = useCallback(() => {
    const timestamp = new Date().toISOString().slice(0, 10);
    const styleLabel = style ? `-${style}` : '';
    downloadAsText(summary, `summary${styleLabel}-${timestamp}.txt`);
  }, [summary, style]);

  const compressionRatio = originalLength > 0 
    ? Math.round((1 - summaryLength / originalLength) * 100) 
    : 0;

  if (error) {
    return (
      <section className={styles.section} role="alert">
        <div className={styles.errorBox}>
          <svg className={styles.errorIcon} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
          <div>
            <h3 className={styles.errorTitle}>Something went wrong</h3>
            <p className={styles.errorMessage}>{error}</p>
          </div>
        </div>
        <button onClick={onClear} className={styles.retryBtn}>
          Try Again
        </button>
      </section>
    );
  }

  if (!summary) return null;

  return (
    <section className={styles.section}>
      <div className={styles.header}>
        <div>
          <h2 className={styles.title}>Summary</h2>
          {style && (
            <span className={styles.styleTag}>{STYLE_LABELS[style] || style}</span>
          )}
        </div>
        <div className={styles.stats}>
          <span className={styles.stat}>
            {originalLength} → {summaryLength} words
          </span>
          <span className={`${styles.stat} ${styles.compression}`}>
            {compressionRatio}% shorter
          </span>
        </div>
      </div>

      <div className={styles.content}>
        {summary}
      </div>

      <div className={styles.actions}>
        <button
          onClick={handleCopy}
          className={`${styles.actionBtn} ${copyStatus === 'success' ? styles.success : ''}`}
          aria-label="Copy summary to clipboard"
        >
          {copyStatus === 'success' ? 'Copied!' : copyStatus === 'error' ? 'Failed' : 'Copy'}
        </button>
        <button 
          onClick={handleDownload} 
          className={styles.actionBtn}
          aria-label="Download summary as text file"
        >
          Download
        </button>
        <button 
          onClick={onClear} 
          className={`${styles.actionBtn} ${styles.secondary}`}
        >
          New Summary
        </button>
      </div>
    </section>
  );
}

export default React.memo(SummaryOutput);