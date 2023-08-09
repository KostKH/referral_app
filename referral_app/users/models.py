import datetime as dt

from django.apps import apps
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import IntegrityError, models
from django.utils.translation import gettext_lazy as _

from .utils import generate_sequense


class CustomUserManager(UserManager):
    """Класс для обработки операций с моделью User. Данный класс
    переопределяет методы создания пользователя и суперпользователя."""

    def _create_user(self, phone, password, **extra_fields):
        if not phone:
            raise ValueError('Должен быть указан номер телефона.')
        if not password:
            password = generate_sequense(60)

        GlobalUserModel = apps.get_model(
            self.model._meta.app_label, self.model._meta.object_name)

        user = self.model(phone=phone, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(phone, password, **extra_fields)

    def create_superuser(self, phone=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(phone, password, **extra_fields)


class User(AbstractUser):
    """Класс User создает БД SQL для хранения
    информации о пользователях."""

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    username = None
    email = models.EmailField(_('email address'), blank=True,)
    phone = models.PositiveBigIntegerField(
        'Номер телефона',
        unique=True,
        validators=[
            MinValueValidator(
                71000000000,
                message='Должно быть значение от 71000000000 до 79999999999'),
            MaxValueValidator(
                79999999999,
                message='Должно быть значение от 71000000000 до 79999999999')
        ]
    )
    verification_code = models.CharField(
        'Код верификации',
        max_length=4,
        blank=True,
        null=True,
    )
    verif_cutoff_timestamp = models.PositiveIntegerField(
        'Срок действия кода',
        blank=True,
        null=True,
    )
    invite_code = models.CharField(
        'Инвайт-код',
        max_length=6,
        blank=True,
        unique=True,
        null=True,
    )
    granted_code = models.CharField(
        'Полученный инвайт-код',
        max_length=6,
        blank=True,
    )

    class Meta:
        ordering = ['-id', 'phone']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return str(self.phone)

    def check_code(self, code):
        if dt.datetime.utcnow().timestamp() > self.verif_cutoff_timestamp:
            return False
        return bool(code == self.verification_code)

    def create_invite_code(self):
        while not self.invite_code:
            try:
                self.invite_code = generate_sequense(6)
                self.save()
            except IntegrityError:
                continue
