import click
import configparser
import json
import os
import random
import requests
import shutil
import subprocess
import unittest

import jinja2

from io import BytesIO
from string import Template
from tabulate import tabulate
from zipfile import ZipFile

from .cli_utils import get_json_path, get_algorithm


this_path = os.path.dirname(os.path.abspath(__file__))
default_registry_url = 'https://algorithmcentral.com'
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group()
def cli():
    '''
    Welcome to the Algorithm Toolkit CLI!
    '''


@cli.command('cp', context_settings=CONTEXT_SETTINGS)
@click.argument('project_name')
@click.option('--example', '-e', help='Install example project', is_flag=True)
@click.option(
    '--with-docs', '-wd', help='Add documentation to portal', is_flag=True)
@click.option('--quiet', '-q', help='Suppress screen output', is_flag=True)
def cp_cmd(project_name, example, with_docs, quiet):
    '''
    Create an algorithm project.
    '''

    if example:
        exmpl_path = os.path.join(this_path, 'examples', 'project')
        shutil.copytree(exmpl_path, project_name)
        path = os.path.abspath(project_name)
        generate_settings(this_path, path)
        try:
            from pip import main as pipmain
        except ImportError:
            from pip._internal import main as pipmain

        reqs = os.path.join(exmpl_path, 'requirements.txt')
        pip_options = ['install', '-r', reqs]
        if quiet:
            pip_options += ['-q']
        pipmain(pip_options)
    else:
        os.mkdir(project_name)
        path = os.path.abspath(project_name)

        create_file(project_name, this_path, path, 'chains', '.json')
        create_file(project_name, this_path, path, 'licenses', '.json')
        create_file(project_name, this_path, path, 'config')
        create_file(project_name, this_path, path, '__init__')
        create_file(project_name, this_path, path, 'run')
        create_file('', this_path, path, 'gitignore', '.')

        generate_settings(this_path, path)

        os.mkdir(os.path.join(path, 'algorithms'))
        create_file(
            project_name,
            this_path,
            os.path.join(path, 'algorithms'),
            '__init__'
        )

        os.mkdir(os.path.join(path, 'logs'))
        logpath = os.path.join(path, 'logs')
        filename = os.path.join(logpath, 'app.log')
        with open(filename, 'a'):
            os.utime(filename, None)

    if with_docs:
        docs_path = os.path.join(
            os.path.abspath(os.path.join(this_path, os.pardir)), 'docs')
        dest_path = os.path.join(path, 'docs')
        if not os.path.exists(dest_path):
            os.mkdir(dest_path)
        cmd = 'sphinx-build ' + docs_path + ' ' + dest_path
        if quiet:
            cmd += ' -q'
        subprocess.call(cmd, shell=True)

    if not quiet:
        click.echo('Project created!')


