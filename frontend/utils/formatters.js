/**
 * Pure formatting utilities — no React, no side-effects.
 */

/**
 * Format an ISO date string to a localised display string.
 * @param {string|null} isoString
 * @returns {string}
 */
export function formatDate(isoString) {
  if (!isoString) return '—';
  return new Date(isoString).toLocaleDateString('uk-UA', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  });
}

/**
 * Format an ISO datetime string.
 * @param {string|null} isoString
 * @returns {string}
 */
export function formatDateTime(isoString) {
  if (!isoString) return '—';
  return new Date(isoString).toLocaleString('uk-UA', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

/**
 * Return first + last name from an object or a plain fallback string.
 * @param {Object} user
 * @returns {string}
 */
export function formatFullName(user) {
  if (!user) return '—';
  const parts = [user.last_name, user.first_name].filter(Boolean);
  return parts.join(' ') || '—';
}

/**
 * Map raw API status keys to Ukrainian display labels.
 * @param {string} status
 * @returns {string}
 */
export function formatStatus(status) {
  const map = {
    active:     'Активний',
    inactive:   'Неактивний',
    archived:   'Архів',
    scheduled:  'Заплановано',
    completed:  'Проведено',
    cancelled:  'Скасовано',
    present:    'Присутній',
    absent:     'Відсутній',
    late:       'Запізнився',
    admin:      'Адміністратор',
    teacher:    'Викладач',
  };
  return map[status] ?? status ?? '—';
}

/**
 * Truncate a string to a given length.
 * @param {string} str
 * @param {number} max
 * @returns {string}
 */
export function truncate(str, max = 60) {
  if (!str) return '—';
  return str.length > max ? `${str.slice(0, max)}…` : str;
}
