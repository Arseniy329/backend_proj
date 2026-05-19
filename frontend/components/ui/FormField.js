import styles from './FormField.module.css';

/**
 * Labelled text/email/tel/date/time/number/password input atom.
 * Designed to work with React Hook Form's `register` prop.
 */
export default function FormField({
  label,
  id,
  type = 'text',
  placeholder,
  error,
  registration, /* spread from register() */
  ...rest
}) {
  return (
    <div className={styles.field}>
      {label && (
        <label htmlFor={id} className={styles.label}>
          {label}
        </label>
      )}
      <input
        id={id}
        type={type}
        placeholder={placeholder}
        className={`${styles.input} ${error ? styles.invalid : ''}`}
        {...registration}
        {...rest}
      />
      {error && <span className={styles.error}>{error}</span>}
    </div>
  );
}
