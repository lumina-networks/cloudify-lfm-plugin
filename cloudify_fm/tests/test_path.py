
import json
import mock
import unittest

from mock import patch

from utils import (
    MockRequestsResponse,
    setup_ctx
)
from cloudify.state import current_ctx

from cloudify_fm.common.constants import (
    PATH_TYPE,
    CONTRAINTS,
    WAYPOINT,
    PROVIDER,
    NAME,
    EP1_NODE_ID,
    EP2_NODE_ID,
    RULES
)

from cloudify_fm import path


class PathTest(unittest.TestCase):
    def setUp(self):
        self.flowmanager_mock = mock.Mock()
        pass

    @patch('requests.get')
    @patch('requests.put')
    def test_create_path(self, mock_put, mock_get):

        # Path
        properties = {}
        props = {
            NAME: 'path_name',
            EP1_NODE_ID: 'openflow:101',
            EP2_NODE_ID: 'openflow:303',
            PROVIDER: 'sr',
            RULES: [],
            CONTRAINTS: {
                WAYPOINT: []
            }
        }
        properties.update(props)

        props = {
            CONTRAINTS: {
                WAYPOINT: ['openflow:102', 'openflow:103']
            },
        }
        properties.update(props)

        ctx = setup_ctx('path_name', properties, PATH_TYPE)
        ctx.instance.runtime_properties['node_type'] = PATH_TYPE

        try:
            ctx.logger.debug("properties: {}".format(properties))
            # controller returns a 201 response when creating a path
            put_resp = MockRequestsResponse()
            mock_put.status_code = 200
            mock_put.return_value = put_resp

            get_resp = MockRequestsResponse()
            get_resp.status_code = 200
            get_resp.content = json.dumps({'path': [{'name': 'path_name'}]})
            mock_get.side_effect = [get_resp]

            path.create(ctx)
            # check mock calls
            self.assertEquals(len(mock_put.mock_calls), 1)
            self.assertEquals(len(mock_get.mock_calls), 1)
            ctx.logger.info(
                "request_calls {}".format(len(mock_put.mock_calls)))

            pass

        finally:
            current_ctx.clear()


if __name__ == '__main__':
    unittest.main()
