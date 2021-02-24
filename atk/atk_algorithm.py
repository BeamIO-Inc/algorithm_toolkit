from algorithm_toolkit.algorithm import Algorithm

from atk import app


class AtkAlgorithm(Algorithm):

    def __init__(self, cl, params, **kwargs):
        super(AtkAlgorithm, self).__init__(cl, params, **kwargs)
        self.logger = app.logger