@cli.command('ca', context_settings=CONTEXT_SETTINGS)
@click.argument('algorithm_name')
def ca_cmd(algorithm_name):
    '''
    Create an algorithm.
    '''

    path = os.path.dirname(os.path.abspath('config.py'))
    dest_path = os.path.join(path, 'algorithms', algorithm_name)

    try:
        os.mkdir(dest_path)
    except OSError:
        return click.echo('Algorithm already exists!')

    create_file(algorithm_name, this_path, dest_path, 'main')
    create_file(algorithm_name, this_path, dest_path, '__init__')
    create_file(algorithm_name, this_path, dest_path, 'test')

    alg_json = {
        'name': algorithm_name,
        'display_name': algorithm_name,
        'description': None,
        'version': '0.0.1',
        'private': False,
        'homepage': None,
        'required_parameters': [],
        'optional_parameters': [],
        'outputs': []
    }
    alg_license = 'other'

    if click.prompt(
            'Set up algorithm using a questionnaire (y/n)?', default='y'
    ) == 'y':
        alg_json['display_name'] = click.prompt('Display name')
        alg_json['description'] = click.prompt('Description', default='')
        alg_json['version'] = click.prompt('Version', default='0.0.1')
        alg_license = click.prompt(
            'License (AGPL|Apache|BSD|GPL|LGPL|MIT|Mozilla|Unlicense|other)',
            default='MIT'
        )
        alg_json['private'] = click.prompt('Private algorithm', default=False)
        alg_json['homepage'] = click.prompt('Developer homepage', default='')

        do_params = click.prompt('Add required parameters (y/n)?', default='n')
        p_x = 0
        while do_params == 'y':
            tp = {}
            retype_name = True
            while retype_name:
                tp['name'] = click.prompt(
                    'Short name (no spaces)').replace(' ', '_')
                name_repeat = False
                for p in alg_json['required_parameters']:
                    if p['name'] == tp['name']:
                        name_repeat = True
                        click.echo(
                            'Parameter names must be unique to an algorithm')
                retype_name = name_repeat

            tp['display_name'] = click.prompt('Display name')
            tp['description'] = click.prompt('Description', default='')
            tp['data_type'] = click.prompt(
                'Data type (string|integer|float|array)', default='string')

            if tp['data_type'] == 'integer' or tp['data_type'] == 'float':
                default_field = 'number'
            else:
                default_field = 'text'
            tp['field_type'] = click.prompt(
                'Field type (number|text|select)', default=default_field)

            tp['help_text'] = click.prompt(
                'Help text (displays below fields)', default='')
            tp['min_value'] = click.prompt(
                'Minimum value (leave blank for non-number inputs)',
                default=''
            )
            if tp['min_value'] == '':
                tp['min_value'] = None
            else:
                try:
                    tp['min_value'] = int(tp['min_value'])
                except ValueError:
                    tp['min_value'] = None

            tp['max_value'] = click.prompt(
                'Maximum value (leave blank for non-number inputs)',
                default=''
            )
            if tp['max_value'] == '':
                tp['max_value'] = None
            else:
                try:
                    tp['max_value'] = int(tp['max_value'])
                except ValueError:
                    tp['max_value'] = None

            tp['default_value'] = click.prompt('Default value', default='')
            tp['custom_validation'] = click.prompt(
                'Custom validation (see docs)', default='')
            tp['parameter_choices'] = click.prompt(
                'Parameter choices (see docs)', default='')
            tp['sort_order'] = click.prompt('Sort order', default=p_x)
            alg_json['required_parameters'].append(tp)
            do_params = click.prompt(
                'Add another required parameter (y/n)', default='n')
            p_x += 1

        do_outs = click.prompt('Add outputs (y/n)?', default='n')
        o_x = 0
        while do_outs == 'y':
            out = {}
            retype_name = True
            while retype_name:
                out['name'] = click.prompt(
                    'Short name (no spaces)').replace(' ', '_')
                name_repeat = False
                for p in alg_json['outputs']:
                    if p['name'] == out['name']:
                        name_repeat = True
                        click.echo(
                            'Output names must be unique to an algorithm')
                retype_name = name_repeat

            out['display_name'] = click.prompt('Display name')
            out['description'] = click.prompt('Description', default='')
            out['data_type'] = click.prompt(
                'Data type (string|integer|float|array)', default='string')
            out['sort_order'] = o_x
            alg_json['outputs'].append(out)
            do_outs = click.prompt('Add another output (y/n)', default='n')
            o_x += 1

    if alg_license != 'other':
        lic_file = os.path.join(
            this_path, 'sources', 'license_' + alg_license + '.txt')
        with open(lic_file) as f:
            contents = f.read()

        with open(os.path.join(dest_path, 'LICENSE'), 'w') as temp_file:
            temp_file.writelines(contents)

        alg_json['license'] = alg_license
    else:
        alg_json['license'] = 'See LICENSE File'

        with open(os.path.join(dest_path, 'LICENSE'), 'w') as temp_file:
            temp_file.write('')

    with open(os.path.join(dest_path, 'algorithm.json'), 'w') as temp_file:
        temp_file.writelines(
            json.dumps(
                alg_json, indent=4, separators=(',', ': '), sort_keys=True))

    r_source = os.path.join(this_path, 'sources', 'algorithm.md')
    with open(r_source) as r_file:
        readme = r_file.read()

    with open(os.path.join(dest_path, 'README.md'), 'w') as temp_file:
        template = jinja2.Template(readme)
        readme_txt = template.render(alg=alg_json)
        temp_file.writelines(readme_txt)

    click.echo('Algorithm created!')


