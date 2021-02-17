from __future__ import division

import importlib
import logging

from algorithm_toolkit.algorithm_exception import AlgorithmException
from algorithm_toolkit.chain_ledger import ChainLedger
from algorithm_toolkit.utils import text2int, get_json_path, get_algorithm, get_chain_def


class AlgorithmChain(object):

    def __init__(self, path, passed_chain):
        self.logger = logging.getLogger('algorithm_toolkit')
        self.atk_path = path
        self.chain_name = passed_chain['chain_name']
        self.algs = passed_chain['algorithms']
        self.chain_ledger = None
        self.chain_definition = get_chain_def(path, self.chain_name)

    def create_ledger(self, status_key):
        self.chain_ledger = ChainLedger(status_key)
        return self.chain_ledger

    def check_licenses(self):  # pragma: no cover
        pass

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
                self.logger.error(str(response))
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
                self.logger.error(str(response))
                return response

            end = time.time()
            self.logger.info("alg ran in: " + str(end - start) + " s")

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