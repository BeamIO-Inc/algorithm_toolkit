import json
import os
import shutil


def make_dir_if_not_exists(dir_to_create):
    if not os.path.exists(dir_to_create):
        os.makedirs(dir_to_create)


def remove_folder(path):
    if os.path.exists(path):
        shutil.rmtree(path)


def list_algorithms(path):
    installed_algs = []
    alg_path = os.path.join(path, 'algorithms')
    for root, dirs, files in os.walk(alg_path):
        for algdir in dirs:
            parent = root[root.rfind(os.sep) + 1:]
            if parent == 'algorithms':
                temp_path = get_json_path(path, algdir)
            else:
                temp_path = get_json_path(path, parent + os.sep + algdir)
            temp_alg = get_algorithm(temp_path)
            if temp_alg != {}:
                installed_algs.append(temp_alg)
    return sorted(installed_algs, key=lambda k: k['name'])


def get_algorithm(path):
    try:
        with open(path, 'r') as alg_file:
            try:
                alg_def = json.load(alg_file)
            except ValueError:
                alg_def = {}
    except IOError:
        alg_def = {}
    return alg_def


def get_chain_def(path, chain_name=None):
    chain_path = os.path.join(path, 'chains')
    if not os.path.exists(chain_path):
        os.makedirs(chain_path)

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


def get_json_path(path, a):
    a = a.replace('\\', os.sep).replace('/', os.sep)
    return os.path.join(path, 'algorithms', a, 'algorithm.json')
