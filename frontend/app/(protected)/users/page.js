'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import { useUsers } from '@/hooks/useUsers';
import PageHeader from '@/components/ui/PageHeader';
import Button from '@/components/ui/Button';
import Modal from '@/components/ui/Modal';
import UserList from '@/components/users/UserList';
import UserForm from '@/components/users/UserForm';
import { useState } from 'react';
import styles from './users.module.css';

export default function UsersPage() {
  const { user } = useAuth();
  const router   = useRouter();

  /* Redirect non-admins away from this page */
  useEffect(() => {
    if (user && user.role !== 'admin') router.replace('/dashboard');
  }, [user, router]);

  const { users, loading, error, addUser, editUser, removeUser } = useUsers();
  const [showCreate, setShowCreate] = useState(false);

  if (!user || user.role !== 'admin') return null;

  async function handleCreate(data) {
    await addUser(data);
    setShowCreate(false);
  }

  return (
    <div>
      <PageHeader
        title="Користувачі"
        subtitle="Управління обліковими записами адміністраторів та викладачів"
        actions={
          <Button id="btn-create-user" onClick={() => setShowCreate(true)}>+ Новий користувач</Button>
        }
      />

      {error   && <p className={styles.error}>{error}</p>}
      {loading && <p className={styles.loading}>Завантаження…</p>}

      {!loading && <UserList users={users} onEdit={editUser} onDelete={removeUser} />}

      <Modal isOpen={showCreate} title="Новий користувач" onClose={() => setShowCreate(false)}>
        <UserForm onSubmit={handleCreate} onCancel={() => setShowCreate(false)} />
      </Modal>
    </div>
  );
}
