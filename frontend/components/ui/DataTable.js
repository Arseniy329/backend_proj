import styles from './DataTable.module.css';

/**
 * Generic data table atom.
 * @param {{ key: string, label: string, render?: (row) => ReactNode }[]} columns
 * @param {Object[]} rows
 * @param {string}   emptyMessage
 */
export default function DataTable({ columns, rows, emptyMessage = 'Даних немає.' }) {
  if (!rows || rows.length === 0) {
    return <p className={styles.empty}>{emptyMessage}</p>;
  }

  return (
    <div className={styles.wrapper}>
      <table className={styles.table}>
        <thead>
          <tr>
            {columns.map((col) => (
              <th key={col.key} className={styles.th}>{col.label}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, rowIndex) => (
            <tr key={row.id ?? rowIndex} className={styles.tr}>
              {columns.map((col) => (
                <td key={col.key} className={styles.td}>
                  {col.render ? col.render(row) : (row[col.key] ?? '—')}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
