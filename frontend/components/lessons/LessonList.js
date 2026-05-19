'use client';

import { useState } from 'react';
import DataTable from '@/components/ui/DataTable';
import StatusBadge from '@/components/ui/StatusBadge';
import Button from '@/components/ui/Button';
import Modal from '@/components/ui/Modal';
import ConfirmDialog from '@/components/ui/ConfirmDialog';
import LessonForm from './LessonForm';
import { formatDate } from '@/utils/formatters';
import styles from './LessonList.module.css';

export default function LessonList({ lessons, groups, subjects, teachers, onEdit, onDelete }) {
  const [editTarget, setEditTarget]     = useState(null);
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [isDeleting, setIsDeleting]     = useState(false);

  const groupMap   = Object.fromEntries(groups.map((g)   => [g.id, g.name]));
  const subjectMap = Object.fromEntries(subjects.map((s) => [s.id, s.name]));

  const columns = [
    { key: 'date',       label: 'Дата',     render: (r) => formatDate(r.date) },
    { key: 'start_time', label: 'Час',      render: (r) => `${r.start_time?.slice(0,5)} – ${r.end_time?.slice(0,5)}` },
    { key: 'group',      label: 'Група',    render: (r) => groupMap[r.group] ?? '—' },
    { key: 'subject',    label: 'Предмет',  render: (r) => subjectMap[r.subject] ?? '—' },
    { key: 'topic',      label: 'Тема',     render: (r) => r.topic || '—' },
    { key: 'room',       label: 'Ауд.',     render: (r) => r.room  || '—' },
    { key: 'status',     label: 'Статус',   render: (r) => <StatusBadge status={r.status} /> },
    {
      key: 'actions', label: '',
      render: (r) => (
        <div className={styles.rowActions}>
          <Button size="sm" variant="ghost"  onClick={() => setEditTarget(r)}>Редаг.</Button>
          <Button size="sm" variant="danger" onClick={() => setDeleteTarget(r)}>Видалити</Button>
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
      <DataTable columns={columns} rows={lessons} emptyMessage="Занять не знайдено." />

      <Modal isOpen={!!editTarget} title="Редагування заняття" onClose={() => setEditTarget(null)} size="lg">
        {editTarget && (
          <LessonForm
            defaultValues={editTarget}
            groups={groups} subjects={subjects} teachers={teachers}
            onSubmit={handleEdit} onCancel={() => setEditTarget(null)}
          />
        )}
      </Modal>

      <Modal isOpen={!!deleteTarget} title="Видалити заняття?" onClose={() => setDeleteTarget(null)} size="sm">
        <ConfirmDialog
          message={`Видалити заняття від ${formatDate(deleteTarget?.date)}?`}
          confirmLabel="Видалити"
          onConfirm={handleDelete}
          onCancel={() => setDeleteTarget(null)}
          isLoading={isDeleting}
        />
      </Modal>
    </>
  );
}
