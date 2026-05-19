'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import FormField from '@/components/ui/FormField';
import Button from '@/components/ui/Button';
import styles from './SubjectForm.module.css';

export default function SubjectForm({ defaultValues = null, onSubmit, onCancel }) {
  const [serverError, setServerError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { register, handleSubmit, formState: { errors } } = useForm({
    defaultValues: defaultValues ?? { name: '', description: '' },
  });

  async function handleFormSubmit(values) {
    setIsSubmitting(true);
    setServerError('');
    try {
      await onSubmit(values);
    } catch (err) {
      const d = err.response?.data;
      setServerError(d?.detail ?? d?.name?.[0] ?? 'Помилка збереження.');
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form className={styles.form} onSubmit={handleSubmit(handleFormSubmit)} noValidate>
      <FormField
        id="subj-name"
        label="Назва предмету"
        placeholder="Математика"
        registration={register('name', { required: 'Введіть назву' })}
        error={errors.name?.message}
      />
      <div className={styles.field}>
        <label htmlFor="subj-desc" className={styles.label}>Опис</label>
        <textarea
          id="subj-desc"
          className={styles.textarea}
          placeholder="Короткий опис предмету…"
          rows={3}
          {...register('description')}
        />
      </div>
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
