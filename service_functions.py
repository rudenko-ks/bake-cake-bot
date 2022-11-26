import os
import json
import datetime
from string import digits, ascii_letters

BAKE_CAKE_DB: str = 'json_files/user_orders.json'


def database_create_users_order():
    if not os.path.exists(BAKE_CAKE_DB):
        os.makedirs('json_files', exist_ok=True)
        empty_db = []
        with open(BAKE_CAKE_DB, 'w', encoding="utf-8") as json_file:
            json.dump(empty_db, json_file, indent=4, ensure_ascii=False)


def database_read_users_order() -> list:
    with open(BAKE_CAKE_DB, 'r', encoding="utf-8") as file:
        return json.load(file)


def database_write_users_order(items: list) -> list:
    with open(BAKE_CAKE_DB, 'w', encoding="utf-8") as json_file:
        json.dump(items, json_file, indent=4, ensure_ascii=False)


def is_new_user(user_id: int) -> bool:
    """Функция возвращает True или False в зависимости от того - есть ли пользователь в базе данных"""
    users = database_read_users_order()
    users_ids = [
        user['user_id'] for user in users if user['user_id'] == user_id
    ]
    return not bool(users_ids)


def get_order_id(usr_orders, effective_user_id):
    for user in usr_orders:
        if user['user_id'] == effective_user_id:
            all_user_orders = user['orders']
            count_order_id = 0
            orders_id = []
            for order in all_user_orders:
                count_order_id = order['id']
                orders_id.append(str(count_order_id))
            message_keyboard = [orders_id, ['Личный кабинет']]
            # c = user['orders']
            return message_keyboard, count_order_id, all_user_orders


def is_fullname_valid(fullname: list) -> bool:
    """Проверка на валидность имени и фамилии"""
    if len(fullname) < 2:
        return True
    return False


def is_digits_in_fullname(fullname: list) -> bool:
    """Проверка на наличие цифр в имени и фамилии"""
    for digit in digits:
        if str(digit) in ' '.join(fullname):
            return True
    return False


def clear_phone_number(phone_number: str) -> str:
    """Функция очищает номер телефона от лишних симоволов"""
    numbers_in_phone = [number for number in phone_number if number in digits]
    phone_without_symbols = "".join(numbers_in_phone)
    if phone_without_symbols.startswith('7'):
        return f'+{phone_without_symbols}'
    else:
        return None


def is_valid_phone_number(phone_number: str) -> bool:
    """Проверка на валидность номера телефона"""
    if len(phone_number) > 12:
        return False
    elif len(phone_number) < 12:
        return False

    cleared_phone_number = clear_phone_number(phone_number)
    if not cleared_phone_number:
        return False

    return True


def is_valid_date(date: str) -> bool:
    chars = ascii_letters + digits
    day = date[0:2]
    month = date[3:5]
    year = date[6:]
    if date[2] in chars or date[5] in chars and not all(map(lambda x: x.isdigit(), [day, month, year])):
        return False
    day, month, year = map(int, [day, month, year])
    try:
        return datetime.date(year, month, day) >= datetime.date.today()
    except:
        return False

