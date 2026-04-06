from django.conf import settings
from django.db import models


class Branch(models.Model):
    """
    Гілка (філія) навчального закладу.
    Поля: назва, адреса, місто, статус.
    Підтримує архівування замість видалення.
    """

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Активна'
        ARCHIVED = 'archived', 'Архівована'

    name = models.CharField('Назва', max_length=255)
    address = models.CharField('Адреса', max_length=255)
    city = models.CharField('Місто', max_length=100)
    status = models.CharField(
        'Статус',
        max_length=10,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    created_at = models.DateTimeField('Дата створення', auto_now_add=True)

    class Meta:
        verbose_name = 'Гілка'
        verbose_name_plural = 'Гілки'

    def __str__(self):
        return f'{self.name} ({self.city})'

    def archive(self):
        """Архівувати гілку замість видалення."""
        self.status = self.Status.ARCHIVED
        self.save(update_fields=['status'])

    def restore(self):
        """Відновити гілку з архіву."""
        self.status = self.Status.ACTIVE
        self.save(update_fields=['status'])

    @property
    def is_archived(self):
        return self.status == self.Status.ARCHIVED


class Subject(models.Model):
    """
    Предмет (дисципліна).
    M2M зв'язок із Branch — предмет може викладатися в кількох гілках.
    """

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Активний'
        ARCHIVED = 'archived', 'Архівований'

    name = models.CharField('Назва', max_length=255)
    description = models.TextField('Опис', blank=True)
    status = models.CharField(
        'Статус',
        max_length=10,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    branches = models.ManyToManyField(
        Branch,
        verbose_name='Гілки',
        related_name='subjects',
        blank=True,
    )
    created_at = models.DateTimeField('Дата створення', auto_now_add=True)

    class Meta:
        verbose_name = 'Предмет'
        verbose_name_plural = 'Предмети'

    def __str__(self):
        return self.name


class Group(models.Model):
    """
    Навчальна група.
    FK → Branch, FK → Subject, FK → Teacher (User).
    M2M → Student.
    """

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Активна'
        INACTIVE = 'inactive', 'Неактивна'

    name = models.CharField('Назва', max_length=255)
    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        verbose_name='Гілка',
        related_name='groups',
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        verbose_name='Предмет',
        related_name='groups',
    )
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        verbose_name='Викладач',
        related_name='teaching_groups',
        null=True,
        blank=True,
        limit_choices_to={'role': 'teacher'},
    )
    students = models.ManyToManyField(
        'students.Student',
        verbose_name='Студенти',
        related_name='groups',
        blank=True,
    )
    status = models.CharField(
        'Статус',
        max_length=10,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    created_at = models.DateTimeField('Дата створення', auto_now_add=True)

    class Meta:
        verbose_name = 'Група'
        verbose_name_plural = 'Групи'

    def __str__(self):
        return f'{self.name} — {self.subject.name} ({self.branch.name})'


class SubscriptionPlan(models.Model):
    """
    Абонемент / підписка.
    Визначає кількість занять, ціну та термін дії.
    """

    name = models.CharField('Назва', max_length=255)
    lessons_count = models.PositiveIntegerField('Кількість занять')
    price = models.DecimalField('Ціна', max_digits=10, decimal_places=2)
    duration_days = models.PositiveIntegerField('Тривалість (днів)', default=30)
    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        verbose_name='Гілка',
        related_name='subscription_plans',
    )
    created_at = models.DateTimeField('Дата створення', auto_now_add=True)

    class Meta:
        verbose_name = 'Абонемент'
        verbose_name_plural = 'Абонементи'

    def __str__(self):
        return f'{self.name} — {self.lessons_count} занять ({self.price} грн)'


class Lesson(models.Model):
    """
    Заняття (урок).
    FK → Group, FK → Teacher.
    """

    class Status(models.TextChoices):
        SCHEDULED = 'scheduled', 'Заплановано'
        COMPLETED = 'completed', 'Проведено'
        CANCELLED = 'cancelled', 'Скасовано'

    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        verbose_name='Група',
        related_name='lessons',
    )
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        verbose_name='Викладач',
        related_name='lessons',
        null=True,
        blank=True,
    )
    date = models.DateField('Дата')
    start_time = models.TimeField('Час початку')
    end_time = models.TimeField('Час закінчення')
    topic = models.CharField('Тема', max_length=255, blank=True)
    status = models.CharField(
        'Статус',
        max_length=10,
        choices=Status.choices,
        default=Status.SCHEDULED,
    )
    created_at = models.DateTimeField('Дата створення', auto_now_add=True)

    class Meta:
        verbose_name = 'Заняття'
        verbose_name_plural = 'Заняття'
        ordering = ['date', 'start_time']

    def __str__(self):
        return f'{self.group.name} — {self.date} {self.start_time}'


class Attendance(models.Model):
    """
    Відвідування.
    FK → Lesson, FK → Student.
    """

    class Status(models.TextChoices):
        PRESENT = 'present', 'Присутній'
        ABSENT = 'absent', 'Відсутній'
        LATE = 'late', 'Запізнився'

    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        verbose_name='Заняття',
        related_name='attendances',
    )
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        verbose_name='Студент',
        related_name='attendances',
    )
    status = models.CharField(
        'Статус',
        max_length=10,
        choices=Status.choices,
        default=Status.PRESENT,
    )
    note = models.TextField('Примітка', blank=True)
    created_at = models.DateTimeField('Дата створення', auto_now_add=True)

    class Meta:
        verbose_name = 'Відвідування'
        verbose_name_plural = 'Відвідування'
        unique_together = ('lesson', 'student')

    def __str__(self):
        return f'{self.student} — {self.lesson} ({self.get_status_display()})'
