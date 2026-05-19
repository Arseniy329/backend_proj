'use client';

import { useState } from 'react';
import { useLessons } from '@/hooks/useLessons';
import { useGroups } from '@/hooks/useGroups';
import { useSubjects } from '@/hooks/useSubjects';
import { useUsers } from '@/hooks/useUsers';
import PageHeader from '@/components/ui/PageHeader';
import Button from '@/components/ui/Button';
import Modal from '@/components/ui/Modal';
import LessonList from '@/components/lessons/LessonList';
import LessonForm from '@/components/lessons/LessonForm';
import styles from './lessons.module.css';

export default function LessonsPage() {
  const { lessons, loading, error, addLesson, editLesson, removeLesson } = useLessons();
  const { groups }   = useGroups();
  const { subjects } = useSubjects();
  const { users }    = useUsers();

  const [showCreate, setShowCreate] = useState(false);

  const teachers = users.filter((u) => u.role === 'teacher' || u.role === 'admin');

  async function handleCreate(data) {
    await addLesson(data);
    setShowCreate(false);
  }

  return (
    <div>
      <PageHeader
        title="Заняття"
        subtitle="Розклад та управління навчальними заняттями"
        actions={
          <Button id="btn-create-lesson" onClick={() => setShowCreate(true)}>+ Нове заняття</Button>
        }
      />

      {error   && <p className={styles.error}>{error}</p>}
      {loading && <p className={styles.loading}>Завантаження…</p>}

      {!loading && (
        <LessonList
          lessons={lessons}
          groups={groups}
          subjects={subjects}
          teachers={teachers}
          onEdit={editLesson}
          onDelete={removeLesson}
        />
      )}

      <Modal isOpen={showCreate} title="Нове заняття" size="lg" onClose={() => setShowCreate(false)}>
        <LessonForm
          groups={groups} subjects={subjects} teachers={teachers}
          onSubmit={handleCreate} onCancel={() => setShowCreate(false)}
        />
      </Modal>
    </div>
  );
}
