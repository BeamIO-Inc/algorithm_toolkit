from algorithm_toolkit.algorithm import Algorithm

from atk import app


class AtkAlgorithm(Algorithm):

    def __init__(self):
        Algorithm.__init__(self)
        self.logger = app.logger
