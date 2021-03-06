import logging
import sys
import socket

WERKZEUG_SHDM_CHANGE_RELEASE = '0.16.0'

import werkzeug

if werkzeug.__version__ < WERKZEUG_SHDM_CHANGE_RELEASE:
    from werkzeug.wsgi import SharedDataMiddleware
else:
    from werkzeug.middleware.shared_data import SharedDataMiddleware

from werkzeug.serving import run_simple
from werkzeug.utils import import_string

DEF_SERVER_IP   = '127.0.0.1'
DEF_SERVER_PORT = 4242

logging.basicConfig(level=logging.INFO)


def run_app(app, ip=DEF_SERVER_IP, port=DEF_SERVER_PORT, use_debugger=True, use_reloader=True, threaded=True):
    app = SharedDataMiddleware(app, {
        '/': 'static'
    })
    while True:
        try:
            run_simple(ip, port, app, use_debugger=use_debugger, use_reloader=use_reloader, threaded=threaded)
            break
        except (OSError, socket.error):
            port += 1


if __name__ == '__main__':
    sys.path.insert(0, '.')
    if len(sys.argv) > 1:
        module_name = sys.argv[1]
        module_name = module_name.split('.py')[0]
        if ':' not in module_name:
            module_name += ':app'
        app = import_string(module_name)

    if len(sys.argv) > 2:
        server_ip = sys.argv[2]
    else:
        server_ip = DEF_SERVER_IP

    if ':' in server_ip:
        server_ip, server_port = server_ip.split(':')

        # For now, werkzeug defaults to localhost if ip == '', but may change.
        if not server_ip:
            server_ip = DEF_SERVER_IP

        try:
            server_port = int(server_port)
        except ValueError:
            try:
                server_port = socket.getservbyname(server_port, 'tcp')

            # OSError in python3, but error in python2.7.
            except Exception:
                server_port = DEF_SERVER_PORT
    else:
        server_port = DEF_SERVER_PORT

    run_app(app, server_ip, server_port)
