import json
import os

import re
import shutil
import subprocess
import sys
import unittest
import warnings

from logging import StreamHandler

from flask_testing import TestCase
from wtforms.fields import core as wtfields
from wtforms import widgets as wtwidgets
from wtforms.validators import InputRequired, Optional

from t_utils import (
    get_algorithms,
    get_chains,
    get_updated_chain,
    get_chain_algs,
    get_test_run_chain,
    test_algorithm_form_data,
    get_chain_builder_block_list,
    get_chain_builder_additional_block,
    get_chain_builder_block_scripts,
    get_chain_builder_additional_script,
    get_chain_builder_chain_blocks
)

os.environ['ATK_CONFIG'] = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 't_config.py')

updated_chain = get_updated_chain()
algs = get_algorithms()
this_path = os.path.dirname(os.path.abspath(__file__))
test_alg_path = os.path.join(this_path, 'test_project')
block_list = get_chain_builder_block_list()
block_scripts = get_chain_builder_block_scripts()

with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=DeprecationWarning)


class ATKTestCase(TestCase):

    def create_app(self):
        from algorithm_toolkit import app
        return app

    def setUp(self):
        sys.path.append(test_alg_path)
        subprocess.call(['alg', 'cp', 'test_project', '-e', '-q'])

    def tearDown(self):
        # pass
        shutil.rmtree(test_alg_path)

    def test_config_vars(self):
        print('Ensure environment is set up properly')
        config = self.app.config
        self.assertEqual(type(config['LOG_HANDLERS'][0]), StreamHandler)
        self.assertEqual(
            config['CORS_ORIGIN_WHITELIST'],
            [
                'http://localhost',
                'https://mytiledriver.com',
                'https://tdprocess.com'
            ]
        )
        self.assertEqual(config['ATK_PATH'], test_alg_path)
        self.assertEqual(
            self.app.jinja_loader.searchpath[0], test_alg_path + '/templates')

    def test_atk_home(self):
        print('Home page should display correctly')
        chain_def = get_chains()
        response = self.client.get('/')
        self.assert200(response)
        self.assertTemplateUsed('index.html')
        self.assertContext('nav', 'index')
        self.assertContext('docs', False)
        self.assertContext('chains', chain_def)

    def test_algorithm_home(self):
        print('Algorithm list page should display correctly')
        chain_def = get_chains()
        response = self.client.get('/algorithms/')
        self.assert200(response)
        self.assertTemplateUsed('algorithms.html')
        self.assertContext('nav', 'algorithms')
        self.assertContext('docs', False)
        self.assertContext('chains', chain_def)
        self.assertContext('algs', sorted(algs, key=lambda a: a['name']))

    def test_list_chains_no_key(self):
        print('List chains should fail if the API key is missing')
        response = self.client.get('/list_chains/')
        self.assert401(response)
        self.assertEqual(response.data, 'API key wrong or missing')

    def test_list_chains(self):
        print('List chains should ... list the chains')
        chain_def = get_chains()
        response = self.client.get('/list_chains/?api_key=testkey')
        self.assert200(response)
        self.assertEqual(response.data, json.dumps(
            chain_def, separators=(',', ':'), sort_keys=True) + '\n')

    def test_chain_info_no_key(self):
        print('Chain info should fail if the API key is missing')
        response = self.client.get('/chain_info/map_tiles/')
        self.assert401(response)
        self.assertEqual(response.data, 'API key wrong or missing')

    def test_chain_info(self):
        print('Chain info should ... provide chain info')
        chain_def = get_chains()
        response = self.client.get('/chain_info/map_tiles/?api_key=testkey')
        self.assert200(response)
        self.assertEqual(response.data, json.dumps(
            chain_def['map_tiles'],
            separators=(',', ':'),
            sort_keys=True
        ) + '\n')

    def test_chain_algs_no_key(self):
        print('Chain algorithms should fail if the API key is missing')
        response = self.client.get('/chain_algorithms/map_tiles/')
        self.assert401(response)
        self.assertEqual(response.data, 'API key wrong or missing')

    def test_chain_algs(self):
        print('Chain algorithms should list the algorithms in a chain')
        chain_algs = get_chain_algs()
        response = self.client.get(
            '/chain_algorithms/map_tiles/?api_key=testkey')
        self.assert200(response)
        self.assertEqual(response.data, json.dumps(
            chain_algs,
            separators=(',', ':'),
            sort_keys=True
        ) + '\n')

        # add a required parameter and ensure it displays in chain_algorithms
        r_param = {
            "default_value": "",
            "field_type": "text",
            "display_name": "Useless Yet Required Parameter",
            "name": "useless_required",
            "data_type": "string",
            "max_value": None,
            "min_value": None,
            "sort_order": 2,
            "parameter_choices": [],
            "help_text": "Don't bother entering anything, and yet you must",
            "custom_validation": None,
            "description": "A completely useless yet required parameter.",
            "source": "user"
        }
        chain_algs[1]['required_parameters'].append(r_param)
        json_file = os.path.join(
            test_alg_path, 'algorithms', 'stitch_tiles', 'algorithm.json')
        chains_file = os.path.join(test_alg_path, 'chains.json')
        with open(json_file, 'r') as alg_file:
            stitch_tiles = json.load(alg_file)
        with open(json_file, 'w') as alg_file:
            stitch_tiles['required_parameters'].append(r_param)
            alg_file.write(json.dumps(stitch_tiles))
        # new parameter is missing fron chains.json
        # atk should assume this is a user parameter
        response = self.client.get(
            '/chain_algorithms/map_tiles/?api_key=testkey')
        self.assert200(response)

        # add param to chains.json
        chain_def = get_chains()
        chain_def['map_tiles'][1]['parameters']['useless_required'] = {
            'source': 'user'
        }
        # print(chain_def)
        with open(chains_file, 'w') as c_file:
            c_file.write(json.dumps(chain_def))

        # should now be included
        response = self.client.get(
            '/chain_algorithms/map_tiles/?api_key=testkey')
        self.assert200(response)
        self.assertEqual(response.data, json.dumps(
            chain_algs,
            separators=(',', ':'),
            sort_keys=True
        ) + '\n')

        # add an optional parameter and ensure it displays in chain_algorithms
        o_param = {
            "default_value": "",
            "field_type": "text",
            "display_name": "Useless Parameter",
            "name": "useless",
            "data_type": "string",
            "max_value": None,
            "min_value": None,
            "sort_order": 2,
            "parameter_choices": [],
            "help_text": "Don't bother entering anything",
            "custom_validation": None,
            "description": "A completely useless parameter.",
            "source": "user"
        }
        chain_algs[1]['optional_parameters'].append(o_param)
        json_file = os.path.join(
            test_alg_path, 'algorithms', 'stitch_tiles', 'algorithm.json')
        chains_file = os.path.join(test_alg_path, 'chains.json')
        with open(json_file, 'r') as alg_file:
            stitch_tiles = json.load(alg_file)
        with open(json_file, 'w') as alg_file:
            stitch_tiles['optional_parameters'].append(o_param)
            alg_file.write(json.dumps(stitch_tiles))
        # new parameter is missing fron chains.json
        # but should be fine
        response = self.client.get(
            '/chain_algorithms/map_tiles/?api_key=testkey')
        self.assert200(response)

        # add param to chains.json
        chain_def['map_tiles'][1]['parameters']['useless'] = {
            'source': 'user'
        }
        # print(chain_def)
        with open(chains_file, 'w') as c_file:
            c_file.write(json.dumps(chain_def))

        # should now be included
        response = self.client.get(
            '/chain_algorithms/map_tiles/?api_key=testkey')
        self.assert200(response)
        self.assertEqual(response.data, json.dumps(
            chain_algs,
            separators=(',', ':'),
            sort_keys=True
        ) + '\n')

    def test_alg_info_no_key(self):
        print('Algorithm info should fail if the API key is missing')
        response = self.client.get('/algorithm_info/getmaptiles_roi/')
        self.assert401(response)
        self.assertEqual(response.data, 'API key wrong or missing')

    def test_alg_info(self):
        print('Algorithm info should ... provide algorithm info')
        alg = [x for x in algs if x['name'] == 'getmaptiles_roi'][0]
        response = self.client.get(
            '/algorithm_info/getmaptiles_roi/?api_key=testkey')
        self.assert200(response)
        self.assertEqual(response.data, json.dumps(
            alg,
            separators=(',', ':'),
            sort_keys=True
        ) + '\n')

    def test_create_algorithms_get(self):
        from algorithm_toolkit.forms import (
            AlgorithmCreateForm,
            AlgorithmOutputForm,
            AlgorithmParameterForm
        )
        print('Create algorithm page should display correctly')
        chain_def = get_chains()
        response = self.client.get('/algorithms/create/')
        form = self.get_context_variable('form')
        o_form = self.get_context_variable('o_form')
        p_form = self.get_context_variable('p_form')
        self.assert200(response)
        self.assertTemplateUsed('create_algorithm.html')
        self.assertContext('nav', 'algorithms')
        self.assertContext('docs', False)
        self.assertContext('chains', chain_def)
        self.assertContext('algs', sorted([x['name'] for x in algs]))
        self.assertEqual(type(form), AlgorithmCreateForm)
        self.assertEqual(type(o_form), AlgorithmOutputForm)
        self.assertEqual(type(p_form), AlgorithmParameterForm)

        # test without the private flag
        json_file = os.path.join(
            test_alg_path, 'algorithms', 'stitch_tiles', 'algorithm.json')
        with open(json_file, 'r') as alg_file:
            stitch_tiles = json.load(alg_file)
        with open(json_file, 'w') as alg_file:
            del stitch_tiles['private']
            alg_file.write(json.dumps(stitch_tiles))
        response = self.client.get('/algorithms/create/stitch_tiles/')
        self.assert200(response)
        self.assertContext(
            'algs',
            sorted([x['name'] for x in algs if x['name'] != 'stitch_tiles'])
        )

    def test_create_algorithms_post(self):
        print('Create algorithm page should create an algorithm correctly')

        data = test_algorithm_form_data()
        data['parameters'] = json.dumps(
            data['parameters'], separators=(', ', ': '), sort_keys=True)
        data['outputs'] = json.dumps(
            data['outputs'], separators=(', ', ': '), sort_keys=True)
        data['api_key'] = 'testkey'
        new_alg_path = os.path.join(
            test_alg_path, 'algorithms', 'add_numbers')

        response = self.client.post(
            '/algorithms/create/', data=data, follow_redirects=True)
        self.assert200(response)
        self.assertTrue(os.path.exists(new_alg_path))

        response = self.client.get('/algorithms/create/add_numbers/')
        form = self.get_context_variable('form')
        self.assertEqual(form.name.data, 'add_numbers')
        self.assertEqual(
            form.display_name.data,
            'Add two numbers'
        )
        self.assertEqual(form.license.data, 'Proprietary')
        self.assertEqual(form.private.data, True)
        self.assertEqual(form.version.data, '0.0.1')
        self.assertEqual(
            form.homepage.data, 'google.com')
        self.assertEqual(
            form.description.data,
            'Add two numbers together to get a result.'
        )
        self.assertEqual(
            json.loads(form.parameters.data), json.loads(data['parameters']))
        self.assertEqual(
            json.loads(form.outputs.data), json.loads(data['outputs']))

    def test_edit_algorithms_get(self):
        from algorithm_toolkit.forms import (
            AlgorithmCreateForm,
            AlgorithmOutputForm,
            AlgorithmParameterForm
        )
        print('Edit algorithm page should display correctly')

        def add_required(p, r):
            p['required'] = r
            return p

        chain_def = get_chains()
        this_alg = [x for x in algs if x['name'] == 'getmaptiles_roi'][0]
        r_params = [add_required(
            x, True) for x in this_alg['required_parameters']]
        o_params = [add_required(
            x, False) for x in this_alg['optional_parameters']]
        params = r_params + o_params
        response = self.client.get('/algorithms/create/getmaptiles_roi/')
        form = self.get_context_variable('form')
        o_form = self.get_context_variable('o_form')
        p_form = self.get_context_variable('p_form')
        self.assert200(response)
        self.assertTemplateUsed('create_algorithm.html')
        self.assertContext('nav', 'algorithms')
        self.assertContext('docs', False)
        self.assertContext('chains', chain_def)
        self.assertContext(
            'algs',
            sorted([x['name'] for x in algs if x['name'] != 'getmaptiles_roi'])
        )
        self.assertEqual(type(form), AlgorithmCreateForm)
        self.assertEqual(type(o_form), AlgorithmOutputForm)
        self.assertEqual(type(p_form), AlgorithmParameterForm)
        self.assertEqual(form.name.data, 'getmaptiles_roi')
        self.assertEqual(form.display_name.data, 'Get Map Tiles In ROI')
        self.assertEqual(form.license.data, 'MIT')
        self.assertEqual(form.private.data, False)
        self.assertEqual(form.version.data, '0.0.1')
        self.assertEqual(
            form.homepage.data, 'https://tiledriver.com/developer')
        self.assertEqual(
            form.description.data,
            'This algorithm will gather up map tiles at a given zoom level '
            'that intersect with the provided polygon. The source is the '
            'national map provided by USGS. All tiles will be written out '
            'to disk at a specified location. This location is also saved '
            'onto the chain ledger.'
        )
        temp_params = json.loads(form.parameters.data)
        for p in temp_params:
            p.pop('original_name', None)

        temp_outs = json.loads(form.outputs.data)
        for out in temp_outs:
            out.pop('original_name', None)

        self.assertEqual(temp_params, params)
        self.assertEqual(temp_outs, this_alg['outputs'])

    def test_edit_algorithms_post(self):
        print('Edit algorithm page should modify an algorithm correctly')

        # get initial algorithm data
        response = self.client.get('/algorithms/create/getmaptiles_roi/')
        form = self.get_context_variable('form')
        this_alg = form.data
        # modify it
        this_alg['display_name'] = 'Do something crazy with map tiles'
        this_alg['license'] = 'GNU LGPLv3'
        this_alg['private'] = True
        this_alg['version'] = '0.0.2'
        this_alg['homepage'] = 'google.com'
        this_alg['description'] = 'Do some stuff, I dunno.'
        this_alg['api_key'] = 'testkey'
        new_license_path = os.path.join(
            test_alg_path, 'algorithms', 'getmaptiles_roi', 'LICENSE')

        # should see new data reflected in the algorithm
        response = self.client.post(
            '/algorithms/create/getmaptiles_roi/',
            data=this_alg,
            follow_redirects=True
        )
        self.assert200(response)
        response = self.client.get('/algorithms/create/getmaptiles_roi/')
        self.assert200(response)
        new_form = self.get_context_variable('form')
        with open(new_license_path, 'r') as lic_file:
            lic = lic_file.read()
        self.assertTrue('GNU LESSER GENERAL PUBLIC LICENSE' in lic)

        self.assertEqual(new_form.name.data, 'getmaptiles_roi')
        self.assertEqual(
            new_form.display_name.data, 'Do something crazy with map tiles')
        self.assertEqual(new_form.license.data, 'GNU LGPLv3')
        self.assertEqual(new_form.private.data, True)
        self.assertEqual(new_form.version.data, '0.0.2')
        self.assertEqual(new_form.homepage.data, 'google.com')
        self.assertEqual(
            new_form.description.data, 'Do some stuff, I dunno.')

    def test_change_algorithm_name(self):
        print('A user should be able to change the name of an algorithm')

        # get initial algorithm data
        response = self.client.get('/algorithms/create/getmaptiles_roi/')
        form = self.get_context_variable('form')
        this_alg = form.data
        # modify it
        this_alg['name'] = 'thingie_splunge'
        new_alg_path = os.path.join(
            test_alg_path, 'algorithms', 'thingie_splunge')
        response = self.client.post(
            '/algorithms/create/getmaptiles_roi/',
            data=this_alg,
            follow_redirects=True
        )
        self.assert200(response)
        response = self.client.get('/algorithms/create/thingie_splunge/')
        self.assert200(response)
        new_form = self.get_context_variable('form')

        self.assertEqual(new_form.name.data, 'thingie_splunge')
        self.assertTrue(os.path.exists(new_alg_path))

    def test_edit_algorithm_not_found(self):
        print(
            'A user trying to edit a non-existing algorithm should get a 404')

        # get initial algorithm data
        response = self.client.get('/algorithms/create/thingie_splunge/')
        self.assert404(response)
        self.assertEqual(response.data, 'Algorithm not found')

    def test_edit_algorithm_no_private_field(self):
        print(
            'An algorithm should still be saved if the private flag is missing'
        )

        # get initial algorithm data
        response = self.client.get('/algorithms/create/getmaptiles_roi/')
        form = self.get_context_variable('form')
        this_alg = form.data
        # modify it
        del this_alg['private']
        response = self.client.post(
            '/algorithms/create/getmaptiles_roi/',
            data=this_alg,
            follow_redirects=True
        )
        self.assert200(response)
        response = self.client.get('/algorithms/create/getmaptiles_roi/')
        self.assert200(response)
        new_form = self.get_context_variable('form')

        self.assertEqual(new_form.private.data, False)

    def test_edit_algorithm_change_license(self):
        print('A user should be able to change the license of an algorithm')

        # get initial algorithm data
        response = self.client.get('/algorithms/create/getmaptiles_roi/')
        form = self.get_context_variable('form')
        this_alg = form.data
        # modify it to AGPL
        this_alg['license'] = 'GNU AGPLv3'
        new_license_path = os.path.join(
            test_alg_path, 'algorithms', 'getmaptiles_roi', 'LICENSE')
        response = self.client.post(
            '/algorithms/create/getmaptiles_roi/',
            data=this_alg,
            follow_redirects=True
        )
        self.assert200(response)
        response = self.client.get('/algorithms/create/getmaptiles_roi/')
        self.assert200(response)
        new_form = self.get_context_variable('form')

        self.assertEqual(new_form.license.data, 'GNU AGPLv3')
        with open(new_license_path, 'r') as lic_file:
            lic = lic_file.read()
        self.assertTrue('GNU AFFERO GENERAL PUBLIC LICENSE' in lic)

        # modify it to GPL
        this_alg['license'] = 'GNU GPLv3'
        new_license_path = os.path.join(
            test_alg_path, 'algorithms', 'getmaptiles_roi', 'LICENSE')
        response = self.client.post(
            '/algorithms/create/getmaptiles_roi/',
            data=this_alg,
            follow_redirects=True
        )
        self.assert200(response)
        response = self.client.get('/algorithms/create/getmaptiles_roi/')
        self.assert200(response)
        new_form = self.get_context_variable('form')

        self.assertEqual(new_form.license.data, 'GNU GPLv3')
        with open(new_license_path, 'r') as lic_file:
            lic = lic_file.read()
        self.assertTrue('GNU GENERAL PUBLIC LICENSE' in lic)

        # modify it to Unlicense
        this_alg['license'] = 'The Unlicense'
        new_license_path = os.path.join(
            test_alg_path, 'algorithms', 'getmaptiles_roi', 'LICENSE')
        response = self.client.post(
            '/algorithms/create/getmaptiles_roi/',
            data=this_alg,
            follow_redirects=True
        )
        self.assert200(response)
        response = self.client.get('/algorithms/create/getmaptiles_roi/')
        self.assert200(response)
        new_form = self.get_context_variable('form')

        self.assertEqual(new_form.license.data, 'The Unlicense')
        with open(new_license_path, 'r') as lic_file:
            lic = lic_file.read()
        self.assertTrue('http://unlicense.org' in lic)

        # modify it to Apache
        this_alg['license'] = 'Apache'
        new_license_path = os.path.join(
            test_alg_path, 'algorithms', 'getmaptiles_roi', 'LICENSE')
        response = self.client.post(
            '/algorithms/create/getmaptiles_roi/',
            data=this_alg,
            follow_redirects=True
        )
        self.assert200(response)
        response = self.client.get('/algorithms/create/getmaptiles_roi/')
        self.assert200(response)
        new_form = self.get_context_variable('form')

        self.assertEqual(new_form.license.data, 'Apache')
        with open(new_license_path, 'r') as lic_file:
            lic = lic_file.read()
        self.assertTrue('http://www.apache.org/licenses/' in lic)

        # modify it to Mozilla
        this_alg['license'] = 'Mozilla'
        new_license_path = os.path.join(
            test_alg_path, 'algorithms', 'getmaptiles_roi', 'LICENSE')
        response = self.client.post(
            '/algorithms/create/getmaptiles_roi/',
            data=this_alg,
            follow_redirects=True
        )
        self.assert200(response)
        response = self.client.get('/algorithms/create/getmaptiles_roi/')
        self.assert200(response)
        new_form = self.get_context_variable('form')

        self.assertEqual(new_form.license.data, 'Mozilla')
        with open(new_license_path, 'r') as lic_file:
            lic = lic_file.read()
        self.assertTrue('Mozilla Public License Version 2.0' in lic)

        # modify it to MIT
        this_alg['license'] = 'MIT'
        new_license_path = os.path.join(
            test_alg_path, 'algorithms', 'getmaptiles_roi', 'LICENSE')
        response = self.client.post(
            '/algorithms/create/getmaptiles_roi/',
            data=this_alg,
            follow_redirects=True
        )
        self.assert200(response)
        response = self.client.get('/algorithms/create/getmaptiles_roi/')
        self.assert200(response)
        new_form = self.get_context_variable('form')

        self.assertEqual(new_form.license.data, 'MIT')
        with open(new_license_path, 'r') as lic_file:
            lic = lic_file.read()
        self.assertTrue('MIT License' in lic)

        # modify it to Propietary
        this_alg['license'] = 'Proprietary'
        new_license_path = os.path.join(
            test_alg_path, 'algorithms', 'getmaptiles_roi', 'LICENSE')
        response = self.client.post(
            '/algorithms/create/getmaptiles_roi/',
            data=this_alg,
            follow_redirects=True
        )
        self.assert200(response)
        response = self.client.get('/algorithms/create/getmaptiles_roi/')
        self.assert200(response)
        new_form = self.get_context_variable('form')

        self.assertEqual(new_form.license.data, 'Proprietary')
        with open(new_license_path, 'r') as lic_file:
            lic = lic_file.read()
        self.assertTrue(lic == '')

        # modify it to Other
        this_alg['license'] = 'Other'
        new_license_path = os.path.join(
            test_alg_path, 'algorithms', 'getmaptiles_roi', 'LICENSE')
        response = self.client.post(
            '/algorithms/create/getmaptiles_roi/',
            data=this_alg,
            follow_redirects=True
        )
        self.assert200(response)
        response = self.client.get('/algorithms/create/getmaptiles_roi/')
        self.assert200(response)
        new_form = self.get_context_variable('form')

        self.assertEqual(new_form.license.data, 'Other')
        with open(new_license_path, 'r') as lic_file:
            lic = lic_file.read()
        self.assertTrue(lic == '')

    def test_copy_algorithms(self):
        print('Users should be able to copy an algorithm')

        def add_required(p, r):
            p['required'] = r
            return p

        # make a copy
        response = self.client.get(
            '/algorithm/copy/getmaptiles_roi/', follow_redirects=True)
        self.assert200(response)
        # ensure we're redirected to algorithms page
        self.assertTemplateUsed('algorithms.html')
        new_alg_path = os.path.join(
            test_alg_path, 'algorithms', 'getmaptiles_roi_copy')
        self.assertTrue(os.path.exists(new_alg_path))

        # ensure copy has the right data
        this_alg = [x for x in algs if x['name'] == 'getmaptiles_roi'][0]
        r_params = [add_required(
            x, True) for x in this_alg['required_parameters']]
        o_params = [add_required(
            x, False) for x in this_alg['optional_parameters']]
        params = r_params + o_params
        response = self.client.get('/algorithms/create/getmaptiles_roi_copy/')
        form = self.get_context_variable('form')
        self.assert200(response)
        self.assertEqual(form.name.data, 'getmaptiles_roi_copy')
        self.assertEqual(form.display_name.data, 'Get Map Tiles In ROI')
        self.assertEqual(form.license.data, 'MIT')
        self.assertEqual(form.private.data, False)
        self.assertEqual(form.version.data, '0.0.1')
        self.assertEqual(
            form.homepage.data, 'https://tiledriver.com/developer')
        self.assertEqual(
            form.description.data,
            'This algorithm will gather up map tiles at a given zoom level '
            'that intersect with the provided polygon. The source is the '
            'national map provided by USGS. All tiles will be written out '
            'to disk at a specified location. This location is also saved '
            'onto the chain ledger.'
        )
        temp_params = json.loads(form.parameters.data)
        for p in temp_params:
            p.pop('original_name', None)

        temp_outs = json.loads(form.outputs.data)
        for out in temp_outs:
            out.pop('original_name', None)

        self.assertEqual(temp_params, params)
        self.assertEqual(temp_outs, this_alg['outputs'])

        # make a second copy
        response = self.client.get(
            '/algorithm/copy/getmaptiles_roi/', follow_redirects=True)
        self.assert200(response)
        new_alg_path = os.path.join(
            test_alg_path, 'algorithms', 'getmaptiles_roi_copy1')
        self.assertTrue(os.path.exists(new_alg_path))

    def test_delete_algorithms(self):
        print('Users should be able to delete an algorithm')

        # set working directory
        os.chdir(test_alg_path)

        # delete the algorithm
        response = self.client.get(
            '/algorithm/delete/getmaptiles_roi/', follow_redirects=True)
        self.assert200(response)
        # ensure we're redirected to algorithms page
        self.assertTemplateUsed('algorithms.html')
        new_alg_path = os.path.join(
            test_alg_path, 'algorithms', 'getmaptiles_roi')
        self.assertFalse(os.path.exists(new_alg_path))
        # ensure references are removed from chains.json
        chain_path = os.path.join(test_alg_path, 'chains.json')
        with open(chain_path, 'r') as chain_file:
            chains = chain_file.read()
        self.assertFalse('getmaptiles_roi' in chains)

        # reset working directory
        os.chdir(this_path)

    def test_chain_builder(self):
        print('Chain builder page should display correctly')

        chain_def = get_chains()
        additional_block = get_chain_builder_additional_block()
        additional_script = get_chain_builder_additional_script()
        response = self.client.get('/chain_builder/')
        blocks = self.get_context_variable('block_list')
        scripts = self.get_context_variable('block_scripts')
        self.assert200(response)
        self.assertTemplateUsed('chain_builder.html')
        self.assertContext('nav', 'chain_builder')
        self.assertContext('docs', False)
        self.assertContext('chains', chain_def)
        for idx, block in enumerate(blocks):
            temp_block = re.sub(r'colour="(\d+)"', 'colour="222"', block)
            self.assertEqual(temp_block, block_list[idx])
        for idx, script in enumerate(scripts):
            temp_script = re.sub(
                r'setColour\((\d+)\)', 'setColour(222)', script)
            self.assertEqual(temp_script, block_scripts[idx])
        self.assertContext('chain_obj', json.dumps(chain_def))

        # add additional algorithm
        data = test_algorithm_form_data()
        data['name'] = 'beamio/add_numbers'
        data['parameters'] = json.dumps(
            data['parameters'], separators=(', ', ': '), sort_keys=True)
        data['outputs'] = json.dumps(
            data['outputs'], separators=(', ', ': '), sort_keys=True)
        data['api_key'] = 'testkey'
        response = self.client.post(
            '/algorithms/create/', data=data, follow_redirects=True)

        response = self.client.get('/chain_builder/')
        blocks = self.get_context_variable('block_list')
        scripts = self.get_context_variable('block_scripts')
        for idx, block in enumerate(blocks):
            temp_block = re.sub(r'colour="(\d+)"', 'colour="222"', block)
            self.assertEqual(temp_block, additional_block[idx])
        for idx, script in enumerate(scripts):
            temp_script = re.sub(
                r'setColour\((\d+)\)', 'setColour(222)', script)
            self.assertEqual(temp_script, additional_script[idx])

        # test removing parameters
        json_file = os.path.join(
            test_alg_path,
            'algorithms',
            'beamio',
            'add_numbers',
            'algorithm.json'
        )
        with open(json_file, 'r') as alg_file:
            add_numbers = json.load(alg_file)
        with open(json_file, 'w') as alg_file:
            add_numbers['required_parameters'] = []
            alg_file.write(json.dumps(add_numbers))
        response = self.client.get('/chain_builder/')
        temp_script = self.get_context_variable('block_scripts')[3]
        self.assert200(response)
        self.assertFalse('Required Input Fields:' in temp_script)
        self.assertTrue('Optional Input Fields:' in temp_script)

        with open(json_file, 'w') as alg_file:
            del add_numbers['required_parameters']
            del add_numbers['optional_parameters']
            alg_file.write(json.dumps(add_numbers))
        response = self.client.get('/chain_builder/')
        temp_script = self.get_context_variable('block_scripts')[3]
        self.assert200(response)
        self.assertFalse('Required Input Fields:' in temp_script)
        self.assertFalse('Optional Input Fields:' in temp_script)

    def test_chain_builder_get_blocks(self):
        print(
            'When a user requests a chain in chain builder, '
            'the chain blocks should display correctly.'
        )
        chain_blocks = get_chain_builder_chain_blocks()
        response = self.client.get('/chain_builder/get_blocks/map_tiles/')
        temp_blocks = re.sub(
            r'<block type="(\w+)" id="\w+"',
            r'<block type="\1" id="testid"',
            response.data
        )
        self.assert200(response)
        self.assertEqual(temp_blocks, chain_blocks)

        # add an optional parameter
        o_param = {
            "default_value": "",
            "field_type": "text",
            "display_name": "Useless Parameter",
            "name": "useless",
            "data_type": "string",
            "max_value": None,
            "min_value": None,
            "sort_order": 2,
            "parameter_choices": [],
            "help_text": "Don't bother entering anything",
            "custom_validation": None,
            "description": "A completely useless parameter.",
        }
        json_file = os.path.join(
            test_alg_path, 'algorithms', 'stitch_tiles', 'algorithm.json')
        chains_file = os.path.join(test_alg_path, 'chains.json')
        with open(json_file, 'r') as alg_file:
            stitch_tiles = json.load(alg_file)
        with open(json_file, 'w') as alg_file:
            stitch_tiles['optional_parameters'].append(o_param)
            alg_file.write(json.dumps(stitch_tiles))
        # add param to chains.json
        chain_def = get_chains()
        chain_def['map_tiles'][1]['parameters']['useless'] = {
            'source': 'user'
        }
        with open(chains_file, 'w') as c_file:
            c_file.write(json.dumps(chain_def))
        new_block = (
            '<value name="useless">\n'
            '<block type="user_input" id="testid">\n'
            '<data>input</data>\n'
        )
        response = self.client.get('/chain_builder/get_blocks/map_tiles/')
        temp_blocks = re.sub(
            r'<block type="(\w+)" id="\w+"',
            r'<block type="\1" id="testid"',
            response.data
        )
        self.assert200(response)
        self.assertTrue(new_block in temp_blocks)

    def test_update_chains_error(self):
        print(
            'If update_chains is called without a chains '
            'value, atk should throw an error'
        )
        response = self.client.post('/chain_builder/update_chains/', data={})
        self.assert400(response)
        self.assertEqual(response.data, 'Missing chain definitions')

    def test_update_chains(self):
        print('Update chains should ... update the chains')
        chain_list = '<a class="dropdown-item" href="'
        chain_list += '/test_run/map_tiles/">map_tiles</a>'
        chain_list += '<a class="dropdown-item" href="'
        chain_list += '/test_run/do_some_math/">do_some_math</a>'
        new_chain_path = os.path.join(test_alg_path, 'chains.json')
        response = self.client.post(
            '/chain_builder/update_chains/',
            data={'chains': json.dumps(updated_chain)}
        )
        with open(new_chain_path) as new_chain_file:
            new_chains = new_chain_file.read()
        self.assert200(response)
        self.assertEqual(json.loads(new_chains), updated_chain)
        self.assertEqual(response.data, chain_list)

    def test_main_errors(self):
        print(
            'If main is called without proper request '
            'values, atk should throw an error'
        )

        # no api key
        response = self.client.post('/main/', data={})
        self.assert401(response)
        self.assertEqual(response.data, 'API key wrong or missing')

        # no chain parameter
        response = self.client.post('/main/', data={'api_key': 'testkey'})
        self.assert400(response)
        self.assertEqual(response.data, 'Missing chain parameter in request')

        # chain parameter is not json serializable
        response = self.client.post(
            '/main/', data={'chain': 'splunge', 'api_key': 'testkey'})
        self.assert400(response)
        self.assertEqual(
            response.data, 'Chain parameter not properly formatted')

        # no key for chain name in chain parameter
        response = self.client.post(
            '/main/', data={
                'chain': '{"thingie": "splunge"}', 'api_key': 'testkey'})
        self.assert400(response)
        self.assertEqual(response.data, 'Chain name not defined')

        # no key for algorithms
        response = self.client.post(
            '/main/', data={
                'chain': '{"chain_name": "splunge"}', 'api_key': 'testkey'})
        self.assert400(response)
        self.assertEqual(response.data, 'Algorithms not defined')

        # chain name does not exist
        response = self.client.post(
            '/main/', data={
                'chain': '{"chain_name": "splunge", "algorithms": []}',
                'api_key': 'testkey'
            })
        self.assert404(response)
        self.assertEqual(response.data, 'Chain name not found')

        # non-existent algorithm name
        test_run_chain = get_test_run_chain()
        test_run_chain['algorithms'][0]['parameters']['zoom'] = 10
        extra_alg = {
            "name": "thingie",
            "parameters": {}
        }
        test_run_chain['algorithms'].append(extra_alg)
        data = {
            'api_key': 'testkey',
            'chain': json.dumps(test_run_chain)
        }
        response = self.client.post('/main/', data=data)
        self.assert400(response)
        self.assertEqual(
            json.loads(response.data),
            {
                "error_list": {
                    "error": "Algorithm not found",
                    "parameter": ""
                },
                "message": "Error in parameters",
                "output_type": "error"
            }
        )

    def test_main_run(self):
        print(
            'Calling the main endpoint should execute a chain'
        )
        test_run_chain = get_test_run_chain()
        test_run_chain['algorithms'][0]['parameters']['zoom'] = 10
        retval = {
            "output_type": "geo_raster",
            "output_value": {
                "extent":
                    "[[39.095962936305476, -77.34374999999999], "
                    "[38.54816542304656, -76.640625]]"
            }
        }
        data = {
            'api_key': 'testkey',
            'chain': json.dumps(test_run_chain)
        }
        response = self.client.post('/main/', data=data)
        self.assert200(response)
        resp_json = json.loads(response.data)
        self.assertEqual(resp_json['output_type'], retval['output_type'])
        self.assertEqual(
            resp_json['output_value']['extent'],
            retval['output_value']['extent'])
        self.assertTrue('raster' in resp_json['output_value'])

    def test_main_run_no_chain_output(self):
        print(
            'Calling the main endpoint without adding chain_output_value '
            ' to the chain ledger should output a default message'
        )
        test_run_chain = get_test_run_chain()
        test_run_chain['algorithms'][0]['parameters']['zoom'] = 10
        del test_run_chain['algorithms'][2]
        retval = {
            "output_type": "string",
            "output_value": 'Chain run complete.'
        }
        data = {
            'api_key': 'testkey',
            'chain': json.dumps(test_run_chain)
        }
        response = self.client.post('/main/', data=data)
        self.assert200(response)
        self.assertEqual(json.loads(response.data), retval)

    def test_main_run_missing_parameters(self):
        print(
            'Calling the main endpoint without parameters should execute '
            'a chain or throw an error, depending'
        )

        test_run_chain = get_test_run_chain()
        test_run_chain['algorithms'][0]['parameters']['zoom'] = 10
        retval = {
            "output_type": "geo_raster",
            "output_value": {
                "extent":
                    "[[39.095962936305476, -77.34374999999999], "
                    "[38.54816542304656, -76.640625]]"
            }
        }

        # removing a chain_ledger parameter should proceed normally
        del test_run_chain['algorithms'][1]['parameters']
        data = {
            'api_key': 'testkey',
            'chain': json.dumps(test_run_chain)
        }
        response = self.client.post('/main/', data=data)
        self.assert200(response)
        resp_json = json.loads(response.data)
        self.assertEqual(resp_json['output_type'], retval['output_type'])
        self.assertEqual(
            resp_json['output_value']['extent'],
            retval['output_value']['extent'])
        self.assertTrue('raster' in resp_json['output_value'])

        # removing a user parameter should fail
        del test_run_chain['algorithms'][0]['parameters']
        data = {
            'api_key': 'testkey',
            'chain': json.dumps(test_run_chain)
        }
        errors = {
            "output_type": "error",
            "error_list": [
                {
                    "error": "Parameter missing",
                    "parameter": "roi"
                }, {
                    "error": "roi",
                    "parameter": "roi"
                }, {
                    "error": "Parameter missing",
                    "parameter": "zoom"
                }, {
                    "error": "zoom",
                    "parameter": "zoom"
                }
            ],
            "message": "Error in parameters"
        }
        response = self.client.post('/main/', data=data)
        self.assert400(response)
        self.assertEqual(json.loads(response.data), errors)

    def test_main_run_get(self):
        print(
            'Applications should be able to call the main endpoint using GET'
        )
        test_run_chain = get_test_run_chain()
        test_run_chain['algorithms'][0]['parameters']['zoom'] = 10
        response = self.client.get(
            '/main/?api_key=testkey&chain=' + json.dumps(test_run_chain))
        self.assert200(response)

        # add a required parameter and ensure chain still runs
        r_param = {
            "default_value": "",
            "field_type": "text",
            "display_name": "Useless Yet Required Parameter",
            "name": "useless_required",
            "data_type": "string",
            "max_value": None,
            "min_value": None,
            "sort_order": 2,
            "parameter_choices": [],
            "help_text": "Don't bother entering anything, and yet you must",
            "custom_validation": None,
            "description": "A completely useless yet required parameter.",
            "source": "user"
        }
        json_file = os.path.join(
            test_alg_path, 'algorithms', 'stitch_tiles', 'algorithm.json')
        chains_file = os.path.join(test_alg_path, 'chains.json')
        with open(json_file, 'r') as alg_file:
            stitch_tiles = json.load(alg_file)
        with open(json_file, 'w') as alg_file:
            stitch_tiles['required_parameters'].append(r_param)
            alg_file.write(json.dumps(stitch_tiles))
        # add param to chains.json
        chain_def = get_chains()
        chain_def['map_tiles'][1]['parameters']['useless_required'] = {
            'source': 'user'
        }
        with open(chains_file, 'w') as c_file:
            c_file.write(json.dumps(chain_def))

        # remove 'source' key from parameter in chain
        test_run_chain['algorithms'][1]['parameters']['useless_required'] = '1'
        response = self.client.get(
            '/main/?api_key=testkey&chain=' + json.dumps(test_run_chain))
        self.assert200(response)
        chain_def['map_tiles'][1]['parameters']['useless_required'] = {}
        with open(chains_file, 'w') as c_file:
            c_file.write(json.dumps(chain_def))

        response = self.client.get(
            '/main/?api_key=testkey&chain=' + json.dumps(test_run_chain))
        self.assert200(response)

        # remove 'occurrence' key in chain parameter
        del chain_def['map_tiles'][1][
            'parameters']['image_filenames']['occurrence']
        with open(chains_file, 'w') as c_file:
            c_file.write(json.dumps(chain_def))

        response = self.client.get(
            '/main/?api_key=testkey&chain=' + json.dumps(test_run_chain))
        self.assert200(response)

        # remove 'source_algorithm' key in chain parameter
        # should fail this time
        del chain_def['map_tiles'][1][
            'parameters']['image_filenames']['source_algorithm']
        with open(chains_file, 'w') as c_file:
            c_file.write(json.dumps(chain_def))

        response = self.client.get(
            '/main/?api_key=testkey&chain=' + json.dumps(test_run_chain))
        self.assert400(response)
        self.assertEqual(
            json.loads(response.data),
            {
                "output_type": "error",
                "error_list": [
                    {
                        "error": "Parameter missing",
                        "parameter": "image_filenames"
                    }, {
                        "error": "image_filenames",
                        "parameter": "image_filenames"
                    }
                ],
                "message": "Error in parameters"
            }
        )

    def test_main_run_not_integer(self):
        print(
            'ATK should return appropriate errors if '
            'a string is submitted for an integer field'
        )
        test_run_chain = get_test_run_chain()
        test_run_chain['algorithms'][0]['parameters']['zoom'] = 'zoom'
        data = {
            'api_key': 'testkey',
            'chain': json.dumps(test_run_chain)
        }
        zoom_errors = {
            "output_type": "error",
            "message": "Error in parameters",
            "error_list": [
                {
                    "error": "Not a valid integer",
                    "parameter": "zoom"
                }
            ],
        }
        response = self.client.post('/main/', data=data)
        self.assert400(response)
        self.assertEqual(json.loads(response.data), zoom_errors)

    def test_main_run_integer_too_large(self):
        print(
            'ATK should return appropriate errors if '
            'an integer value is larger than the max value'
        )
        test_run_chain = get_test_run_chain()
        test_run_chain['algorithms'][0]['parameters']['zoom'] = 20
        data = {
            'api_key': 'testkey',
            'chain': json.dumps(test_run_chain)
        }
        zoom_errors = {
            "output_type": "error",
            "error_list": [
                {
                    "error": "Value too large",
                    "parameter": "zoom"
                }
            ],
            "message": "Error in parameters"
        }
        response = self.client.post('/main/', data=data)
        self.assert400(response)
        self.assertEqual(json.loads(response.data), zoom_errors)

    def test_main_run_integer_too_small(self):
        print(
            'ATK should return appropriate errors if '
            'an integer value is smaller than the min value'
        )
        test_run_chain = get_test_run_chain()
        test_run_chain['algorithms'][0]['parameters']['zoom'] = 2
        data = {
            'api_key': 'testkey',
            'chain': json.dumps(test_run_chain)
        }
        zoom_errors = {
            "output_type": "error",
            "error_list": [
                {
                    "error": "Value too small",
                    "parameter": "zoom"
                }
            ],
            "message": "Error in parameters"
        }
        response = self.client.post('/main/', data=data)
        self.assert400(response)
        self.assertEqual(json.loads(response.data), zoom_errors)

    def test_main_run_status_key(self):
        print(
            'Applications should be able to supply a '
            'status key to the main endpoint'
        )
        # TODO: see if we can make this more reliable
        # because of USGS web TMS
        test_run_chain = get_test_run_chain()
        test_run_chain['algorithms'][0]['parameters']['zoom'] = 10
        retval = {
            'all_msg':
                'Starting chain run...  \nRunning algorithm: '
                'getmaptiles_roi  \nstarting to fetch 3 tiles  \n'
                'fetched tile: /tmp/throatwarblermangrove/temp/'
                '292_392_10.png  \nfetched tile: /tmp/throatwarblermangrove/'
                'temp/292_391_10.png  \nfetched tile: /tmp/'
                'throatwarblermangrove/temp/293_391_10.png  \n'
                'Running algorithm: stitch_tiles  \n'
                'Stitching tile: /tmp/throatwarblermangrove/temp/'
                '292_392_10.png  \nStitching tile: /tmp/throatwarblermangrove/'
                'temp/292_391_10.png  \nStitching tile: /tmp/'
                'throatwarblermangrove/temp/293_391_10.png  \n'
                'writing out stitched image to disk  \n'
                'Running algorithm: output_image_to_client  \n'
                'Chain run complete',
            'batch_percent_complete': 0,
            'chain_percent_complete': 100,
            'latest_msg': 'Chain run complete',
            'algorithm_percent_complete': 100
        }
        data = {
            'api_key': 'testkey',
            'chain': json.dumps(test_run_chain),
            'status_key': 'throatwarblermangrove'
        }
        response = self.client.post('/main/', data=data)
        if response.status_code != 200:
            print(response.data)
        self.assert200(response)
        response = self.client.post(
            '/chain_run_status/throatwarblermangrove/?api_key=testkey')
        resp_json = json.loads(response.data)
        self.assert200(response)
        self.assertEqual(resp_json, retval)

    def test_get_status_errors(self):
        print(
            'Calling the chain_run_status endpoint '
            'improperly should return errors'
        )
        test_run_chain = get_test_run_chain()
        test_run_chain['algorithms'][0]['parameters']['zoom'] = 10
        data = {
            'api_key': 'testkey',
            'chain': json.dumps(test_run_chain),
            'status_key': 'johangambolputty'
        }
        response = self.client.post('/main/', data=data)

        # GET instead of POST
        response = self.client.get('/chain_run_status/johangambolputty/')
        self.assert405(response)
        self.assertTrue('405 Method Not Allowed' in response.data)

        # no api key
        response = self.client.post('/chain_run_status/johangambolputty/')
        self.assert401(response)
        self.assertEqual(response.data, 'API key wrong or missing')

        # wrong status key
        response = self.client.post(
            '/chain_run_status/ofulm/', data={'api_key': 'testkey'})
        self.assert404(response)
        self.assertEqual(response.data, 'Invalid status key')

    def test_test_run(self):
        print('test_run endpoint should display correctly')

        chain_def = get_chains()

        # no chain name
        response = self.client.get('/test_run/')
        self.assert404(response)

        response = self.client.get('/test_run/map_tiles/')
        form = self.get_context_variable('form')
        self.assert200(response)
        self.assertTemplateUsed('test_run.html')
        self.assertContext('nav', 'test_run')
        self.assertContext('docs', False)
        self.assertContext('chains', chain_def)
        self.assertContext('chain', {})

        this_field = form._fields['getmaptiles_roi__roi_0']
        self.assertTrue('getmaptiles_roi__roi_0' in form._fields)
        self.assertEqual(type(this_field), wtfields.StringField)
        self.assertEqual(type(this_field.widget), wtwidgets.core.TextInput)
        self.assertEqual(this_field.description, '')
        self.assertEqual(this_field.short_name, 'getmaptiles_roi__roi_0')
        self.assertEqual(this_field.id, 'getmaptiles_roi__roi_0')
        self.assertEqual(this_field.name, 'getmaptiles_roi__roi_0')
        self.assertEqual(
            this_field.default,
            'POLYGON((-77.0419692993164 38.9933585922412,-77.17311859130861 '
            '38.891887936025896,-77.03853607177736 38.790272111428706,'
            '-76.91013336181642 38.891887936025896,-77.0419692993164 '
            '38.9933585922412))'
        )
        self.assertEqual(this_field.default, this_field.data)
        self.assertEqual(this_field.default, this_field.object_data)
        self.assertEqual(this_field.type, 'StringField')
        self.assertEqual(type(this_field.validators[0]), InputRequired)
        self.assertEqual(this_field.render_kw, {'required': True})
        self.assertEqual(
            this_field.label.__str__(),
            '<label for="getmaptiles_roi__roi_0">Polygon WKT</label>'
        )

        this_field = form._fields['getmaptiles_roi__zoom_0']
        self.assertTrue('getmaptiles_roi__zoom_0' in form._fields)
        self.assertEqual(type(this_field), wtfields.IntegerField)
        self.assertEqual(type(this_field.widget), wtwidgets.html5.NumberInput)
        self.assertEqual(this_field.description, '')
        self.assertEqual(this_field.short_name, 'getmaptiles_roi__zoom_0')
        self.assertEqual(this_field.id, 'getmaptiles_roi__zoom_0')
        self.assertEqual(this_field.name, 'getmaptiles_roi__zoom_0')
        self.assertEqual(this_field.default, 14)
        self.assertEqual(this_field.default, this_field.data)
        self.assertEqual(this_field.default, this_field.object_data)
        self.assertEqual(this_field.type, 'IntegerField')
        self.assertEqual(type(this_field.validators[0]), InputRequired)
        self.assertEqual(this_field.render_kw, {'required': True})
        self.assertEqual(
            this_field.label.__str__(),
            '<label for="getmaptiles_roi__zoom_0">Zoom level</label>'
        )

        this_field = form._fields['api_key']
        self.assertTrue('api_key' in form._fields)
        self.assertEqual(type(this_field), wtfields.StringField)
        self.assertEqual(type(this_field.widget), wtwidgets.TextInput)
        self.assertEqual(this_field.description, '')
        self.assertEqual(this_field.short_name, 'api_key')
        self.assertEqual(this_field.id, 'api_key')
        self.assertEqual(this_field.name, 'api_key')
        self.assertEqual(this_field.default, None)
        self.assertEqual(this_field.default, this_field.data)
        self.assertEqual(this_field.default, this_field.object_data)
        self.assertEqual(this_field.type, 'StringField')
        self.assertEqual(type(this_field.validators[0]), InputRequired)
        self.assertEqual(this_field.render_kw, None)
        self.assertEqual(
            this_field.label.__str__(),
            '<label for="api_key">API Key</label>'
        )

        self.assertFalse(self.get_context_variable('fetching_results'))

    def test_test_run_optional_parameter(self):
        print('test_run endpoint should display optional parameters')

        # add an optional parameter
        o_param = {
            "default_value": "",
            "field_type": "text",
            "display_name": "Useless Parameter",
            "name": "useless",
            "data_type": "string",
            "max_value": None,
            "min_value": None,
            "sort_order": 2,
            "parameter_choices": [],
            "help_text": "Don't bother entering anything",
            "custom_validation": None,
            "description": "A completely useless parameter.",
        }
        json_file = os.path.join(
            test_alg_path, 'algorithms', 'getmaptiles_roi', 'algorithm.json')
        with open(json_file, 'r') as alg_file:
            roi = json.load(alg_file)
        with open(json_file, 'w') as alg_file:
            roi['optional_parameters'].append(o_param)
            alg_file.write(json.dumps(roi))

        response = self.client.get('/test_run/map_tiles/')
        form = self.get_context_variable('form')
        self.assert200(response)

        this_field = form._fields['getmaptiles_roi__useless_0']
        self.assertEqual(type(this_field), wtfields.StringField)
        self.assertEqual(type(this_field.widget), wtwidgets.core.TextInput)
        self.assertEqual(this_field.description, '')
        self.assertEqual(this_field.short_name, 'getmaptiles_roi__useless_0')
        self.assertEqual(this_field.id, 'getmaptiles_roi__useless_0')
        self.assertEqual(this_field.name, 'getmaptiles_roi__useless_0')
        self.assertEqual(this_field.default, '')
        self.assertEqual(this_field.default, this_field.data)
        self.assertEqual(this_field.default, this_field.object_data)
        self.assertEqual(this_field.type, 'StringField')
        self.assertEqual(type(this_field.validators[0]), Optional)
        self.assertEqual(this_field.render_kw, {})
        self.assertEqual(
            this_field.label.__str__(),
            '<label for="getmaptiles_roi__useless_0">Useless Parameter</label>'
        )

        # add optional parameter to stitch_tiles
        json_file = os.path.join(
            test_alg_path, 'algorithms', 'stitch_tiles', 'algorithm.json')
        chains_file = os.path.join(test_alg_path, 'chains.json')
        with open(json_file, 'r') as alg_file:
            stitch_tiles = json.load(alg_file)
        with open(json_file, 'w') as alg_file:
            stitch_tiles['optional_parameters'].append(o_param)
            alg_file.write(json.dumps(stitch_tiles))

        # if you don't specify a source, assume it's user input
        response = self.client.get('/test_run/map_tiles/')
        form = self.get_context_variable('form')
        self.assert200(response)
        self.assertTrue('stitch_tiles__useless_1' in form._fields)

        # add param to chains.json
        chain_def = get_chains()
        chain_def['map_tiles'][1]['parameters']['useless'] = {
            "source": "chain_ledger",
            "source_algorithm": "getmaptiles_roi",
            "key": "image_chips_dir",
            "occurrence": "first"
        }
        with open(chains_file, 'w') as c_file:
            c_file.write(json.dumps(chain_def))

        response = self.client.get('/test_run/map_tiles/')
        form = self.get_context_variable('form')
        self.assert200(response)
        self.assertFalse('stitch_tiles__useless_1' in form._fields)

        # execute chain with additional parameter
        data = {
            'api_key': 'testkey',
            'getmaptiles_roi__roi_0':
                'POLYGON((-77.0419692993164 38.9933585922412,'
                '-77.17311859130861 38.891887936025896,'
                '-77.03853607177736 38.790272111428706,'
                '-76.91013336181642 38.891887936025896,'
                '-77.0419692993164 38.9933585922412))',
            'getmaptiles_roi__zoom_0': 14,
            'getmaptiles_roi__cache_path_0': '/tmp/tiles/map_tiles',
            'getmaptiles_roi__useless_0': 'crunchyfrog'
        }
        test_run_chain = get_test_run_chain()
        test_run_chain['algorithms'][0]['parameters']['useless'] = (
            'crunchyfrog')
        response = self.client.post('/test_run/map_tiles/', data=data)
        page = response.data
        self.assert200(response)
        self.assertTrue(self.get_context_variable('fetching_results'))
        self.assertTrue(json.dumps(test_run_chain), page)
        self.assertContext('chain', test_run_chain)

        # remove default value from parameter, make it an int
        # field and set min and max values
        del o_param['default_value']
        o_param['field_type'] = 'number'
        o_param['data_type'] = 'integer'
        o_param['min_value'] = 1
        o_param['max_value'] = 100
        o_param['name'] = 'useless2'
        o_param['display_name'] = 'Useless Parameter #2'
        json_file = os.path.join(
            test_alg_path, 'algorithms', 'getmaptiles_roi', 'algorithm.json')
        with open(json_file, 'w') as alg_file:
            roi['optional_parameters'][0] = o_param
            alg_file.write(json.dumps(roi))

        response = self.client.get('/test_run/map_tiles/')
        form = self.get_context_variable('form')
        self.assert200(response)
        this_field = form._fields['getmaptiles_roi__useless2_0']
        self.assertEqual(this_field.default, None)
        self.assertEqual(this_field.widget.min, 1)
        self.assertEqual(this_field.widget.max, 100)

        # make it a float
        roi['optional_parameters'][0]['data_type'] = 'float'
        with open(json_file, 'w') as alg_file:
            alg_file.write(json.dumps(roi))

        response = self.client.get('/test_run/map_tiles/')
        form = self.get_context_variable('form')
        self.assert200(response)
        this_field = form._fields['getmaptiles_roi__useless2_0']
        self.assertEqual(this_field.default, None)
        self.assertEqual(this_field.widget.step, 'any')

        # remove min value from parameter
        del roi['optional_parameters'][0]['min_value']
        with open(json_file, 'w') as alg_file:
            alg_file.write(json.dumps(roi))

        response = self.client.get('/test_run/map_tiles/')
        form = self.get_context_variable('form')
        self.assert200(response)
        this_field = form._fields['getmaptiles_roi__useless2_0']
        self.assertEqual(this_field.widget.min, None)

        # remove max value from parameter
        del roi['optional_parameters'][0]['max_value']
        with open(json_file, 'w') as alg_file:
            alg_file.write(json.dumps(roi))

        response = self.client.get('/test_run/map_tiles/')
        form = self.get_context_variable('form')
        self.assert200(response)
        this_field = form._fields['getmaptiles_roi__useless2_0']
        self.assertEqual(this_field.widget.max, None)

    def test_test_run_submit(self):
        print('test_run should execute a chain')

        data = {
            'api_key': 'testkey',
            'getmaptiles_roi__roi_0':
                'POLYGON((-77.0419692993164 38.9933585922412,'
                '-77.17311859130861 38.891887936025896,'
                '-77.03853607177736 38.790272111428706,'
                '-76.91013336181642 38.891887936025896,'
                '-77.0419692993164 38.9933585922412))',
            'getmaptiles_roi__zoom_0': 14
        }
        test_run_chain = get_test_run_chain()
        response = self.client.post('/test_run/map_tiles/', data=data)
        page = response.data
        self.assert200(response)
        self.assertTrue(self.get_context_variable('fetching_results'))
        self.assertTrue(json.dumps(test_run_chain), page)
        self.assertContext('chain', json.loads(json.dumps(test_run_chain)))


