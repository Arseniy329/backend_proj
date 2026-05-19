'use client';

import { useState } from 'react';
import DataTable from '@/components/ui/DataTable';
import StatusBadge from '@/components/ui/StatusBadge';
import Button from '@/components/ui/Button';
import Modal from '@/components/ui/Modal';
import ConfirmDialog from '@/components/ui/ConfirmDialog';
import SubjectForm from './SubjectForm';
import { truncate } from '@/utils/formatters';
import styles from './SubjectList.module.css';

export default function SubjectList({ subjects, onEdit, onDelete, isAdmin }) {
  const [editTarget, setEditTarget]     = useState(null);
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [isDeleting, setIsDeleting]     = useState(false);

  const columns = [
    { key: 'name',        label: 'Назва' },
    { key: 'description', label: 'Опис', render: (r) => truncate(r.description, 50) },
    { key: 'status',      label: 'Статус', render: (r) => <StatusBadge status={r.status} /> },
    ...(isAdmin ? [{
      key: 'actions', label: '',
      render: (r) => (
        <div className={styles.rowActions}>
          <Button size="sm" variant="ghost" onClick={() => setEditTarget(r)}>Редаг.</Button>
          <Button size="sm" variant="danger" onClick={() => setDeleteTarget(r)}>Видалити</Button>
        </div>
      ),
    }] : []),
  ];

  async function handleEdit(d) { await onEdit(editTarget.id, d); setEditTarget(null); }
  async function handleDelete() {
    setIsDeleting(true);
    try { await onDelete(deleteTarget.id); setDeleteTarget(null); }
    finally { setIsDeleting(false); }
  }

  return (
    <>
      <DataTable columns={columns} rows={subjects} emptyMessage="Предметів не знайдено." />

      <Modal isOpen={!!editTarget} title="Редагування предмету" onClose={() => setEditTarget(null)}>
        {editTarget && <SubjectForm defaultValues={editTarget} onSubmit={handleEdit} onCancel={() => setEditTarget(null)} />}
      </Modal>

      <Modal isOpen={!!deleteTarget} title="Видалити предмет?" onClose={() => setDeleteTarget(null)} size="sm">
        <ConfirmDialog
          message={`Видалити предмет "${deleteTarget?.name}"?`}
          confirmLabel="Видалити"
          onConfirm={handleDelete}
          onCancel={() => setDeleteTarget(null)}
          isLoading={isDeleting}
        />
      </Modal>
    </>
  );
}
