'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import FormField from '@/components/ui/FormField';
import SelectField from '@/components/ui/SelectField';
import Button from '@/components/ui/Button';
import styles from './GroupForm.module.css';

export default function GroupForm({ defaultValues = null, branches = [], onSubmit, onCancel }) {
  const [serverError, setServerError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { register, handleSubmit, formState: { errors } } = useForm({
    defaultValues: defaultValues ?? { name: '', branch: '', status: 'active' },
  });

  async function handleFormSubmit(values) {
    setIsSubmitting(true);
    setServerError('');
    try {
      await onSubmit({ ...values, branch: Number(values.branch) });
    } catch (err) {
      const d = err.response?.data;
      setServerError(d?.detail ?? d?.name?.[0] ?? 'Помилка збереження.');
    } finally {
      setIsSubmitting(false);
    }
  }

  const branchOptions = branches.map((b) => ({ value: String(b.id), label: b.name }));
  const statusOptions = [
    { value: 'active',   label: 'Активна' },
    { value: 'inactive', label: 'Неактивна' },
  ];

  return (
    <form className={styles.form} onSubmit={handleSubmit(handleFormSubmit)} noValidate>
      <FormField
        id="group-name"
        label="Назва групи"
        placeholder="Група А"
        registration={register('name', { required: 'Введіть назву' })}
        error={errors.name?.message}
      />
      <SelectField
        id="group-branch"
        label="Філія"
        options={branchOptions}
        registration={register('branch', { required: 'Виберіть філію' })}
        error={errors.branch?.message}
      />
      <SelectField
        id="group-status"
        label="Статус"
        options={statusOptions}
        registration={register('status')}
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
