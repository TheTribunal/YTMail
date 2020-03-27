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
        return conn
    except Error as e:
        print(e)
    return conn


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


def create_ticket(conn, ticket):
    """
    :param conn: sql connection
    :param ticket: (discord_user, ticket_status)
    :return: ticket id
    """
    # TODO: add timestamps
    sql = """ INSERT INTO tickets (discord_user, status, bot_msg_id) VALUES (?, ?, ?) """
    cur = conn.cursor()
    cur.execute(sql, ticket)
    return cur.lastrowid


def create_msg_log(conn, msg_log):
    """
    :param conn: sql connection
    :param msg_log:  (ticket_id, sender, msg_content, bot_msg_id)
    :return: msg_log id
    """
    # TODO: add timestamps
    sql = """ INSERT INTO msg_logs (ticket_id, sender, msg_content) VALUES (?, ?, ?) """
    cur = conn.cursor()
    cur.execute(sql, msg_log)
    return cur.lastrowid


def new_ticket_wrapper(ticket, msg):
    sqlite_file = Path.cwd() / 'test_db.db'
    conn = create_connection(sqlite_file)
    new_ticket(conn, ticket, msg)


def new_ticket(conn, ticket, msg):
    ticket_id = create_ticket(conn, ticket)
    msg_log = (ticket_id[0], msg)
    msg_row = create_msg_log(conn, msg_log)
    return ticket_id


def get_user_ticket_wrapper(user_id):
    sqlite_file = Path.cwd() / 'test_db.db'
    conn = create_connection(sqlite_file)
    return get_user_ticket_id(conn, user_id)


def get_user_ticket_id(conn, user_id: ()) -> ():
    """

    :param conn: database connection
    :param user_id: as a tuple
    :return: ticket_id: tuple
    """
    sql = """ SELECT id FROM tickets WHERE discord_user = ?  AND status = 'open' """
    cur = conn.cursor()
    cur.execute(sql, user_id)
    ticket_id = cur.fetchone()
    return ticket_id


def get_ticket_by(select, column, val):
    sqlite_file = Path.cwd() / 'test_db.db'
    conn = create_connection(sqlite_file)
    sql = """ SELECT ? from tickets WHERE ? = ? """
    cur = conn.cursor()
    cur.execute(sql, (select, column, val))
    result = cur.fetchone()
    return result


def get_msg_logs_by_ticket_id(conn, ticket_id):
    sql = """ SELECT * FROM msg_logs WHERE ticket_id = ? """
    cur = conn.cursor()
    cur.execute(sql, ticket_id)
    rows = cur.fetchall()
    return rows


def update_ticket_wrapper(ticket_id, column, new_val):
    sqlite_file = Path.cwd() / 'test_db.db'
    conn = create_connection(sqlite_file)
    update_ticket(conn, ticket_id, column, new_val)


def update_ticket(conn, ticket_id, column, new_val):
    sql = """ UPDATE tickets
     SET ? = ? 
     WHERE id = ? """
    cur = conn.cursor()
    cur.execute(sql, (column, new_val, ticket_id))


def get_msg_logs_by_user_id(conn, user_id):
    ticket_id = get_user_ticket_id(conn, user_id)
    rows = get_msg_logs_by_ticket_id(conn, ticket_id)
    return rows


def create_tables(sqlite_file):

    sql_create_tickets_table = (' CREATE TABLE IF NOT EXISTS tickets (\n'
                                'id integer PRIMARY KEY,\n'
                                'discord_user int NOT NULL,\n'
                                'status text NOT NULL,\n'
                                'bot_msg_id integer \n'
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

    # if not sqlite_file.is_file():
    create_tables(sqlite_file)

    # conn = create_connection(sqlite_file)
    #
    # with conn:
    #     user = 'norb_norb#3499'
    #     ticket = (user, 'open', 2565426)
    #     ticket_id = create_ticket(conn, ticket)
    #
    #     msg_log = (ticket_id, user, 'help! little timmy fell down a well!')
    #     msg_log_id = create_msg_log(conn, msg_log)


if __name__ == '__main__':
    main()
