
'''
    *****************
    ELine Node module
    *****************

    The ELine node module that makes calls to the Lumina Flow Manager
    in order to create point to point ethernet services (i.e. E-Lines).

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
    ENDPOINT1,
    ENDPOINT2,
    PATH_NAME,
    SEGMENTATION_ID,
    NETWORK_TYPE,
    SWITCH_PORT,
    SWITCH_ID,
    PROTOCOL_TYPE
)


@operation
@with_fm_client
def create(ctx, **kwargs):
    '''Cloudify create operation for an ELine.  This assumes the
       FP node called us and pre-populated all our connection points

       :param  args: arguments from the service template
       :param  kwargs: keyword arguments from the service template
       :rtype: None
    '''

    ctx.logger.info("ELine create")
    ctx.logger.debug("ctx object: {}".format(
        json.dumps(ctx.node.properties, default=lambda o: o.__dict__,
                   sort_keys=True, indent=4)))
    fm_client = kwargs['fm_client']
    props = ctx.node.properties
    path_name = props.get(PATH_NAME)
    endpoint1 = props.get(ENDPOINT1)
    endpoint2 = props.get(ENDPOINT2)
    protocol_type = props.get(PROTOCOL_TYPE)
    name = props.get('name')
    eline = Eline(name=name,
                  fm_client=fm_client,
                  path_name=path_name,
                  endpoint1=endpoint1,
                  endpoint2=endpoint2,
                  protocol_type=protocol_type)
    eline.create()
    ctx.logger.debug("End Create Eline")


@operation
def start(**kwargs):
    '''Cloudify start operation doesn't really do anything at the moment

       :param  kwargs: keyword arguments from the service template
       :rtype: None
    '''

    # Could have something to turn on the service here
    ctx = kwargs['ctx']
    ctx.logger.info("ELine start")


@operation
def stop(**kwargs):
    '''Cloudify stop operation doesn't really do anything at the moment

       :param  kwargs: keyword arguments from the service template
       :rtype: None
    '''

    ctx = kwargs['ctx']
    ctx.logger.info("ELine stop")


@operation
@with_fm_client
def delete(ctx, **kwargs):
    '''Cloudify delete operation uses the saved paths in the runtime
       properties to make delete path calls to flow manager

       :param  kwargs: keyword arguments from the service template
       :rtype: None
    '''

    ctx.logger.debug('Start Delete Eline')
    ctx.logger.debug("ctx object: {}".format(
        json.dumps(ctx.node.properties, default=lambda o: o.__dict__,
                   sort_keys=True, indent=4)))

    props = ctx.node.properties
    name = props.get('name')
    fm_client = kwargs['fm_client']
    eline = Eline(name=name,
                  fm_client=fm_client)
    eline.delete()
    ctx.logger.debug('End Delete Eline')


@operation
def refresh(**kwargs):
    '''Go get the latest information from the SDN Controller

       :param  kwargs: keyword arguments from the service template
       :rtype: None
    '''
    ctx.logger.info("ELine refresh")


@operation
def creation_validation(**kwargs):
    '''Cloudify validation operation doesn't do anything at the moment.
       Could probably validate the nodes here rather than waiting until
       the create operation where we build the forwarding path dict

       :param  kwargs: keyword arguments from the service template
       :rtype: None
    '''
    ctx.logger.info("Eline validate")


class Eline:
    def __init__(self, name, fm_client, path_name='', endpoint1=None,
                 endpoint2=None, protocol_type=''):
        self.name = name
        self.fm_client = fm_client
        self.path_name = path_name
        self.endpoint1 = endpoint1
        self.endpoint2 = endpoint2
        if endpoint1 is not None:
            self.ep1_switch_id = endpoint1[SWITCH_ID]
            self.ep1_switch_port = endpoint1[SWITCH_PORT]
            self.ep1_network_type = endpoint1[NETWORK_TYPE]
            self.ep1_segmentation_id = endpoint1[SEGMENTATION_ID]
        if endpoint2 is not None:
            self.ep2_switch_id = endpoint2[SWITCH_ID]
            self.ep2_switch_port = endpoint2[SWITCH_PORT]
            self.ep2_network_type = endpoint2[NETWORK_TYPE]
            self.ep2_segmentation_id = endpoint2[SEGMENTATION_ID]
        self.protocol_type = protocol_type
        self.ep1_order = 2
        self.ep1_name = 0  # needs a key name, for single match it's not needed
        self.ep2_order = 2
        self.ep2_name = 0  # needs a key name, for single match it's not needed

    def vlan_match(self, ep_network_type, segmentation_id):
        return {
            ep_network_type + '-id': {
                ep_network_type + '-id-present': True,
                ep_network_type + '-id': segmentation_id  # 1804
            }
        }

    def ethernet_match(self, ep_network_type, protocol_type):
        map = {'ip': '2048', 'arp': '2054', 'ipv6': '34525',
               'ipx': '33079', 'mpls': '34887', 'mmpls': '34888',
               'ppoed': '34915', 'pppoes': '34916'}

        return {
            ep_network_type + '-type': {
                'type': map[protocol_type]  # 2054  # 2048 / 2054
            }
        }

    def endpoint(self,
                 ep_switch_id,
                 ep_switch_port,
                 ep_network_type,
                 ep_segmentation_id,
                 order,
                 name,
                 protocol_type):
        port = {}
        match = {}

        if ep_network_type == "vlan":
            port = ep_switch_port
            match = self.vlan_match(
                ep_network_type,
                ep_segmentation_id)

        if ep_network_type == "ethernet":
            port = ep_switch_id + ":" + ep_switch_port
            match = self.ethernet_match(
                ep_network_type,
                protocol_type)

        ep = {}
        props = {
            'egress': {
                'action': [
                    {
                        'order': order + 1,  # starts at 3
                        'output-action': {
                            'output-node-connector': ep_switch_port
                            # "13"
                        }
                    }
                ]
            }
        }
        ep.update(props)
        props = {
            'matches': [
                {
                    'name': str(name),
                    'match': {
                        ep_network_type + '-match': match,
                        'in-port': port  # "13"
                    }
                }
            ]
        }
        ep.update(props)

        # ethernet does not have ingress
        if ep_network_type == "vlan":
            props = {
                'ingress': {
                    'action': [
                        {
                            'order': order,  # starts at 2
                            'set-field': {
                                ep_network_type + '-match': match
                            }
                        }
                    ]
                }
            }
            ep.update(props)

        return ep

    def fm_mock_response(self):
        obj = {"eline": [self.fm_payload()]}
        return json.dumps(obj, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def fm_payload(self):
        obj = {
            'name': self.name,
            'path-name': self.path_name,
            'endpoint1': self.endpoint(self.ep1_switch_id,
                                       self.ep1_switch_port,
                                       self.ep1_network_type,
                                       self.ep1_segmentation_id,
                                       self.ep1_order,
                                       self.ep1_name,
                                       self.protocol_type),
            'endpoint2': self.endpoint(self.ep2_switch_id,
                                       self.ep2_switch_port,
                                       self.ep2_network_type,
                                       self.ep2_segmentation_id,
                                       self.ep2_order,
                                       self.ep2_name,
                                       self.protocol_type)
        }
        return obj

    def create(self):
        schema = {
            'name': {'type': 'string',
                     'empty': False,
                     'required': True},
            'ep1_switch_id': {'type': 'string',
                              'empty': False,
                              'required': True},
            'ep1_switch_port': {'type': 'string',
                                'empty': False,
                                'required': True},
            'ep1_network_type': {'type': 'string',
                                 'empty': False,
                                 'required': True},
            'ep1_segmentation_id': {'type': ['string', 'integer'],
                                    'empty': False,
                                    'required': True},
            'ep2_switch_id': {'type': 'string',
                              'empty': False,
                              'required': True},
            'ep2_switch_port': {'type': 'string',
                                'empty': False,
                                'required': True},
            'ep2_network_type': {'type': 'string',
                                 'empty': False,
                                 'required': True},
            'ep2_segmentation_id': {'type': ['string', 'integer'],
                                    'empty': False,
                                    'required': True},
        }
        v = Validator(schema, allow_unknown=True)
        if not v.validate(self.__dict__):
            raise NonRecoverableError(
                "Object schema not valid. Errors: {}".format(v.errors))

        data = self.fm_payload()
        ctx.logger.debug("data object: {}".format(data))

        # ethernet create twice arp + ip

        # vlan create once
        response = self.fm_client.add_eline(eline=data)

        ctx.logger.info(
            "Eline {} {} response: {} {}".format('PUT',
                                                 self.name,
                                                 response['status_code'],
                                                 response['content']))
        if response['status_code'] not in [200, 201]:
            raise NonRecoverableError(
                "Create ELine {0} failed with response {1} {2}".format(
                    self.name,
                    response['status_code'],
                    response['content']))
        else:
            ctx.logger.info(
                "Create ELine {0} successful: {1} {2}".format(
                    self.name,
                    response['status_code'],
                    response['content']))

    def delete(self):
        schema = {
            'name': {'type': 'string',
                     'empty': False,
                     'required': True},
        }
        v = Validator(schema, allow_unknown=True)
        if not v.validate(self.__dict__):
            raise NonRecoverableError("Object schema not valid")

        response = self.fm_client.delete_eline(name=self.name)

        if response['status_code'] != 200:
            ctx.logger.info(
                "Deletion of eline {0} failed: {1} {2}".format(
                    self.name,
                    response['status_code'],
                    response['content']))
        else:
            ctx.logger.info(
                "Eline {} response: {} {}".format(
                    self.name,
                    response['status_code'],
                    response['content']))