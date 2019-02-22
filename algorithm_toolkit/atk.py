from __future__ import division

import copy
import glob
import importlib
import json
import numpy as np
import os
import re
import traceback

from . import app

from .utils.data_utils import find_in_dict, text2int, test_json_serialize
from .utils.file_utils import (
    get_json_path,
    get_algorithm,
    make_dir_if_not_exists,
    get_chain_def,
    remove_folder
)

from markupsafe import escape


class AlgorithmException(Exception):
    """Raise ATK-specific errors"""


class Algorithm:

    def __init__(self, cl=None, params=None, **kwargs):
        self.logger = app.logger
        self.name = None
        self.errors = []
        self.params = params
        self.cl = cl

    def set_up(self, name, json_path):
        self.name = name

        with open(json_path) as json_file:
            definition = json.load(json_file)

        if self.check_params(definition):
            return self.run()
        else:
            self.raise_parameter_errors(self.errors)

    def custom_check(self, val, val2, check):
        if check == 'greaterthan' and val <= val2:
            return False
        elif check == 'lessthan' and val >= val2:
            return False
        else:
            return True

    def add_error_message(self, p, err):
        self.errors.append({
            "parameter": p,
            "error": err
        })

    def check_param(self, p, required, is_valid):
        p_type = p['data_type'].lower()
        params = self.params

        """
        Data type validation
        """
        if required:
            if p['name'] not in params:
                self.add_error_message(p['name'], 'Parameter missing')
                is_valid = False

        if p_type == 'string' and type(params[p['name']]) != str:
            try:
                str(params[p['name']])
            except ValueError:  # pragma: no cover
                self.add_error_message(p['name'], 'Not a valid string')
                is_valid = False
        elif p_type == 'integer' and type(params[p['name']]) != int:
            try:
                params[p['name']] = int(params[p['name']])
            except ValueError:
                if not required and params[p['name']] == '':
                    pass
                else:
                    self.add_error_message(p['name'], 'Not a valid integer')
                    is_valid = False
        elif p_type == 'float' and type(params[p['name']]) != float:
            try:
                params[p['name']] = float(params[p['name']])
            except ValueError:
                if not required and params[p['name']] == '':
                    pass
                else:
                    self.add_error_message(p['name'], 'Not a valid float')
                    is_valid = False
        elif p_type == 'array' and type(
                params[p['name']]) != list and type(
                params[p['name']]) != np.ndarray:
            try:
                if params[p['name']][0] == '[':
                    [item for item in params[p['name']][1:-1].split(",")]
                else:
                    [item for item in params[p['name']].split(",")]
            except (ValueError, TypeError):
                self.add_error_message(p['name'], 'Not a valid array')
                is_valid = False

        """
        Parameter value validation: numeric parameters
        """
        if is_valid and (p_type == 'integer' or p_type == 'float'):
            if 'min_value' in p and p['min_value']:
                if params[p['name']] < p['min_value']:
                    self.add_error_message(p['name'], 'Value too small')
                    is_valid = False
            if 'max_value' in p and p['max_value']:
                if params[p['name']] > p['max_value']:
                    self.add_error_message(p['name'], 'Value too large')
                    is_valid = False
            if 'custom_validation' in p:
                p_cv = p['custom_validation']
                if p_cv:
                    p_cv = p_cv.lower().replace(' ', '')
                    if (
                            p_cv[:11] == 'greaterthan' or
                            p_cv[:8] == 'lessthan'
                    ):
                        p_check = p_cv.split('.')[0]
                        p_param = params[p_cv.split('.')[1]]
                        if p_type == 'integer':
                            p_param = int(p_param)
                        else:
                            p_param = float(p_param)
                        if not self.custom_check(
                                params[p['name']], p_param, p_check):
                            if p_check == 'greaterthan':
                                self.add_error_message(
                                    p['name'],
                                    'Value must be greater than ' + str(
                                        p_param)
                                )
                            else:
                                self.add_error_message(
                                    p['name'],
                                    'Value must be less than ' + str(
                                        p_param)
                                )
                            is_valid = False
                if p_type == 'integer':
                    if p_cv == 'evenonly' and params[p['name']] % 2 != 0:
                        self.add_error_message(
                            p['name'], 'Value must be an even number')
                        is_valid = False
                    elif p_cv == 'oddonly' and params[p['name']] % 2 == 0:
                        self.add_error_message(
                            p['name'], 'Value must be an odd number')
                        is_valid = False

        """
        Parameter value validation: value in list
        """
        if 'parameter_choices' in p:
            p_c = p['parameter_choices']
            if is_valid and p_c is not None:
                if len(p_c) > 0 and params[p['name']] not in p_c:
                    self.add_error_message(
                        p['name'],
                        'Value not in list of valid choices: ' + str(
                            p_c
                        )
                    )
                    is_valid = False

        """
        Parameter value validation: Regular Expression
        """
        if 'custom_validation' in p:
            p_cv = p['custom_validation']
            if is_valid and p_cv and p_cv[0] == '^':
                if not re.match(p_cv, params[p['name']]):
                    self.add_error_message(
                        p['name'],
                        'Value does not match expression: "' + p_cv + '"'
                    )
                    is_valid = False

        return is_valid

    def check_params(self, definition):
        rps = definition['required_parameters']
        ops = definition['optional_parameters']
        is_valid = True
        for rp in rps:
            try:
                is_valid = self.check_param(rp, True, is_valid)
            except Exception as e:
                if hasattr(e, 'message'):
                    msg = e.message
                else:
                    msg = e.args[0]

                self.add_error_message(rp['name'], msg)
                is_valid = False

        for op in ops:
            if op['name'] in self.params:
                if self.params[op['name']] != '':
                    try:
                        is_valid = self.check_param(op, False, is_valid)
                    except Exception as e:
                        if hasattr(e, 'message'):
                            msg = e.message
                        else:
                            msg = e.args[0]

                        self.add_error_message(op['name'], msg)
                        is_valid = False
                else:
                    del self.params[op['name']]

        return is_valid

    def run(self):  # pragma: no cover
        pass

    def raise_parameter_errors(self, err):
        raise ValueError(err)

    def raise_client_error(self, err):
        raise AlgorithmException(err)


