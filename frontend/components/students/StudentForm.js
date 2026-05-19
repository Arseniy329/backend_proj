'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import FormField from '@/components/ui/FormField';
import SelectField from '@/components/ui/SelectField';
import Button from '@/components/ui/Button';
import styles from './StudentForm.module.css';

export default function StudentForm({ defaultValues = null, branches = [], onSubmit, onCancel }) {
  const [serverError, setServerError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { register, handleSubmit, formState: { errors } } = useForm({
    defaultValues: defaultValues ?? {
      first_name: '', last_name: '', phone: '',
      date_of_birth: '', parent_name: '', parent_phone: '',
      parent_email: '', branch: '',
    },
  });

  async function handleFormSubmit(values) {
    setIsSubmitting(true);
    setServerError('');
    try {
      const payload = { ...values, branch: values.branch ? Number(values.branch) : null };
      await onSubmit(payload);
    } catch (err) {
      const d = err.response?.data;
      setServerError(d?.detail ?? d?.first_name?.[0] ?? 'Помилка збереження.');
    } finally {
      setIsSubmitting(false);
    }
  }

  const branchOptions = branches.map((b) => ({ value: String(b.id), label: b.name }));

  return (
    <form className={styles.form} onSubmit={handleSubmit(handleFormSubmit)} noValidate>
      <div className={styles.grid2}>
        <FormField id="s-first-name" label="Ім'я" placeholder="Іван"
          registration={register('first_name', { required: "Введіть ім'я" })}
          error={errors.first_name?.message} />
        <FormField id="s-last-name" label="Прізвище" placeholder="Петренко"
          registration={register('last_name', { required: 'Введіть прізвище' })}
          error={errors.last_name?.message} />
      </div>

      <div className={styles.grid2}>
        <FormField id="s-phone" label="Телефон" type="tel" placeholder="+380991234567"
          registration={register('phone')} />
        <FormField id="s-dob" label="Дата народження" type="date"
          registration={register('date_of_birth')} />
      </div>

      <SelectField id="s-branch" label="Філія" options={branchOptions}
        placeholder="— без філії —" registration={register('branch')} />

      <FormField id="s-parent-name" label="ПІБ батьків / опікуна" placeholder="Петренко Олена"
        registration={register('parent_name')} />

      <div className={styles.grid2}>
        <FormField id="s-parent-phone" label="Телефон батьків" type="tel" placeholder="+380991234567"
          registration={register('parent_phone')} />
        <FormField id="s-parent-email" label="Email батьків" type="email" placeholder="example@mail.com"
          registration={register('parent_email', {
            pattern: { value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/, message: 'Невірний email' },
          })}
          error={errors.parent_email?.message} />
      </div>

      {serverError && <p className={styles.error}>{serverError}</p>}

      <div className={styles.actions}>
        <Button variant="secondary" type="button" onClick={onCancel}>Скасувати</Button>
        <Button variant="primary" type="submit" disabled={isSubmitting}>
          {isSubmitting ? 'Збереження…' : defaultValues ? 'Зберегти' : 'Зареєструвати'}
        </Button>
      </div>
    </form>
  );
}