@cli.command('generate_settings', context_settings=CONTEXT_SETTINGS)
@click.option(
    '--production', '-p', help='Use production settings', is_flag=True)
def generate_settings_cmd(production):
    '''
    Generate new environment variables for your algorithm project.
    '''

    path = os.path.dirname(os.path.abspath('config.py'))
    if production:
        generate_settings(this_path, path, True)
    else:
        generate_settings(this_path, path)
    click.echo('Settings files generated!')


def create_file(subst, source, dest, name, ext='.py'):
    with open(os.path.join(source, 'sources', name + '.txt')) as f:
        contents = f.read()
    if ext == '.':
        full_name = '.' + name
    else:
        full_name = name + ext
    with open(os.path.join(dest, full_name), 'w') as temp_file:
        s = Template(contents)
        if subst != '':
            contents = s.substitute(subst=subst)
        temp_file.writelines(contents)


def generate_settings(this_path, path, is_prod=False):
    # if not os.path.exists(os.path.join(path, '.flaskenv')):
    #    create_file('', this_path, path, 'flaskenv', '.')

    http_seq = (
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    )
    all_seq = http_seq + '._~`!@#$%^&*()-=+[]|?<>:;'
    api_key = "".join(
        [random.SystemRandom().choice(http_seq) for i in range(20)])
    management_api_key = "".join(
        [random.SystemRandom().choice(http_seq) for i in range(40)])
    secret_key = "".join(
        [random.SystemRandom().choice(all_seq) for i in range(100)])
    settings = (
        'FLASK_SECRET_KEY="%s"\nATK_API_KEY="%s"\nATK_MANAGEMENT_API_KEY="%s"'
    ) % (secret_key, api_key, management_api_key)

    if is_prod:
        settings += '\nFLASK_ENV=production'
    else:
        settings += '\nFLASK_ENV=development'

    create_file(settings, this_path, path, 'env', '.')


def get_reg_config_option(c, s, o):
    try:
        val = c.get(s, o)
        return val
    except configparser.NoOptionError:
        if o == 'api_key':
            return None
        elif o == 'tiledriver_api_key':
            return None
        return click.echo('Missing ' + o + ' option in config file!')


def get_reg_config(r):
    reg_config = {}
    home_dir = os.path.expanduser('~')
    if not os.path.exists(os.path.join(home_dir, '.atk', 'config')):
        return reg_config

    reg_connect = os.path.join(home_dir, '.atk', 'config')

    if r is None:
        r = 'DEFAULT'
    config = configparser.ConfigParser()
    config.read(reg_connect)

    try:
        url = get_reg_config_option(config, r, 'url')
        email = get_reg_config_option(config, r, 'email')
        api_key = get_reg_config_option(config, r, 'api_key')
        tiledriver_api_key = get_reg_config_option(
            config, r, 'tiledriver_api_key')
    except configparser.NoSectionError:
        return click.echo('No such registry in your config file!')

    reg_config['url'] = url
    reg_config['email'] = email
    reg_config['api_key'] = api_key
    reg_config['tiledriver_api_key'] = tiledriver_api_key

    return reg_config


