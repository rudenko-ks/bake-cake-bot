import os
import requests


from dotenv import load_dotenv
from telegram import (Update, ReplyKeyboardMarkup, KeyboardButton)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          CallbackContext, ConversationHandler)

from messages import *
from service_functions import *

# USER_FULLNAME, PHONE_NUMBER, END_AUTH, NUMBER_ORDER, CHOICE_ORDER = range(5)

USER_FULLNAME, PHONE_NUMBER, END_AUTH, PERSONAL_ACCOUNT, CHOICE_ORDER, CAKE_SHAPE, TOPPING, BERRIES, \
DECOR, INSCRIPTION, ORDER_COMMENT, ADDRESS, DELIVERY_DATE, DELIVERY_TIME, ORDER_SAVING, PRINT_ORDER, ORDER_MENU = range(17)

SELF_STORAGE_AGREEMENTS: str = 'documents/sample.pdf'

SELF_STORAGE_USER_ORDERS: str = 'json_files/user_orders.json'

PRICES = {
    '1': 40,
    '2': 75,
    '3': 110,
    'Квадрат': 60,
    'Круг': 40,
    'Прямоугольник': 100,
    'Молочный шоколад': 20,
    'Карамельный сироп': 18,
    'Белый соус': 20,
    'Кленовый сироп': 20,
    'Клубничный сироп': 30,
    'Черничный сироп': 35,
    'Без топпинга': 0,
    'Ежевика': 40,
    'Малина': 30,
    'Голубика': 45,
    'Клубника': 50,
    'Фисташки': 30,
    'Безе': 40,
    'Фундук': 35,
    'Пекан': 30,
    'Маршмеллоу': 20,
    'Марципан': 28,
}

ORDER_DESCRIPTIONS = [
    'Номер заказа:',
    'Статус:',
    'Количество ярусов:',
    'Форма:',
    'Топпинг:',
    'Ягоды:',
    'Декор:',
    'Надпись:',
    'Комментарий:',
    'Адрес:',
    'Дата доставки:',
    'Время доставки:',
    'Стоимость:',
]


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
        if 'ammount_of_layers' in context.user_data:
            context.user_data.clear()
        return PERSONAL_ACCOUNT


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

    user_fullname = user_data['Имя и фамилия'].split()
    if is_fullname_valid(user_fullname):
        update.message.reply_text(
            'Вы не указали фамилию или имя, попробуйте снова.')
        return get_fullname(update, context)
    if is_digits_in_fullname(user_fullname):
        update.message.reply_text('В имени или фамилии присутствуют цифры!')
        return get_fullname(update, context)

    context.user_data['choice'] = 'Телефон'

    message_keyboard = [[
        KeyboardButton('Отправить свой номер телефона', request_contact=True)
    ]]
    markup = ReplyKeyboardMarkup(message_keyboard,
                                 one_time_keyboard=True,
                                 resize_keyboard=True)
    update.message.reply_text(
        f'Введите телефон в формате +7... или нажав на кнопку ниже:',
        reply_markup=markup)
    return END_AUTH


def push_user_orders(update: Update, context: CallbackContext):
    with open(SELF_STORAGE_USER_ORDERS, 'rb') as json_file:
        usr_orders = json.load(json_file)
    effective_user_id = update.effective_user.id
    message_keyboard = get_order_id(usr_orders, effective_user_id)[0]
    count_order_id = get_order_id(usr_orders, effective_user_id)[1]
    markup = ReplyKeyboardMarkup(message_keyboard,
                                 resize_keyboard=True,
                                 one_time_keyboard=True)
    if count_order_id == 0:
        update.effective_message.reply_text('У вас нет заказов ',
                                            reply_markup=markup)
    else:
        update.effective_message.reply_text(
            'Выберите номер заказа. Кол-во заказов: ' + str(count_order_id),
            reply_markup=markup)
    return CHOICE_ORDER


