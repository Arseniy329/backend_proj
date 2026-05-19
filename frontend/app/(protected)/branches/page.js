'use client';

import { useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { useBranches } from '@/hooks/useBranches';
import PageHeader from '@/components/ui/PageHeader';
import SearchInput from '@/components/ui/SearchInput';
import Button from '@/components/ui/Button';
import Modal from '@/components/ui/Modal';
import BranchList from '@/components/branches/BranchList';
import BranchForm from '@/components/branches/BranchForm';
import styles from './branches.module.css';

export default function BranchesPage() {
  const { user } = useAuth();
  const isAdmin = user?.role === 'admin';

  const { branches, loading, error, addBranch, editBranch, removeBranch, recoverBranch, setParams } = useBranches();
  const [search, setSearch]       = useState('');
  const [showCreate, setShowCreate] = useState(false);

  function handleSearch(value) {
    setSearch(value);
    setParams({ search: value });
  }

  async function handleCreate(data) {
    await addBranch(data);
    setShowCreate(false);
  }

  return (
    <div>
      <PageHeader
        title="Філії"
        subtitle="Управління навчальними філіями"
        actions={
          <>
            <SearchInput value={search} onChange={handleSearch} placeholder="Пошук філії…" />
            {isAdmin && (
              <Button id="btn-create-branch" onClick={() => setShowCreate(true)}>
                + Нова філія
              </Button>
            )}
          </>
        }
      />

      {error   && <p className={styles.error}>{error}</p>}
      {loading && <p className={styles.loading}>Завантаження…</p>}

      {!loading && (
        <BranchList
          branches={branches}
          isAdmin={isAdmin}
          onEdit={editBranch}
          onDelete={removeBranch}
          onRestore={recoverBranch}
        />
      )}

      <Modal isOpen={showCreate} title="Нова філія" onClose={() => setShowCreate(false)}>
        <BranchForm onSubmit={handleCreate} onCancel={() => setShowCreate(false)} />
      </Modal>
    </div>
  );
}
