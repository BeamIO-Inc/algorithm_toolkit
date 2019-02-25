import copy
import json
import os
import random
import requests
import shutil

from flask import (
    request,
    jsonify,
    render_template,
    make_response,
    send_from_directory,
    redirect,
    url_for
)
from flask_cors import cross_origin
from requests.exceptions import RequestException
from werkzeug import MultiDict
from wtforms import validators

from .. import (
    AlgorithmChain,
    check_api_key,
    debug_only,
    app,
)
from ..forms import (
    AlgorithmForm,
    set_field,
    AlgorithmCreateForm,
    AlgorithmParameterForm,
    AlgorithmOutputForm
)
from ..utils.file_utils import (
    get_json_path,
    get_chain_def,
    get_algorithm,
    make_dir_if_not_exists,
    list_algorithms
)
from ..utils.data_utils import create_random_string
from cli.cli import do_uninstall

from . import home

path = app.config['ATK_PATH']
api_key = app.config['API_KEY']
cors_origins = app.config['CORS_ORIGIN_WHITELIST']
u_block = '<block type="user_input" id="{randid}">\n'


def get_docs_link():
    if os.path.exists(os.path.join(path, 'docs')):
        link_to_docs = True
    else:
        link_to_docs = False
    return link_to_docs


def get_notice(r):
    notice = None
    if not r.cookies.get('dismiss_notice'):
        try:
            response = requests.get(
                app.config['TILEDRIVER_URL'] + 'ads/atk_notice/')
            if response.status_code == 200:
                notice = json.loads(response.content.decode('utf-8'))['ads'][0]
                if notice['ad_content'] == 'empty':
                    notice = None
        except RequestException:
            return None

    return notice


@home.route('/dismiss_notice/', methods=['GET'])
@debug_only(app.config)
def dismiss_notice():
    # dismiss an ATK notice for 24 hours
    resp = make_response()
    resp.set_cookie('dismiss_notice', 'True', max_age=86400)
    return resp


@home.route('/', methods=['GET'])
@debug_only(app.config)
def index():
    try:
        response = requests.get(app.config['TILEDRIVER_URL'] + 'ads/atk_ad/')
    except RequestException:
        response = None

    t_path = app.jinja_loader.searchpath[1]
    t_path = os.path.join(t_path, 'default_ads.json')
    with open(t_path, 'r') as ad_file:
        default_obj = json.loads(ad_file.read())
        default_ads = default_obj['ads']

    if response:
        if response.status_code == 200:
            ad_object = json.loads(response.content.decode('utf-8'))
            ads = ad_object['ads']
            if len(ads) < 3:
                ads = ads + default_ads
        else:
            ads = default_ads
    else:
        ads = default_ads

    ad1 = ads[0]
    ad2 = ads[1]
    ad3 = ads[2]

    return render_template(
        'index.html',
        chains=get_chain_def(path),
        docs=get_docs_link(),
        ad1=ad1,
        ad2=ad2,
        ad3=ad3,
        show_notice=get_notice(request),
        nav='index'
    )


@home.route('/docs/<path:filename>', methods=['GET'])
@debug_only(app.config)
def show_docs(filename):
    docs_path = os.path.join(path, 'docs')
    return send_from_directory(docs_path, filename)


