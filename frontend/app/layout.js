import './globals.css';
import { AuthProvider } from '@/context/AuthContext';

export const metadata = {
  title: 'EduPlatform — Управління навчанням',
  description: 'Система управління навчальними філіями, групами, студентами та заняттями.',
};

export default function RootLayout({ children }) {
  return (
    <html lang="uk">
      <body>
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
