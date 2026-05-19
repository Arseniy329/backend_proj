import styles from './Modal.module.css';
import Button from './Button';

/**
 * Accessible dialog overlay. Traps focus and closes on backdrop click.
 * @param {boolean} isOpen
 * @param {string}  title
 * @param {() => void} onClose
 * @param {'sm'|'md'|'lg'} size
 */
export default function Modal({ isOpen, title, onClose, size = 'md', children }) {
  if (!isOpen) return null;

  function handleBackdropClick(e) {
    if (e.target === e.currentTarget) onClose();
  }

  return (
    <div className={styles.backdrop} onClick={handleBackdropClick} role="dialog" aria-modal="true" aria-label={title}>
      <div className={`${styles.dialog} ${styles[size]}`}>
        <div className={styles.header}>
          <h2 className={styles.title}>{title}</h2>
          <button className={styles.closeBtn} onClick={onClose} aria-label="Закрити">✕</button>
        </div>
        <div className={styles.body}>{children}</div>
      </div>
    </div>
  );
}
