#!/usr/bin/env python3

"""
apated clean env from earlier project.
shuts down the rest_app server instance
by invoking a get request to a specific
shutdown route in the server.

tries 3 times with 2 second delay.
"""
import requests
from time import sleep


def send_stop(port: int):
    """
    handles the request.get part to stop the server,
    coded to be localhost at port # <port> supplied.

    :param port: int, which port at localhost is the server?
    :return: 200 if successful, else 500
    """
    attempts = 1
    while attempts <= 3:
        try:
            res = requests.get(f'http://127.0.0.1:{port}/stop_server')
            if res.ok:
                print(f'server at port {port} shut down success, 200')
                print('===============\n')
                return 200

            elif res.status_code == 404:
                raise requests.exceptions.RequestException('No path!')

        except requests.exceptions.RequestException as e:
            print(f'Connection error!\n'
                  f'the Error was:\n{e}\n')

            print(f'this is attempt #{attempts}/3...\n')
            print('\t\n----------------\n')
            sleep(2)
            attempts += 1
            continue

    if attempts > 3:
        print(f'server shutdown at localhost port {port} failed!')
        print('\t\n================\n')
        return 500


def main():
    # to add more servers: {'<server_name>': send_stop(<int: listening port>)}
    # TODO: make server address group an optional arg
    servers_status = {'rest_app': send_stop(5000)}

    if 500 in servers_status.values():
        fails = [x for x in servers_status.keys() if
                 servers_status[x] == 500]
        print(f'\nThe following server/s had fail state:\n{fails}\n')
        raise Exception('!!FAILED!! - server/s failed to shutdown.')
    else:
        print('\nall server/s successfully stopped.')
        return 0


if __name__ == '__main__':
    main()