@home.route('/main/', methods=['POST', 'GET'])
@cross_origin(origins=cors_origins)
@check_api_key(request, api_key)
def main():
    chain = None
    status_key = None
    run_mode = None
    iter_param = None
    iter_type = None
    iter_value = None

    if request.method == 'POST':
        try:
            chain = request.form['chain']
        except KeyError:
            chain = None

        try:
            status_key = request.form['status_key']
        except KeyError:
            status_key = None

        if 'run_mode' in request.form:
            if request.form['run_mode'] == 'batch':
                try:
                    run_mode = 'batch'
                    iter_param = request.form['iter_param']
                    iter_type = request.form['iter_type']
                    iter_value = request.form['iter_value']
                except KeyError:
                    return make_response('Batch mode misconfigured', 400)
            else:
                run_mode = 'single'
        else:
            run_mode = 'single'
    elif request.method == 'GET':  # pragma: no branch
        chain = request.args.get('chain', None)
        status_key = request.args.get('status_key', None)
        run_mode = request.args.get('run_mode', 'single')
        iter_param = request.args.get('iter_param', None)
        iter_type = request.args.get('iter_type', None)
        iter_value = request.args.get('iter_value', None)

    if chain is None:
        return make_response('Missing chain parameter in request', 400)

    try:
        chain = json.loads(chain)
    except ValueError:
        return make_response('Chain parameter not properly formatted', 400)

    if 'chain_name' not in chain:
        return make_response('Chain name not defined', 400)

    if 'algorithms' not in chain:
        return make_response('Algorithms not defined', 400)

    if status_key is None:
        status_key = create_random_string(http_safe=True)

    c_obj = AlgorithmChain(path, chain)
    if c_obj.chain_definition == {}:
        return make_response('Chain name not found', 404)
    cl = c_obj.create_ledger(status_key)
    cl.make_working_folders()

    if run_mode == 'single':
        response = c_obj.call_chain_algorithms()
        save_fname = status_key + '.json'
        if 'CHAIN_LEDGER_HISTORY_PATH' in app.config:
            save_path = os.path.join(
                app.config['CHAIN_LEDGER_HISTORY_PATH'], save_fname)
        else:
            make_dir_if_not_exists(os.path.join(path, 'history'))
            save_path = os.path.join(path, 'history', save_fname)
        c_obj.chain_ledger.save_history_to_json(save_path, pretty=True)
    else:
        response = c_obj.call_batch(iter_param, iter_type, iter_value)

    cl.remove_working_folders()

    if response['output_type'] == 'error':
        return make_response(jsonify(response), 400)

    return jsonify(response)


@home.route('/chain_run_status/<status_key>/', methods=['POST'])
@cross_origin(origins=cors_origins)
@check_api_key(request, api_key)
def chain_run_status(status_key):
    chain_status = {}
    try:
        chain_status = app.config[status_key]
    except KeyError:
        return make_response('Invalid status key', 404)

    return jsonify(chain_status)


@home.route('/list_chains/', methods=['GET'])
@cross_origin(origins=cors_origins)
@check_api_key(request, api_key)
def list():
    return jsonify(get_chain_def(path))


@home.route('/chain_info/<chain>/', methods=['GET'])
@cross_origin(origins=cors_origins)
@check_api_key(request, api_key)
def chain_info(chain):
    return jsonify(get_chain_def(path, chain))


def set_param_source(alg, param):
    temp_source = 'chain_ledger'
    if 'parameter_source' in alg:
        if alg['parameter_source'] == 'user':  # pragma: no branch
            temp_source = 'user'
    else:
        try:
            if alg['parameters'][param['name']]['source'] == 'user':
                temp_source = 'user'
        except KeyError:
            temp_source = 'user'
    return temp_source


@home.route('/chain_algorithms/<chain>/', methods=['GET'])
@cross_origin(origins=cors_origins)
@check_api_key(request, api_key)
def chain_algorithms(chain):
    chain_obj = get_chain_def(path, chain)
    alg_list = []
    for alg in chain_obj:
        a_path = get_json_path(path, alg['algorithm'])
        temp_alg = get_algorithm(a_path)
        for rp in temp_alg['required_parameters']:
            try:
                rp['source'] = set_param_source(alg, rp)
            except KeyError:
                return make_response(
                    'Chain definition is missing parameter: ' + rp['name'],
                    400
                )
        for op in temp_alg['optional_parameters']:
            try:
                op['source'] = set_param_source(alg, op)
            except KeyError:
                return make_response(
                    'Chain definition is missing parameter: ' + op['name'],
                    400
                )
        alg_list.append(temp_alg)

    return jsonify(alg_list)


@home.route('/algorithm_info/<path:algorithm>/', methods=['GET'])
@cross_origin(origins=cors_origins)
@check_api_key(request, api_key)
def algorithm_info(algorithm=None):
    a_path = get_json_path(path, algorithm)
    return jsonify(get_algorithm(a_path))


@home.route('/algorithms/', methods=['GET'])
@debug_only(app.config)
def algorithms():
    return render_template(
        'algorithms.html',
        algs=list_algorithms(path),
        chains=get_chain_def(path),
        docs=get_docs_link(),
        nav='algorithms'
    )


