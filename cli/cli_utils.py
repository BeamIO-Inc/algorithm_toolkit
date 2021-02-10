import json
import os


def get_algorithm(path):
    try:
        with open(path, 'r') as alg_file:
            alg_def = json.load(alg_file)
    except IOError:
        alg_def = {}
    return alg_def


def get_json_path(path, a):
    a = a.replace('\\', os.sep).replace('/', os.sep)
    return os.path.join(path, 'algorithms', a, 'algorithm.json')


def get_chain_def(path, chain_name=None):
    chain_path = os.path.join(path, 'chains')
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


def clear_chains(path):
    chain_path = os.path.join(path, 'chains')

    for root, dirs, files in os.walk(chain_path):
        for f in files:
            try:
                os.unlink(os.path.join(chain_path, f))
            except IOError:
                pass


def save_chain_files(path, chains):
    for k, v in chains.items():
        try:
            with open(os.path.join(path, 'chains', k + '.json'), 'w') as f:
                temp_json = {k: v}
                json.dump(temp_json, f, indent=4, separators=(',', ': '))
        except IOError:
            pass
