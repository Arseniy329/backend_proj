import LoginForm from '@/components/auth/LoginForm';
import styles from './login.module.css';

export const metadata = {
  title: 'Вхід — EduPlatform',
};

export default function LoginPage() {
  return (
    <main className={styles.page}>
      <LoginForm />
    </main>
  );
}
