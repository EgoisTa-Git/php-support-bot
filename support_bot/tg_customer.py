"""Модуль телеграм-бота для заказчика"""
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


# Стартовое сообщение заказчика
def handle_main_customer(update, context):
    message_text = 'Привет! С чего начнем?'
    reply_markup = customer_main_keyboard()
    update.message.text(
        text=message_text,
        reply_markup=reply_markup
    )


def customer_selected_tariff(update, context):
    reply_markup = get_tariff_keyboard()
    update.message.reply_text(
        'Выбирете тариф',
        reply_markup=reply_markup
    )
    return 'CONFIRMATION_TARIFF'


def conformation_tariff(update, context):
    tariff_id = update.message.text
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
    update.message.reply_text(
        text= description_tariff,
        reply_markup=reply_markup
    )

    return 'SAVE_CUSTOMER'


def save_customer(update, context):
    tariff_id = context.user_data['tariff_id']
    selected_tariff = Tariff.objects.get(id=int(tariff_id))

    chat_id = update.message.chat_id
    client = CustomUser.get(tg_id=chat_id)
    Subscription.objects.create(
        user=client,
        tariff=selected_tariff,
        expire_at=timezone.now()
    )
    bot_state = handle_main_customer(update, context)
    message_text = 'Для оплаты и активации подписки свяжитесь с менеджером {контакты менеджера}'
    update.message.reply_text(text=message_text)
    return bot_state


def back_tariffs(update, context):
    return 'CONFIRMATION_TARIFF'


# Регистрация заказчика
registr_customer = ConversationHandler(
    entry_points=[],
    states={},
    fallbacks=[]
)


# Создание заказа клиентом
def order_start(update, context):
    update.message.reply_text(
        "Введите заголовок заказа",
        reply_markup=ReplyKeyboardRemove()
    )
    return 'CUSTOMER_REG_ORDER_TITLE'


def order_title(update, context):
    title_order = update.message.text
    if len(title_order) == 0:
        update.message.reply_text('Введите заголовок заказа')
        return 'CUSTOMER_REG_ORDER_TITLE'
    else:
        context.user_data['order'] = {'title': title_order}
        update.message.reply_text('Введите описание заказа')
        return 'CUSTOMER_REG_ORDER_DESCRIPTION'


def order_description(update, context):
    description_order = update.message.text
    if len(description_order) == 0:
        update.message.reply_text('Введите описание заказа')
        return 'CUSTOMER_REG_ORDER_DESCRIPTION'
    else:
        context.user_data['order']['description'] = description_order

        # Сохранение заказа в бд
        chat_id = update.message.chat_id
        author = CustomUser.get(tg_id=chat_id)
        try:
            Request.objects.create(
                title=context.user_data['order']['title'],
                description=description_order,
                author=author,
            )
            subscription = Subscription.objects.get(user=author)
            subscription.requests_created = F('requests_created') + 1
            subscription.save()
        except:
            print('Шеф, всё пропало!')
        bot_state = handle_main_customer(update, context)
        update.message.reply_text('Заказ размещен!')
        return bot_state


def order_dontknow(update, context):
    update.message.reply_text('Я вас не понимаю')