class ATKTestCaseWithDocs(TestCase):

    def create_app(self):
        from algorithm_toolkit import app
        return app

    def setUp(self):
        sys.path.append(test_alg_path)
        subprocess.call(['alg', 'cp', 'test_project', '-q', '-wd'])

    def tearDown(self):
        # pass
        shutil.rmtree(test_alg_path)

    def test_atk_home(self):
        print('Home page should display with docs link')
        response = self.client.get('/')
        self.assert200(response)
        self.assertContext('docs', True)

    def test_show_docs(self):
        print('User should be able to see ATK documentation')
        response = self.client.get('/docs/index.html')
        self.assert200(response)


class ATKTestCaseTestAlgorithm(TestCase):

    test_alg = {}
    r_param = {}
    p_submit = {}

    def create_app(self):
        from algorithm_toolkit import app
        return app

    def setUp(self):
        self.test_alg = get_algorithms()[0]
        self.r_param = {
            "default_value": '',
            "field_type": "test",
            "display_name": "Test parameter",
            "name": "test",
            "data_type": "string",
            "max_value": None,
            "min_value": None,
            "sort_order": 99,
            "parameter_choices": [],
            "help_text": "Some help text",
            "custom_validation": None,
            "description": "A test parameter"
        }
        self.p_submit = {
            "zoom": 14,
            "roi":
                "POLYGON((-77.0419692993164 38.99335"
                "85922412,-77.17311859130861 38.891887936025896,"
                "-77.03853607177736 38.790272111428706,-76.91013336"
                "181642 38.891887936025896,-77.0419692993164 "
                "38.9933585922412))",
            "test": "dinsdale",
        }

    def tearDown(self):
        pass

    def checkit(self, p, d):
        from algorithm_toolkit import Algorithm
        algorithm = Algorithm(test_alg_path, p)
        valid = algorithm.check_params(d)
        response = {
            'errors': algorithm.errors,
            'valid': valid
        }
        return response

    def test_bad_float(self):
        print('Algorithm should catch malformed floats')

        self.r_param['field_type'] = 'number'
        self.r_param['data_type'] = 'float'
        self.test_alg['required_parameters'].append(self.r_param)
        response = self.checkit(self.p_submit, self.test_alg)
        self.assertFalse(response['valid'])
        self.assertEqual(
            response['errors'],
            [{'parameter': 'test', 'error': 'Not a valid float'}]
        )

        self.p_submit['test'] = 19.3
        response = self.checkit(self.p_submit, self.test_alg)
        self.assertTrue(response['valid'])
        self.assertEqual(response['errors'], [])

    def test_bad_array(self):
        print('Algorithm should catch malformed arrays')

        self.r_param['field_type'] = 'text'
        self.r_param['data_type'] = 'array'
        self.test_alg['required_parameters'].append(self.r_param)
        self.p_submit['test'] = 19.3
        response = self.checkit(self.p_submit, self.test_alg)
        self.assertFalse(response['valid'])
        self.assertEqual(
            response['errors'],
            [{'parameter': 'test', 'error': 'Not a valid array'}]
        )

        self.p_submit['test'] = [0, 1, 2, 3]
        response = self.checkit(self.p_submit, self.test_alg)
        self.assertTrue(response['valid'])
        self.assertEqual(response['errors'], [])

        self.p_submit['test'] = '0, 1, 2, 3'
        response = self.checkit(self.p_submit, self.test_alg)
        self.assertTrue(response['valid'])
        self.assertEqual(response['errors'], [])

        self.p_submit['test'] = '[0, 1, 2, 3]'
        response = self.checkit(self.p_submit, self.test_alg)
        self.assertTrue(response['valid'])
        self.assertEqual(response['errors'], [])

    def test_no_min_max(self):
        print('Algorithm should allow missing min or max values')

        self.r_param['data_type'] = 'integer'
        self.r_param['field_type'] = 'number'
        del self.r_param['min_value']
        del self.r_param['max_value']
        self.test_alg['required_parameters'].append(self.r_param)
        self.p_submit['test'] = 42
        response = self.checkit(self.p_submit, self.test_alg)
        self.assertTrue(response['valid'])
        self.assertEqual(response['errors'], [])

    def test_custom_gt(self):
        print(
            'Algorithm should catch custom "greaterthan" validation errors'
        )

        self.r_param['field_type'] = 'number'
        self.r_param['data_type'] = 'integer'
        self.r_param['custom_validation'] = 'greaterthan.zoom'
        self.test_alg['required_parameters'].append(self.r_param)
        self.p_submit['test'] = 13
        response = self.checkit(self.p_submit, self.test_alg)
        self.assertFalse(response['valid'])
        self.assertEqual(
            response['errors'],
            [{'parameter': 'test', 'error': 'Value must be greater than 14'}]
        )

        self.p_submit['test'] = 14
        response = self.checkit(self.p_submit, self.test_alg)
        self.assertFalse(response['valid'])
        self.assertEqual(
            response['errors'],
            [{'parameter': 'test', 'error': 'Value must be greater than 14'}]
        )

        self.p_submit['test'] = 19
        response = self.checkit(self.p_submit, self.test_alg)
        self.assertTrue(response['valid'])
        self.assertEqual(response['errors'], [])

    def test_custom_gt_float(self):
        print(
            'Algorithm should catch custom "greaterthan" '
            'validation errors with floats'
        )

        self.r_param['field_type'] = 'number'
        self.r_param['data_type'] = 'float'
        self.r_param['custom_validation'] = 'greaterthan.zoom'
        self.test_alg['required_parameters'].append(self.r_param)
        self.p_submit['test'] = 13.1
        response = self.checkit(self.p_submit, self.test_alg)
        self.assertFalse(response['valid'])
        self.assertEqual(
            response['errors'],
            [{'parameter': 'test', 'error': 'Value must be greater than 14.0'}]
        )

        self.p_submit['test'] = 14.0
        response = self.checkit(self.p_submit, self.test_alg)
        self.assertFalse(response['valid'])
        self.assertEqual(
            response['errors'],
            [{'parameter': 'test', 'error': 'Value must be greater than 14.0'}]
        )

        self.p_submit['test'] = 19.7
        response = self.checkit(self.p_submit, self.test_alg)
        self.assertTrue(response['valid'])
        self.assertEqual(response['errors'], [])

    def test_custom_lt(self):
        print(
            'Algorithm should catch custom "lessthan" validation errors'
        )

        self.r_param['field_type'] = 'number'
        self.r_param['data_type'] = 'integer'
        self.r_param['custom_validation'] = 'lessthan.zoom'
        self.test_alg['required_parameters'].append(self.r_param)
        self.p_submit['test'] = 19
        response = self.checkit(self.p_submit, self.test_alg)
        self.assertFalse(response['valid'])
        self.assertEqual(
            response['errors'],
            [{'parameter': 'test', 'error': 'Value must be less than 14'}]
        )

        self.p_submit['test'] = 14
        response = self.checkit(self.p_submit, self.test_alg)
        self.assertFalse(response['valid'])
        self.assertEqual(
            response['errors'],
            [{'parameter': 'test', 'error': 'Value must be less than 14'}]
        )

        self.p_submit['test'] = 13
        response = self.checkit(self.p_submit, self.test_alg)
        self.assertTrue(response['valid'])
        self.assertEqual(response['errors'], [])

    def test_custom_even(self):
        print(
            'Algorithm should catch custom "evenonly" validation errors'
        )

        self.r_param['field_type'] = 'number'
        self.r_param['data_type'] = 'integer'
        self.r_param['custom_validation'] = 'evenonly'
        self.test_alg['required_parameters'].append(self.r_param)
        self.p_submit['test'] = 19
        response = self.checkit(self.p_submit, self.test_alg)
        self.assertFalse(response['valid'])
        self.assertEqual(
            response['errors'],
            [{'parameter': 'test', 'error': 'Value must be an even number'}]
        )

        self.p_submit['test'] = 14
        response = self.checkit(self.p_submit, self.test_alg)
        self.assertTrue(response['valid'])
        self.assertEqual(response['errors'], [])

    def test_custom_odd(self):
        print(
            'Algorithm should catch custom "oddonly" validation errors'
        )

        self.r_param['field_type'] = 'number'
        self.r_param['data_type'] = 'integer'
        self.r_param['custom_validation'] = 'oddonly'
        self.test_alg['required_parameters'].append(self.r_param)
        self.p_submit['test'] = 18
        response = self.checkit(self.p_submit, self.test_alg)
        self.assertFalse(response['valid'])
        self.assertEqual(
            response['errors'],
            [{'parameter': 'test', 'error': 'Value must be an odd number'}]
        )

        self.p_submit['test'] = 13
        response = self.checkit(self.p_submit, self.test_alg)
        self.assertTrue(response['valid'])
        self.assertEqual(response['errors'], [])

    def test_custom_re(self):
        print(
            'Algorithm should catch custom regular '
            'expression validation errors'
        )

        self.r_param['custom_validation'] = '^[0-9][0-9]'
        self.test_alg['required_parameters'].append(self.r_param)
        response = self.checkit(self.p_submit, self.test_alg)
        self.assertFalse(response['valid'])
        self.assertEqual(
            response['errors'],
            [
                {
                    'parameter': 'test',
                    'error': 'Value does not match expression: "^[0-9][0-9]"'
                }
            ]
        )

        self.p_submit['test'] = '1'
        response = self.checkit(self.p_submit, self.test_alg)
        self.assertFalse(response['valid'])
        self.assertEqual(
            response['errors'],
            [
                {
                    'parameter': 'test',
                    'error': 'Value does not match expression: "^[0-9][0-9]"'
                }
            ]
        )

        self.p_submit['test'] = '13'
        response = self.checkit(self.p_submit, self.test_alg)
        self.assertTrue(response['valid'])
        self.assertEqual(response['errors'], [])

    def test_custom_no_custom(self):
        print(
            'Algorithm should proceed if "custom_validation" is missing'
        )

        self.r_param['field_type'] = 'number'
        self.r_param['data_type'] = 'integer'
        del self.r_param['custom_validation']
        self.p_submit['test'] = 13
        self.test_alg['required_parameters'].append(self.r_param)
        response = self.checkit(self.p_submit, self.test_alg)
        self.assertTrue(response['valid'])
        self.assertEqual(response['errors'], [])

    def test_no_choices(self):
        print(
            'Algorithm should proceed if "parameter_choices" is missing'
        )

        del self.r_param['parameter_choices']
        self.test_alg['required_parameters'].append(self.r_param)
        response = self.checkit(self.p_submit, self.test_alg)
        self.assertTrue(response['valid'])
        self.assertEqual(response['errors'], [])

    def test_value_in_list(self):
        print(
            'Algorithm should catch "value in list" validation errors'
        )

        self.r_param['parameter_choices'] = ['thing1', 'thing2']
        self.test_alg['required_parameters'].append(self.r_param)
        response = self.checkit(self.p_submit, self.test_alg)
        self.assertFalse(response['valid'])
        self.assertEqual(
            response['errors'],
            [
                {
                    'parameter': 'test',
                    'error':
                        "Value not in list of valid choices: "
                        "['thing1', 'thing2']"
                }
            ]
        )

        self.p_submit['test'] = 'thing1'
        response = self.checkit(self.p_submit, self.test_alg)
        self.assertTrue(response['valid'])
        self.assertEqual(response['errors'], [])


