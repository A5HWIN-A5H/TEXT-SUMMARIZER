import React from 'react';
import { useSummarizer } from './hooks/useSummarizer';
import Header from './components/Header/Header';
import TextInput from './components/TextInput/TextInput';
import SummaryOutput from './components/SummaryOutput/SummaryOutput';
import LoadingSpinner from './components/LoadingSpinner/LoadingSpinner';
import styles from './App.module.css';

function App() {
  const {
    summary,
    isLoading,
    error,
    originalLength,
    summaryLength,
    style,
    generateSummary,
    clearSummary,
  } = useSummarizer();

  return (
    <div className={styles.app}>
      <Header />
      
      <main className={styles.main}>
        <TextInput
          onSubmit={generateSummary}
          isLoading={isLoading}
          onClear={clearSummary}
        />
        
        {(summary || error) && (
          <SummaryOutput
            summary={summary}
            originalLength={originalLength}
            summaryLength={summaryLength}
            error={error}
            style={style}
            onClear={clearSummary}
          />
        )}
      </main>

      {isLoading && <LoadingSpinner />}
      
      <footer className={styles.footer}>
        <p>Powered by BART (facebook/bart-large-cnn) via Hugging Face</p>
      </footer>
    </div>
  );
}

export default App;