def push_user_order(update: Update, context: CallbackContext):
    with open(SELF_STORAGE_USER_ORDERS, 'rb') as json_file:
        usr_orders = json.load(json_file)
    effective_user_id = update.effective_user.id
    all_user_orders = get_order_id(usr_orders, effective_user_id)[2]
    order = update.message.text
    for user_order in all_user_orders:
        if str(user_order['id']) == order:
            print_order(update, context)


def get_amount_of_layers(update: Update, context: CallbackContext) -> int:
    message_keyboard = [['1', '2', '3']]
    markup = ReplyKeyboardMarkup(message_keyboard,
                                 one_time_keyboard=True,
                                 resize_keyboard=True)
    context.user_data['choice'] = 'ammount_of_layers'
    update.message.reply_text(f'''
    Выберите количество ярусов торта
    1 уровень      {PRICES['1']}р
    2 уровень      {PRICES['1']}р
    3 уровень      {PRICES['1']}р
    ''',
                              reply_markup=markup)

    return CAKE_SHAPE


def get_cake_shape(update: Update, context: CallbackContext) -> int:
    save_user_choice(update, context)
    message_keyboard = [['Квадрат', 'Круг'], ['Прямоугольник']]
    markup = ReplyKeyboardMarkup(message_keyboard,
                                 one_time_keyboard=True,
                                 resize_keyboard=True)
    context.user_data['choice'] = 'shape'
    update.message.reply_text(f'''
    Выберите форму
    Квадрат            {PRICES['Квадрат']}р
    Круг               {PRICES['Круг']}р
    Прямоугольник      {PRICES['Прямоугольник']}р
    ''',
                              reply_markup=markup)

    return TOPPING


def get_topping(update: Update, context: CallbackContext) -> int:
    save_user_choice(update, context)

    message_keyboard = [['Молочный шоколад', 'Белый соус'],
                        ['Карамельный сироп', 'Кленовый сироп'],
                        ['Клубничный сироп', 'Черничный сироп'],
                        ['Без топпинга']]

    markup = ReplyKeyboardMarkup(message_keyboard,
                                 one_time_keyboard=True,
                                 resize_keyboard=True)

    context.user_data['choice'] = 'topping'

    update.message.reply_text(f'''
    Выберите Топпинг
    Молочный шоколад      {PRICES['Молочный шоколад']}р
    Белый соус            {PRICES['Белый соус']}р
    Карамельный сироп     {PRICES['Карамельный сироп']}р
    Кленовый сироп        {PRICES['Кленовый сироп']}р
    Клубничный сироп      {PRICES['Клубничный сироп']}р
    Черничный сироп       {PRICES['Черничный сироп']}р
    Без топпинга          {PRICES['Без топпинга']}р
        ''',
                              reply_markup=markup)

    return BERRIES


def get_berries(update: Update, context: CallbackContext) -> int:
    save_user_choice(update, context)

    message_keyboard = [
        ['Ежевика', 'Малина'],
        ['Голубика', 'Клубника'],
        ['Пропустить'],
    ]

    markup = ReplyKeyboardMarkup(message_keyboard,
                                 one_time_keyboard=True,
                                 resize_keyboard=True)

    context.user_data['choice'] = 'berries'
    update.message.reply_text(f'''
    Выберите ягоды:
    Ежевика       {PRICES['Ежевика']}р
    Малина        {PRICES['Малина']}р
    Голубика      {PRICES['Голубика']}р
    Клубника      {PRICES['Клубника']}р
    ''',
                              reply_markup=markup)
    return DECOR


