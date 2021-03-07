"""
this module is made to test the backend part - rest_app.py
(and db_connector by proxy)

if started by calling main(), uses path and user_name randomly from
database via get_test_config, UID is random int.
cleans up the DB after each run.
"""

from random import randint as rr
import pymysql as sql
import requests

UID = rr(20, 30)

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


def get_test_configuration() -> dict:
    """
    probes mysql to get random test configurations
    :return:  dict, with APP_PATH, BROWSER, NAME
    """
    prep = 'SELECT {0} FROM config WHERE {0}' \
           ' IS NOT NULL ORDER BY RAND() LIMIT 1;'
    CRED['password'] = passwd()
    with sql.connect(**CRED) as con:
        with con.cursor() as cur:
            cur.execute(prep.format('API_gateway',))
            api_selc = cur.fetchone()[0]

            cur.execute(prep.format('Browser_type',))
            browser_sel = cur.fetchone()[0]

            cur.execute(prep.format('Usernames', ))
            user_sel = cur.fetchone()[0]

            return {'Gateway': api_selc,
                    'Browser': browser_sel,
                    'User': user_sel}


def fail():
    """
    used as a shorthand to raise exception of test failure
    """
    raise Exception("test failed")


def post_2_db_api(path: str, username):
    """
    posts to rest_app via POST method.
    uses address parameter as well as sending username as json
    :param path: str, path to api address at required uid
    :param username: str, username to set at uid
    :raises fail exception if post unsuccessful via fail()
    """
    query = requests.post(path, json={"user_name": username})
    res = query.json()["status"]
    if res == "OK":
        print("->\tAPI POST test successful!")
        return
    else:
        fail()


def get_from_db_api(path: str, username):
    """
    posts to rest_app via GET method
    uses address parameter as well as sending username as json
    to check expected reply from db.
    :param path: str, path to api address at required uid
    :param username: str, username to set at uid
    :raises fail exception if can't GET, user is not as expected, or return
            status code is not 200 (ok)
    """
    query = requests.get(path)
    res_name = query.json()["user_name"]
    if res_name == username and query.status_code == 200:
        print("->\tAPI GET test successful!")
        return
    else:
        fail()


def get_from_mysql(uid: int, username):
    """
    Queries the db directly to double check actual mysql username
    fits uid as expected.

    uses uid to query, and evaluates answer against supplied expected
    username.

    :param uid: int, the uid of username to query
    :param username: str, username expected at uid
    :raises fail exception if expected username = username from MySQL
    """
    try:
        CRED['password'] = passwd()
        with sql.connect(**CRED) as con:
            with con.cursor() as cur:
                cur.execute('SELECT user_name FROM users'
                            f' WHERE user_id = {uid}')
                if cur.fetchone()[0] == username:
                    print("->\tSQL GET QUERY test successful!")
                    return
                else:
                    fail()
    except sql.Error:
        fail()


def cleanup(uid: int):
    """
    Tidies the working id row from MySQL, so tests can use the id
    freely.
    :param uid: int, arbitrary uid to clean before testing on
    """
    try:
        CRED['password'] = passwd()
        with sql.connect(**CRED) as con:
            with con.cursor() as cur:
                cur.execute('DELETE FROM users'
                            f' WHERE user_id = {uid}')
                con.commit()
        print("DONE.")
    except sql.Error:
        fail()


def main():
    """
    main driver for the test itself,
    Calls testing functions with args from get_test_configuration func.
    """

    # setting current test parameters from db
    this_test = get_test_configuration()
    USER_NAME, APP_PATH = (this_test['User'], this_test['Gateway'])
    APP_PATH = APP_PATH + str(UID)

    print(f"Testing with UID {UID} as {USER_NAME}...\n\nProgress:")
    try:
        post_2_db_api(APP_PATH, USER_NAME)
        get_from_db_api(APP_PATH, USER_NAME)
        get_from_mysql(UID, USER_NAME)
        print("\nAll tests successful!\n")

    # Always cleanup db
    finally:
        print("Cleaning up after tests... ", end='')
        cleanup(UID)


if __name__ == '__main__':
    main()
