
'''
    ****************
    Path Node module
    ****************

    The Path node module that makes calls to the Lumina Flow Manager
    in order to create either MPLS LSP or SR paths across the network.

'''

import json
from cerberus import Validator
from cloudify import ctx
from cloudify.decorators import operation
from cloudify.exceptions import NonRecoverableError
from cloudify_fm.common.client import (
    with_fm_client
)
from cloudify_fm.common.constants import (
    EP1_NODE_ID,
    EP2_NODE_ID,
    CONTRAINTS,
    WAYPOINT
)


@operation
@with_fm_client
def create(ctx, **kwargs):
    '''Cloudify create operation for a Path

       :param  args: arguments from the service template
       :param  kwargs: keyword arguments from the service template
       :rtype: None
    '''

    ctx.logger.debug("Start Create Path")
    ctx.logger.debug("ctx object: {}".format(
        json.dumps(ctx.node.properties, default=lambda o: o.__dict__,
                   sort_keys=True, indent=4)))
    fm_client = kwargs['fm_client']
    props = ctx.node.properties
    name = props.get('name')
    ep1_node_id = props.get(EP1_NODE_ID)
    ep2_node_id = props.get(EP2_NODE_ID)
    constraints = props.get(CONTRAINTS)
    path = Path(
        name=name,
        fm_client=fm_client,
        ep1_node_id=ep1_node_id,
        ep2_node_id=ep2_node_id,
        constraints=constraints)
    path.create()

    ctx.logger.debug("End Create Path")


@operation
def start(**kwargs):
    '''Cloudify start operation doesn't really do anything at the moment

       :param  kwargs: keyword arguments from the service template
       :rtype: None
    '''

    ctx.logger.debug("Path start")


@operation
def stop(**kwargs):
    '''Cloudify stop operation doesn't really do anything at the moment

       :param  kwargs: keyword arguments from the service template
       :rtype: None
    '''

    ctx.logger.debug("Path stop")


@operation
@with_fm_client
def delete(ctx, **kwargs):
    '''Cloudify delete operation uses the saved paths in the runtime
       properties to make delete path calls to flow manager

       :param  kwargs: keyword arguments from the service template
       :rtype: None
    '''

    ctx.logger.debug('Start Delete Path')
    ctx.logger.debug("ctx object: {}".format(
        json.dumps(ctx.node.properties, default=lambda o: o.__dict__,
                   sort_keys=True, indent=4)))
    props = ctx.node.properties
    fm_client = kwargs['fm_client']
    name = props.get('name')
    path = Path(
        name=name,
        fm_client=fm_client)
    path.delete()
    ctx.logger.debug('End Delete Path')


@operation
def refresh(**kwargs):
    '''Go get the latest information from the SDN Controller

       :param  kwargs: keyword arguments from the service template
       :rtype: None
    '''

    ctx.logger.info('Path refresh')


@operation
def creation_validation(**kwargs):
    '''Cloudify validation operation doesn't do anything at the moment.

       :param  kwargs: keyword arguments from the service template
       :rtype: None
    '''

    ctx.logger.info('Path validate')


class Path:
    def __init__(self, name, fm_client, ep1_node_id='', ep2_node_id='',
                 constraints=None, provider="sr"):
        self.name = name
        self.fm_client = fm_client
        self.ep1_node_id = ep1_node_id
        self.ep2_node_id = ep2_node_id
        self.endpoint1 = {'node': self.ep1_node_id}
        self.endpoint2 = {'node': self.ep2_node_id}
        self.constraints = constraints
        self.provider = provider
        self.constraints = {
            WAYPOINT: []
        }

        if constraints is not None:
            # self.constraints[WAYPOINT] = []
            order = 0
            for waypoint in constraints.get(WAYPOINT, []):
                self.constraints[WAYPOINT].append(
                    {'order': order, 'nodeid': waypoint}
                )
                order += 1

    def fm_mock_response(self):
        obj = {"path": [self.fm_payload()]}
        return json.dumps(obj, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def fm_payload(self):
        obj = {
            'name': self.name,
            'provider': self.provider,
            'endpoint1': self.endpoint1,
            'endpoint2': self.endpoint2,
            'constraints': self.constraints
        }
        return obj

    def create(self):
        schema = {
            'name': {'type': 'string',
                     'empty': False,
                     'required': True},
            # 'config': VALIDATION_SCHEMA_CONFIG,
            'ep1_node_id': {'type': 'string',
                            'empty': False,
                            'required': True},
            'ep2_node_id': {'type': 'string',
                            'empty': False,
                            'required': True},
            'provider': {'type': 'string',
                         'empty': False,
                         'allowed': ["sr"],
                         'required': True},
            'constraints': {'type': 'dict',
                            'empty': False,
                            'required': True},
        }
        v = Validator(schema, allow_unknown=True)
        if not v.validate(self.__dict__):
            raise NonRecoverableError(
                "Object schema not valid. Errors: {}".format(v.errors))

        data = self.fm_payload()
        ctx.logger.debug("data object: {}".format(data))
        response = self.fm_client.add_path(path=data)
        ctx.logger.debug(
            "Path {} {} response: {} {}".format('PUT',
                                                self.name,
                                                response['status_code'],
                                                response['content']))

        if response['status_code'] not in [200, 201]:
            raise NonRecoverableError(
                "Create Path {0} failed with response {1} {2}".format(
                    self.name,
                    response['status_code'],
                    response['content']))
        else:
            ctx.logger.info(
                "Create Path {0} successful: {1} {2}".format(
                    self.name,
                    response['status_code'],
                    response['content']))

    def delete(self):
        schema = {
            'name': {'type': 'string',
                     'empty': False,
                     'required': True}
        }
        v = Validator(schema, allow_unknown=True)
        if not v.validate(self.__dict__):
            raise NonRecoverableError("Object schema not valid")

        response = self.fm_client.delete_path(name=self.name)
        ctx.logger.debug(
            "Path {} {} response: {} {}".format('DELETE',
                                                self.name,
                                                response['status_code'],
                                                response['content']))
        if response['status_code'] != 200:
            raise NonRecoverableError(
                "Delete Path {0} failed with response {1} {2}".format(
                    self.name,
                    response['status_code'],
                    response['content']))
        else:
            ctx.logger.info(
                "Delete Path {} response successful: {} {}".format(
                    self.name,
                    response['status_code'],
                    response['content']))