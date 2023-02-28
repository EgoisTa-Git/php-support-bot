"""Основной модуль ТГ бота"""

import datetime
from support_bot.models import Subscription
from users.models import CustomUser
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram.ext import ConversationHandler


class TGBot(object):
    """Описывает работу ТГ бота"""
    def __init__(self, tg_token, states_functions) -> None:
        self.tg_token = tg_token
        self.states_functions = states_functions
        self.updater = Updater(token=self.tg_token, use_context=True)
        self.updater.dispatcher.add_handler(CallbackQueryHandler(self.get_user(self.handle_users_reply)))
        self.updater.dispatcher.add_handler(MessageHandler(Filters.text, self.get_user(self.handle_users_reply)))
        self.updater.dispatcher.add_handler(CommandHandler('start', self.get_user(self.handle_users_reply)))

    def handle_users_reply(self, update, context):
        """Метод, который запускается при любом сообщении от пользователя и решает как его обработать"""
        user = context.user_data['user']
        if update.message:
            user_reply = update.message.text
            chat_id = update.message.chat_id
            username = update.message.from_user.username
        elif update.callback_query:
            user_reply = update.callback_query.data
            chat_id = update.callback_query.message.chat_id
            username = update.callback_query.message.from_user.username
        else:
            return

        if user_reply == '/start':
            user_state = user.bot_state if user.bot_state else 'START'
        elif user_reply == 'Главное меню' and user.role == 'freelancer':
            user_state = 'HANDLE_FRELANCER_REGISTER'
        else:
            user_state = user.bot_state
            user_state = user_state if user_state else 'START'

        context.user_data.update({'chat_id': chat_id, 'username': username})

        state_handler = self.states_functions[user_state]
        next_state = state_handler(context.bot, update, context)
        user.bot_state = next_state
        user.save()

    def get_user(self, func):
        def wrapper(update, context):
            chat_id = context.user_data.get('chat_id')
            username = context.user_data.get('username')
            if not chat_id:
                chat_id = update.message.chat_id
                username = update.message.from_user.username
            user, created = CustomUser.objects.get_or_create(tg_id=chat_id, defaults={'username': username})
            if created:
                user.is_active = False
                user.save()
            context.user_data['user'] = user
            return func(update, context)
        return wrapper

def start(bot, update, context):
    """Метод вывода стартового диалога"""
    chat_id = update.message.chat_id
    user = context.user_data['user']
    if user.role == 'client' or user.role == 'freelancer':
        return user.bot_state
    else:
        custom_keyboard = [[InlineKeyboardButton('Заказчик', callback_data='client'),
                            InlineKeyboardButton('Фрилансер', callback_data='freelancer')]]
        reply_markup = InlineKeyboardMarkup(custom_keyboard)

        update.message.reply_text('Привет! Выберите свою роль.', reply_markup=reply_markup)
        return 'HANDLE_ROLE'

def handle_role(bot, update, context):
    """Метод обработки выбора роли"""
    user = context.user_data['user']
    chat_id = context.user_data['chat_id']
    role_selected = update.callback_query.data
    if role_selected == 'client':
        user.role = 'client'
        user.is_active = True
        user.save()
        active_subscribe = Subscription.objects.filter(user=user, expire_at__gte=datetime.now()).exists()
        if active_subscribe:
            return 'HANDLE_APPLICATION_MENU'
        return 'HANDLE_BUY_SUBSCRIBE'
    elif role_selected == 'freelancer':
        user.role = 'freelancer'
        user.save()
        bot.send_message(chat_id=chat_id, text='Для регистрации напишите администратору в ТГ @adminphpsupport')
        return 'HANDLE_FRELANCER_REGISTER'
    else:
        return 'HANDLE_ROLE'
