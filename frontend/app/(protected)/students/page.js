'use client';

import { useState } from 'react';
import { useStudents } from '@/hooks/useStudents';
import { useBranches } from '@/hooks/useBranches';
import PageHeader from '@/components/ui/PageHeader';
import SearchInput from '@/components/ui/SearchInput';
import Button from '@/components/ui/Button';
import Modal from '@/components/ui/Modal';
import StudentList from '@/components/students/StudentList';
import StudentForm from '@/components/students/StudentForm';
import styles from './students.module.css';

export default function StudentsPage() {
  const { students, loading, error, addStudent, editStudent, removeStudent, recoverStudent, setParams } = useStudents();
  const { branches } = useBranches();
  const [search, setSearch]         = useState('');
  const [showCreate, setShowCreate] = useState(false);

  function handleSearch(value) {
    setSearch(value);
    setParams({ search: value });
  }

  async function handleCreate(data) {
    await addStudent(data);
    setShowCreate(false);
  }

  return (
    <div>
      <PageHeader
        title="Студенти"
        subtitle="Реєстрація та управління студентами"
        actions={
          <>
            <SearchInput value={search} onChange={handleSearch} placeholder="Пошук студента…" />
            <Button id="btn-create-student" onClick={() => setShowCreate(true)}>+ Зареєструвати</Button>
          </>
        }
      />

      {error   && <p className={styles.error}>{error}</p>}
      {loading && <p className={styles.loading}>Завантаження…</p>}

      {!loading && (
        <StudentList
          students={students}
          branches={branches}
          onEdit={editStudent}
          onDelete={removeStudent}
          onRestore={recoverStudent}
        />
      )}

      <Modal isOpen={showCreate} title="Реєстрація студента" size="lg" onClose={() => setShowCreate(false)}>
        <StudentForm branches={branches} onSubmit={handleCreate} onCancel={() => setShowCreate(false)} />
      </Modal>
    </div>
  );
}
