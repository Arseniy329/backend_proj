'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import Navbar from '@/components/layout/Navbar';
import Footer from '@/components/layout/Footer';
import styles from './protected.module.css';

/**
 * Auth guard layout for all protected routes.
 * Redirects unauthenticated visitors to /login.
 */
export default function ProtectedLayout({ children }) {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) {
      router.replace('/login');
    }
  }, [user, loading, router]);

  if (loading || !user) return null;

  return (
    <div className={styles.shell}>
      <Navbar />
      <main className={styles.main}>
        <div className={styles.content}>{children}</div>
      </main>
      <Footer />
    </div>
  );
}
