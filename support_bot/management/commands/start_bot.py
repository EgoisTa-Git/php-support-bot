"""Менеджмент команда запуска ТГ бота"""
from support_bot.tg_frelance import handle_application_menu, handle_buy_subscribe, handle_freelancer_register
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
                    "HANDLE_ROLE": handle_role,
                    'HANDLE_APPLICATION_MENU': handle_application_menu,
                    'HANDLE_BUY_SUBSCRIBE': handle_buy_subscribe,
                    'HANDLE_FRELANCER_REGISTER': handle_freelancer_register
                }
            )
            tg_bot.updater.start_polling()
            tg_bot.updater.idle()
        except Exception as err:
            print(err)
