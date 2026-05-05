from .models import Lesson


CONFLICT_STATUSES = [Lesson.Status.SCHEDULED, Lesson.Status.COMPLETED]


def check_schedule_conflicts(
    date,
    start_time,
    end_time,
    teacher=None,
    student_ids=None,
    exclude_lesson_id=None,
):

    conflicts = []

    def _base_conflict_qs():
        qs = Lesson.objects.filter(
            date=date,
            status__in=CONFLICT_STATUSES,
            start_time__lt=end_time,
            end_time__gt=start_time,
        )
        if exclude_lesson_id:
            qs = qs.exclude(pk=exclude_lesson_id)
        return qs

    if teacher is not None:
        teacher_conflicts = _base_conflict_qs().filter(
            teacher=teacher,
        ).select_related('group', 'subject')

        for lesson in teacher_conflicts:
            conflicts.append({
                'type': 'teacher',
                'entity': str(teacher),
                'conflicting_lesson': str(lesson),
                'lesson_id': lesson.pk,
                'message': (
                    f'Викладач «{teacher}» вже має заняття '
                    f'{lesson.date} {lesson.start_time}–{lesson.end_time} '
                    f'(група «{lesson.group.name}»).'
                ),
            })

    if student_ids:
        student_conflict_qs = _base_conflict_qs().filter(
            group__students__id__in=student_ids,
        ).prefetch_related('group__students').select_related('group')

        for lesson in student_conflict_qs.distinct():
            conflicting_student_ids = set(
                lesson.group.students.filter(id__in=student_ids).values_list('id', flat=True)
            )
            for sid in conflicting_student_ids:
                conflicts.append({
                    'type': 'student',
                    'entity': f'студент ID={sid}',
                    'conflicting_lesson': str(lesson),
                    'lesson_id': lesson.pk,
                    'student_id': sid,
                    'message': (
                        f'Студент ID={sid} вже має заняття '
                        f'{lesson.date} {lesson.start_time}–{lesson.end_time} '
                        f'(група «{lesson.group.name}»).'
                    ),
                })

    return conflicts


def get_group_student_ids(group):

    return list(group.students.values_list('id', flat=True))