@home.route('/algorithms/create/', methods=['GET', 'POST'])
@home.route('/algorithms/create/<path:algorithm>/', methods=['GET', 'POST'])
@debug_only(app.config)
def create_algorithm(algorithm=None):
    if algorithm is not None:
        a_path = get_json_path(path, algorithm)
        this_alg = get_algorithm(a_path)
        if this_alg == {}:
            return make_response('Algorithm not found', 404, {})
        for rp in this_alg['required_parameters']:
            rp['required'] = True
            rp['original_name'] = rp['name']
        for op in this_alg['optional_parameters']:
            op['required'] = False
            op['original_name'] = op['name']
        this_alg['parameters'] = json.dumps(
            this_alg['required_parameters'] + this_alg['optional_parameters'])
        for out in this_alg['outputs']:
            out['original_name'] = out['name']
        this_alg['outputs'] = json.dumps(this_alg['outputs'])
        if 'private' in this_alg:
            this_alg['private'] = str(this_alg['private']).lower()
        form = AlgorithmCreateForm(MultiDict(this_alg))
    else:
        form = AlgorithmCreateForm()

    algs = [x['name'] for x in list_algorithms(path)]
    if algorithm is not None:
        algs.remove(algorithm)
    form.name.validators = [validators.NoneOf(
        algs, message='Algorithm name must be unique')]

    p_form = AlgorithmParameterForm()
    o_form = AlgorithmOutputForm()

    if form.validate_on_submit():
        f = request.form
        temp_alg = {}
        temp_alg['name'] = f['name'].strip().replace(' ', '_')
        temp_alg['display_name'] = f['display_name']
        temp_alg['description'] = f['description']
        temp_alg['version'] = f['version']
        temp_alg['homepage'] = f['homepage']
        if 'private' in f:
            temp_alg['private'] = f['private']
        else:
            temp_alg['private'] = False
        temp_alg['license'] = f['license']

        params = json.loads(request.form['parameters'])
        del_params = request.form['deleted_parameters'].split(',')
        r_params = []
        o_params = []
        p_name_changes = []
        for p in params:
            if p['original_name'] != '' and p['original_name'] != p['name']:
                temp_name_change = {
                    'original_name': p['original_name'],
                    'new_name': p['name']
                }
                p_name_changes.append(temp_name_change)

            p.pop('original_name')

            if p['required']:
                r_params.append(p)
            else:
                o_params.append(p)
        temp_alg['required_parameters'] = r_params
        temp_alg['optional_parameters'] = o_params

        outs = json.loads(request.form['outputs'])
        del_outs = request.form['deleted_outputs'].split(',')
        o_name_changes = []
        for o in outs:
            if o['original_name'] != '' and o['original_name'] != o['name']:
                temp_name_change = {
                    'original_name': o['original_name'],
                    'new_name': o['name']
                }
                o_name_changes.append(temp_name_change)

            o.pop('original_name')
        temp_alg['outputs'] = outs

        dest_path = os.path.join(path, 'algorithms', temp_alg['name'])
        source_path = os.path.dirname(os.path.abspath(__file__))
        source_path = os.path.abspath(os.path.join(
            source_path, os.pardir, os.pardir, 'cli', 'sources'))

        def write_readme():
            with open(os.path.join(dest_path, 'README.md'), 'w') as temp_file:
                readme_txt = render_template('algorithm.md', alg=temp_alg)
                temp_file.writelines(readme_txt)

        if not algorithm:
            os.makedirs(dest_path)
            shutil.copyfile(
                os.path.join(source_path, 'main.txt'),
                os.path.join(dest_path, 'main.py')
            )
            shutil.copyfile(
                os.path.join(source_path, '__init__.txt'),
                os.path.join(dest_path, '__init__.py')
            )
            shutil.copyfile(
                os.path.join(source_path, 'test.txt'),
                os.path.join(dest_path, 'test.py')
            )
            save_license_file(source_path, dest_path, f['license'])
            write_readme()
        else:
            if f['name'] != algorithm:
                old_dest_path = os.path.join(path, 'algorithms', algorithm)
                new_dest_path = os.path.join(
                    path, 'algorithms', temp_alg['name'])
                new_dest_root = os.path.join(path, 'algorithms')
                if '/' in temp_alg['name']:
                    new_dest_root = os.path.join(
                        new_dest_root, temp_alg['name'].split('/')[0])
                    make_dir_if_not_exists(new_dest_root)
                    shutil.copyfile(
                        os.path.join(source_path, '__init__.txt'),
                        os.path.join(new_dest_root, '__init__.py')
                    )
                os.rename(old_dest_path, new_dest_path)
                dest_path = new_dest_path

            with open(os.path.join(path, 'chains.json'), 'r+') as c_file:
                chain_content = json.loads(c_file.read())
                for c_key, c_val in enumerate(chain_content):
                    for c_alg in chain_content[c_val]:
                        if f['name'] != algorithm:
                            # handle algorithm name change
                            if c_alg['algorithm'] == algorithm:
                                c_alg['algorithm'] = f['name']
                            elif 'parameters' in c_alg:
                                for p_key, p_val in enumerate(
                                        c_alg['parameters']):
                                    temp_val = c_alg['parameters'][p_val]
                                    if 'source_algorithm' in temp_val:
                                        if (
                                            temp_val['source_algorithm'] ==
                                                algorithm
                                        ):
                                            temp_val[
                                                'source_algorithm'
                                            ] = f['name']

                        if len(p_name_changes) > 0:
                            # handle parameter name changes
                            if c_alg['algorithm'] == f['name']:
                                for nc in p_name_changes:
                                    try:
                                        c_alg[
                                            'parameters'
                                        ][
                                            nc['new_name']
                                        ] = c_alg[
                                            'parameters'
                                        ].pop(nc['original_name'])
                                    except KeyError:
                                        pass

                        if len(del_params) > 0:
                            # check for and remove parameters that have been
                            # deleted but are named in chains.json
                            if 'parameters' in c_alg:
                                if c_alg['algorithm'] == f['name']:
                                    for p_key in del_params:
                                        c_alg['parameters'].pop(p_key, None)

                                    if len(c_alg['parameters']) == 0:
                                        c_alg.pop('parameters', None)
                                        c_alg['parameter_source'] = 'user'

                        if len(o_name_changes) > 0:
                            # handle output name changes
                            if 'parameters' in c_alg:
                                for p_key, p_val in enumerate(
                                        c_alg['parameters']):
                                    temp_val = c_alg['parameters'][p_val]
                                    for nc in o_name_changes:
                                        try:
                                            if temp_val[
                                                'source_algorithm'
                                            ] == f['name']:
                                                if temp_val[
                                                    'key'
                                                ] == nc['original_name']:
                                                    temp_val[
                                                        'key'
                                                    ] = nc['new_name']
                                        except KeyError:
                                            pass

                        if len(del_outs) > 0:
                            # check for parameters that reference deleted
                            # outputs and remove
                            if 'parameters' in c_alg:
                                p_loop = copy.deepcopy(c_alg['parameters'])
                                for p_key, p_val in enumerate(p_loop):
                                    temp_val = p_loop[p_val]
                                    if 'source_algorithm' in temp_val:
                                        if temp_val[
                                            'source_algorithm'
                                        ] == f['name']:
                                            if temp_val['key'] in del_outs:
                                                del c_alg['parameters'][p_val]

                                if len(c_alg['parameters']) == 0:
                                    c_alg.pop('parameters', None)
                                    c_alg['parameter_source'] = 'user'

                c_file.seek(0)
                c_file.truncate()
                c_file.write(json.dumps(
                    chain_content,
                    indent=4,
                    separators=(',', ': '),
                    sort_keys=True
                ))

            if f['license'] != this_alg['license']:
                save_license_file(source_path, dest_path, f['license'])

            if 'update_readme' in f:
                if f['update_readme']:
                    write_readme()

        with open(os.path.join(dest_path, 'algorithm.json'), 'w') as temp_file:
            temp_file.writelines(
                json.dumps(
                    temp_alg,
                    indent=4,
                    separators=(',', ': '),
                    sort_keys=True
                )
            )
        return redirect(url_for('home.algorithms'))

    return render_template(
        'create_algorithm.html',
        form=form,
        p_form=p_form,
        o_form=o_form,
        docs=get_docs_link(),
        algs=algs,
        chains=get_chain_def(path),
        nav='algorithms'
    )


