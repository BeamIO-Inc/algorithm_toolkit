from __future__ import division

import json
import os

from algorithm_toolkit import app

from algorithm_toolkit.utils.data_utils import find_in_dict, test_json_serialize
from algorithm_toolkit.utils.file_utils import (
    make_dir_if_not_exists,
    remove_folder
)

from markupsafe import escape


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
