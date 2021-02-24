import json
import os

# TODO verify if these are needed or if the matching methods in algorithm_toolkit.utils can be used


def get_algorithm(json_path):
    try:
        with open(json_path, 'r') as alg_file:
            alg_def = json.load(alg_file)
    except IOError:
        alg_def = {}
    return alg_def


def get_json_path(project_path, algorithm_name):
    algorithm_name = algorithm_name.replace('\\', os.sep).replace('/', os.sep)
    json_path = os.path.join(project_path, 'algorithms', algorithm_name, 'algorithm.json')
    if not os.path.isfile(json_path):
        json_path = os.path.join(project_path, 'algorithms', algorithm_name, algorithm_name + '.json')
    return json_path


def get_chain_def(project_path, chain_name=None):
    chain_path = os.path.join(project_path, 'chains')
    chain_defs = {}

    for root, dirs, files in os.walk(chain_path):
        for f in files:
            if '.json' in f:
                temp_key = f.replace('.json', '')
                try:
                    with open(os.path.join(chain_path, f)) as the_file:
                        try:
                            temp_obj = json.load(the_file)
                            chain_defs[temp_key] = temp_obj[temp_key]
                        except ValueError:
                            return {}
                except IOError:
                    return {}

    if chain_name:
        try:
            return chain_defs[chain_name]
        except KeyError:
            return {}
    else:
        return chain_defs


def clear_chains(project_path):
    chain_path = os.path.join(project_path, 'chains')

    for root, dirs, files in os.walk(chain_path):
        for f in files:
            try:
                os.unlink(os.path.join(chain_path, f))
            except IOError:
                pass


def save_chain_files(project_path, chains):
    for k, v in chains.items():
        try:
            with open(os.path.join(project_path, 'chains', k + '.json'), 'w') as f:
                temp_json = {k: v}
                json.dump(temp_json, f, indent=4, separators=(',', ': '))
        except IOError:
            pass