def save_license_file(source_path, dest_path, license):
    lic_filename = os.path.join(dest_path, 'LICENSE')
    lic_source = 'license_%s.txt'
    if license == 'GNU AGPLv3':
        lic_add = 'AGPL'
    elif license == 'GNU GPLv3':
        lic_add = 'GPL'
    elif license == 'GNU LGPLv3':
        lic_add = 'LGPL'
    elif license == 'The Unlicense':
        lic_add = 'Unlicense'
    else:
        lic_add = license

    if license == 'Proprietary' or license == 'Other':
        if os.path.exists(lic_filename):
            with open(lic_filename, 'w') as lic_file:
                lic_file.write('')
        else:
            with open(lic_filename, 'a'):
                os.utime(lic_filename, None)
    else:
        shutil.copyfile(
            os.path.join(source_path, lic_source % lic_add),
            lic_filename
        )


@home.route('/algorithm/delete/<path:algorithm>/', methods=['GET'])
@debug_only(app.config)
def delete_algorithm(algorithm):
    do_uninstall(algorithm)
    return redirect(url_for('home.algorithms'))


@home.route('/algorithm/copy/<path:algorithm>/', methods=['GET'])
@debug_only(app.config)
def copy_algorithm(algorithm):
    source_path = os.path.join(path, 'algorithms', algorithm)
    new_alg = algorithm + '_copy'
    alg_iterator = 0
    while os.path.isdir(os.path.join(path, 'algorithms', new_alg)):
        alg_iterator += 1
        new_alg = algorithm + '_copy' + str(alg_iterator)
    dest_path = os.path.join(path, 'algorithms', new_alg)
    shutil.copytree(source_path, dest_path)
    this_alg = os.path.join(dest_path, 'algorithm.json')
    temp_alg = get_algorithm(this_alg)
    temp_alg['name'] = new_alg
    with open(this_alg, 'w') as temp_file:
        temp_file.writelines(
            json.dumps(
                temp_alg,
                indent=4,
                separators=(',', ': '),
                sort_keys=True
            )
        )
    return redirect(url_for('home.algorithms'))


