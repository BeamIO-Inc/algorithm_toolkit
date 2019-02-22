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
    chain_defs = {}
    try:
        with open(os.path.join(path, 'chains.json'), 'r') as chain_file:
            try:
                chain_defs = json.load(chain_file)
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


def get_json_path(path, a):
    a = a.replace('\\', os.sep).replace('/', os.sep)
    return os.path.join(path, 'algorithms', a, 'algorithm.json')
