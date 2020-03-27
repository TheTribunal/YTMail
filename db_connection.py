
from pathlib import Path
import sqlite3
from sqlite3 import Error

# TODO: check for sql injection


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        conn.row_factory = sqlite3.Row
        return conn
    except Error as e:
        print(e)
    return conn


def get_connection():
    sqlite_file = Path.cwd() / 'test_db.db'
    conn = create_connection(sqlite_file)
    return conn


def get_cursor_with_connection():
    conn = get_connection()
    cur = conn.cursor()
    return cur


def update_ticket(update_col, search_col, search_val, new_val):
    sql = f""" UPDATE tickets SET {update_col} = {new_val} WHERE {search_col} = {search_val} """
    cur = get_cursor_with_connection()
    cur.execute(sql)
    return cur.fetchone()


def select_ticket(search_col, search_val):
    sql = f""" SELECT * FROM tickets WHERE {search_col} = {search_val} """
    cur = get_cursor_with_connection()
    cur.execute(sql)
    row = cur.fetchone()
    cur.close()
    return row


def select_ticket2(search_col, search_val):  # not working because of row_factory = Row ?
    sql = f""" SELECT * FROM tickets WHERE ? = ? """
    vals = (search_col, search_val)
    cur = get_cursor_with_connection()
    cur.execute(sql, vals)
    row = cur.fetchone()
    cur.close()
    return row


def create_ticket(discord_user, bot_msg_id,  status='open'):
    sql = f""" INSERT INTO tickets (discord_user, bot_msg_id, status) VALUES ({discord_user}, {bot_msg_id}, '{status}') """
    print(sql)
    # inserts = (discord_user, bot_msg_id, status)
    # print(inserts)
    # cur = get_cursor_with_connection()
    # cur.execute(sql)
    # row = cur.fetchone()
    # cur.close()
    con = get_connection()
    cur = con.cursor()
    cur.execute(sql)
    row = cur.lastrowid
    con.commit()
    con.close()
    return row


def create_ticket2(discord_user, bot_msg_id,  status='open'):  # not working because of row_factory = Row ?
    sql = """ INSERT INTO tickets (discord_user, bot_msg_id, status) VALUES (?, ?, ?) """
    inserts = (discord_user, bot_msg_id, status)
    print(inserts)
    cur = get_cursor_with_connection()
    cur.execute(sql, inserts)
    return cur.fetchone()


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


def create_tables(sqlite_file):

    sql_create_tickets_table = (' CREATE TABLE IF NOT EXISTS tickets (\n'
                                'id integer PRIMARY KEY,\n'
                                'discord_user int NOT NULL,\n'
                                'status text NOT NULL,\n'
                                'bot_msg_id integer NOT NULL\n'
                                ');\n')

    sql_create_msg_log_table = (' CREATE TABLE IF NOT EXISTS msg_logs (\n'
                                'id integer PRIMARY KEY,\n'
                                'ticket_id integer NOT NULL,\n'
                                'sender text NOT NULL,\n'
                                'msg_content text NOT NULL,\n'
                                'FOREIGN KEY (ticket_id) REFERENCES tickets (id)\n'
                                ');\n')

    conn = create_connection(sqlite_file)

    if conn:
        create_table(conn, sql_create_tickets_table)
        create_table(conn, sql_create_msg_log_table)
    else:
        print(f'ERROR: cannot create db connection')


def main():
    sqlite_file = Path.cwd() / 'test_db.db'
    create_tables(sqlite_file)


if __name__ == '__main__':
    main()
