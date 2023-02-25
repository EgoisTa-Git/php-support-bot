"""Основной модуль ТГ бота"""

from users.models import CustomUser
from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler


class TGBot(object):
    """Описывает работу ТГ бота"""
    def __init__(self, tg_token, states_functions) -> None:
        self.tg_token = tg_token
        self.states_functions = states_functions
        self.updater = Updater(token=self.tg_token)
        self.updater.dispatcher.add_handler(CommandHandler('start', self.handle_users_reply))

    def handle_users_reply(self, bot, update):
        """Метод, который запускается при любом сообщении от пользователя и решает как его обработать"""
        if update.message:
            user_reply = update.message.text
            chat_id = update.message.chat_id
        elif update.callback_query:
            user_reply = update.callback_query.data
            chat_id = update.callback_query.message.chat_id
        else:
            return

        if user_reply == '/start':
            user_state = 'START'
        else:
            user = CustomUser.objects.get(tg_id=chat_id)
            user_state = user.bot_state

        state_handler = self.states_functions[user_state]
        next_state = state_handler(bot, update)
        user.bot_state = next_state
        user.save()

def start(bot, update):
    """Метод вывода стартового диалога"""
    chat_id = update.message.chat_id
    try:
        user = CustomUser.objects.get(tg_id=chat_id)
        if user.role == 'client':
            return 'HANDLE_CLIENT'
        elif user.role == 'freelancer':
            return 'HANDLE_FREELANCER'
    except CustomUser.DoesNotExist:
        custom_keyboard = [['Заказчик', 'Фрилансер']]
        reply_markup = ReplyKeyboardMarkup(custom_keyboard)

        update.message.reply_text('Привет! Выберите свою роль.', reply_markup=reply_markup)
        return 'HANDLE_ROLE'

def handle_role(bot, update):
    """Метод обработки выбора роли"""
        
