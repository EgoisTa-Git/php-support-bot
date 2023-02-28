"""Модуль телеграм-бота для фрилансера"""

import textwrap
from more_itertools import chunked
from support_bot.models import Request
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup


def handle_application_menu(bot, update, context):
    """TODO Это заглушка для реализации работы заказчика"""

def handle_buy_subscribe(bot, update, context):
    """TODO Заглушка для реализации функционала покупки подписки"""

def handle_freelancer_register(bot, update, context):
    """Регистрация фрилансера"""
    user = context.user_data['user']
    chat_id = context.user_data['chat_id']
    if user.is_active:
        custom_keyboard = [['Главное меню']]
        reply_markup = ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)
        bot.send_message(chat_id=chat_id, text='PHP Support. Личный кабинет фрилансера', reply_markup=reply_markup)
        custom_keyboard = [[InlineKeyboardButton('Выбрать заказ', callback_data='new_order'),
                            InlineKeyboardButton('Заявки в работе', callback_data='orders')]]
        reply_markup = InlineKeyboardMarkup(custom_keyboard)

        bot.send_message(chat_id=chat_id, text='Привет! Выберите дальнейшее действие.', reply_markup=reply_markup)
        return 'HANDLER_SELECT_ACTION'
    bot.send_message(chat_id=chat_id, text='Администратор еще не зарегистрировал Вас.')
    return 'HANDLE_FRELANCER_REGISTER'

def handle_select_action(bot, update, context):
    """Выбор действия в главном меню фрилансера"""
    chat_id = context.user_data['chat_id']
    if not update.callback_query:
        return 'HANDLE_FRELANCER_REGISTER'
    action_selected = update.callback_query.data
    user = context.user_data['user']
    context.user_data['action'] = action_selected
    if action_selected == 'orders':
        orders = Request.objects.filter(freelancer=user, done=False)
    elif action_selected == 'new_order':
        if not context.user_data.get('orders_chunk'):
            orders_query = Request.objects.filter(freelancer=None, done=False)
            orders_chunk = chunked(orders_query, 5)
            context.user_data['orders_chunk'] = orders_chunk
        else:
            orders_chunk = context.user_data.get('orders_chunk')
        try:
            orders = next(orders_chunk)
        except StopIteration:
            bot.send_message(chat_id=chat_id, text='Больше новых заказов нет')

    context.user_data['orders'] = orders
    new_bot_state = display_orders(bot, update, context)
    if action_selected == 'new_order':
        display_more_button(bot, update, context)
    return new_bot_state

def display_more_button(bot, update, context):
    chat_id = context.user_data['chat_id']
    custom_keyboard = [[InlineKeyboardButton('Еще', callback_data='more')]]
    reply_markup = InlineKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=chat_id, text='Посмотреть другие заявки:', reply_markup=reply_markup)

def display_orders(bot, update, context):
    chat_id = context.user_data['chat_id']
    user = context.user_data['user']
    orders = context.user_data['orders']
    if not orders:
        return 'HANDLE_FRELANCER_REGISTER'
    for order in orders:
        custom_keyboard = [[InlineKeyboardButton(order.title, callback_data=f'id={order.id}')]]
        reply_markup = InlineKeyboardMarkup(custom_keyboard)
        bot.send_message(chat_id=chat_id, text=f'Заказ № {order.id}', reply_markup=reply_markup)
    return 'HANDLE_SELECT_ORDER'

def handle_select_order(bot, update, context):
    """Обработка выбранного заказа"""
    chat_id = context.user_data['chat_id']
    if not update.callback_query:
        return 'HANDLE_SELECT_ORDER'
    order_selected = update.callback_query.data
    if order_selected == 'more':
        orders_chunk = context.user_data.get('orders_chunk')
        try:
            context.user_data['orders'] = next(orders_chunk)
        except StopIteration:
            bot.send_message(chat_id=chat_id, text='Больше новых заказов нет')
            context.user_data['orders'] = []
            context.user_data['orders_chunk'] = []
        bot_state = display_orders(bot, update, context)
        if context.user_data['orders']:
            display_more_button(bot, update, context)
        return bot_state
    user = context.user_data['user']
    _, order_id = order_selected.split('=')
    order = Request.objects.get(pk=int(order_id), done=False)
    context.user_data['order'] = order
    order_text = textwrap.dedent(f'''Наименование заказа: {order.title}
                                 Описание проблемы: {order.description}''')
    if order.freelancer == user:
        action_button_text = 'Завершить заказ'
    else:
        action_button_text = 'Принять заказ'
    custom_keyboard = [[InlineKeyboardButton(action_button_text, callback_data='action_order'),
                        InlineKeyboardButton('Назад', callback_data='back')]]
    reply_markup = InlineKeyboardMarkup(custom_keyboard)

    bot.send_message(chat_id=chat_id, text=order_text, reply_markup=reply_markup)

    return 'HANDLE_ACTION_ORDER'

def handle_action_order(bot, update, context):
    """Обрабатывает действия над заказом"""
    chat_id = context.user_data['chat_id']
    user = context.user_data['user']
    if not update.callback_query:
        return 'HANDLE_ACTION_ORDER'
    order_action = update.callback_query.data
    order = context.user_data['order']
    if order_action == 'back':
        bot_state = display_orders(bot, update, context)
    elif order_action == 'action_order':
        client_chat_id = order.author.tg_id
        if order.freelancer == user:
            order.done = True
            order.save()
            bot.send_message(chat_id=chat_id, text=f'Закрыта заявка {order.id} - {order.title}.')
            # bot.send_message(chat_id=client_chat_id, text=f'Закрыта заявка {order.id} - {order.title}.')
        else:
            order.freelancer = user
            order.save()
            bot.send_message(chat_id=chat_id, text=f'Взята в работу заявка {order.id} - {order.title}.')
            # bot.send_message(chat_id=client_chat_id, text=f'Взята в работу заявка {order.id} - {order.title}.')
        bot_state = 'HANDLE_FRELANCER_REGISTER'
    return bot_state
