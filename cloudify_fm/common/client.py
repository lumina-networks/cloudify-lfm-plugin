
import os
import json
from cerberus import Validator
from functools import wraps
from cloudify import ctx
from cloudify.exceptions import NonRecoverableError
from requests.exceptions import ConnectTimeout
from requests.exceptions import ConnectionError
from lfmcli.api import (
    FlowManagerClientException,
    Client
)
from constants import (
    SDN_CONFIG,
    VALIDATION_SCHEMA_CONFIG
)


class FlowManagerClient(object):
    '''FlowManagerClient class'''

    SDN_CONFIG_PATH_ENV_VAR = 'SDN_CONFIG_PATH'
    SDN_CONFIG_PATH_DEFAULT_PATH = '~/.lumina/sdn_config.json'

    def __init__(self, ctx):
        self.ctx = ctx
        self.cfg = self.get_config()
        self.fm = Client(config=self.cfg)

    def get_config(self):

        cfg = dict()

        default_location = os.path.expanduser(
            self.SDN_CONFIG_PATH_DEFAULT_PATH)
        config_path = os.getenv(self.SDN_CONFIG_PATH_ENV_VAR,
                                default_location)

        try:
            with open(config_path) as f:
                cfg = json.loads(f.read())[SDN_CONFIG]
        except IOError:
            cfg['protocol'] = 'http'  # https / http
            cfg['user'] = 'admin'
            cfg['password'] = 'admin'
            cfg['verify'] = False
            cfg['ip'] = '192.168.50.21'
            cfg['port'] = 8181  # 8443 / 8181
            # pass

        schema = VALIDATION_SCHEMA_CONFIG
        v = Validator(schema, allow_unknown=True)
        if not v.validate(cfg):
            raise NonRecoverableError(
                "Object schema not valid. Errors: {}".format(v.errors))

        return cfg


def with_fm_client(f):
    '''decorator to add exception handling'''

    @wraps(f)
    def wrapper(*args, **kw):
        kw['fm_client'] = FlowManagerClient(ctx).fm

        try:
            return f(*args, **kw)
        except ConnectTimeout, e:
            raise NonRecoverableError(
                "connect timeout occured: {0}".format(e))
        except ConnectionError, e:
            raise NonRecoverableError(
                "connection error occured: {0}".format(e))
        except FlowManagerClientException, e:
            raise NonRecoverableError(
                "Flow Manager Client error: {0}".format(e))

        return f(*args, **kw)

    return wrapper
