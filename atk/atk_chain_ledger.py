from algorithm_toolkit.chain_ledger import ChainLedger

from atk import app


class AtkChainLedger(ChainLedger):

    def __init__(self, status_key):
        ChainLedger.__init__(self, status_key)
        self.store = app.config
