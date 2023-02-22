from django.contrib import admin

from support_bot.models import Tariff, Request, Subscription

admin.site.site_header = 'Сервис PHP Support'
admin.site.site_title = 'PHP Support'
admin.site.index_title = 'Панель администратора'


@admin.register(Tariff)
class TariffAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'max_requests',
        'response_time',
        'bind_freelancer',
        'see_contacts',
        'price',
    ]


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'created_at',
        'author',
        'freelancer',
        'done',
    ]
    list_filter = [
        'freelancer',
        'done',
    ]
    search_fields = [
        'title',
        'author',
    ]
    readonly_fields = (
        'created_at',
    )
    raw_id_fields = (
        'author',
        'freelancer',
    )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    raw_id_fields = (
        'user',
    )
    list_display = [
        'user',
        'tariff',
        'expire_at',
        'requests_created',
    ]
