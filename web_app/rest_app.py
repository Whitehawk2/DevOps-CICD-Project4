"""
    REST api Flask gateway to database access.
    uses module db_connector to interface with MySQL user database.
    accepts 4 HTML methods: POST, GET, PUT and DELETE.

"""
from flask import Flask, request, jsonify
import db_connector as db

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False  # to keep original order for looks


@app.route('/users/<user_id>', methods=['POST', 'GET', 'PUT', 'DELETE'])
def user(user_id):
    """
    Accepts requests by various HTTP methods, returns json response
    and appropriate HTML status code.

    :param user_id: the user id to check/update/add. either from json,
           or from html address
    :return: a json response + HTML status code
    """
    # GET
    if request.method == 'GET':
        """
        GET accepts json with id taken from address, or
        just by browsing to the address + requested user id,
        returns request from database via db_connector
        as json + status code
        """
        db_response = db.get_from_db({'id': user_id})

        # using jsonify to set mime type & look better as a response
        if db_response == 500:
            return jsonify({'status': 'error',
                            'reason': 'no such id'}), 500
        else:
            return jsonify({'status': 'OK',
                            'user_name': db_response}), 200

    # POST
    elif request.method == 'POST':
        """
        POST accepts json with user_id and required user name,
        inserts it to the DB via db_connector, and returns response
        json + status code.

        Change "db.post_to_db()" to "db.post_to_db_prep_stmt()
        to use the prepared statement + datetime column version
        """
        request_data = request.json.get('user_name')
        db_response = db.post_to_db({'id': user_id,
                                     'user_name': request_data})

        if db_response == 500:
            return jsonify({'status': 'error',
                            'reason': 'id already exists'}), 500
        else:
            return jsonify({'status': 'OK',
                            'user_added': request_data}), 200

    # PUT
    elif request.method == 'PUT':
        """
        PUT accepts json with user id and username,
        and updates a record from the DB via db_connector,
        returning json + status code of result.

        if requested id doesn't exist or requested change
        isn't actually a change, this will result in failure.
        """
        request_data = request.json.get('user_name')
        db_response = db.update_db({'id': user_id,
                                    'user_name': request_data})

        if db_response == 500:
            return jsonify({'status': 'error',
                            'reason': 'no such id'}), 500
        else:
            return jsonify({'status': 'OK',
                            'user_updated': request_data}), 200

    # DELETE
    elif request.method == 'DELETE':
        """
        DELETE accepts a user id, and using db_connector,
        attempts to delete the row with corresponding userid.

        returns json + status code.
        """
        db_response = db.delete_from_db({'id': user_id})

        if db_response == 500:
            return jsonify({'status': 'error',
                            'reason': 'no such id'}), 500
        else:
            return jsonify({'status': 'OK',
                            'user_deleted': user_id}), 200


@app.route('/stop_server')
def stop_server():
    """
    Stops the running server by sending a CTRL-C / SIGTERM
    thru signal module
    """
    import os
    import signal
    try:
        # on windows:
        os.kill(os.getpid(), signal.CTRL_C_EVENT)
        print('server stopped - SIGTERM')
        return 'server stopped'

    except AttributeError:
        # on linux:
        os.kill(os.getpid(), signal.SIGTERM)
        print('server stopped')
        return 'server stopped'


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)

