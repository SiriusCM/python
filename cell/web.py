import importlib

from flask import request, Flask

import login


def create_server(host, port):
    flask = Flask(__name__)

    @flask.route('/gm/reload')
    def info():
        id = request.args.get('id')
        importlib.reload(login)
        return id

    flask.run(host, port)
