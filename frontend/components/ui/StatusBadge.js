import styles from './StatusBadge.module.css';

/**
 * Pill badge for displaying entity statuses.
 * @param {'active'|'inactive'|'archived'|'scheduled'|'completed'|'cancelled'|'present'|'absent'|'late'|'admin'|'teacher'} status
 */
export default function StatusBadge({ status }) {
  const labelMap = {
    active:    'Активний',
    inactive:  'Неактивний',
    archived:  'Архів',
    scheduled: 'Заплановано',
    completed: 'Проведено',
    cancelled: 'Скасовано',
    present:   'Присутній',
    absent:    'Відсутній',
    late:      'Запізнився',
    admin:     'Адміністратор',
    teacher:   'Викладач',
  };

  return (
    <span className={`${styles.badge} ${styles[status] ?? ''}`}>
      {labelMap[status] ?? status}
    </span>
  );
}
