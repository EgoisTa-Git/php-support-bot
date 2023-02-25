"""Менеджмент команда запуска ТГ бота"""
from support_bot.tg_bot_main import TGBot, handle_role, start
from django.conf import settings
from django.core.management import BaseCommand

class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            tg_bot = TGBot(
                settings.TG_BOT_TOKEN,
                {
                    "START": start,
                    "HANDLE_ROLE": handle_role
                }
            )
        except Exception as err:
            print(err)
