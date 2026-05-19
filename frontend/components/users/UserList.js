'use client';

import { useState } from 'react';
import StatusBadge from '@/components/ui/StatusBadge';
import Button from '@/components/ui/Button';
import Modal from '@/components/ui/Modal';
import ConfirmDialog from '@/components/ui/ConfirmDialog';
import UserForm from './UserForm';
import styles from './UserList.module.css';

/**
 * Renders the users table with inline edit and delete modals.
 *
 * @param {Object[]} users      - Array of user objects from the API
 * @param {Function} onEdit     - (id, formData) => Promise<void>
 * @param {Function} onDelete   - (id) => Promise<void>
 */
export default function UserList({ users = [], onEdit, onDelete }) {
  const [editTarget, setEditTarget]     = useState(null);
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [isDeleting, setIsDeleting]     = useState(false);

  async function handleEdit(formData) {
    await onEdit(editTarget.id, formData);
    setEditTarget(null);
  }

  async function handleDelete() {
    setIsDeleting(true);
    try {
      await onDelete(deleteTarget.id);
      setDeleteTarget(null);
    } finally {
      setIsDeleting(false);
    }
  }

  if (!users.length) {
    return <p className={styles.empty}>Користувачів не знайдено.</p>;
  }

  return (
    <>
      <div className={styles.tableWrapper}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th className={styles.th}>Телефон</th>
              <th className={styles.th}>Прізвище</th>
              <th className={styles.th}>Ім'я</th>
              <th className={styles.th}>Роль</th>
              <th className={styles.th}>Статус</th>
              <th className={styles.th}></th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user.id} className={styles.tr}>
                <td className={styles.td}>{user.phone ?? '—'}</td>
                <td className={styles.td}>{user.last_name || '—'}</td>
                <td className={styles.td}>{user.first_name || '—'}</td>
                <td className={styles.td}>
                  <StatusBadge status={user.role} />
                </td>
                <td className={styles.td}>
                  <StatusBadge status={user.is_active ? 'active' : 'inactive'} />
                </td>
                <td className={styles.td}>
                  <div className={styles.rowActions}>
                    <Button
                      size="sm"
                      variant="ghost"
                      id={`btn-edit-user-${user.id}`}
                      onClick={() => setEditTarget(user)}
                    >
                      Редаг.
                    </Button>
                    <Button
                      size="sm"
                      variant="danger"
                      id={`btn-delete-user-${user.id}`}
                      onClick={() => setDeleteTarget(user)}
                    >
                      Видалити
                    </Button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Edit modal */}
      <Modal
        isOpen={!!editTarget}
        title="Редагування користувача"
        onClose={() => setEditTarget(null)}
      >
        {editTarget && (
          <UserForm
            defaultValues={editTarget}
            onSubmit={handleEdit}
            onCancel={() => setEditTarget(null)}
          />
        )}
      </Modal>

      {/* Delete confirmation modal */}
      <Modal
        isOpen={!!deleteTarget}
        title="Видалити користувача?"
        onClose={() => setDeleteTarget(null)}
        size="sm"
      >
        <ConfirmDialog
          message={`Видалити обліковий запис «${deleteTarget?.last_name ?? ''} ${deleteTarget?.first_name ?? ''}»? Цю дію неможливо скасувати.`}
          confirmLabel="Видалити"
          onConfirm={handleDelete}
          onCancel={() => setDeleteTarget(null)}
          isLoading={isDeleting}
        />
      </Modal>
    </>
  );
}
