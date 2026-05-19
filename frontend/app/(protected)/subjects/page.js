'use client';

import { useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { useSubjects } from '@/hooks/useSubjects';
import PageHeader from '@/components/ui/PageHeader';
import SearchInput from '@/components/ui/SearchInput';
import Button from '@/components/ui/Button';
import Modal from '@/components/ui/Modal';
import SubjectList from '@/components/subjects/SubjectList';
import SubjectForm from '@/components/subjects/SubjectForm';
import styles from './subjects.module.css';

export default function SubjectsPage() {
  const { user } = useAuth();
  const isAdmin = user?.role === 'admin';

  const { subjects, loading, error, addSubject, editSubject, removeSubject, setParams } = useSubjects();
  const [search, setSearch]         = useState('');
  const [showCreate, setShowCreate] = useState(false);

  function handleSearch(value) {
    setSearch(value);
    setParams({ search: value });
  }

  async function handleCreate(data) {
    await addSubject(data);
    setShowCreate(false);
  }

  return (
    <div>
      <PageHeader
        title="Предмети"
        subtitle="Управління навчальними предметами"
        actions={
          <>
            <SearchInput value={search} onChange={handleSearch} placeholder="Пошук предмету…" />
            {isAdmin && (
              <Button id="btn-create-subject" onClick={() => setShowCreate(true)}>+ Новий предмет</Button>
            )}
          </>
        }
      />

      {error   && <p className={styles.error}>{error}</p>}
      {loading && <p className={styles.loading}>Завантаження…</p>}

      {!loading && (
        <SubjectList
          subjects={subjects}
          isAdmin={isAdmin}
          onEdit={editSubject}
          onDelete={removeSubject}
        />
      )}

      <Modal isOpen={showCreate} title="Новий предмет" onClose={() => setShowCreate(false)}>
        <SubjectForm onSubmit={handleCreate} onCancel={() => setShowCreate(false)} />
      </Modal>
    </div>
  );
}