@cli.command('publish', context_settings=CONTEXT_SETTINGS)
@click.argument('algorithm_name')
@click.option('--registry', '-r', help='Publish to which registry?')
def publish_algorithm_cmd(algorithm_name, registry):
    '''
    Publish an algorithm to the Algorithm Registry.
    '''

    reg_config = get_reg_config(registry)
    if reg_config == {}:
        # cannot publish without an account
        return click.echo('ATK Registry config file missing!')

    a_name = algorithm_name.replace('\\', os.sep).replace('/', os.sep)
    alg_path = os.path.join(os.getcwd(), 'algorithms', a_name)

    try:
        with open(os.path.join(alg_path, 'algorithm.json')) as alg_file:
            alg_def = alg_file.read()
    except IOError:
        return click.echo('Algorithm not found!')

    try:
        with open(os.path.join(alg_path, 'CHANGELOG')) as change_file:
            changelog = change_file.read()
    except IOError:
        changelog = None

    check_alg = json.loads(alg_def)
    if 'name' not in check_alg:
        return click.echo('Your algorithm needs a name!')
    elif 'display_name' not in check_alg:
        return click.echo('Your algorithm needs a display name!')
    elif 'version' not in check_alg:
        return click.echo('Your algorithm needs a version number!')

    payload = {
        'email': reg_config['email'],
        'api_key': reg_config['api_key'],
        'tiledriver_api_key': reg_config['tiledriver_api_key'],
        'algorithm_definition': alg_def
    }

    zip_filename = os.path.join(
        os.getcwd(),
        'algorithm_uploads',
        a_name,
        str(check_alg['version'])
    )
    zip_file = shutil.make_archive(zip_filename, 'zip', alg_path)
    # print(os.path.getsize(zip_file))

    if changelog:
        payload['changelog'] = changelog

    url = reg_config['url']
    if url[-1] != '/':
        url = url + '/'
    files = {'contents': open(zip_file, 'rb')}
    try:
        req = requests.post(url + 'publish/', data=payload, files=files)
    except requests.exceptions.RequestException:
        return click.echo('There was a problem publishing this algorithm')

    if req.status_code != 200:
        return click.echo(
            'There was a problem publishing this algorithm: ' + req.content)
    click.echo(req.text)


@cli.command('search', context_settings=CONTEXT_SETTINGS)
@click.argument('search_string')
@click.option(
    '--registry', '-r', help='Search algorithms from which registry?')
def search_cmd(search_string, registry):
    '''
    Search the Algorithm Registry for algorithm names matching a string.
    '''
    reg_config = get_reg_config(registry)
    payload = {}
    if reg_config != {}:
        payload['email'] = reg_config['email']
        payload['api_key'] = reg_config['api_key']
        url = reg_config['url']
    else:
        url = default_registry_url
    payload['s'] = search_string

    req = requests.get(url + '/search/', params=payload)
    if req.status_code == 200:
        algs = json.loads(req.text)
        alg_list = [[x['name'], x['description'][:75] + '...'] for x in algs]
        click.echo(
            tabulate(alg_list, headers=['Algorithm Name', 'Description']))
    else:
        click.echo(req.text)


@cli.command('info', context_settings=CONTEXT_SETTINGS)
@click.argument('algorithm')
@click.option(
    '--registry', '-r', help='Get algorithm info from which registry?')
@click.option(
    '--version', '-v', help='Specify an algorithm version', default='current')
def info_cmd(algorithm, registry, version):
    '''
    Get detailed info about an algorithm from the Registry.
    '''
    reg_config = get_reg_config(registry)
    payload = {}
    if reg_config != {}:
        payload['email'] = reg_config['email']
        payload['api_key'] = reg_config['api_key']
        url = reg_config['url']
    else:
        url = default_registry_url
    payload['a'] = algorithm
    payload['v'] = version

    req = requests.get(url + '/info/', params=payload)
    if req.status_code == 200:
        alg_info = json.loads(req.text)
        alg_obj = alg_info['algorithm'][0]
        alg_detail = alg_info['detail'][0]
        msg = alg_detail['display_name'] + ' (' + alg_obj['name'] + ')\n'
        msg += alg_detail['description'] + '\n\n'
        msg += 'License: ' + alg_detail['license'] + '\n'
        msg += 'Homepage: ' + alg_detail['homepage'] + '\n\n'
        msg += 'PARAMETERS:' + '\n'
        msg += '-----------' + '\n'
        p_list = alg_detail['parameters']
        for param in sorted(p_list, key=lambda k: k['sort_order']):
            msg += str(int(param['sort_order'])) + '. '
            msg += param['display_name'] + ' (' + param['parameter_name'] + ')'
            msg += '\n'
            if param['required']:
                msg += '   REQUIRED\n'
            msg += '   ' + param['description'] + '\n'
            msg += '   Data type: ' + param['data_type'] + '\n'
            if param['min_value'] is not None:
                msg += '   Minimum value: ' + str(param['min_value']) + '\n'
            if param['max_value'] is not None:
                msg += '   Maximum value: ' + str(param['max_value']) + '\n'
            if param['default_value'] is not None:
                msg += '   Default value: ' + param['default_value'] + '\n'
            if param['custom_validation'] is not None:
                msg += '   Custom validation: ' + param['custom_validation']
                msg += '\n'
            msg += '\n'
        o_list = alg_detail['outputs']
        msg += 'OUTPUTS:\n--------\n'
        for output in o_list:
            msg += output['display_name'] + ' ('
            msg += output['output_name'] + ')\n'
            msg += '   ' + output['description'] + '\n'
            msg += '   Data type: ' + param['data_type'] + '\n\n'
        click.echo(msg)
    else:
        click.echo('The server returned an error:\n' + req.text)


