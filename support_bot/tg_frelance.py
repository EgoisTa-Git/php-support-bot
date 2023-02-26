"""Модуль телеграм-бота для фрилансера"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def handle_application_menu(bot, update, context):
    """TODO Это заглушка для реализации работы заказчика"""

def handle_buy_subscribe(bot, update, context):
    """TODO Заглушка для реализации функционала покупки подписки"""

def handle_freelancer_register(bot, update, context):
    """Регистрация фрилансера"""
    user = context.user_data['user']
    chat_id = context.user_data['chat_id']
    if user.is_active:
        custom_keyboard = [[InlineKeyboardButton('Выбрать заказ', callback_data='new_order'),
                            InlineKeyboardButton('Заявки в работе', callback_data='orders')]]
        reply_markup = InlineKeyboardMarkup(custom_keyboard)

        update.message.reply_text('Привет! Выберите дальнейшее действие.', reply_markup=reply_markup)
        return 'HANDLER_SELECT_ACTION'
    bot.send_message(chat_id=chat_id, text='Администратор еще не зарегистрировал Вас.')
    return 'HANDLE_FRELANCER_REGISTER'
