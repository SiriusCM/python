from flask import request, Flask


def create_server(host, port):
    flask = Flask(__name__)

    @flask.route('/gm/info')
    def info():
        id = request.args.get('id')
        return id

    flask.run(host, port)
