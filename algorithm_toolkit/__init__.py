import datetime
import logging
import os

from flask import Flask
from flask.logging import default_handler
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)

from .atk import (
    Algorithm,
    AlgorithmChain,
    AlgorithmException
)
from .atk_test import AlgorithmTestCase
from .decorators import check_api_key, check_management_api_key, debug_only
from .utils.data_utils import (
    find_in_dict,
    text2int
)
from .utils.file_utils import (
    get_algorithm,
    get_chain_def,
    get_json_path,
    make_dir_if_not_exists
)


__all__ = [
    Algorithm, AlgorithmChain, AlgorithmException, AlgorithmTestCase,
    check_api_key, debug_only, get_algorithm, get_chain_def, get_json_path,
    make_dir_if_not_exists, find_in_dict, text2int, check_management_api_key
]

app.config.from_pyfile('atk_default_config.py')

app.config.from_envvar('ATK_CONFIG')

if 'ATK_MANAGEMENT_API_KEY' in os.environ:
    app.config['ATK_MANAGEMENT_API_KEY'] = os.environ['ATK_MANAGEMENT_API_KEY']

for handler in app.config['LOG_HANDLERS']:
    app.logger.addHandler(handler)
app.logger.setLevel(logging.DEBUG)

app.config['CORS_ORIGIN_WHITELIST'].append('https://mytiledriver.com')
app.config['CORS_ORIGIN_WHITELIST'].append('https://tdprocess.com')
app.config['TILEDRIVER_URL'] = 'https://app.tiledriver.com/'

from .views.home import home, main, chain_run_status
from .views.manage import manage

app.register_blueprint(home)
app.register_blueprint(manage)

app.jinja_loader.searchpath.insert(0, app.config['ATK_PATH'] + '/templates')

csrf = CSRFProtect(app)
csrf.exempt(main)
csrf.exempt(chain_run_status)


@app.context_processor
def inject_date():
    return dict(date=datetime.datetime.now())
