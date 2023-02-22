from django.contrib.auth.models import AbstractUser
from django.db import models

ROLES = [
    ('manager', 'Менеджер'),
    ('client', 'Заказчик'),
    ('freelancer', 'Фрилансер'),
]


class CustomUser(AbstractUser):
    role = models.CharField(
        'Роль',
        max_length=30,
        choices=ROLES,
        blank=True,
    )
    tg_id = models.IntegerField(
        'ID в Telegram',
        unique=True,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
