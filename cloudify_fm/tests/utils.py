
from cloudify.mocks import MockCloudifyContext
from cloudify.state import current_ctx


class MockRequestsResponse:
    def __init__(self, status_code=200,
                 content='{"success":true,''"message":"success"}'):
        self.status_code = status_code
        self.content = content


def setup_ctx(name, props, type):
    '''setup a mock cloudify context'''

    properties = {
        type: {
            'name': name + '_name',
        },
        'rules': [],  # For security_group
    }
    properties.update(props)
    ctx = MockCloudifyContext(
        node_name=name + '_name',
        node_id='nodeid',
        properties=properties
    )

    current_ctx.set(ctx)
    ctx.instance.runtime_properties['node_type'] = type

    return ctx
