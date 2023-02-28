"""Менеджмент команда запуска ТГ бота"""
from support_bot.tg_frelance import handle_application_menu, handle_buy_subscribe,\
    handle_freelancer_register, handle_select_action, handle_select_order, handle_action_order
from support_bot.tg_customer import handler_check_subscribe, conformation_tariff, save_customer, handle_main_customer, \
    order_title, action_customer, order_start, order_description
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
                    # 'HANDLE_APPLICATION_MENU': handle_application_menu,
                    # 'HANDLE_BUY_SUBSCRIBE': handle_buy_subscribe,
                    'HANDLE_APPLICATION_MENU': handle_main_customer,
                    'HANDLE_BUY_SUBSCRIBE': conformation_tariff,
                    'SAVE_CUSTOMER': save_customer,
                    'ACTION_CUSTOMER': action_customer,
                    'ORDER_START': order_start,
                    'CUSTOMER_REG_ORDER_TITLE': order_title,
                    'CUSTOMER_REG_ORDER_DESCRIPTION': order_description,
                    'HANDLER_CHECK_SUBSCRIBE': handler_check_subscribe,
                    'HANDLE_FRELANCER_REGISTER': handle_freelancer_register,
                    'HANDLER_SELECT_ACTION': handle_select_action,
                    'HANDLE_SELECT_ORDER': handle_select_order,
                    'HANDLE_ACTION_ORDER': handle_action_order
                }
            )
            tg_bot.updater.start_polling()
            tg_bot.updater.idle()
        except Exception as err:
            print(err)
