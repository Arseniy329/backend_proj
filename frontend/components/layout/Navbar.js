'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import styles from './Navbar.module.css';

const ADMIN_LINKS = [
  { href: '/dashboard',    label: 'Огляд' },
  { href: '/branches',     label: 'Філії' },
  { href: '/groups',       label: 'Групи' },
  { href: '/students',     label: 'Студенти' },
  { href: '/subjects',     label: 'Предмети' },
  { href: '/lessons',      label: 'Заняття' },
  { href: '/users',        label: 'Користувачі' },
];

const TEACHER_LINKS = [
  { href: '/dashboard',    label: 'Огляд' },
  { href: '/groups',       label: 'Групи' },
  { href: '/students',     label: 'Студенти' },
  { href: '/lessons',      label: 'Заняття' },
];

export default function Navbar() {
  const { user, logout } = useAuth();
  const pathname = usePathname();

  const links = user?.role === 'admin' ? ADMIN_LINKS : TEACHER_LINKS;

  return (
    <header className={styles.header}>
      <nav className={styles.nav} aria-label="Головна навігація">
        <span className={styles.brand}>EduPlatform</span>

        <ul className={styles.links}>
          {links.map(({ href, label }) => (
            <li key={href}>
              <Link
                href={href}
                className={`${styles.link} ${pathname === href ? styles.active : ''}`}
              >
                {label}
              </Link>
            </li>
          ))}
        </ul>

        <div className={styles.user}>
          <span className={styles.userName}>{user?.full_name ?? user?.phone}</span>
          <button id="btn-logout" className={styles.logoutBtn} onClick={logout}>
            Вийти
          </button>
        </div>
      </nav>
    </header>
  );
}