@home.route('/chain_builder/', methods=['GET'])
@debug_only(app.config)
def chain_builder():
    block_list = []
    block_scripts = []
    used_colours = [360]
    all_algs = []
    drop_str = '.appendField(new Blockly.FieldDropdown(['
    drop_str += '["first","first"],'
    drop_str += '["second","second"],'
    drop_str += '["third","third"],'
    drop_str += '["fourth","fourth"],'
    drop_str += '["fifth","fifth"],'
    drop_str += '["sixth","sixth"],'
    drop_str += ']), "occurrence");'

    algpath = os.path.join(path, 'algorithms')

    for root, dirs, files in os.walk(algpath):
        for algdir in dirs:
            parent = root[root.rfind(os.sep) + 1:]
            if parent == 'algorithms':
                temp_path = get_json_path(path, algdir)
            else:
                temp_path = get_json_path(path, parent + os.sep + algdir)
            temp_alg = get_algorithm(temp_path)
            all_algs.append(temp_alg)
            if temp_alg != {}:  # pragma: no branch
                temp_name = temp_alg['name']
                temp_display = temp_alg['display_name']

                this_colour = random.randrange(0, 330, 10)
                while this_colour in used_colours:  # pragma: no cover
                    this_colour = random.randrange(0, 330, 10)
                used_colours.append(this_colour)
                this_colour = str(this_colour)

                this_block = ''

                this_block += '<category name="'
                if '/' in temp_name:
                    this_block += temp_name.split('/')[0] + '/'
                else:
                    this_block += ' '
                this_block += temp_display
                this_block += '" colour="' + this_colour + '">\n'
                this_block += '    <block type="' + temp_name
                this_block += '"></block>\n'

                this_script = 'Blockly.Blocks["' + temp_name + '"] = {'
                this_script += 'init: function() {this.appendDummyInput()'
                this_script += '.setAlign(Blockly.ALIGN_CENTRE)'
                this_script += '.appendField(new Blockly.FieldLabel("'
                this_script += 'ALGORITHM", "font-weight-bold"));'
                this_script += 'this.appendDummyInput()'
                this_script += '.appendField("' + temp_display + '");'
                # this_script += drop_str

                if 'required_parameters' in temp_alg:
                    if len(temp_alg['required_parameters']) > 0:
                        this_script += 'this.appendDummyInput().setAlign('
                        this_script += 'Blockly.ALIGN_RIGHT).appendField('
                        this_script += 'new Blockly.FieldLabel("Required '
                        this_script += 'Input Fields:", "font-weight-bold"));'
                    for rp in temp_alg['required_parameters']:
                        this_script += 'this.appendValueInput("' + rp['name']
                        this_script += '").setCheck("' + rp['data_type'] + '")'
                        this_script += '.setAlign(Blockly.ALIGN_RIGHT)'
                        this_script += '.appendField("' + rp['name'] + '");'

                if 'optional_parameters' in temp_alg:
                    if len(temp_alg['optional_parameters']) > 0:
                        this_script += 'this.appendDummyInput().setAlign('
                        this_script += 'Blockly.ALIGN_RIGHT).appendField('
                        this_script += 'new Blockly.FieldLabel("Optional '
                        this_script += 'Input Fields:", "font-weight-bold"));'
                    for op in temp_alg['optional_parameters']:
                        this_script += 'this.appendValueInput("' + op['name']
                        this_script += '").setCheck("' + op['data_type'] + '")'
                        this_script += '.setAlign(Blockly.ALIGN_RIGHT)'
                        this_script += '.appendField("' + op['name'] + '");'

                this_script += 'this.setInputsInline(false);'
                this_script += 'this.setPreviousStatement(true, null);'
                this_script += 'this.setNextStatement(true, null);'
                this_script += 'this.setColour(' + this_colour + ');'
                this_script += 'this.setTooltip("' + temp_display + '");'
                this_script += 'this.data = "algorithm";} };\n'

                if 'outputs' in temp_alg:  # pragma: no branch
                    for out in temp_alg['outputs']:
                        this_out = temp_name + '__' + out['name']
                        this_type = out['data_type']
                        this_block += '    <block type="' + this_out
                        this_block += '"></block>\n'

                        this_script += 'Blockly.Blocks["' + this_out + '"] = {'
                        this_script += 'init: function() {'
                        this_script += 'this.appendDummyInput()'
                        this_script += '.setAlign(Blockly.ALIGN_CENTRE)'
                        this_script += '.appendField(new Blockly.FieldLabel('
                        this_script += '"OUTPUT FIELD", "font-weight-bold"));'
                        this_script += 'this.appendDummyInput()'
                        this_script += '.appendField("' + temp_display + '")'
                        this_script += drop_str
                        this_script += 'this.appendDummyInput()'
                        this_script += '.appendField("' + out['name'] + '");'
                        this_script += 'this.setOutput(true, "' + this_type
                        this_script += '");'
                        this_script += 'this.setColour(' + this_colour + ');'
                        this_script += 'this.data = "input";} };\n'

                this_block += '</category>'

                block_list.append(this_block)
                block_scripts.append(this_script)

    chain_obj = get_chain_def(path)

    return render_template(
        'chain_builder.html',
        block_list=sorted(block_list),
        block_scripts=block_scripts,
        chain_obj=json.dumps(chain_obj),
        chains=chain_obj,
        docs=get_docs_link(),
        nav='chain_builder'
    )


