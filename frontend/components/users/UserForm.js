'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import FormField from '@/components/ui/FormField';
import SelectField from '@/components/ui/SelectField';
import Button from '@/components/ui/Button';
import styles from './UserForm.module.css';

const ROLE_OPTIONS = [
  { value: 'admin', label: 'Адміністратор' },
  { value: 'teacher', label: 'Викладач' },
];

export default function UserForm({ defaultValues = null, onSubmit, onCancel }) {
  const [serverError, setServerError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { register, handleSubmit, formState: { errors } } = useForm({
    defaultValues: defaultValues ?? {
      phone: '', first_name: '', last_name: '',
      role: 'teacher', password: '',
    },
  });

  async function handleFormSubmit(values) {
    setIsSubmitting(true);
    setServerError('');
    try {
      const payload = { ...values };
      if (!payload.password) delete payload.password;
      await onSubmit(payload);
    } catch (err) {
      const d = err.response?.data;
      setServerError(d?.detail ?? d?.phone?.[0] ?? 'Помилка збереження.');
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form className={styles.form} onSubmit={handleSubmit(handleFormSubmit)} noValidate>
      <FormField
        id="u-phone" label="Номер телефону" type="tel" placeholder="+380991234567"
        registration={register('phone', { required: 'Введіть номер' })}
        error={errors.phone?.message}
      />
      <div className={styles.grid2}>
        <FormField id="u-last-name" label="Прізвище" placeholder="Іванов"
          registration={register('last_name')} />
        <FormField id="u-first-name" label="Ім'я" placeholder="Іван"
          registration={register('first_name')} />
      </div>
      <SelectField id="u-role" label="Роль" options={ROLE_OPTIONS} registration={register('role')} />
      <FormField
        id="u-password" label={defaultValues ? "Новий пароль (необов'язково)" : 'Пароль'}
        type="password" placeholder="••••••••"
        registration={register('password', { ...(!defaultValues && { required: 'Введіть пароль' }) })}
        error={errors.password?.message}
      />
      {serverError && <p className={styles.error}>{serverError}</p>}
      <div className={styles.actions}>
        <Button variant="secondary" type="button" onClick={onCancel}>Скасувати</Button>
        <Button variant="primary" type="submit" disabled={isSubmitting}>
          {isSubmitting ? 'Збереження…' : defaultValues ? 'Зберегти' : 'Створити'}
        </Button>
      </div>
    </form>
  );
}
