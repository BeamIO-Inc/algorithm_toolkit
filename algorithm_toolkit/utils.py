import inflect
import random
import json
import os
import shutil
import re

p = inflect.engine()
word_to_number_mapping = {}
http_chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
all_chars = http_chars + '`~!@#$%*()-_=+[]{}|;:,./?'


def test_json_serialize(val):
    try:
        json.dumps(val)
        return True
    except TypeError:
        return False


def find_in_dict(key, dictionary):
    if key in dictionary:
        return dictionary[key]
    else:
        return None


def text2int(textnum):
    if len(word_to_number_mapping) == 0:
        for i in range(1, 500):
            word_form = p.number_to_words(i)  # 1 -> 'one'
            ordinal_word = p.ordinal(word_form)  # 'one' -> 'first'
            word_to_number_mapping[ordinal_word] = i - 1

    index = -1
    if textnum in word_to_number_mapping:
        index = word_to_number_mapping[textnum]
    return index


def create_random_string(n=20, http_safe=False):
    if http_safe is False:
        chars = all_chars
    else:
        chars = http_chars
    temp_str = "".join([random.SystemRandom().choice(chars) for i in range(n)])
    return temp_str


def make_dir_if_not_exists(dir_to_create):
    if not os.path.exists(dir_to_create):
        os.makedirs(dir_to_create)


def remove_folder(project_path):
    if os.path.exists(project_path):
        shutil.rmtree(project_path)


def list_algorithms(project_path):
    installed_algs = []
    alg_path = os.path.join(project_path, 'algorithms')
    for root, dirs, files in os.walk(alg_path):
        for algdir in dirs:
            parent = root[root.rfind(os.sep) + 1:]
            if parent == 'algorithms':
                temp_path = get_json_path(project_path, algdir)
            else:
                temp_path = get_json_path(project_path, parent + os.sep + algdir)
            temp_alg = get_algorithm(temp_path)
            if temp_alg != {}:
                installed_algs.append(temp_alg)
    return sorted(installed_algs, key=lambda k: k['name'])


def get_algorithm(project_path):
    try:
        with open(project_path, 'r') as alg_file:
            try:
                alg_def = json.load(alg_file)
            except ValueError:
                alg_def = {}
    except IOError:
        alg_def = {}
    return alg_def


def get_chain_def(project_path, chain_name=None):
    chain_path = os.path.join(project_path, 'chains')
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


def get_json_path(project_path, a):
    a = a.replace('\\', os.sep).replace('/', os.sep)
    return os.path.join(project_path, 'algorithms', a, 'algorithm.json')


def camel_to_snake(name):
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()


def snake_to_camel(name):
    return ''.join(word.title() for word in name.split('_'))
