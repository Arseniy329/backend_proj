import styles from './SelectField.module.css';

/**
 * Labelled <select> atom. Works with React Hook Form register.
 * @param {{ value: string, label: string }[]} options
 */
export default function SelectField({
  label,
  id,
  options = [],
  error,
  registration,
  placeholder = 'Виберіть…',
  ...rest
}) {
  return (
    <div className={styles.field}>
      {label && (
        <label htmlFor={id} className={styles.label}>
          {label}
        </label>
      )}
      <select
        id={id}
        className={`${styles.select} ${error ? styles.invalid : ''}`}
        {...registration}
        {...rest}
      >
        <option value="">{placeholder}</option>
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
      {error && <span className={styles.error}>{error}</span>}
    </div>
  );
}
