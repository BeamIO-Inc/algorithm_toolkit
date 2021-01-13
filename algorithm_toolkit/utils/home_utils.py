import requests
import json

from flask import make_response

from .data_utils import create_random_string
from .file_utils import get_chain_def


def chain_check(request, chain_name, path):

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
        'iter_val': iter_value
    })
