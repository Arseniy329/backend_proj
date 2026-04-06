from django.db import models


class Student(models.Model):
    """
    Студент із контактними даними батьків.
    FK → Branch.
    Підтримує архівування замість видалення.
    """

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Активний'
        ARCHIVED = 'archived', 'Архівований'

    first_name = models.CharField('Ім\'я', max_length=150)
    last_name = models.CharField('Прізвище', max_length=150)
    phone = models.CharField('Телефон', max_length=20, blank=True)
    date_of_birth = models.DateField('Дата народження', null=True, blank=True)

    # Контактні дані батьків
    parent_name = models.CharField('ПІБ батьків', max_length=255, blank=True)
    parent_phone = models.CharField('Телефон батьків', max_length=20, blank=True)
    parent_email = models.EmailField('Email батьків', blank=True)

    branch = models.ForeignKey(
        'branches.Branch',
        on_delete=models.CASCADE,
        verbose_name='Гілка',
        related_name='students',
        null=True,
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
        verbose_name = 'Студент'
        verbose_name_plural = 'Студенти'

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    def archive(self):
        """Архівувати студента замість видалення."""
        self.status = self.Status.ARCHIVED
        self.save(update_fields=['status'])

    def restore(self):
        """Відновити студента з архіву."""
        self.status = self.Status.ACTIVE
        self.save(update_fields=['status'])

    @property
    def is_archived(self):
        return self.status == self.Status.ARCHIVED