class ATKTestCaseTestAlgorithmChain(TestCase):

    chain_name = 'map_tiles'
    test_chain = {}
    ac = None
    cl = None
    alg_data = {}

    def create_app(self):
        from algorithm_toolkit import app
        return app

    def setUp(self):
        from algorithm_toolkit import AlgorithmChain
        self.test_chain = get_chains()['map_tiles']
        self.ac = AlgorithmChain(test_alg_path, get_test_run_chain())
        self.cl = self.ac.ChainLedger('tim')
        self.alg_data = {
            "zoom": 14,
            "roi":
                "POLYGON((-77.0419692993164 38.99335"
                "85922412,-77.17311859130861 38.891887936025896,"
                "-77.03853607177736 38.790272111428706,-76.91013336"
                "181642 38.891887936025896,-77.0419692993164 "
                "38.9933585922412))"
        }

    def tearDown(self):
        try:
            shutil.rmtree(test_alg_path)
        except OSError:
            pass

    def test_add_to_metadata(self):
        print(
            'A developer should be able to add a '
            'key-value pair to the chain ledger'
        )
        self.cl.add_to_metadata('hedgehog', 'Spiny Norman')
        self.assertTrue('hedgehog' in self.cl.metadata)

    def test_get_from_metadata(self):
        print(
            'A developer should be able to retrieve a '
            'key-value pair from the chain ledger'
        )
        self.cl.add_to_metadata('hedgehog', 'Spiny Norman')
        m_key = self.cl.get_from_metadata('hedgehog')
        self.assertEqual(m_key, 'Spiny Norman')

    def test_archive_metadata(self):
        print('Test archiving ledger metadata')
        self.cl.archive_metadata('getmaptiles_roi', self.alg_data)
        history = self.cl.history
        self.assertEqual(history[0]['algorithm_name'], 'getmaptiles_roi')
        self.assertEqual(history[0]['algorithm_params'], self.alg_data)

    def test_clear_current_metadata(self):
        print('Test clearing ledger metadata')
        self.cl.metadata = self.alg_data
        self.assertEqual(self.cl.metadata, self.alg_data)
        self.cl.archive_metadata('getmaptiles_roi', self.alg_data)
        self.cl.clear_current_metadata()
        self.assertEqual(self.cl.metadata, {})

    def test_get_history_size(self):
        print('Test retrieving size of chain ledger metadata history')
        self.cl.archive_metadata('getmaptiles_roi', self.alg_data)
        self.cl.clear_current_metadata()
        self.cl.add_to_metadata('hedgehog', 'Spiny Norman')
        history = self.cl.history
        self.assertEqual(len(history), 1)
        self.assertEqual(self.cl.get_history_size(), 1)
        self.cl.archive_metadata(
            'piranha_brothers', {'hedgehog': 'Spiny Norman'})
        self.assertEqual(self.cl.get_history_size(), 2)

    def test_get_from_history(self):
        print('Test retrieving from chain ledger metadata history')
        self.cl.archive_metadata('getmaptiles_roi', self.alg_data)
        alg_name = self.cl.get_from_history(0, 'algorithm_name')
        alg_params = self.cl.get_from_history(0, 'algorithm_params')
        self.assertEqual(alg_name, 'getmaptiles_roi')
        self.assertEqual(alg_params, self.alg_data)

    def test_search_history(self):
        print('Test searching chain ledger metadata history')
        self.cl.metadata = self.alg_data
        self.cl.archive_metadata('getmaptiles_roi', self.alg_data)
        h_list = self.cl.search_history('zoom', 'getmaptiles_roi')
        self.assertEqual(h_list, [14])
        h_list = self.cl.search_history('thingie', 'getmaptiles_roi')
        self.assertEqual(h_list, [None])

    def test_chain_ledger_status(self):
        print('Test setting chain ledger status')
        msg1 = 'I... am an enchanter.'
        msg2 = "There are some who call me... 'Tim'?"
        self.cl.set_status(msg1)
        self.cl.set_status(msg2)
        latest_msg = self.app.config['tim']['latest_msg'].__str__()
        all_msg = self.app.config['tim']['all_msg'].__str__()
        self.assertEqual(latest_msg, msg2.replace("'", "&#39;"))
        self.assertEqual(
            all_msg,
            msg1 + '  \n' + msg2.replace("'", "&#39;")
        )

    def test_params_to_json(self):
        print('Test creating a JSON object from chain ledger history')
        self.cl.archive_metadata('getmaptiles_roi', self.alg_data)
        self.cl.clear_current_metadata()
        self.cl.archive_metadata(
            'piranha_brothers', {'hedgehog': 'Spiny Norman'})
        self.cl.clear_current_metadata()
        json_obj = self.cl.params_to_json()
        test_obj_list = [
            {
                'algorithm_name': 'getmaptiles_roi',
                'algorithm_params': self.alg_data
            },
            {
                'algorithm_name': 'piranha_brothers',
                'algorithm_params': {'hedgehog': 'Spiny Norman'}
            }
        ]
        test_obj = {
            'atk_chain_metadata': test_obj_list
        }
        self.assertEqual(json_obj, test_obj)

    def test_params_to_json_not_json(self):
        print('AlgorithmChain should catch non JSON-serializable objects')

        class TestClass():
            pass

        self.cl.archive_metadata('getmaptiles_roi', self.alg_data)
        self.cl.clear_current_metadata()
        self.cl.archive_metadata(
            'piranha_brothers', {'hedgehog': TestClass()})
        self.cl.clear_current_metadata()
        json_obj = self.cl.params_to_json()
        test_obj_list = [
            {
                'algorithm_name': 'getmaptiles_roi',
                'algorithm_params': self.alg_data
            },
            {
                'algorithm_name': 'piranha_brothers',
                'algorithm_params': {'hedgehog': 'Value not JSON serializable'}
            }
        ]
        test_obj = {
            'atk_chain_metadata': test_obj_list
        }
        self.assertEqual(json_obj, test_obj)

    def test_params_to_json_save_to_file(self):
        print(
            'Test creating a JSON object from chain '
            'ledger history and saving to file'
        )
        tmp_path = '/tmp/testtest.json'
        self.cl.archive_metadata('getmaptiles_roi', self.alg_data)
        self.cl.clear_current_metadata()
        self.cl.archive_metadata(
            'piranha_brothers', {'hedgehog': 'Spiny Norman'})
        self.cl.clear_current_metadata()
        self.cl.save_params_to_json(tmp_path)
        test_obj_list = [
            {
                'algorithm_name': 'getmaptiles_roi',
                'algorithm_params': self.alg_data
            },
            {
                'algorithm_name': 'piranha_brothers',
                'algorithm_params': {'hedgehog': 'Spiny Norman'}
            }
        ]
        test_obj = {
            'atk_chain_metadata': test_obj_list
        }
        with open(tmp_path, 'r') as json_file:
            json_obj = json_file.read()
            self.assertEqual(json_obj, json.dumps(test_obj))

        self.cl.save_params_to_json(tmp_path, pretty=True)
        with open(tmp_path, 'r') as json_file:
            json_obj = json_file.read()
            self.assertEqual(
                json_obj,
                json.dumps(test_obj, separators=(',', ': '), indent=4)
            )

    def test_get_request_dict(self):
        print(
            'Test returning a dictionary containing '
            'chain parameters with defaults'
        )
        sys.path.append(test_alg_path)
        subprocess.call(['alg', 'cp', 'test_project', '-e', '-q'])
        from algorithm_toolkit import AlgorithmChain
        self.ac = AlgorithmChain(test_alg_path, get_test_run_chain())
        self.cl = self.ac.ChainLedger('tim')

        check_dict = {
            'chain_name': 'map_tiles',
            'algorithms': [
                {
                    'parameters': self.alg_data,
                    'algorithm': 'getmaptiles_roi'
                }, {
                    'parameters': {
                        'image_filenames': None
                    },
                    'algorithm': 'stitch_tiles'
                }, {
                    'parameters': {
                        'image_bounds': None,
                        'image_path': None
                    },
                    'algorithm': 'output_image_to_client'
                }
            ]
        }

        test_dict = self.ac.get_request_dict()
        self.assertEqual(check_dict, test_dict)

        # add an optional parameter
        o_param = {
            "default_value": "",
            "field_type": "text",
            "display_name": "Useless Parameter",
            "name": "useless",
            "data_type": "string",
            "max_value": None,
            "min_value": None,
            "sort_order": 2,
            "parameter_choices": [],
            "help_text": "Don't bother entering anything",
            "custom_validation": None,
            "description": "A completely useless parameter.",
        }
        json_file = os.path.join(
            test_alg_path, 'algorithms', 'getmaptiles_roi', 'algorithm.json')
        with open(json_file, 'r') as alg_file:
            roi = json.load(alg_file)
        with open(json_file, 'w') as alg_file:
            roi['optional_parameters'].append(o_param)
            alg_file.write(json.dumps(roi))
        check_dict['algorithms'][0]['parameters']['useless'] = ''

        test_dict = self.ac.get_request_dict()
        self.assertEqual(check_dict, test_dict)

        # remove default value
        del o_param['default_value']
        with open(json_file, 'w') as alg_file:
            roi['optional_parameters'].append(o_param)
            alg_file.write(json.dumps(roi))
        check_dict['algorithms'][0]['parameters']['useless'] = None

        test_dict = self.ac.get_request_dict()
        self.assertEqual(check_dict, test_dict)

        # remove default value from required param
        del roi['required_parameters'][0]['default_value']
        with open(json_file, 'w') as alg_file:
            alg_file.write(json.dumps(roi))
        check_dict['algorithms'][0]['parameters']['roi'] = None

        test_dict = self.ac.get_request_dict()
        self.assertEqual(check_dict, test_dict)


