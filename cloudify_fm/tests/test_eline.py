
import mock
import unittest
from mock import patch
from utils import (
    MockRequestsResponse,
    setup_ctx
)
from cloudify.state import current_ctx

from cloudify_fm.common.constants import (
    ELINE_TYPE,
    NAME,
    PATH_NAME,
    ENDPOINT1,
    ENDPOINT2,
    PROTOCOL_TYPE,
)

from cloudify_fm import eline
import json


class ElineTest(unittest.TestCase):
    def setUp(self):
        self.flowmanager_mock = mock.Mock()
        pass

    # @patch('cloudify_fm.common.fm_client_s.FMConnection.api')
    # @patch('requests.delete')
    @patch('requests.delete')
    def test_delete_eline(self, mock_delete):  # mock_get,
        properties = {}
        props = {
            NAME: 'eline_name',
            PATH_NAME: 'path_name',
        }
        properties.update(props)
        ctx = setup_ctx('eline_name', properties, ELINE_TYPE)
        try:
            # controller returns a 201 response when deleting an eline
            put_resp = MockRequestsResponse()
            mock_delete.status_code = 201
            mock_delete.return_value = put_resp

            eline.delete(ctx)
            self.assertEquals(len(mock_delete.mock_calls), 1)

            ctx.logger.info(
                "request_calls {}".format(len(mock_delete.mock_calls)))
            pass

        finally:
            current_ctx.clear()

    @patch('requests.get')
    @patch('requests.put')
    def test_create_eline_vlan(self, mock_put, mock_get):

        # Eline
        properties = {}
        props = {
            NAME: 'eline_name',
            PATH_NAME: 'path_name',
            ENDPOINT1: {
                'network_type': 'vlan',
                'switch_id': 'openflow:101',
                'switch_port': '3',
                'segmentation_id': 100
            },
            ENDPOINT2: {
                'network_type': 'vlan',
                'switch_id': 'openflow:303',
                'switch_port': '3',
                'segmentation_id': 100  # range: 0 - 4094
            },
            PROTOCOL_TYPE: ''
        }
        properties.update(props)

        ctx = setup_ctx('eline_name', properties, ELINE_TYPE)

        try:
            ctx.logger.debug("properties: {}".format(properties))
            put_resp = MockRequestsResponse()
            mock_put.status_code = 200
            mock_put.return_value = put_resp

            get_resp = MockRequestsResponse()
            get_resp.status_code = 200
            get_resp.content = json.dumps({'eline': [{'name': 'eline_name'}]})
            mock_get.side_effect = [get_resp]

            eline.create(ctx)

            self.assertEquals(len(mock_put.mock_calls), 1)
            self.assertEquals(len(mock_get.mock_calls), 1)

            ctx.logger.info(
                "request_calls {}".format(len(mock_put.mock_calls)))

            pass

        finally:
            current_ctx.clear()

    @patch('requests.get')
    @patch('requests.put')
    def test_create_eline_ethernet(self, mock_put, mock_get):

        # Eline
        properties = {}
        props = {
            NAME: 'eline_name',
            PATH_NAME: 'path_name',
            ENDPOINT1: {
                'network_type': 'ethernet',
                'switch_id': 'openflow:101',
                'switch_port': '3',
                'segmentation_id': 100
            },
            ENDPOINT2: {
                'network_type': 'ethernet',
                'switch_id': 'openflow:303',
                'switch_port': '3',
                'segmentation_id': 100  # range: 0 - 4094
            },
            PROTOCOL_TYPE: ''
        }
        properties.update(props)

        try:

            # create ip eline 2048
            name = 'eline_name_ip'
            properties[NAME] = 'eline_name_ip'
            properties[PROTOCOL_TYPE] = 'ip'

            put_resp = MockRequestsResponse()
            mock_put.status_code = 200
            mock_put.return_value = put_resp

            get_resp = MockRequestsResponse()
            get_resp.status_code = 200
            get_resp.content = json.dumps({'eline': [{NAME: name}]})
            mock_get.side_effect = [get_resp]

            ctx = setup_ctx(name, properties, ELINE_TYPE)
            ctx.logger.debug("eline properties: {}".format(properties))
            eline.create(ctx)

            # create arp eline 2056
            name = 'eline_name_arp'
            properties[NAME] = name
            properties[PROTOCOL_TYPE] = 'arp'

            get_resp.content = json.dumps({'eline': [{NAME: name}]})
            mock_get.side_effect = [get_resp]

            ctx = setup_ctx(name, properties, ELINE_TYPE)
            ctx.logger.debug("eline properties: {}".format(properties))
            eline.create(ctx)

            self.assertEquals(len(mock_put.mock_calls), 2)
            self.assertEquals(len(mock_get.mock_calls), 2)

            ctx.logger.info(
                "request_calls {}".format(len(mock_put.mock_calls)))

            pass

        finally:
            current_ctx.clear()


if __name__ == '__main__':
    unittest.main()