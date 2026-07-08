import React from 'react';
import styles from './LoadingSpinner.module.css';

function LoadingSpinner() {
  return (
    <div className={styles.overlay} role="status" aria-live="polite">
      <div className={styles.spinner}>
        <div className={styles.ring}></div>
      </div>
      <p className={styles.text}>Generating summary...</p>
      <p className={styles.subtext}>This may take a few seconds</p>
    </div>
  );
}

export default React.memo(LoadingSpinner);