class ATKTestCaseFileUtils(TestCase):

    def create_app(self):
        from algorithm_toolkit import app
        return app

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_make_dir_if_not_exists(self):
        from algorithm_toolkit import utils
        print('Ensure we can create multiple folders if needed')
        test_dir = 'test_project/algorithms'
        utils.file_utils.make_dir_if_not_exists(test_dir)
        self.assertTrue(os.path.exists(test_dir))

        # don't recreate if path exists
        utils.file_utils.make_dir_if_not_exists(test_dir)
        self.assertTrue(os.path.exists(test_dir))

        shutil.rmtree(test_alg_path)
        self.assertFalse(os.path.exists(test_dir))

    def test_get_algorithms_valueerror(self):
        from algorithm_toolkit import utils
        print(
            'Ensure ValueError conditions are handled when '
            'getting an algorithm definition'
        )
        with open('testalgorithm.json', 'w') as json_file:
            json_file.write('{[1, 2 , 3]: "splunge"}')

        response = utils.file_utils.get_algorithm('testalgorithm.json')
        self.assertEqual(response, {})
        os.remove('testalgorithm.json')

    def test_get_chain_def_valueerror(self):
        from algorithm_toolkit import utils
        print(
            'Ensure ValueError conditions are handled when '
            'getting a chain definition'
        )
        os.makedirs(test_alg_path)
        chain_path = os.path.join(test_alg_path, 'chains.json')
        with open(chain_path, 'w') as json_file:
            json_file.write('{[1, 2 , 3]: "splunge"}')

        response = utils.file_utils.get_chain_def(test_alg_path)
        self.assertEqual(response, {})
        shutil.rmtree(test_alg_path)

    def test_get_chain_def_ioerror(self):
        from algorithm_toolkit import utils
        print(
            'Ensure IOError conditions are handled when '
            'getting a chain definition'
        )
        response = utils.file_utils.get_chain_def(test_alg_path)
        self.assertEqual(response, {})


