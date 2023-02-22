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


class Request(models.Model):
    title = models.CharField(
        'Краткое описание',
        max_length=60,
    )
    description = models.TextField(
        'Описание проблемы',
        blank=True,
    )
    attachment = models.FileField(
        'Приложение',
        upload_to='attachments/%Y/%m/%d',
        blank=True,
    )
    done = models.BooleanField(
        'Заявка закрыта',
        default=False,
        db_index=True,
    )
    created_at = models.DateTimeField(
        'Дата создания',
        auto_now_add=True,
    )
    author = models.CharField(
        'Автор - заглушка',
        max_length=30,
    )
    freelancer = models.CharField(
        'Фрилансер - заглушка',
        max_length=30,
        blank=True,
    )

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
        ordering = ('created_at', )

    def __str__(self):
        return f'{self.created_at} - {self.title}'


class Subscription(models.Model):
    user = models.ForeignKey(
        'users.CustomUser',
        related_name='users',
        verbose_name='Заказчик',
        on_delete=models.CASCADE,
    )
    tariff = models.ForeignKey(
        'Tariff',
        verbose_name='Тариф',
        related_name='subscriptions',
        on_delete=models.CASCADE,
    )
    expire_at = models.DateTimeField(
        'Подписка активна до даты',
    )
    requests_created = models.IntegerField(
        'Заявок подано',
        default=0,
        validators=[MinValueValidator(0)],
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.tariff} - {self.user}'
