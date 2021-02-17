import logging

logging.basicConfig(format='%(asctime)s:%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG)

store = {}

# TODO fill in config
config = {
    'DEFAULT_WORKING_ROOT': ''
}
