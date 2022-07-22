import sqlite3
from core.money.getters import get_user_balance


def update_user_balance(user_id: int, money: int) -> None:
    balance = get_user_balance(user_id)
    db = sqlite3.connect("./databases/main.sqlite")
    cursor = db.cursor()
    sql = "UPDATE money SET money = ? WHERE user_id = ?"
    values = (balance + money, user_id)
    cursor.execute(sql, values)
    db.commit()
    cursor.close()
    db.close()
    return
