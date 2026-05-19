'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useAuth } from '@/context/AuthContext';
import { useRouter } from 'next/navigation';
import FormField from '@/components/ui/FormField';
import Button from '@/components/ui/Button';
import styles from './LoginForm.module.css';

export default function LoginForm() {
  const { login } = useAuth();
  const router = useRouter();
  const [serverError, setServerError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({ defaultValues: { phone: '', password: '' } });

  async function onSubmit(values) {
    setIsSubmitting(true);
    setServerError('');
    try {
      const user = await login(values.phone, values.password);
      router.replace('/dashboard');
    } catch (err) {
      const detail = err.response?.data?.detail ?? err.response?.data?.non_field_errors?.[0];
      setServerError(detail ?? 'Невірний номер телефону або пароль.');
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className={styles.card}>
      <h1 className={styles.heading}>Вхід</h1>
      <p className={styles.sub}>Education Platform — управління навчанням</p>

      <form className={styles.form} onSubmit={handleSubmit(onSubmit)} noValidate>
        <FormField
          id="phone"
          label="Номер телефону"
          type="tel"
          placeholder="+380991234567"
          registration={register('phone', {
            required: "Введіть номер телефону",
            pattern: { value: /^\+?\d{10,15}$/, message: "Невірний формат номера" },
          })}
          error={errors.phone?.message}
        />

        <FormField
          id="password"
          label="Пароль"
          type="password"
          placeholder="••••••••"
          registration={register('password', { required: "Введіть пароль" })}
          error={errors.password?.message}
        />

        {serverError && <p className={styles.serverError}>{serverError}</p>}

        <Button id="btn-login" type="submit" variant="primary" disabled={isSubmitting}>
          {isSubmitting ? 'Вхід…' : 'Увійти'}
        </Button>
      </form>
    </div>
  );
}
