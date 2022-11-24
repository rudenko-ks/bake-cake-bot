import os
import json
from string import digits

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
    for i in usr_orders:
        if i['user_id'] == effective_user_id:
            all_orders = i['orders']
            b = 0
            x = []
            for j in all_orders:
                vivod_orderov = j['id']
                b = vivod_orderov
                x.append(str(vivod_orderov))
            message_keyboard = [x, ['Личный кабинет']]
            c = i['orders']
            return message_keyboard, b, c


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