def get_decor(update: Update, context: CallbackContext) -> int:
    save_user_choice(update, context)
    message_keyboard = [['Фисташки', 'Безе'], ['Фундук', 'Пекан'],
                        ['Маршмеллоу', 'Марципан'], ['Пропустить']]
    markup = ReplyKeyboardMarkup(message_keyboard,
                                 one_time_keyboard=True,
                                 resize_keyboard=True)
    context.user_data['choice'] = 'decor'
    update.message.reply_text(f'''
    Выберите декор:
    Фисташки        {PRICES['Фисташки']}р
    Безе            {PRICES['Безе']}р
    Фундук          {PRICES['Фундук']}р
    Пекан           {PRICES['Пекан']}р
    Маршмеллоу      {PRICES['Маршмеллоу']}р
    Марципан        {PRICES['Марципан']}р
    ''',
                              reply_markup=markup)
    return INSCRIPTION


def get_inscription(update: Update, context: CallbackContext) -> int:
    save_user_choice(update, context)
    message_keyboard = [['Пропустить']]
    markup = ReplyKeyboardMarkup(message_keyboard,
                                 one_time_keyboard=True,
                                 resize_keyboard=True)
    context.user_data['choice'] = 'inscription'
    update.message.reply_text('''
    Мы можем разместить на торте любую надпись, например:
    "С днем рождения!
    Стоимость      500р"
    ''',
                              reply_markup=markup)

    return ORDER_COMMENT


def get_order_comment(update: Update, context: CallbackContext) -> int:
    save_user_choice(update, context)
    message_keyboard = [['Пропустить']]
    markup = ReplyKeyboardMarkup(message_keyboard,
                                 one_time_keyboard=True,
                                 resize_keyboard=True)
    context.user_data['choice'] = 'comment'
    update.message.reply_text('Коментарий к заказу', reply_markup=markup)

    return ADDRESS


def get_address(update: Update, context: CallbackContext) -> int:
    save_user_choice(update, context)
    context.user_data['choice'] = 'address'
    message_keyboard = [[
        KeyboardButton('Отправить геопозицию', request_location=True)
    ]]
    markup = ReplyKeyboardMarkup(message_keyboard,
                                 one_time_keyboard=True,
                                 resize_keyboard=True)
    update.message.reply_text('Введите ваш адрес', reply_markup=markup)

    return DELIVERY_DATE


def get_delivery_date(update: Update, context: CallbackContext) -> int:
    if update.message.location:
        address = f"{update.message.location['latitude']}, {update.message.location['longitude']}"
    else:
        address = update.message.text
    category = context.user_data['choice']
    context.user_data[category] = [address, 0]
    context.user_data['choice'] = 'delivery_date'
    update.message.reply_text('Введите дату доставки в формате: ДД.ММ.ГГГГ')

    return DELIVERY_TIME


def get_delivery_time(update: Update, context: CallbackContext) -> int:
    date = update.message.text
    if not is_valid_date(date):
        update.message.reply_text('Некорректная дата')
        return get_delivery_date(update, context)
    category = context.user_data['choice']
    context.user_data[category] = [date, 0]
    context.user_data['choice'] = 'delivery_time'
    update.message.reply_text('Введите время доставки в формате: ЧЧ.ММ')

    return ORDER_SAVING


def get_delivery_time_2(update: Update, context: CallbackContext) -> int:
    """
    Функция вызывается вместо get_delivery_time если
    пользователь ошибся при вводе даты в первый раз
    """
    context.user_data['choice'] = 'delivery_time'
    update.message.reply_text('Введите время доставки в формате: ЧЧ.ММ')
    return ORDER_SAVING


def save_time(update, context) -> None:
    time = update.message.text
    hours, minutes = map(
        lambda x: f'{int(x):02}',
        time.split(re.search(r'[-.:]{1}', time).group())
    )
    category = context.user_data['choice']
    context.user_data[category] = [f'{hours}.{minutes}', 0]
    del context.user_data['choice']
    return


