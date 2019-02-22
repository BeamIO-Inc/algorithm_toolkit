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
