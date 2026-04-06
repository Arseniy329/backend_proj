from django.conf import settings
from django.db import models


class Branch(models.Model):
    """
    Гілка (філія) навчального закладу.
    Поля: назва, адреса, місто, статус.
    """

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Активна'
        INACTIVE = 'inactive', 'Неактивна'

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


class Subject(models.Model):
    """
    Предмет (дисципліна).
    M2M зв'язок із Branch — предмет може викладатися в кількох гілках.
    """

    name = models.CharField('Назва', max_length=255)
    description = models.TextField('Опис', blank=True)
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
