import sqlite3
import logging as log

# log конфиг
log.basicConfig(
    level=log.INFO,
    filemode="w",
    filename="logbook.txt",
    format='%(asctime)s - %(levelname)s - %(message)s')
log.info('data_base')


def create_db():
    """Создает базу данных и таблицу"""
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    name TEXT,
    subject TEXT,
    level TEXT, 
    task TEXT DEFAULT "",
    answer TEXT DEFAULT ""
); 
    """)
    con.close()
    return


create_db()


def insert_data(user_id: int):
    """Добавляет запись о пользователе"""
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    sql_query = """
    INSERT INTO users
    (user_id)
    Values(?);
    """
    cur.execute(sql_query, (user_id,))
    con.commit()
    con.close()
    log.info(f"New data recieved user_id: {user_id}")
    return


def update_data(column: str, value, user_id: int):
    """Обновляет данные о пользователе в выбранном столбце"""
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    sql_query = f"""
    UPDATE users
    SET {column} = ?
    WHERE user_id = ?;
    """
    cur.execute(sql_query, (value, user_id))
    con.commit()
    con.close()
    log.info(f"Data updated user_id: {user_id}, column: {column}, value: {value}")
    return


def update_answer(value, user_id: int):
    """Обновляет данные о пользователе в выбранном столбце"""
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    prev_answ = select_data('answer', user_id)
    if prev_answ is None:
        prev_answ = ''
    sql_query = f"""
    UPDATE users
    SET answer = "{prev_answ}" || ?
    WHERE user_id = ?;
    """
    cur.execute(sql_query, (value, user_id))
    con.commit()
    con.close()
    log.info(f"Answer updated user_id: {user_id},, value: {value}")
    return


def select_data(column: str, user_id: int):
    """Возвращает данные о пользователе из выбранного столбца"""
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    sql_query = f"""
    SELECT {column}
    FROM users
    WHERE user_id = ?;
    """
    try:
        select = cur.execute(sql_query, (user_id,))
        for i in select:
            result = i[0]
        con.close()
        return result
    except:
        con.close()
        log.info('Data not found')
        return "not found"


def delete_user_data(user_id: id):
    """Удаляет запись о пользователе"""
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    sql_query = f"""
    DELETE
    FROM users
    WHERE user_id = ?;
    """
    cur.execute(sql_query, (user_id,))
    con.commit()
    con.close()
    log.info(f"Data deleted user_id: {user_id}")
    return


def pr_db():
    """Выводит всю базу данных"""
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    res = cur.execute("""
    SELECT *
    FROM users;
    """)
    for r in res:
        print(r)
        log.info(r)
    return


# def delete_data():
#     """Удаляет все записи"""
#     con = sqlite3.connect('database.db')
#     cur = con.cursor()
#     cur.execute("""
#     DELETE
#     FROM users
#     """)
#     con.commit()
#     con.close()
#     return
