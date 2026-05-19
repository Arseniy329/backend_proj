'use client';

import { useState } from 'react';
import DataTable from '@/components/ui/DataTable';
import StatusBadge from '@/components/ui/StatusBadge';
import Button from '@/components/ui/Button';
import Modal from '@/components/ui/Modal';
import ConfirmDialog from '@/components/ui/ConfirmDialog';
import GroupForm from './GroupForm';
import styles from './GroupList.module.css';

export default function GroupList({ groups, branches, onEdit, onDelete, isAdmin }) {
  const [editTarget, setEditTarget]     = useState(null);
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [isDeleting, setIsDeleting]     = useState(false);

  const branchMap = Object.fromEntries(branches.map((b) => [b.id, b.name]));

  const columns = [
    { key: 'name',   label: 'Назва' },
    { key: 'branch', label: 'Філія', render: (r) => branchMap[r.branch] ?? '—' },
    { key: 'status', label: 'Статус', render: (r) => <StatusBadge status={r.status} /> },
    ...(isAdmin ? [{
      key: 'actions', label: '',
      render: (r) => (
        <div className={styles.rowActions}>
          <Button size="sm" variant="ghost" onClick={() => setEditTarget(r)}>Редаг.</Button>
          <Button size="sm" variant="danger" onClick={() => setDeleteTarget(r)}>Деактивувати</Button>
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
      <DataTable columns={columns} rows={groups} emptyMessage="Групи не знайдено." />

      <Modal isOpen={!!editTarget} title="Редагування групи" onClose={() => setEditTarget(null)}>
        {editTarget && <GroupForm defaultValues={editTarget} branches={branches} onSubmit={handleEdit} onCancel={() => setEditTarget(null)} />}
      </Modal>

      <Modal isOpen={!!deleteTarget} title="Деактивувати групу?" onClose={() => setDeleteTarget(null)} size="sm">
        <ConfirmDialog
          message={`Деактивувати групу "${deleteTarget?.name}"?`}
          confirmLabel="Деактивувати"
          onConfirm={handleDelete}
          onCancel={() => setDeleteTarget(null)}
          isLoading={isDeleting}
        />
      </Modal>
    </>
  );
}
