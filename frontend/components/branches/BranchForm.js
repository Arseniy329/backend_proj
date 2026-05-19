'use client';

import { useForm } from 'react-hook-form';
import { useState } from 'react';
import FormField from '@/components/ui/FormField';
import Button from '@/components/ui/Button';
import styles from './BranchForm.module.css';

/**
 * Create / edit branch form.
 * @param {Object|null} defaultValues - populate when editing an existing branch
 * @param {(data) => Promise<void>} onSubmit
 * @param {() => void} onCancel
 */
export default function BranchForm({ defaultValues = null, onSubmit, onCancel }) {
  const [serverError, setServerError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { register, handleSubmit, formState: { errors } } = useForm({
    defaultValues: defaultValues ?? { name: '', address: '', city: '' },
  });

  async function handleFormSubmit(values) {
    setIsSubmitting(true);
    setServerError('');
    try {
      await onSubmit(values);
    } catch (err) {
      const data = err.response?.data;
      setServerError(data?.detail ?? data?.name?.[0] ?? 'Помилка збереження.');
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form className={styles.form} onSubmit={handleSubmit(handleFormSubmit)} noValidate>
      <FormField
        id="branch-name"
        label="Назва філії"
        placeholder="Філія «Центр»"
        registration={register('name', { required: 'Введіть назву' })}
        error={errors.name?.message}
      />
      <FormField
        id="branch-city"
        label="Місто"
        placeholder="Київ"
        registration={register('city', { required: 'Введіть місто' })}
        error={errors.city?.message}
      />
      <FormField
        id="branch-address"
        label="Адреса"
        placeholder="вул. Хрещатик, 1"
        registration={register('address', { required: 'Введіть адресу' })}
        error={errors.address?.message}
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
