import os

from flask import jsonify, request
from flask_cors import cross_origin

from . import manage
from .. import app, check_management_api_key, debug_only
from ..utils.manage_utils import vital_stats

management_api_key = app.config['ATK_MANAGEMENT_API_KEY']
api_key = app.config['API_KEY']
cors_origins = app.config['CORS_ORIGIN_WHITELIST']


def shutdown_server():  # pragma: no cover
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


@manage.route('/up/', methods=['GET'])
@cross_origin(origins=cors_origins)
def up():
    return 'Running'


@manage.route('/vitals/', methods=['GET'])
@cross_origin(origins=cors_origins)
@check_management_api_key(request, api_key, management_api_key)
def get_vitals():
    return jsonify(vital_stats())


@manage.route('/get_log/', methods=['GET'])
@cross_origin(origins=cors_origins)
@check_management_api_key(request, api_key, management_api_key)
def get_log():
    log_path = os.path.join(app.config['ATK_PATH'], 'logs', 'app.log')

    if os.path.isfile(log_path):
        with open(log_path, 'r') as log_file:
            log_contents = log_file.read()
    else:
        log_contents = 'Log file not found'
    return jsonify(log_contents)


@manage.route('/get_ledger/<status_key>/', methods=['GET'])
@cross_origin(origins=cors_origins)
@check_management_api_key(request, api_key, management_api_key)
def get_ledger(status_key):
    run_mode = request.args.get('run_mode', None)
    filename = status_key + '.json'
    if run_mode:
        if run_mode == 'batch':
            filename = 'batch_' + filename

    ledger_path = os.path.join(app.config['ATK_PATH'], 'history', filename)

    if os.path.isfile(ledger_path):
        with open(ledger_path, 'r') as ledger_file:
            ledger_contents = ledger_file.read()
    else:
        ledger_contents = 'Ledger not found'
    return jsonify(ledger_contents)


@manage.route('/cancel_job/<status_key>/', methods=['GET'])
@cross_origin(origins=cors_origins)
@check_management_api_key(request, api_key, management_api_key)
def cancel_job(status_key):
    app.config[status_key + '_run_state'] = 0
    return 'Job cancellation submitted'


@manage.route('/shutdown/', methods=['GET'])
@debug_only(app.config)
def shutdown():  # pragma: no cover
    shutdown_server()
    return 'Server shutting down...'
