"""
 A connector to handle mysql db related commits and gets.

 All functions can also return a 500 status code if there's an error caught
 by the errorhandler decorator function.
"""
import pymysql as sql
from datetime import datetime
import functools  # to make decorated functions self report ok


CRED = {'host': 'remotemysql.com',
        'user': 'qJAFjFrDlh',
        'database': 'qJAFjFrDlh',
        'port': 3306}


def passwd() -> str:
    """
    simple mysql pass de-abstraction.
    gets pass from env var set by jenkins.
    """
    from os import environ as envi
    return envi.get('SECRET')


def error_handler(func):
    """
    a wrapper function to handle errors in db operations.
    used as decorator.
    :return: the decorated function, handles sql/type errors and returns 500
            if they occur instead.
    """

    @functools.wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except sql.Error as sql_e:
            print(f'SQL error encountered!\n-> Detail:\n\t-> {sql_e}')
            return 500
        except TypeError as type_e:
            print(f'Type error encountered!\n-> Detail:\n\t-> {type_e}')
            return 500

    return inner


def fix_payload(payload: dict) -> dict:
    """
    checks if requested uid exists, and if it does = set payload's id
    to last one from db + 1.
    :returns payload, with modified uid if needed
    """
    while True:
        if get_from_db({'id': payload['id']}) == 500:
            return payload
        else:
            CRED['password'] = passwd()
            with sql.connect(**CRED) as con:
                with con.cursor() as cur:
                    cur.execute('SELECT user_id FROM users ORDER BY user_id'
                                ' DESC LIMIT 1')
                    payload['id'] = str(int(cur.fetchone()[0]) + 1)
                    return payload


# For 'POST':
@error_handler
def post_to_db(payload: dict) -> int:
    """
    support for POST requests.
    Queries the database to insert a new row into users table with
    the payload json. Also uses the datetime module to generate
    current time and date as datetime for the 'Creation_date' field.
    uses fix_payload function to change id if it already exists in the db.

    :param payload: json/dict, must include "id" and "user_name"
    :return: 201 status code if success, else 500 via error handler decorator
    """
    print(f'POST initial id requested for insert: {payload["id"]}')
    payload = fix_payload(payload)
    NOW = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    CRED['password'] = passwd()
    with sql.connect(**CRED) as con:
        with con.cursor() as cur:
            cur.execute(f'INSERT INTO users (user_id,'
                        f' user_name, creation_date) VALUES('
                        f'"{payload["id"]}", '
                        f'"{payload["user_name"]}", '
                        f'"{NOW}")')
            print(f'POST Success!\nRows affected = {cur.rowcount}')
            con.commit()
            print(f'POST id used for insert: {payload["id"]}')

        return 201


# For 'POST' using prepared statement, to users_date table with datetime:
@error_handler
def post_to_db_prep_stmt(payload: dict) -> int:
    """
    support for POST requests, using a prepared statement.
    Also posts to users_date table, in which "Creation_date" column is
    of datetime type, not varchar.

    :param payload: json/dict, must include "id" and "user_name"
    :return: 201 status code if success, else 500 via error handler decorator
    """
    NOW = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    CRED['password'] = passwd()
    with sql.connect(**CRED) as con:
        with con.cursor() as cur:
            cur.execute("PREPARE stmt1 FROM"
                        "'INSERT INTO users_date (user_id, user_name, "
                        "creation_date) Values"
                        "(?, ?, ?)'")
            cur.execute("""SET @a = '{}', @b ='{}', @c = '{}'"""
                        .format(payload["id"], payload['user_name'], NOW))
            cur.execute("""EXECUTE stmt1 USING @a, @b, @c""")
            cur.execute("DEALLOCATE PREPARE stmt1")
            print(f'POST Success!\nRows affected = {cur.rowcount}')
            con.commit()

        return 201


# For 'GET':
@error_handler
def get_from_db(payload: dict):
    """
    support for GET requests.
    Queries the database to fetch USER_NAME from supplied id in
    the payload json.

    :param payload: json/dict, must include "id".
    :return: str, username corresponding to supplied id# in payload
    """
    CRED['password'] = passwd()
    with sql.connect(**CRED) as con:
        with con.cursor() as cur:
            cur.execute(f'SELECT user_name FROM users '
                        f'WHERE user_id = "{payload["id"]}"')
            q = cur.fetchone()[0]
            print("GET success!")
            return q


# For 'UPDATE':
@error_handler
def update_db(payload: dict) -> int:
    """
    support for PUT requests.
    Queries the database to update an existing row's username field
    with a new one, with its' id and new value supplied in payload.

    if no rows changed - i.e, because id doesn't exist in db
    or if requested change doesn't actually change anything
    (change "Jane" to "Jane"), returns as fail.

    :param payload: json/dict, must include "id" and "user_name"
    :return: 200 status code if success, else 500
    """
    CRED['password'] = passwd()
    with sql.connect(**CRED) as con:
        with con.cursor() as cur:
            q = "UPDATE users SET user_name = %s WHERE user_id = %s"
            vals = (payload['user_name'], payload['id'])
            cur.execute(q, vals)
            effect = cur.rowcount

            # no rows are affected -> no id / same change; return 500
            if effect > 0:
                print(f'UPDATE Success!\nRows affected: {effect}')
                con.commit()
                return 200
            else:
                return 500


# For 'DELETE':
@error_handler
def delete_from_db(payload: dict) -> int:
    """
    support for DELETE requests.
    Queries the database to delete the row identified by "id" supplied
    by json payload.

    if delete failed - nonexistent id record for example - uses
    '0 rows affected' to detect and return fail state.

    :param payload: json/dict, must include "id".
    :return: 200 status code if success, else 500
    """
    CRED['password'] = passwd()
    with sql.connect(**CRED) as con:
        with con.cursor() as cur:
            cur.execute(f'DELETE FROM users '
                        f'WHERE user_id = "{payload["id"]}"')
            effect = cur.rowcount

            # SQL doesnt raise error when deleting already nonexistent record
            if effect > 0:
                print(f'DELETE Success!\nRows affected: {cur.rowcount}')
                con.commit()
                return 200
            else:
                return 500