class AlgorithmChain(object):

    def __init__(self, path, passed_chain):
        self.atk_path = path
        self.chain_name = passed_chain['chain_name']
        self.algs = passed_chain['algorithms']
        self.chain_ledger = None
        self.chain_definition = get_chain_def(path, self.chain_name)

    class ChainLedger(object):
        '''
        ## ChainLedger

        The ChainLedger is the accounting system for an AlgorithmChain. It
        keeps track of changes made to algorithm metadata throughout
        the course of a Chain of an arbitrary set of algorithms.

        The metadata dict is available for developers to use to pass key/value
        pairs to future algorithms, or to inform the Chain regarding how to
        output a final result. A copy of the current state of the metadata
        dict is added to the 'history' list after each algorithm in the Chain
        executes.
        '''

        def __init__(self, status_key):
            self.status_key = status_key
            self.metadata = {}
            self.history = []
            self.chain_percent = 0
            self.batch_percent = 0

        def add_to_metadata(self, key, value):
            self.metadata[key] = value

        def get_from_metadata(self, key):
            return self.metadata[key]

        def archive_metadata(self, algorithm_name, algorithm_params):
            self.metadata['algorithm_name'] = algorithm_name
            self.metadata['algorithm_params'] = algorithm_params
            self.history.append(self.metadata)

        def clear_current_metadata(self):
            self.metadata = {}

        def get_history_size(self):
            return len(self.history)

        def get_from_history(self, history_index, key):
            return self.history[history_index][key]

        def search_all_history(self, key):
            names = list(set(
                [item['algorithm_name'] for item in self.history]))
            items = []
            for name in names:
                items.extend(self.search_history(key, name))
            return [item for item in items if item]

        def search_history(self, key, algorithm_name):
            items = []
            for item in self.history:
                if item['algorithm_name'] == algorithm_name:
                    value = find_in_dict(key, item)
                    items.append(value)
            return items

        def is_algo_in_history(self, algorithm_name):
            for item in self.history:
                if item['algorithm_name'] == algorithm_name:
                    return True

            return False

        def set_status(self, status, percent=0):
            chain_status = {}
            status = escape(str(status))
            chain_status['latest_msg'] = status
            try:
                all_msg = app.config[self.status_key]['all_msg'] + '  \n'
                all_msg += status
            except KeyError:
                all_msg = status
            chain_status['all_msg'] = all_msg
            chain_status['algorithm_percent_complete'] = percent
            chain_status['chain_percent_complete'] = self.chain_percent
            chain_status['batch_percent_complete'] = self.batch_percent
            app.config[self.status_key] = chain_status

        def get_run_state(self):
            # set run_state for the chain or batch job
            # 0 = cancel
            # 1 = running
            if self.status_key + '_run_state' in app.config:
                return app.config[self.status_key + '_run_state']
            return 1

        def history_to_json(self):
            alg_param_history = self.params_to_json()
            for ind in range(self.get_history_size()):
                metadata = self.history[ind]
                for k, v in metadata.items():
                    if (
                        k != 'algorithm_params' and
                        k != 'algorithm_name' and
                        k != 'chain_output_value'
                    ):
                        if not test_json_serialize(v):
                            v = 'Value not JSON serializable'
                        alg_param_history['atk_chain_metadata'][ind][k] = v

            return alg_param_history

        def save_history_to_json(self, filename, pretty=False):
            json_dict = self.history_to_json()
            self.save_json_to_file(json_dict, filename, pretty)

        def params_to_json(self):
            alg_chain_info = []
            for ind in range(self.get_history_size()):
                params = self.get_from_history(ind, 'algorithm_params')
                for k, v in params.items():
                    if not test_json_serialize(v):
                        params[k] = 'Value not JSON serializable'

                alg_chain_info.append(
                    {
                        'algorithm_name': self.get_from_history(
                            ind, 'algorithm_name'),
                        'algorithm_params': params
                    }
                )
            return {'atk_chain_metadata': alg_chain_info}

        def save_params_to_json(self, filename, pretty=False):
            json_dict = self.params_to_json()
            self.save_json_to_file(json_dict, filename, pretty)

        def save_json_to_file(self, content, filename, pretty):
            fp = open(filename, 'w')
            if pretty:
                fp.write(json.dumps(
                    content, indent=4, separators=(',', ': ')))
            else:
                fp.write(json.dumps(content))
            fp.close()

        def make_working_folders(self):
            base_path = os.path.join(
                app.config['DEFAULT_WORKING_ROOT'], self.status_key)
            temp_path = os.path.join(base_path, 'temp')
            make_dir_if_not_exists(temp_path)

        def get_temp_folder(self):
            return os.path.join(
                app.config['DEFAULT_WORKING_ROOT'], self.status_key, 'temp')

        def clear_temp_folder(self):
            remove_folder(self.get_temp_folder())
            self.make_working_folders()

        def remove_working_folders(self):
            base_path = os.path.join(
                app.config['DEFAULT_WORKING_ROOT'], self.status_key)
            remove_folder(base_path)

    def create_ledger(self, status_key):
        self.chain_ledger = self.ChainLedger(status_key)
        return self.chain_ledger

    def check_licenses(self):  # pragma: no cover
        pass

    def call_batch(self, iter_param, iter_type, iter_value):
        alg, param = iter_param.split('__')
        batch_has_error = False
        msg = ''
        iter_list = []

        if iter_type == 'files':
            iter_list = glob.glob(str(iter_value))
        elif iter_type == 'range':
            try:
                ranges = [int(x.strip()) for x in iter_value.split(',')]
                if len(ranges) == 3:
                    iter_list = range(ranges[0], ranges[1] + 1, ranges[2])
                elif len(ranges) == 2:
                    iter_list = range(ranges[0], ranges[1] + 1)
                else:
                    batch_has_error = True
                    msg = 'Invalid iterator'
            except ValueError:
                batch_has_error = True
                msg = 'Invalid iterator'

        if len(iter_list) == 0:
            batch_has_error = True
            if msg == '':
                msg = 'Empty batch'

        if batch_has_error:
            response = {
                'output_type': 'error',
                'message': msg
            }
            return response

        batch_result = []
        batch_output = {}
        original_algs = self.algs
        temp_alg = [x for x in original_algs if x['name'] == alg][0]
        batch_length = len(iter_list)

        self.chain_ledger.set_status('Starting batch job...', 0)

        for idx, i in enumerate(iter_list):
            if self.chain_ledger.get_run_state() == 0:
                response = {
                    'output_type': 'error',
                    'message': 'Batch job cancelled'
                }
                return response
            temp_alg['parameters'][param] = i
            self.algs = copy.deepcopy(original_algs)
            try:
                response = self.call_chain_algorithms()
            except Exception as e:
                message = str(type(e).__name__) + ':' + str(e.args)
                app.logger.error(str(traceback.format_exc()))
                response = {
                    'output_type': 'error',
                    'error_message': str(message)
                }

            batch_result.append(response)
            batch_output[idx] = self.chain_ledger.history_to_json()

            self.chain_ledger.history = []
            self.chain_ledger.metadata = {}
            self.chain_ledger.batch_percent = int(
                (idx + 1) / batch_length * 100)

        response = {
            'output_type': 'batch_result',
            'output_value': batch_result
        }

        batch_output['batch_type'] = iter_type
        batch_output['batch_iterator'] = iter_param
        batch_output['batch_iteration_value'] = iter_value

        save_fname = 'batch_' + self.chain_ledger.status_key + '.json'
        if 'CHAIN_LEDGER_HISTORY_PATH' in app.config:
            save_path = os.path.join(
                app.config['CHAIN_LEDGER_HISTORY_PATH'], save_fname)
        else:
            make_dir_if_not_exists(os.path.join(self.atk_path, 'history'))
            save_path = os.path.join(self.atk_path, 'history', save_fname)
        self.chain_ledger.save_json_to_file(
            batch_output, save_path, pretty=True)

        self.chain_ledger.batch_percent = 100
        self.chain_ledger.set_status('Batch complete', 100)

        return response

    def call_chain_algorithms(self):
        cl = self.chain_ledger
        algs = self.algs
        cl.set_status('Starting chain run...', 0)

        import time
        chain_length = len(algs)
        cl.chain_percent = 0
        for idx, a in enumerate(algs):
            cl.chain_percent = int(idx / chain_length * 100)
            start = time.time()
            cl.set_status('Running algorithm: ' + a['name'])

            try:
                temp_params = a['parameters']
            except KeyError:
                temp_params = {}

            try:
                cl = self.call_algorithm(a['name'], temp_params, idx)
                cl.archive_metadata(a['name'], temp_params)
                if idx != len(algs) - 1:
                    cl.clear_current_metadata()
            except ValueError as e:
                if hasattr(e, 'message'):
                    msg = e.message
                else:
                    msg = e.args[0]
                response = {
                    'output_type': 'error',
                    'message': 'Error in parameters',
                    'error_list': msg
                }
                app.logger.error(str(response))
                return response
            except AlgorithmException as e:
                if hasattr(e, 'message'):
                    msg = e.message
                else:
                    msg = e.args[0]
                response = {
                    'output_type': 'error',
                    'message': msg
                }
                app.logger.error(str(response))
                return response

            end = time.time()
            app.logger.info("alg ran in: " + str(end - start) + " s")

        cl.chain_percent = 100
        cl.set_status('Chain run complete', 100)

        if 'chain_output_value' in cl.metadata:
            response = cl.metadata['chain_output_value']
        else:
            response = {
                'output_type': 'string',
                'output_value': 'Chain run complete.'
            }

        return response

    def call_algorithm(self, algorithm, params, idx):
        cl = self.chain_ledger
        cd = self.chain_definition
        try:
            this_def = cd[idx]
        except IndexError:
            err = {
                "parameter": '',
                "error": 'Algorithm not found'
            }
            raise ValueError(err)

        temp_params = []
        if 'parameters' in this_def:
            temp_params = this_def['parameters']

        for p in temp_params:
            p_items = temp_params[p]
            if 'source' in p_items:
                if p_items['source'] == 'chain_ledger':
                    if 'source_algorithm' in p_items:
                        temp_output_list = cl.search_history(
                            p_items['key'], p_items['source_algorithm'])

                        if 'occurrence' in p_items:
                            index = text2int(p_items['occurrence'])
                        else:
                            index = -1
                        params[p] = temp_output_list[index]

        import_str = '.' + algorithm.replace('/', '.') + '.main'
        try:
            m = importlib.import_module(import_str, package='algorithms')
        except ImportError:
            import_str = 'algorithms' + import_str
            m = importlib.import_module(import_str, package=None)

        json_path = get_json_path(self.atk_path, algorithm)
        return_value = m.Main(cl=cl, params=params).set_up(
            algorithm, json_path)

        return return_value

    def get_request_dict(self):
        '''
        Return a dict containing all algorithms in the current chain and their
        default parameter values as if making a request to run a chain (e.g.:
        from a web form)
        '''
        request_dict = {}
        request_dict['chain_name'] = self.chain_name
        cd = self.chain_definition
        temp_alg_list = []
        for alg in cd:
            a_name = alg['algorithm']
            json_path = get_json_path(self.atk_path, a_name)
            alg_def = get_algorithm(json_path)
            temp_alg = {}
            temp_alg['algorithm'] = a_name
            temp_params = {}
            for rp in alg_def['required_parameters']:
                if 'default_value' in rp:
                    temp_params[rp['name']] = rp['default_value']
                else:
                    temp_params[rp['name']] = None

            for op in alg_def['optional_parameters']:
                if 'default_value' in op:
                    temp_params[op['name']] = op['default_value']
                else:
                    temp_params[op['name']] = None
            temp_alg['parameters'] = temp_params
            temp_alg_list.append(temp_alg)

        request_dict['algorithms'] = temp_alg_list
        return request_dict