def add_parameter_blocks(params, chain_alg):
    temp_block = ''
    temp_param = {}
    for p in params:
        temp_block += '<value name="' + p['name'] + '">\n'
        if 'parameter_source' in chain_alg:
            if chain_alg['parameter_source'] == 'user':  # pragma: no branch
                temp_block += u_block.replace(
                    '{randid}', create_random_string(http_safe=True))
        else:
            try:
                temp_param = chain_alg['parameters'][p['name']]
            except KeyError:
                temp_param['source'] = 'user'

            if temp_param['source'] == 'user':
                temp_block += u_block.replace(
                    '{randid}', create_random_string(http_safe=True))
            else:
                temp_block += '<block type="'
                temp_block += temp_param['source_algorithm']
                temp_block += '__' + temp_param['key'] + '" id="'
                temp_block += create_random_string(http_safe=True) + '">\n'
                temp_block += '<field name="occurrence">'
                temp_block += temp_param['occurrence'] + '</field>'
        temp_block += '<data>input</data>\n'
        temp_block += '</block>\n'
        temp_block += '</value>\n'
    return temp_block


@home.route('/chain_builder/get_blocks/<chain>/', methods=['GET'])
@debug_only(app.config)
def get_blocks(chain):
    chain_obj = get_chain_def(path)
    alg_count = 0
    for chain_alg in chain_obj[chain]:
        temp_path = get_json_path(path, chain_alg['algorithm'])
        temp_alg = get_algorithm(temp_path)
        if alg_count == 0:
            temp_block = '<xml xmlns="http://www.w3.org/1999/xhtml" id="'
            temp_block += 'workspaceBlocks" style="display:none">\n'
            temp_block += '<variables></variables>\n'
            temp_block += '<block type="' + chain_alg['algorithm'] + '" '
            temp_block += 'id="' + create_random_string(http_safe=True) + '" '
            temp_block += 'x="10" y="10">\n'
        else:
            temp_block += '<next>\n'
            temp_block += '<block type="' + chain_alg['algorithm'] + '" '
            temp_block += 'id="' + create_random_string(http_safe=True)
            temp_block += '">\n'

        temp_block += '<data>algorithm</data>\n'

        if 'required_parameters' in temp_alg:  # pragma: no branch
            temp_block += add_parameter_blocks(
                temp_alg['required_parameters'], chain_alg)

        if 'optional_parameters' in temp_alg:  # pragma: no branch
            temp_block += add_parameter_blocks(
                temp_alg['optional_parameters'], chain_alg)

        alg_count += 1
    for a in range(0, alg_count - 1):
        temp_block += '</block>\n</next>\n'
    temp_block += '</block>\n</xml>\n'

    r = make_response(
        temp_block, 200, {'Content-Type': 'text/xml; charset=utf-8'})
    return r


