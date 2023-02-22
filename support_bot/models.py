from datetime import timedelta

from django.db import models
from django.core.validators import MinValueValidator


class Tariff(models.Model):
    title = models.CharField(
        'Название',
        max_length=30,
        db_index=True,
    )
    max_requests = models.IntegerField(
        'Заявок в месяц',
        validators=[MinValueValidator(1)],
    )
    response_time = models.DurationField(
        'Время на ответ',
        default=timedelta(hours=12),
    )
    bind_freelancer = models.BooleanField(
        'Возможность закрепить фрилансера',
        default=False,
        db_index=True,
    )
    see_contacts = models.BooleanField(
        'Возможность увидеть контакты фрилансера',
        default=False,
        db_index=True,
    )
    price = models.DecimalField(
        'Цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        verbose_name = 'Тариф'
        verbose_name_plural = 'Тарифы'

    def __str__(self):
        return self.title
