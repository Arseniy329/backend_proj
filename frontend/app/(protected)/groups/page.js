'use client';

import { useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { useGroups } from '@/hooks/useGroups';
import { useBranches } from '@/hooks/useBranches';
import PageHeader from '@/components/ui/PageHeader';
import SearchInput from '@/components/ui/SearchInput';
import Button from '@/components/ui/Button';
import Modal from '@/components/ui/Modal';
import GroupList from '@/components/groups/GroupList';
import GroupForm from '@/components/groups/GroupForm';
import styles from './groups.module.css';

export default function GroupsPage() {
  const { user } = useAuth();
  const isAdmin = user?.role === 'admin';

  const { groups, loading, error, addGroup, editGroup, removeGroup, setParams } = useGroups();
  const { branches } = useBranches();
  const [search, setSearch]         = useState('');
  const [showCreate, setShowCreate] = useState(false);

  function handleSearch(value) {
    setSearch(value);
    setParams({ search: value });
  }

  async function handleCreate(data) {
    await addGroup(data);
    setShowCreate(false);
  }

  return (
    <div>
      <PageHeader
        title="Групи"
        subtitle="Управління навчальними групами"
        actions={
          <>
            <SearchInput value={search} onChange={handleSearch} placeholder="Пошук групи…" />
            {isAdmin && (
              <Button id="btn-create-group" onClick={() => setShowCreate(true)}>
                + Нова група
              </Button>
            )}
          </>
        }
      />

      {error   && <p className={styles.error}>{error}</p>}
      {loading && <p className={styles.loading}>Завантаження…</p>}

      {!loading && (
        <GroupList
          groups={groups}
          branches={branches}
          isAdmin={isAdmin}
          onEdit={editGroup}
          onDelete={removeGroup}
        />
      )}

      <Modal isOpen={showCreate} title="Нова група" onClose={() => setShowCreate(false)}>
        <GroupForm branches={branches} onSubmit={handleCreate} onCancel={() => setShowCreate(false)} />
      </Modal>
    </div>
  );
}