@home.route('/chain_builder/update_chains/', methods=['POST'])
@debug_only(app.config)
def update_chains():
    try:
        chains = json.loads(request.form['chains'])
    except KeyError:
        return make_response('Missing chain definitions', 400)

    with open(os.path.join(path, 'chains.json'), 'w+') as f:
        json.dump(chains, f, indent=4, separators=(',', ': '))

    chain_list = ''
    for k, v in chains.items():
        chain_link = '<a class="dropdown-item" href="'
        chain_link += url_for('home.test_run', chain_name=k) + '">'
        chain_link += k + '</a>'
        chain_list += chain_link

    return make_response(chain_list, 200)


@home.route('/test_run/<chain_name>/', methods=['GET', 'POST'])
@debug_only(app.config)
def test_run(chain_name):
    class F(AlgorithmForm):
        pass

    def get_source(a, p_name):
        try:
            p_source = a['parameter_source']
        except KeyError:
            try:
                this_p = a['parameters'][p_name]
                p_source = this_p['source']
            except KeyError:
                p_source = 'user'
        return p_source

    a_list = []
    a_iterator = 0
    fetching_results = False
    chain = {}
    alg_choices = []

    chain_definition = get_chain_def(path, chain_name)

    for a in chain_definition:
        a_name = a['algorithm']
        json_path = get_json_path(path, a_name)
        with open(json_path) as json_file:
            alg_definition = json.load(json_file)

        for rp in alg_definition['required_parameters']:
            if get_source(a, rp['name']) == 'user':
                temp_field = set_field(rp, 'required')
                temp_name = a_name.replace('/', '___') + '__' + rp['name']
                temp_name += '_' + str(a_iterator)
                setattr(F, temp_name, temp_field)
                rp['field'] = eval('F().' + temp_name)

        for op in alg_definition['optional_parameters']:
            if get_source(a, op['name']) == 'user':
                temp_field = set_field(op, '')
                temp_name = a_name.replace(os.sep, '___') + '__' + op['name']
                temp_name += '_' + str(a_iterator)
                setattr(F, temp_name, temp_field)
                op['field'] = eval('F().' + temp_name)

        a_list.append(alg_definition)
        alg_choices.append((a, a))
        a_iterator += 1

    form = F()

    if form.validate_on_submit():
        fetching_results = True
        temp_input_algorithms = []

        for a in a_list:
            temp_item = {}
            temp_item['name'] = a['name']
            temp_params = {}
            for rp in a['required_parameters']:
                try:
                    temp_params[rp['name']] = request.form[rp['field'].name]
                except KeyError:
                    pass
            for op in a['optional_parameters']:
                try:
                    temp_params[op['name']] = request.form[op['field'].name]
                except KeyError:
                    pass
            temp_item['parameters'] = temp_params
            temp_input_algorithms.append(temp_item)
        chain['chain_name'] = chain_name
        chain['algorithms'] = temp_input_algorithms

    return render_template(
        'test_run.html',
        form=form,
        a_list=a_list,
        fetching_results=fetching_results,
        chain=chain,
        chains=get_chain_def(path),
        docs=get_docs_link(),
        nav='test_run'
    )
