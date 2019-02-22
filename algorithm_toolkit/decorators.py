from functools import wraps

from flask import make_response


def check_api_key(request, key):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            api_key = None
            if request.form:
                api_key = request.form['api_key']
            else:
                api_key = request.args.get('api_key', None)

            if api_key != key or api_key is None:
                return make_response('API key wrong or missing', 401, {})

            rv = f(*args, **kwargs)
            return rv
        return decorated_function
    return decorator


def check_management_api_key(request, main_key, manage_key):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if manage_key is None or manage_key == '':
                return make_response('Management API key not set', 401, {})

            if main_key == manage_key:
                return make_response(
                    'Management API key must not be the '
                    'same as other API keys',
                    401,
                    {}
                )

            management_api_key = None
            if request.form:
                management_api_key = request.form['management_api_key']
            else:
                management_api_key = request.args.get(
                    'management_api_key', None)

            if management_api_key != manage_key or management_api_key is None:
                return make_response(
                    'Management API key wrong or missing', 401, {})

            rv = f(*args, **kwargs)
            return rv
        return decorated_function
    return decorator


def debug_only(config):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not config['DEBUG'] and not config['TESTING']:
                return make_response('This view is not accessible', 400, {})

            rv = f(*args, **kwargs)
            return rv
        return decorated_function
    return decorator
