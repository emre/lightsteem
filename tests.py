import unittest

import requests_mock

from lightsteem.client import Client


class TestClient(unittest.TestCase):
    NODES = ["https://api.steemit.com"]

    def setUp(self):
        self.client = Client(nodes=TestClient.NODES)

    def test_dynamic_api_selection(self):
        self.client('tags_api')
        self.assertEqual('tags_api', self.client.api_type)

    def test_default_api_selection(self):
        with requests_mock.mock() as m:
            m.post(TestClient.NODES[0], json={"result": {}})
            self.client.get_block(12323)
            self.assertEqual('condenser_api', self.client.api_type)

    def test_get_rpc_request_body_condenser_multiple_args(self):
        self.client('condenser_api')
        rpc_body = self.client.get_rpc_request_body(
            ('get_account_bandwidth', 'steemit', 'forum'),
            {'batch': True, 'id': 1}
        )

        self.assertEqual(
            "condenser_api.get_account_bandwidth",
            rpc_body["method"],
        )

        self.assertEqual(
            ('steemit', 'forum'),
            rpc_body["params"],
        )

    def test_get_rpc_request_body_condenser_single_arg(self):
        self.client('condenser_api')
        rpc_body = self.client.get_rpc_request_body(
            ('get_block', '123'),
            {},
        )

        self.assertEqual(
            ('123',),
            rpc_body["params"],
        )

    def test_get_rpc_request_body_non_condenser_api_with_arg(self):
        self.client('database_api')
        rpc_body = self.client.get_rpc_request_body(
            ('list_vesting_delegations',
             {"start": [None], "limit": 20, "order": "by_delegation"}),
            {},
            )

        self.assertEqual(
            {'start': [None], 'limit': 20, 'order': 'by_delegation'},
            rpc_body["params"]
        )

    def test_get_rpc_request_body_non_condenser_api_no_arg(self):
        self.client('database_api')
        rpc_body = self.client.get_rpc_request_body(
            ('get_active_witnesses',),
            {},
        )

        self.assertEqual({}, rpc_body["params"])

    def test_get_rpc_request_body_condenser_api_no_arg(self):
        rpc_body = self.client.get_rpc_request_body(
            ('get_active_witnesses',),
            {},
        )

        self.assertEqual([], rpc_body["params"])


if __name__ == '__main__':
    unittest.main()