def save_user_choice(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    category = context.user_data['choice']
    if text in PRICES:
        context.user_data[category] = [text, PRICES[text]]
    elif text == 'Пропустить':
        context.user_data[category] = ['-', 0]
    else:
        context.user_data[category] = [text, 0]
    del context.user_data['choice']
    return


def save_order(update: Update, context: CallbackContext) -> int:
    time = update.message.text
    if not is_time_valid(time):
        update.message.reply_text('Некорректное время')
        return get_delivery_time_2(update, context)
    save_time(update, context)
    if 'order' in context.user_data:
        del context.user_data['order']
    user_data = context.user_data
    user_id = update.effective_user.id
    users = database_read_users_order()
    for user in users:
        if user_id in user.values():
            user_ids = [order['id'] for order in user['orders']]
            id = 1
            while True:
                if id not in user_ids:
                    break
                id += 1
            order = {
                'id':
                    id,
                'status':
                    'Принят',
                'cake_layers':
                    user_data['ammount_of_layers'][0],
                'cake_shape':
                    user_data['shape'][0],
                'cake_toping':
                    user_data['topping'][0],
                'cake_berries':
                    user_data['berries'][0],
                'cakes_decor':
                    user_data['decor'][0],
                'cake_inscription':
                    user_data['inscription'][0],
                'cake_comment':
                    user_data['comment'][0],
                'address':
                    user_data['address'][0],
                'delivery_date':
                    user_data['delivery_date'][0],
                'delivery_time':
                    user_data['delivery_time'][0],
                'order_cost': [
                    sum([value[1] for value in user_data.values()]), ''
                ][0]
            }
            if order['cake_inscription'] != '-':
                order['order_cost'] += 500

            user['orders'].append(order)
            break

    database_write_users_order(users)
    user_data.clear()
    message_keyboard = [['Детали заказа', 'Личный кабинет']]
    markup = ReplyKeyboardMarkup(message_keyboard,
                                 one_time_keyboard=True,
                                 resize_keyboard=True)

    update.message.reply_text('Заказ сформирован', reply_markup=markup)

    return PRINT_ORDER


def print_order(update: Update, context: CallbackContext) -> int:
    user_input = update.message.text
    user_id = update.effective_user.id
    users = database_read_users_order()
    for user in users:
        if user_id in user.values():
            if update.message.text == 'Детали заказа':
                order = user['orders'][-1]
            elif not user_input.isdigit() or int(user_input) not in [order['id'] for order in user['orders']]:
                return start(update, context)
            else:
                order = ''
                for i in user['orders']:
                    if i['id'] == int(user_input):
                        order = i
                        break
    order_details = ''
    for i, v in zip(ORDER_DESCRIPTIONS, order.values()):
        order_details += f"{i} {v if v else '-'}\n"
    message_keyboard = [['Удалить', 'Оплатить'],
                        ['Личный кабинет']]
    markup = ReplyKeyboardMarkup(message_keyboard,
                                 one_time_keyboard=True,
                                 resize_keyboard=True)
    update.message.reply_text(order_details, reply_markup=markup)
    context.user_data['order'] = order
    return ORDER_MENU


def end_auth(update: Update, context: CallbackContext):
    user_data = context.user_data
    if update.message.contact:
        text = update.message.contact.phone_number
    else:
        text = update.message.text

    if not is_valid_phone_number(text):
        invalid_phone_msg = invalid_phone_number_message()
        update.message.reply_text(invalid_phone_msg)
        return get_phone_number(update, context)

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


def pay_for_order(update: Update, context: CallbackContext):
    order = context.user_data['order']
    if order['status'] != 'Принят':
        update.message.reply_text('Заказ уже оплачен')
        return start(update, context)
    user = update.effective_user
    payment = order['order_cost']
    prices = json.dumps([{'label': 'Руб', 'amount': payment * 100}])
    print(payment)
    url = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_TOKEN')}/sendInvoice"
    params = {
        'chat_id': user.id,
        'title': 'Заказ номер',
        'description': '.',
        'payload': '.',
        'provider_token': os.getenv('PAYMENT_TOKEN_UKASSA'),
        'currency': 'RUB',
        'start_parameter': 'test',
        'prices': prices
    }

    response = requests.post(url, params=params)
    response.raise_for_status()
    return start(update, context)


def delete_order(update: Update, context: CallbackContext):
    order = context.user_data['order']
    users = database_read_users_order()
    user_id = update.effective_user.id
    for user in users:
        if user_id in user.values():
            user['orders'].remove(order)
    database_write_users_order(users)
    return start(update, context)


if __name__ == '__main__':
    load_dotenv()
    telegram_bot_token = os.environ['TELEGRAM_TOKEN']

    database_create_users_order()
    #  From version 13 use_context=True it is the default.
    updater = Updater(telegram_bot_token)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        allow_reentry=True,
        states={
            USER_FULLNAME: [
                MessageHandler(Filters.regex('^(✅ Согласен)$'), get_fullname),
            ],
            PHONE_NUMBER: [MessageHandler(Filters.text, get_phone_number)],
            END_AUTH: [
                MessageHandler(Filters.contact, end_auth),
                MessageHandler(Filters.text, end_auth),
            ],
            PERSONAL_ACCOUNT: [
                MessageHandler(Filters.regex('^(Собрать торт)$'),
                               get_amount_of_layers),
                MessageHandler(Filters.regex('^(Мои заказы)$'),
                               push_user_orders),
                MessageHandler(Filters.regex('^(Личный кабинет)$'), start)
            ],
            CHOICE_ORDER: [MessageHandler(Filters.text, print_order)],
            CAKE_SHAPE: [
                MessageHandler(
                    Filters.regex('^1$') | Filters.regex('^2$') |
                    Filters.regex('^3$'), get_cake_shape)
            ],
            TOPPING: [
                MessageHandler(
                    Filters.regex('^Квадрат$') | Filters.regex('^Круг$') |
                    Filters.regex('^Прямоугольник$'), get_topping)
            ],
            BERRIES: [
                MessageHandler(
                    Filters.regex('^Пропустить$') |
                    Filters.regex('^Без топпинга$') |
                    Filters.regex('^Белый соус$') |
                    Filters.regex('^Карамельный сироп$') |
                    Filters.regex('^Кленовый сироп$') |
                    Filters.regex('^Клубничный сироп$') |
                    Filters.regex('^Черничный сироп$') |
                    Filters.regex('^Молочный шоколад$'), get_berries)
            ],
            DECOR: [
                MessageHandler(
                    Filters.regex('^Пропустить$') | Filters.regex('^Ежевика$') |
                    Filters.regex('^Малина$') | Filters.regex('^Голубика$') |
                    Filters.regex('^Клубника$'), get_decor)
            ],
            INSCRIPTION: [
                MessageHandler(
                    Filters.regex('^Пропустить$') |
                    Filters.regex('^Фисташки$') | Filters.regex('^Безе$') |
                    Filters.regex('^Фундук$') | Filters.regex('^Пекан$') |
                    Filters.regex('^Маршмеллоу$') | Filters.regex('^Марципан'),
                    get_inscription)
            ],
            ORDER_COMMENT: [MessageHandler(Filters.text, get_order_comment)],
            ADDRESS: [MessageHandler(Filters.text, get_address)],
            DELIVERY_DATE: [
                MessageHandler(Filters.location, get_delivery_date),
                MessageHandler(Filters.text, get_delivery_date)
            ],
            DELIVERY_TIME: [MessageHandler(Filters.text, get_delivery_time)],
            ORDER_SAVING: [MessageHandler(Filters.text, save_order)],
            PRINT_ORDER: [
                MessageHandler(Filters.regex('^Детали заказа$'), print_order),
                MessageHandler(Filters.regex('^Личный кабинет$'), start),
            ],
            ORDER_MENU: [
                MessageHandler(Filters.regex('^Оплатить$'), pay_for_order),
                MessageHandler(Filters.regex('^Личный кабинет$'), start),
                MessageHandler(Filters.regex('^Удалить$'), delete_order),
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
