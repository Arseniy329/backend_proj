'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import FormField from '@/components/ui/FormField';
import SelectField from '@/components/ui/SelectField';
import Button from '@/components/ui/Button';
import styles from './LessonForm.module.css';

const STATUS_OPTIONS = [
  { value: 'scheduled',  label: 'Заплановано' },
  { value: 'completed',  label: 'Проведено' },
  { value: 'cancelled',  label: 'Скасовано' },
];

export default function LessonForm({ defaultValues = null, groups = [], subjects = [], teachers = [], onSubmit, onCancel }) {
  const [serverError, setServerError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { register, handleSubmit, formState: { errors } } = useForm({
    defaultValues: defaultValues ?? {
      group: '', subject: '', teacher: '',
      date: '', start_time: '', end_time: '',
      topic: '', room: '', notes: '', status: 'scheduled',
    },
  });

  async function handleFormSubmit(values) {
    setIsSubmitting(true);
    setServerError('');
    try {
      const payload = {
        ...values,
        group:   Number(values.group),
        subject: values.subject  ? Number(values.subject)  : null,
        teacher: values.teacher  ? Number(values.teacher)  : null,
      };
      await onSubmit(payload);
    } catch (err) {
      const d = err.response?.data;
      setServerError(d?.detail ?? d?.non_field_errors?.[0] ?? 'Помилка збереження.');
    } finally {
      setIsSubmitting(false);
    }
  }

  const groupOptions   = groups.map((g)   => ({ value: String(g.id),   label: g.name }));
  const subjectOptions = subjects.map((s) => ({ value: String(s.id),   label: s.name }));
  const teacherOptions = teachers.map((t) => ({ value: String(t.id),   label: `${t.last_name} ${t.first_name}` }));

  return (
    <form className={styles.form} onSubmit={handleSubmit(handleFormSubmit)} noValidate>
      <SelectField id="l-group"   label="Група"    options={groupOptions}   registration={register('group',  { required: 'Виберіть групу' })} error={errors.group?.message} />
      <SelectField id="l-subject" label="Предмет"  options={subjectOptions} registration={register('subject')} placeholder="— без предмету —" />
      <SelectField id="l-teacher" label="Викладач" options={teacherOptions} registration={register('teacher')} placeholder="— без викладача —" />

      <FormField id="l-date"  label="Дата"          type="date" registration={register('date', { required: 'Вкажіть дату' })} error={errors.date?.message} />

      <div className={styles.grid2}>
        <FormField id="l-start" label="Початок" type="time" registration={register('start_time', { required: 'Вкажіть час' })} error={errors.start_time?.message} />
        <FormField id="l-end"   label="Кінець"  type="time" registration={register('end_time',   { required: 'Вкажіть час' })} error={errors.end_time?.message} />
      </div>

      <div className={styles.grid2}>
        <FormField id="l-topic" label="Тема"      placeholder="Назва теми" registration={register('topic')} />
        <FormField id="l-room"  label="Аудиторія" placeholder="А-101"      registration={register('room')} />
      </div>

      <SelectField id="l-status" label="Статус" options={STATUS_OPTIONS} registration={register('status')} />

      {serverError && <p className={styles.error}>{serverError}</p>}
      <div className={styles.actions}>
        <Button variant="secondary" type="button" onClick={onCancel}>Скасувати</Button>
        <Button variant="primary"   type="submit" disabled={isSubmitting}>
          {isSubmitting ? 'Збереження…' : defaultValues ? 'Зберегти' : 'Створити'}
        </Button>
      </div>
    </form>
  );
}
