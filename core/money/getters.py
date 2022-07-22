import sqlite3


def get_user_balance(user_id: int) -> int:
    db = sqlite3.connect("./databases/main.sqlite")
    cursor = db.cursor()
    balance = \
        cursor.execute(f"SELECT money FROM money WHERE user_id = {user_id}").fetchone()[0]
    cursor.close()
    db.close()
    return balance
