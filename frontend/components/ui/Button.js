import styles from './Button.module.css';

/**
 * Single-purpose button atom.
 * @param {'primary'|'secondary'|'danger'|'ghost'} variant
 * @param {'sm'|'md'} size
 */
export default function Button({
  children,
  variant = 'primary',
  size = 'md',
  type = 'button',
  disabled = false,
  onClick,
  id,
}) {
  return (
    <button
      id={id}
      type={type}
      disabled={disabled}
      onClick={onClick}
      className={`${styles.btn} ${styles[variant]} ${styles[size]}`}
    >
      {children}
    </button>
  );
}
