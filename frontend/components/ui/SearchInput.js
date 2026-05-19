import styles from './SearchInput.module.css';

/**
 * Controlled search input atom with a debounce-ready onChange.
 */
export default function SearchInput({ value, onChange, placeholder = 'Пошук…', id = 'search' }) {
  return (
    <div className={styles.wrapper}>
      <span className={styles.icon} aria-hidden="true">⌕</span>
      <input
        id={id}
        type="search"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className={styles.input}
        autoComplete="off"
      />
    </div>
  );
}