@cli.command('list', context_settings=CONTEXT_SETTINGS)
def list_cmd():
    '''
    List algorithms in the current project.
    '''
    path = os.path.dirname(os.path.abspath('config.py'))
    alg_path = os.path.join(path, 'algorithms')
    if not os.path.exists(alg_path):
        return click.echo('No algorithms installed yet!')

    installed_algs = []
    for root, dirs, files in os.walk(alg_path):
        for algdir in dirs:
            parent = root[root.rfind(os.sep) + 1:]
            if parent == 'algorithms':
                temp_path = get_json_path(path, algdir)
            else:
                temp_path = get_json_path(path, parent + os.sep + algdir)
            temp_alg = get_algorithm(temp_path)
            if temp_alg != {}:
                temp_desc = temp_alg['description']
                if len(temp_desc) > 75:
                    temp_desc = temp_desc[:75] + '...'
                installed_algs.append([
                    temp_alg['name'],
                    temp_alg['version'],
                    temp_desc
                ])
    click.echo(tabulate(
        installed_algs, headers=['Algorithm Name', 'Version', 'Description']))


@cli.command('install', context_settings=CONTEXT_SETTINGS)
@click.argument('algorithm')
@click.option(
    '--registry', '-r', help='Install algorithm from which registry?')
@click.option(
    '--version', '-v', help='Specify an algorithm version', default='current')
def install_cmd(algorithm, registry, version):
    '''
    Install an algorithm from the Registry.
    '''
    reg_config = get_reg_config(registry)
    payload = {}
    if reg_config != {}:
        payload['email'] = reg_config['email']
        payload['api_key'] = reg_config['api_key']
        url = reg_config['url']
    else:
        url = default_registry_url
    payload['a'] = algorithm
    payload['v'] = version

    req = requests.get(url + '/download/', params=payload)
    if req.status_code == 200:
        path = os.path.dirname(os.path.abspath('config.py'))
        dest_path = os.path.join(path, 'algorithms', algorithm)
        if not os.path.exists(dest_path):
            os.makedirs(dest_path)
            if os.sep in algorithm:
                namespace_path = os.path.join(
                    path,
                    'algorithms',
                    algorithm[:algorithm.find(os.sep)],
                    '__init__.py'
                )
                open(namespace_path, 'a').close()

        with ZipFile(BytesIO(req.content)) as alg_zip:
            alg_zip.extractall(dest_path)
        click.echo('Algorithm installed.')
    else:
        click.echo(req.content)


def do_uninstall(algorithm):
    path = os.path.dirname(os.path.abspath('config.py'))
    alg_path = os.path.join(path, 'algorithms', algorithm)
    if not os.path.exists(alg_path):
        return click.echo('Algorithm not found!')
    shutil.rmtree(alg_path)

    with open(os.path.join(path, 'chains.json'), 'r') as chain_file:
        chains = json.loads(chain_file.read())
    for k, v in chains.items():
        chains[k] = [x for x in chains[k] if x['algorithm'] != algorithm]
        for alg in chains[k]:
            if 'parameters' in alg:
                alg_params = alg['parameters']
                p_count = len(alg_params.items())
                for ak, av in alg_params.items():
                    if 'source_algorithm' in av:
                        if av['source_algorithm'] == algorithm:
                            if p_count == 1:
                                alg['parameter_source'] = 'user'
                                alg.pop('parameters')
                            else:
                                av.pop('occurrence', None)
                                av.pop('key', None)
                                av.pop('source_algorithm', None)
                                av['source'] = 'user'
    with open(os.path.join(path, 'chains.json'), 'w+') as f:
        json.dump(chains, f, indent=4, separators=(',', ': '))


