import os
import json

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
