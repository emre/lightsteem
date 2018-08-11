import unittest

import requests_mock

from lightsteem.client import Client

import lightsteem.exceptions


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

    def test_batch_rpc_calls(self):
        self.client.get_block(1, batch=True)
        self.client.get_block_header(2, batch=True)

        self.assertEqual(2, len(self.client.queue))
        self.assertEqual("condenser_api.get_block",
                         self.client.queue[0]["method"])
        self.assertEqual("condenser_api.get_block_header",
                         self.client.queue[1]["method"])

    def test_validate_response_rpc_error(self):
        resp = {
            'jsonrpc': '2.0',
            'error': {'code': -32000,
                      'message': "Parse Error:Couldn't parse uint64_t",
                      'data': ""},
            'id': 'f0acccf6-ebf6-4952-97da-89b248dfb0d0'
        }

        with self.assertRaises(lightsteem.exceptions.RPCNodeException):
            self.client.validate_response(resp)

    def test_validate_repsonse_batch_call(self):
        resp = [{'previous': '017d08b4416e4ea77d5f582ddf4fc06bcf888eef',
                 'timestamp': '2018-08-11T10:25:00',
                 'witness': 'thecryptodrive',
                 'transaction_merkle_root': '23676c4bdc0074489392892bcf'
                                            '1a5b779f280c8e',
                 'extensions': []},
                {'previous': '017d08b55aa2520bc3a777eaec77e872bb6b8943',
                 'timestamp': '2018-08-11T10:25:03', 'witness': 'drakos',
                 'transaction_merkle_root': 'a4be1913157a1be7e4ab'
                                            'c36a22ffde1c110e683c',
                 'extensions': []}]
        validated_resp = self.client.validate_response(resp)

        self.assertEqual(True, isinstance(validated_resp, list))
        self.assertEqual(2, len(validated_resp))

    def test_validate_repsonse_batch_call_one_error_one_fail(self):
        resp = [{'previous': '017d08b4416e4ea77d5f582ddf4fc06bcf888eef',
                 'timestamp': '2018-08-11T10:25:00',
                 'witness': 'thecryptodrive',
                 'transaction_merkle_root': '23676c4bdc0074489392892bcf'
                                            '1a5b779f280c8e',
                 'extensions': []},
                {
                    'jsonrpc': '2.0',
                    'error': {'code': -32000,
                              'message': "Parse Error:Couldn't parse uint64_t",
                              'data': ""},
                    'id': 'f0acccf6-ebf6-4952-97da-89b248dfb0d0'
                }]

        with self.assertRaises(lightsteem.exceptions.RPCNodeException):
            self.client.validate_response(resp)

    def test_process_batch(self):
        with requests_mock.mock() as m:
            m.post(TestClient.NODES[0], json={"result": {}})
            self.client.get_block(12323, batch=True)
            self.client.get_block(1234, batch=True)

            self.assertEqual(2, len(self.client.queue))
            self.client.process_batch()
            self.assertEqual(0, len(self.client.queue))


if __name__ == '__main__':
    unittest.main()
