import logging
import os

from logging import Formatter, StreamHandler

ATK_PATH = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'test_project')
API_KEY = 'testkey'
PRESERVE_CONTEXT_ON_EXCEPTION = False
TESTING = True
SECRET_KEY = 'testsecret'
WTF_CSRF_ENABLED = False

dirname = os.path.dirname
handler = StreamHandler()
handler.setLevel(logging.WARNING)
handler.setFormatter(Formatter(
    '%(asctime)s %(levelname)s %(message)s [in %(pathname)s:%(lineno)d]'
))

LOG_HANDLERS = [handler, ]
CORS_ORIGIN_WHITELIST = ['http://localhost', ]
