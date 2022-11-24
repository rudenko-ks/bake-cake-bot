import os

from dotenv import load_dotenv
from telegram import (Update, ReplyKeyboardMarkup, KeyboardButton)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          CallbackContext, ConversationHandler)

from messages import *
from service_functions import *

USER_FULLNAME, PHONE_NUMBER, END_AUTH, NUMBER_ORDER, CHOICE_ORDER = range(5)

SELF_STORAGE_AGREEMENTS: str = 'documents/sample.pdf'

SELF_STORAGE_USER_ORDERS: str = 'json_files/user_orders.json'


def start(update: Update, context: CallbackContext) -> int:
    user = update.effective_user

    if is_new_user(user.id):
        message_keyboard = [['✅ Согласен', '❌ Не согласен']]
        markup = ReplyKeyboardMarkup(message_keyboard,
                                     resize_keyboard=True,
                                     one_time_keyboard=True)

        with open(SELF_STORAGE_AGREEMENTS, 'rb') as image:
            user_agreement_pdf = image.read()

        greeting_msg = create_start_message_new_user(user.name)
        update.message.reply_document(
            user_agreement_pdf,
            filename='Соглашение на обработку персональных данных.pdf',
            caption=greeting_msg,
            reply_markup=markup)

        return USER_FULLNAME
    else:
        message_keyboard = [['Собрать торт', 'Мои заказы']]
        markup = ReplyKeyboardMarkup(message_keyboard,
                                     one_time_keyboard=True,
                                     resize_keyboard=True)

        menu_msg = create_start_message_exist_user(user.name)
        update.effective_message.reply_text(menu_msg, reply_markup=markup)
        return NUMBER_ORDER


def get_fullname(update: Update, context: CallbackContext) -> int:
    context.user_data['choice'] = 'Имя и фамилия'
    update.message.reply_text(f'Введите имя и фамилию:')

    return PHONE_NUMBER


def get_phone_number(update: Update, context: CallbackContext):
    user_data = context.user_data
    text = update.message.text
    category = user_data['choice']
    user_data[category] = text
    del user_data['choice']

    context.user_data['choice'] = 'Телефон'
    update.message.reply_text(f'Введите телефон в формате +7...')

    return END_AUTH


# Если пользователь зарегистрирован - return PERSONAL_ACCOUNT из функции start
def push_user_orders(update: Update, context: CallbackContext):
    with open(SELF_STORAGE_USER_ORDERS, 'rb') as json_file:
        usr_orders = json.load(json_file)
    effective_user_id = update.effective_user.id
    a = get_order_id(usr_orders, effective_user_id)[0]
    b = get_order_id(usr_orders, effective_user_id)[1]
    c = get_order_id(usr_orders, effective_user_id)[2]
    markup = ReplyKeyboardMarkup(a,
                                 resize_keyboard=True,
                                 one_time_keyboard=True)
    update.effective_message.reply_text('Выберите номер заказа. Кол-во заказов: ' + str(b), reply_markup=markup)
    return CHOICE_ORDER


def push_user_order(update: Update, context: CallbackContext):
    with open(SELF_STORAGE_USER_ORDERS, 'rb') as json_file:
        usr_orders = json.load(json_file)
    effective_user_id = update.effective_user.id
    c = get_order_id(usr_orders, effective_user_id)[2]
    text = update.message.text
    context.user_data['переходить'] = text
    update.message.reply_text(f'____________________')
    for k in c:
        if str(k['id']) == context.user_data['переходить']:
            update.message.reply_text(str(k))
    return start(update, context)


def end_auth(update: Update, context: CallbackContext):
    user_data = context.user_data
    text = update.message.text

    category = user_data['choice']
    user_data[category] = text

    if 'choice' in user_data:
        del user_data['choice']

        user_fullname = user_data['Имя и фамилия'].split()
        user_phone_number = user_data['Телефон']
        user_id = update.effective_user.id

        user = {
            "user_id": user_id,
            "first_name": user_fullname[0],
            "last_name": user_fullname[1],
            "phone_number": user_phone_number,
            "orders": []
        }

        database_without_new_user = database_read_users_order()
        database_without_new_user.append(user)

        database_write_users_order(database_without_new_user)

        user_data.clear()
        return start(update, context)


def cancel_auth(update: Update, context: CallbackContext) -> None:
    message_keyboard = [['✅ Согласен', '❌ Не согласен']]
    markup = ReplyKeyboardMarkup(message_keyboard,
                                 resize_keyboard=True,
                                 one_time_keyboard=True)
    update.message.reply_text(
        'Извините, тогда мы не сможем пропустить вас дальше. '
        'Чтобы изменить решение - напишите /start.',
        reply_markup=markup)
    return ConversationHandler.END


if __name__ == '__main__':
    load_dotenv()
    telegram_bot_token = os.environ['TELEGRAM_TOKEN']

    database_create_users_order()
    #  From version 13 use_context=True it is the default.
    updater = Updater(telegram_bot_token, use_context=True)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            USER_FULLNAME: [
                MessageHandler(Filters.regex('^(✅ Согласен)$'), get_fullname),
            ],
            PHONE_NUMBER: [
                MessageHandler(Filters.text, get_phone_number)
            ],
            END_AUTH: [
                MessageHandler(Filters.text, end_auth),
            ],
            NUMBER_ORDER: [
                MessageHandler(Filters.text, push_user_orders),
            ],
            CHOICE_ORDER: [
                MessageHandler(Filters.text, push_user_order),
            ]
        },
        fallbacks=[MessageHandler(Filters.regex('^Стоп$'), start)],
    )

    dispatcher.add_handler(
        MessageHandler(Filters.regex('^❌ Не согласен$'), cancel_auth))
    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(CommandHandler("start", start))
    updater.start_polling()
    updater.idle()
