from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    """
    Менеджер для кастомної моделі користувача,
    де ідентифікатором є номер телефону.
    """

    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError('Номер телефону є обов\'язковим')
        extra_fields.setdefault('is_active', True)
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', CustomUser.Role.ADMIN)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Суперкористувач повинен мати is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Суперкористувач повинен мати is_superuser=True.')

        return self.create_user(phone, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Кастомна модель користувача.
    Ідентифікатор — номер телефону (не email).
    Ролі: ADMIN, TEACHER.
    """

    class Role(models.TextChoices):
        ADMIN = 'admin', 'Адміністратор'
        TEACHER = 'teacher', 'Викладач'

    phone = models.CharField(
        'Номер телефону',
        max_length=20,
        unique=True,
    )
    first_name = models.CharField('Ім\'я', max_length=150, blank=True)
    last_name = models.CharField('Прізвище', max_length=150, blank=True)
    role = models.CharField(
        'Роль',
        max_length=10,
        choices=Role.choices,
        default=Role.TEACHER,
    )
    is_active = models.BooleanField('Активний', default=True)
    is_staff = models.BooleanField('Персонал', default=False)
    date_joined = models.DateTimeField('Дата реєстрації', default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = 'Користувач'
        verbose_name_plural = 'Користувачі'

    def __str__(self):
        return f'{self.first_name} {self.last_name} ({self.phone})'

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    @property
    def is_teacher(self):
        return self.role == self.Role.TEACHER
