from __future__ import division

import json
import re
import logging

import numpy as np

from algorithm_toolkit.algorithm_exception import AlgorithmException


class Algorithm:

    def __init__(self, cl=None, params=None, **kwargs):
        self.logger = logging.getLogger('algorithm_toolkit')
        self.name = None
        self.errors = []
        self.params = params
        self.cl = cl

    def set_up(self, name, json_path):
        self.name = name

        with open(json_path) as json_file:
            definition = json.load(json_file)

        if self.check_params(definition):
            return self.run()
        else:
            self.raise_parameter_errors(self.errors)

    def custom_check(self, val, val2, check):
        if check == 'greaterthan' and val <= val2:
            return False
        elif check == 'lessthan' and val >= val2:
            return False
        else:
            return True

    def add_error_message(self, p, err):
        self.errors.append({
            "parameter": p,
            "error": err
        })

    def check_param(self, p, required, is_valid):
        p_type = p['data_type'].lower()
        params = self.params

        """
        Data type validation
        """
        if required:
            if p['name'] not in params:
                self.add_error_message(p['name'], 'Parameter missing')
                is_valid = False

        if p_type == 'string' and type(params[p['name']]) != str:
            try:
                str(params[p['name']])
            except ValueError:  # pragma: no cover
                self.add_error_message(p['name'], 'Not a valid string')
                is_valid = False
        elif p_type == 'integer' and type(params[p['name']]) != int:
            try:
                params[p['name']] = int(params[p['name']])
            except ValueError:
                if not required and params[p['name']] == '':
                    pass
                else:
                    self.add_error_message(p['name'], 'Not a valid integer')
                    is_valid = False
        elif p_type == 'float' and type(params[p['name']]) != float:
            try:
                params[p['name']] = float(params[p['name']])
            except ValueError:
                if not required and params[p['name']] == '':
                    pass
                else:
                    self.add_error_message(p['name'], 'Not a valid float')
                    is_valid = False
        elif p_type == 'array' and type(
                params[p['name']]) != list and type(
                params[p['name']]) != np.ndarray:
            try:
                if params[p['name']][0] == '[':
                    [item for item in params[p['name']][1:-1].split(",")]
                else:
                    [item for item in params[p['name']].split(",")]
            except (ValueError, TypeError):
                self.add_error_message(p['name'], 'Not a valid array')
                is_valid = False

        """
        Parameter value validation: numeric parameters
        """
        if is_valid and (p_type == 'integer' or p_type == 'float'):
            if 'min_value' in p and p['min_value']:
                if params[p['name']] < p['min_value']:
                    self.add_error_message(p['name'], 'Value too small')
                    is_valid = False
            if 'max_value' in p and p['max_value']:
                if params[p['name']] > p['max_value']:
                    self.add_error_message(p['name'], 'Value too large')
                    is_valid = False
            if 'custom_validation' in p:
                p_cv = p['custom_validation']
                if p_cv:
                    p_cv = p_cv.lower().replace(' ', '')
                    if (
                            p_cv[:11] == 'greaterthan' or
                            p_cv[:8] == 'lessthan'
                    ):
                        p_check = p_cv.split('.')[0]
                        p_param = params[p_cv.split('.')[1]]
                        if p_type == 'integer':
                            p_param = int(p_param)
                        else:
                            p_param = float(p_param)
                        if not self.custom_check(
                                params[p['name']], p_param, p_check):
                            if p_check == 'greaterthan':
                                self.add_error_message(
                                    p['name'],
                                    'Value must be greater than ' + str(
                                        p_param)
                                )
                            else:
                                self.add_error_message(
                                    p['name'],
                                    'Value must be less than ' + str(
                                        p_param)
                                )
                            is_valid = False
                if p_type == 'integer':
                    if p_cv == 'evenonly' and params[p['name']] % 2 != 0:
                        self.add_error_message(
                            p['name'], 'Value must be an even number')
                        is_valid = False
                    elif p_cv == 'oddonly' and params[p['name']] % 2 == 0:
                        self.add_error_message(
                            p['name'], 'Value must be an odd number')
                        is_valid = False

        """
        Parameter value validation: value in list
        """
        if 'parameter_choices' in p:
            p_c = p['parameter_choices']
            if is_valid and p_c is not None:
                if len(p_c) > 0 and params[p['name']] not in p_c:
                    self.add_error_message(
                        p['name'],
                        'Value not in list of valid choices: ' + str(
                            p_c
                        )
                    )
                    is_valid = False

        """
        Parameter value validation: Regular Expression
        """
        if 'custom_validation' in p:
            p_cv = p['custom_validation']
            if is_valid and p_cv and p_cv[0] == '^':
                if not re.match(p_cv, params[p['name']]):
                    self.add_error_message(
                        p['name'],
                        'Value does not match expression: "' + p_cv + '"'
                    )
                    is_valid = False

        return is_valid

    def check_params(self, definition):
        rps = definition['required_parameters']
        ops = definition['optional_parameters']
        is_valid = True
        for rp in rps:
            try:
                is_valid = self.check_param(rp, True, is_valid)
            except Exception as e:
                if hasattr(e, 'message'):
                    msg = e.message
                else:
                    msg = e.args[0]

                self.add_error_message(rp['name'], msg)
                is_valid = False

        for op in ops:
            if op['name'] in self.params:
                if self.params[op['name']] != '' and self.params[op['name']] is not None:
                    try:
                        is_valid = self.check_param(op, False, is_valid)
                    except Exception as e:
                        if hasattr(e, 'message'):
                            msg = e.message
                        else:
                            msg = e.args[0]

                        self.add_error_message(op['name'], msg)
                        is_valid = False
                else:
                    del self.params[op['name']]

        return is_valid

    def run(self):  # pragma: no cover
        pass

    def raise_parameter_errors(self, err):
        raise ValueError(err)

    def raise_client_error(self, err):
        raise AlgorithmException(err)