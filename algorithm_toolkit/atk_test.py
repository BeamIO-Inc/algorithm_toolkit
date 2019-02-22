import unittest

from . import AlgorithmChain, app


class AlgorithmTestCase(unittest.TestCase):

    def setUp(self):
        self.params = {}
        path = app.config['ATK_PATH']
        test_chain = {
            'chain_name': 'test_chain',
            'algorithms': []
        }
        self.cl = AlgorithmChain(path, test_chain).ChainLedger('test')

    def check_metadata(self, key, value):
        return self.cl.get_from_metadata(key) == value

    def check_status(self, status):
        return app.config['test']['latest_msg'] == status
