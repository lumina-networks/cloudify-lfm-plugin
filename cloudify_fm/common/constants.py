# # cloudify node properties
EP1_NODE_ID = 'ep1_node_id'
EP2_NODE_ID = 'ep2_node_id'
ENDPOINT1 = 'endpoint1'
ENDPOINT2 = 'endpoint2'
PATH_NAME = 'path_name'
CONTRAINTS = 'contraints'
NAME = 'name'
PROVIDER = 'provider'
RULES = 'rules'
SDN_CONFIG = 'sdn_config'
SEGMENTATION_ID = 'segmentation_id'
NETWORK_TYPE = 'network_type'
SWITCH_PORT = 'switch_port'
SWITCH_ID = 'switch_id'
CONSTRAINTS = 'constraints'
WAYPOINT = 'waypoint'
PROTOCOL_TYPE = 'protocol_type'

# # cloudify node types
ELINE_TYPE = 'sdn_controller.nodes.sdn.VL.ELine'
PATH_TYPE = 'sdn_controller.nodes.sdn.Path'
CP_TYPE = 'sdn_controller.nodes.sdn.CP'
EP1_TYPE = 'sdn_controller.nodes.sdn.CP.EP1'
EP2_TYPE = 'sdn_controller.nodes.sdn.CP.EP2'

CONNECTS_TO_TYPE = 'sdn_controller.relationships.ConnectsTo'

# VALIDATION_SCHEMA_CONFIG = {
#     'type': 'dict',
#     'empty': False,
#     'required': True,
#     'schema': {
#        'ip': {'type': 'string'},
#        'user': {'type': 'string'},
#        'password': {'type': 'string'},
#        'protocol': {'type': 'string'},
#        'port': {'type': ['integer', 'string']},
#        'verify': {'type': ['boolean', 'string']},
#     },
# }
VALIDATION_SCHEMA_CONFIG = {
    'ip': {'type': 'string'},
    'user': {'type': 'string'},
    'password': {'type': 'string'},
    'protocol': {'type': 'string'},
    'port': {'type': ['integer', 'string']},
    'verify': {'type': ['boolean', 'string']},
}