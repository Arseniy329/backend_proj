'use client';

import { useState } from 'react';
import DataTable from '@/components/ui/DataTable';
import StatusBadge from '@/components/ui/StatusBadge';
import Button from '@/components/ui/Button';
import Modal from '@/components/ui/Modal';
import ConfirmDialog from '@/components/ui/ConfirmDialog';
import StudentForm from './StudentForm';
import { formatDate } from '@/utils/formatters';
import styles from './StudentList.module.css';

export default function StudentList({ students, branches, onEdit, onDelete, onRestore }) {
  const [editTarget, setEditTarget]     = useState(null);
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [isDeleting, setIsDeleting]     = useState(false);

  const branchMap = Object.fromEntries(branches.map((b) => [b.id, b.name]));

  const columns = [
    { key: 'last_name',  label: 'Прізвище' },
    { key: 'first_name', label: "Ім'я" },
    { key: 'phone',      label: 'Телефон' },
    { key: 'branch',     label: 'Філія', render: (r) => branchMap[r.branch] ?? '—' },
    { key: 'date_of_birth', label: 'Народження', render: (r) => formatDate(r.date_of_birth) },
    { key: 'status',     label: 'Статус', render: (r) => <StatusBadge status={r.status} /> },
    {
      key: 'actions', label: '',
      render: (r) => (
        <div className={styles.rowActions}>
          <Button size="sm" variant="ghost" onClick={() => setEditTarget(r)}>Редаг.</Button>
          {r.is_archived
            ? <Button size="sm" variant="secondary" onClick={() => onRestore(r.id)}>Відновити</Button>
            : <Button size="sm" variant="danger" onClick={() => setDeleteTarget(r)}>Архів</Button>
          }
        </div>
      ),
    },
  ];

  async function handleEdit(d) { await onEdit(editTarget.id, d); setEditTarget(null); }
  async function handleDelete() {
    setIsDeleting(true);
    try { await onDelete(deleteTarget.id); setDeleteTarget(null); }
    finally { setIsDeleting(false); }
  }

  return (
    <>
      <DataTable columns={columns} rows={students} emptyMessage="Студентів не знайдено." />

      <Modal isOpen={!!editTarget} title="Редагування студента" onClose={() => setEditTarget(null)} size="lg">
        {editTarget && <StudentForm defaultValues={editTarget} branches={branches} onSubmit={handleEdit} onCancel={() => setEditTarget(null)} />}
      </Modal>

      <Modal isOpen={!!deleteTarget} title="Архівувати студента?" onClose={() => setDeleteTarget(null)} size="sm">
        <ConfirmDialog
          message={`Архівувати "${deleteTarget?.last_name} ${deleteTarget?.first_name}"?`}
          confirmLabel="Архівувати"
          onConfirm={handleDelete}
          onCancel={() => setDeleteTarget(null)}
          isLoading={isDeleting}
        />
      </Modal>
    </>
  );
}
