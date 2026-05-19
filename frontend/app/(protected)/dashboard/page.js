'use client';

import { useAuth } from '@/context/AuthContext';
import styles from './dashboard.module.css';

export default function DashboardPage() {
  const { user } = useAuth();

  const roleLabel = user?.role === 'admin' ? 'Адміністратор' : 'Викладач';

  return (
    <div>
      <h1 className={styles.heading}>Огляд</h1>
      <p className={styles.welcome}>
        Вітаємо, <strong>{user?.full_name ?? user?.phone}</strong> — {roleLabel}
      </p>

      <div className={styles.grid}>
        <DashCard label="Філії"      href="/branches" />
        <DashCard label="Групи"      href="/groups" />
        <DashCard label="Студенти"   href="/students" />
        <DashCard label="Предмети"   href="/subjects" />
        <DashCard label="Заняття"    href="/lessons" />
        {user?.role === 'admin' && <DashCard label="Користувачі" href="/users" />}
      </div>
    </div>
  );
}

function DashCard({ label, href }) {
  return (
    <a href={href} className={styles.card}>
      <span className={styles.cardLabel}>{label}</span>
      <span className={styles.cardArrow}>→</span>
    </a>
  );
}
