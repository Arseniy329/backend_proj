'use client';

import { useState } from 'react';
import DataTable from '@/components/ui/DataTable';
import StatusBadge from '@/components/ui/StatusBadge';
import Button from '@/components/ui/Button';
import Modal from '@/components/ui/Modal';
import ConfirmDialog from '@/components/ui/ConfirmDialog';
import BranchForm from './BranchForm';
import styles from './BranchList.module.css';

/**
 * Renders the branches table with inline edit and delete modals.
 */
export default function BranchList({ branches, onEdit, onDelete, onRestore, isAdmin }) {
  const [editTarget, setEditTarget] = useState(null);
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const columns = [
    { key: 'name',    label: 'Назва' },
    { key: 'city',    label: 'Місто' },
    { key: 'address', label: 'Адреса' },
    {
      key: 'status',
      label: 'Статус',
      render: (row) => <StatusBadge status={row.is_archived ? 'archived' : 'active'} />,
    },
    ...(isAdmin ? [{
      key: 'actions',
      label: '',
      render: (row) => (
        <div className={styles.rowActions}>
          <Button size="sm" variant="ghost" onClick={() => setEditTarget(row)}>Редаг.</Button>
          {row.is_archived
            ? <Button size="sm" variant="secondary" onClick={() => onRestore(row.id)}>Відновити</Button>
            : <Button size="sm" variant="danger" onClick={() => setDeleteTarget(row)}>Архів</Button>
          }
        </div>
      ),
    }] : []),
  ];

  async function handleEdit(formData) {
    await onEdit(editTarget.id, formData);
    setEditTarget(null);
  }

  async function handleDelete() {
    setIsDeleting(true);
    try { await onDelete(deleteTarget.id); setDeleteTarget(null); }
    finally { setIsDeleting(false); }
  }

  return (
    <>
      <DataTable columns={columns} rows={branches} emptyMessage="Філій не знайдено." />

      <Modal isOpen={!!editTarget} title="Редагування філії" onClose={() => setEditTarget(null)}>
        {editTarget && (
          <BranchForm defaultValues={editTarget} onSubmit={handleEdit} onCancel={() => setEditTarget(null)} />
        )}
      </Modal>

      <Modal isOpen={!!deleteTarget} title="Архівувати філію?" onClose={() => setDeleteTarget(null)} size="sm">
        <ConfirmDialog
          message={`Архівувати "${deleteTarget?.name}"? Це приховає філію зі списку.`}
          confirmLabel="Архівувати"
          onConfirm={handleDelete}
          onCancel={() => setDeleteTarget(null)}
          isLoading={isDeleting}
        />
      </Modal>
    </>
  );
}
