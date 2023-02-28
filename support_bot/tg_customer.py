"""Модуль телеграм-бота для заказчика"""
import datetime

from telegram import ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, MessageHandler, Filters

from django.db.models import F
from django.utils import timezone

from users.models import CustomUser
from support_bot.models import Request, Subscription, Tariff


def customer_main_keyboard():
    keybord = [
        [InlineKeyboardButton('Разместить заказ', callback_data='Разместить заказ'),
         InlineKeyboardButton('Мои заказы', callback_data='Мои заказы')]
    ]
    return InlineKeyboardMarkup(keybord)


def get_tariff_keyboard():
    keyboard = []
    tariffs = Tariff.objects.all()
    for tariff in tariffs:
        callback = tariff.id
        keyboard.append([InlineKeyboardButton(tariff.title, callback_data=callback)])
    return InlineKeyboardMarkup(keyboard)


def confirmation_tariff_keyboard():
    keyboard = [
        [
            InlineKeyboardButton('Оформить подписку', callback_data='OK'),
            InlineKeyboardButton('Назад', callback_data='BACK')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


# Проверка на возможность создания заказа
def check_create_order():
    pass


# Вывод созданных заказов
def get_user_orders():
    pass


# HANDLER_CHECK_SUBSCRIBE
def handler_check_subscribe(bot, update, context):
    chat_id = context.user_data['chat_id']
    user = context.user_data['user']
    active_subscribe = Subscription.objects.filter(user=user, expire_at__gte=datetime.datetime.now()).exists()
    print(active_subscribe)

    if active_subscribe:
        bot.send_message(chat_id=chat_id, text='Добро пожаловать!')
        handle_main_customer(bot, update, context)
        return 'ACTION_CUSTOMER'
    else:
        message_text = 'Для оплаты и активации подписки свяжитесь с менеджером {контакты менеджера}'
        bot.send_message(chat_id=chat_id, text=message_text)


# Стартовое сообщение заказчика
def handle_main_customer(bot, update, context):
    chat_id = context.user_data['chat_id']
    message_text = 'С чего начнем?'
    reply_markup = customer_main_keyboard()
    bot.send_message(chat_id=chat_id, text=message_text, reply_markup=reply_markup)
    return 'ACTION_CUSTOMER'


def customer_selected_tariff(bot, update, context):
    chat_id = context.user_data['chat_id']
    if not update.callback_query:
        return 'HANDLE_BUY_SUBSCRIBE'
    action_selected = update.callback_query.data
    user = context.user_data['user']
    print(action_selected)
    context.user_data['action'] = action_selected
    if action_selected == 'client':
        reply_markup = get_tariff_keyboard()
        message_text = 'Выбирете тариф'
        bot.send_message(chat_id=chat_id, text=message_text, reply_markup=reply_markup)
        return 'HANDLE_BUY_SUBSCRIBE'


def conformation_tariff(bot, update, context):
    chat_id = context.user_data['chat_id']
    tariff_id = update.callback_query.data
    context.user_data['tariff_id'] = tariff_id
    tariff = Tariff.objects.get(id=int(tariff_id))

    description_tariff = f'''Выбран тариф:
Название: {tariff.title}
Количество заявок в месяц: {tariff.max_requests}
Время ответа: {tariff.response_time}
Возможность закрепить фрилансера: {tariff.bind_freelancer}
Возможность увидеть контакты фрилансера: {tariff.see_contacts}
Цена: {tariff.price}
'''
    reply_markup = confirmation_tariff_keyboard()
    bot.send_message(chat_id=chat_id, text=description_tariff, reply_markup=reply_markup)

    return 'SAVE_CUSTOMER'


def save_customer(bot, update, context):
    chat_id = context.user_data['chat_id']
    tariff_id = context.user_data['tariff_id']
    selected_tariff = Tariff.objects.get(id=int(tariff_id))

    # chat_id = update.message.chat_id
    client = CustomUser.objects.get(tg_id=chat_id)
    subscription = Subscription.objects.create(
        user=client,
        tariff=selected_tariff,
        expire_at=timezone.now()
    )
    subscription.save()

    # bot_state = handle_main_customer(bot, update, context)
    # message_text = 'Для оплаты и активации подписки свяжитесь с менеджером {контакты менеджера}'
    message_text = 'Для оплаты и активации подписки свяжитесь с менеджером {контакты менеджера}'
    bot.send_message(chat_id=chat_id, text=message_text)
    return 'HANDLER_CHECK_SUBSCRIBE'


def back_tariffs(bot, update, context):
    customer_selected_tariff(bot, update, context)
    return 'CONFIRMATION_TARIFF'


# Создание заказа клиентом
def action_customer(bot, update, context):
    chat_id = context.user_data['chat_id']
    if update.callback_query.data == 'Разместить заказ':
        message_text = 'Начнем создание заказа'
        bot.send_message(chat_id=chat_id, text=message_text)
        # state = 'ORDER_START'
        return order_start(bot, update, context)
    elif update.callback_query.data == 'Мои заказы':
        return 'SHOW_ORDERS'


def order_start(bot, update, context):
    chat_id = context.user_data['chat_id']
    # update.message.reply_text(
    #     "Введите заголовок заказа",
    #     reply_markup=ReplyKeyboardRemove()
    # )
    message_text = 'Введите заголовок заказа'
    bot.send_message(chat_id=chat_id, text=message_text)
    return 'CUSTOMER_REG_ORDER_TITLE'


def order_title(bot, update, context):
    chat_id = context.user_data['chat_id']
    title_order = update.message.text
    if len(title_order) == 0:
        message_text = 'Введите заголовок заказа'
        bot.send_message(chat_id=chat_id, text=message_text)
        return 'CUSTOMER_REG_ORDER_TITLE'
    else:
        context.user_data['order'] = {'title': title_order}
        message_text = 'Введите описание заказа'
        bot.send_message(chat_id=chat_id, text=message_text)
        return 'CUSTOMER_REG_ORDER_DESCRIPTION'


def order_description(bot, update, context):
    chat_id = context.user_data['chat_id']
    description_order = update.message.text
    if len(description_order) == 0:
        message_text = 'Введите описание заказа'
        bot.send_message(chat_id=chat_id, text=message_text)
        return 'CUSTOMER_REG_ORDER_DESCRIPTION'
    else:
        context.user_data['order']['description'] = description_order

        # Сохранение заказа в бд
        chat_id = context.user_data['chat_id']
        author = CustomUser.objects.get(tg_id=chat_id)
        try:
            customer_request =Request.objects.create(
                title=context.user_data['order']['title'],
                description=description_order,
                author=author,
            )
            customer_request.save()
            subscription = Subscription.objects.get(user=author)
            subscription.requests_created = F('requests_created') + 1
            subscription.save()
        except:
            print('Шеф, всё пропало!')
        bot.send_message(chat_id=chat_id, text='Заказ размещен!')
        # bot_state = handle_main_customer(bot, update, context)

        # update.message.reply_text('Заказ размещен!')
        return handle_main_customer(bot, update, context)


def order_dontknow(update, context):
    update.message.reply_text('Я вас не понимаю')

