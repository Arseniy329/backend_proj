import styles from './ConfirmDialog.module.css';
import Button from './Button';

/**
 * Inline confirmation dialog — renders inside a Modal.
 *
 * @param {string}   message        - Warning text shown to the user
 * @param {Function} onConfirm      - Called when the confirm button is clicked
 * @param {Function} onCancel       - Called when the cancel button is clicked
 * @param {string}   confirmLabel   - Label for the confirm button (default: "Підтвердити")
 * @param {boolean}  isLoading      - Disables both buttons while async action is in progress
 */
export default function ConfirmDialog({
  message,
  onConfirm,
  onCancel,
  confirmLabel = 'Підтвердити',
  isLoading = false,
}) {
  return (
    <div className={styles.wrapper}>
      <p className={styles.message}>{message}</p>
      <div className={styles.actions}>
        <Button
          variant="secondary"
          onClick={onCancel}
          disabled={isLoading}
        >
          Скасувати
        </Button>
        <button
          type="button"
          className={styles.confirmBtn}
          onClick={onConfirm}
          disabled={isLoading}
        >
          {isLoading ? 'Зачекайте…' : confirmLabel}
        </button>
      </div>
    </div>
  );
}
