import copy
import glob
import os
import traceback

from algorithm_toolkit.algorithm_chain import AlgorithmChain
from algorithm_toolkit.utils import make_dir_if_not_exists

from atk import app


class AtkAlgorithmChain(AlgorithmChain):

    def __init__(self, path, passed_chain):
        AlgorithmChain.__init__(self, path, passed_chain)
        self.logger = app.logger
        self.config = app.config

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
                self.logger.error(str(traceback.format_exc()))
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
        if 'CHAIN_LEDGER_HISTORY_PATH' in self.config:
            save_path = os.path.join(
                self.config['CHAIN_LEDGER_HISTORY_PATH'], save_fname)
        else:
            make_dir_if_not_exists(os.path.join(self.atk_path, 'history'))
            save_path = os.path.join(self.atk_path, 'history', save_fname)

        self.chain_ledger.save_json_to_file(
            batch_output, save_path, pretty=True)

        self.chain_ledger.batch_percent = 100
        self.chain_ledger.set_status('Batch complete', 100)

        return response