@cli.command('uninstall', context_settings=CONTEXT_SETTINGS)
@click.argument('algorithm')
def uninstall_cmd(algorithm):
    '''
    Remove an algorithm from your project.
    '''
    do_uninstall(algorithm)

    click.echo('Algorithm uninstalled.')


@cli.command('test', context_settings=CONTEXT_SETTINGS)
@click.argument('algorithm', required=False)
def test_cmd(algorithm=None):
    '''
    \b
    Test algorithms in your project. You may specify an algorithm to test:
        >>> alg test my_algorithm

    \b
    or test all algorithms:
        >>> alg test
    '''
    from flask.cli import load_dotenv
    load_dotenv()

    os.environ['FLASK_APP'] = 'run'
    os.environ['ATK_CONFIG'] = os.path.join(os.getcwd(), 'config.py')

    if algorithm:
        base_dir = os.path.join('algorithms', algorithm)
    else:
        base_dir = '.'

    try:
        suite = unittest.TestLoader().discover(base_dir)
        unittest.TextTestRunner(verbosity=2).run(suite)
    except ImportError:
        click.echo('Algorithm does not exist')


@cli.command('register', context_settings=CONTEXT_SETTINGS)
@click.option(
    '--registry', '-r', help='Register with which registry?')
def register_cmd(registry):
    '''
    Register with the Algorithm Registry.
    '''
    reg_config = get_reg_config(registry)
    if reg_config == {}:
        return click.echo(
            'Missing ATK config file. You must have a TileDriver account to '
            'register; create one today at https://app.tiledriver.com/'
            'accounts/login/'
        )

    reg_url = reg_config['url']
    payload = {
        'email': reg_config['email'],
        'tiledriver_api_key': reg_config['tiledriver_api_key'],
    }

    try:
        click.echo('Contacting server, please wait...')
        r = requests.post(reg_url + '/register/', data=payload)
    except requests.exceptions.RequestException:
        return click.echo('There was a problem contacting the registry')

    if r.status_code != 200:
        if r.status_code == 403:
            return click.echo('Invalid login')
        return click.echo('There was a problem contacting the registry')

    click.echo(
        'Registration successful. You can now publish '
        'algorithms to the Registry.'
    )


@cli.command('run', context_settings=dict(ignore_unknown_options=True))
@click.argument('args', nargs=-1, type=click.UNPROCESSED, required=False)
def run(args):
    os.environ['FLASK_APP'] = 'run'
    os.environ['ATK_CONFIG'] = os.path.join(os.getcwd(), 'config.py')

    path = os.path.dirname(os.environ['ATK_CONFIG'])
    if not os.path.exists(os.path.join(path, '.env')):
        generate_settings(this_path, path)

    if not os.path.exists(os.path.join(path, 'logs')):
        os.mkdir(os.path.join(path, 'logs'))

    subprocess.call(['flask', 'run'] + list(args))


@cli.command('shell', context_settings=dict(ignore_unknown_options=True))
@click.argument('args', nargs=-1, type=click.UNPROCESSED, required=False)
def shell(args):
    os.environ['FLASK_APP'] = 'run'
    os.environ['ATK_CONFIG'] = os.path.join(os.getcwd(), 'config.py')

    path = os.path.dirname(os.environ['ATK_CONFIG'])
    if not os.path.exists(os.path.join(path, '.env')):
        generate_settings(this_path, path)

    if not os.path.exists(os.path.join(path, 'logs')):
        os.mkdir(os.path.join(path, 'logs'))

    subprocess.call(['flask', 'shell'] + list(args))
