import json
import os
import distro
import pkg_resources
import platform
import psutil

from flask import make_response, jsonify

from algorithm_toolkit.utils import create_random_string, get_chain_def, make_dir_if_not_exists

from atk.atk_algorithm_chain import AtkAlgorithmChain
from atk import app


def check_chain_request_form(request, chain_name, path):
    chain = None
    status_key = None
    run_mode = None
    iter_param = None
    iter_type = None
    iter_value = None

    if request.method == 'POST':
        try:
            chain = request.form['chain']
        except KeyError:
            chain = None

        try:
            status_key = request.form['status_key']
        except KeyError:
            status_key = None

        if 'run_mode' in request.form:
            if request.form['run_mode'] == 'batch':
                try:
                    run_mode = 'batch'
                    iter_param = request.form['iter_param']
                    iter_type = request.form['iter_type']
                    iter_value = request.form['iter_value']
                except KeyError:
                    return make_response('Batch mode misconfigured', 400)
            else:
                run_mode = 'single'
        else:
            run_mode = 'single'
    elif request.method == 'GET':  # pragma: no branch
        chain = request.args.get('chain', None)
        status_key = request.args.get('status_key', None)
        run_mode = request.args.get('run_mode', 'single')
        iter_param = request.args.get('iter_param', None)
        iter_type = request.args.get('iter_type', None)
        iter_value = request.args.get('iter_value', None)

    if status_key is None:
        status_key = create_random_string(http_safe=True)

    if chain is None:
        return make_response('Missing chain parameter in request', 400)

    if chain.lower() == 'from_global':
        try:
            chain = app.config['CHAIN_DATA'].pop(status_key)
        except ValueError:
            return make_response(
                'Chain parameter not present in app configuration', 400)
    else:
        try:
            chain = json.loads(chain)
        except ValueError:
            return make_response('Chain parameter not properly formatted', 400)

    if chain_name not in get_chain_def(path):
        return make_response('Chain name does not exist', 400)

    if 'algorithms' not in chain:
        return make_response('Algorithms not defined', 400)

    return ({
        'chain': chain,
        'status_key': status_key,
        'run_mode': run_mode,
        'iter_param': iter_param,
        'iter_type': iter_type,
        'iter_value': iter_value
    })


def process_chain_request(checked_response, path):
    chain = checked_response['chain']
    status_key = checked_response['status_key']
    run_mode = checked_response['run_mode']
    iter_param = checked_response['iter_param']
    iter_type = checked_response['iter_type']
    iter_value = checked_response['iter_value']

    c_obj = AtkAlgorithmChain(path, chain)
    if c_obj.chain_definition == {}:
        return make_response('Chain name not found', 404)

    cl = c_obj.create_ledger(status_key)
    cl.make_working_folders()

    if run_mode == 'single':
        response = c_obj.call_chain_algorithms()
        save_fname = status_key + '.json'

        if 'CHAIN_LEDGER_HISTORY_PATH' in app.config:
            save_path = os.path.join(
                app.config['CHAIN_LEDGER_HISTORY_PATH'], save_fname)
        else:
            make_dir_if_not_exists(os.path.join(path, 'history'))
            save_path = os.path.join(path, 'history', save_fname)
        c_obj.chain_ledger.save_history_to_json(save_path, pretty=True)

        if 'CHAIN_HISTORY' in app.config:
            if app.config['CHAIN_HISTORY_LENGTH'] > 0:
                ch = app.config['CHAIN_HISTORY']

                if len(ch) > app.config['CHAIN_HISTORY_LENGTH']:
                    ch.popitem(last=False)

                ch[status_key] = c_obj.chain_ledger
    else:
        response = c_obj.call_batch(iter_param, iter_type, iter_value)

    cl.remove_working_folders()

    if response['output_type'] == 'error':
        return make_response(jsonify(response), 400)

    return jsonify(response)


def bytes2human(n):
    # http://code.activestate.com/recipes/578019
    # >>> bytes2human(10000)
    # '9.8K'
    # >>> bytes2human(100001221)
    # '95.4M'
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.1f%s' % (value, s)
    return "%sB" % n


def vital_stats():
    vitals = {}
    system = platform.system()
    if system == 'Darwin':
        os = 'Mac OS ' + platform.mac_ver()[0]
    elif system == 'Windows':
        os = 'Windows ' + ' '.join(str(x) for x in platform.win32_ver())
    elif system == 'Linux':
        os = ' '.join(str(x) for x in distro.linux_distribution())
    elif system == 'Java':
        os = 'Java ' + platform.java_ver()[0]
    else:
        os = platform.platform()
    vitals['os'] = os
    vitals['python'] = platform.python_version()
    vitals['atk'] = pkg_resources.get_distribution('algorithm_toolkit').version
    vitals['cpu'] = psutil.cpu_percent(interval=0.1, percpu=True)

    disk_stats = psutil.disk_usage('/')
    vitals['disk'] = {
        'free': bytes2human(disk_stats.free),
        'percent': disk_stats.percent,
        'total': bytes2human(disk_stats.total),
        'used': bytes2human(disk_stats.used)
    }

    mem_stats = psutil.virtual_memory()
    vitals['mem'] = {
        'used': mem_stats.used,
        'percent': mem_stats.percent
    }

    return vitals