class ATKTestCaseDataUtils(TestCase):

    def create_app(self):
        from algorithm_toolkit import app
        return app

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_text2int_not_in_mapping(self):
        from algorithm_toolkit import utils
        print('Return -1 if text is not found in word_to_number_mapping')
        response = utils.data_utils.text2int('deadparrot')
        self.assertEqual(response, -1)

    def test_create_random_string_all_chars(self):
        from algorithm_toolkit import utils
        print(
            'If desired, random string can include symbols '
            '(i.e.: not just http-safe characters)'
        )
        symbols = '`~!@#$%*()-_=+[]{}|;:,./?'
        for x in range(100):
            response = utils.data_utils.create_random_string(http_safe=False)
            # TODO: rewrite this test
            # self.assertTrue(any(s for s in symbols if s in response))

        for x in range(100):
            response = utils.data_utils.create_random_string(http_safe=True)
            self.assertFalse(any(s for s in symbols if s in response))


class ATKTestCaseDecorators(TestCase):

    def create_app(self):
        from algorithm_toolkit import app
        return app

    def setUp(self):
        self.app.config['TESTING'] = False

    def tearDown(self):
        self.app.config['TESTING'] = True
        self.app.config['DEBUG'] = True

    def test_not_debug(self):
        print(
            'debug-only views should be blocked if '
            'not in debug or testing mode'
        )
        self.app.config['DEBUG'] = False
        response = self.client.get('/')
        self.assert400(response)
        self.assertEqual(response.data, 'This view is not accessible')


if __name__ == '__main__':
    unittest.main()
