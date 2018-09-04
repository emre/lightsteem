import unittest
import datetime
import json

import requests_mock

from lightsteem.client import Client
from lightsteem.helpers.account import Account

import lightsteem.exceptions

mock_history_max_index = [[3, {
    'trx_id': '0000000000000000000000000000000000000000', 'block': 25641925,
    'trx_in_block': 4294967295, 'op_in_trx': 0, 'virtual_op': 7,
    'timestamp': '2018-09-03T17:24:48', 'op': ['fill_vesting_withdraw',
                                               {'from_account': 'hellosteem',
                                                'to_account': 'hellosteem',
                                                'withdrawn': '187.37083 VESTS',
                                                'deposited': '0.092 STEEM'}]}]]


mock_history = [[1,
                 {'trx_id': '985bb048e2068cdb311829ad3d76f4dc2947811a',
                  'block': 25153549, 'trx_in_block': 1, 'op_in_trx': 0,
                  'virtual_op': 0, 'timestamp': '2018-08-17T18:12:57',
                  'op': ['transfer',
                         {'from': 'hellosteem', 'to': 'sekhmet',
                          'amount': '0.001 STEEM', 'memo': ''}]}],
                [2,
                 {'trx_id': 'bb1b6ddf13bcffe5bba8d55c3c37a5c672ff7309',
                  'block': 25153549, 'trx_in_block': 0, 'op_in_trx': 0,
                  'virtual_op': 0, 'timestamp': '2018-08-17T18:12:57',
                  'op': ['limit_order_create',
                         {'owner': 'hellosteem', 'orderid': 1534529209,
                          'amount_to_sell': '0.100 STEEM',
                          'min_to_receive': '100.000 SBD',
                          'fill_or_kill': False,
                          'expiration': '1969-12-31T23:59:59'}]}],
                [3,
                 {'trx_id': '851c9a4ec9a32855b9981ea6b97c7911abaf8996',
                  'block': 25153418, 'trx_in_block': 0, 'op_in_trx': 0,
                  'virtual_op': 0, 'timestamp': '2018-08-17T18:06:24',
                  'op': ['transfer',
                         {'from': 'hellosteem', 'to': 'fabien',
                          'amount': '0.001 STEEM', 'memo': 'Test'}]}]]


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


class TestAccountHelper(unittest.TestCase):

    def setUp(self):
        self.client = Client(nodes=TestClient.NODES)

    def test_vp(self):
        last_vote_time = datetime.datetime.utcnow() - datetime.timedelta(
            hours=24)

        result = {
            "last_vote_time": last_vote_time.strftime("%Y-%m-%dT%H:%M:%S"),
            "voting_power": 7900,
        }
        with requests_mock.mock() as m:
            m.post(TestClient.NODES[0], json={"result": [result]})
            account = self.client.account('emrebeyler')

        self.assertEqual(99.0, account.vp())

    def test_reputation(self):
        reputation_sample = '74765490672156'  # 68.86
        with requests_mock.mock() as m:
            m.post(
                TestClient.NODES[0],
                json={"result": [{"reputation": reputation_sample}]})
            account = self.client.account('emrebeyler')

        self.assertEqual(68.86, account.reputation())

    def test_account_history_simple(self):
        def match_max_index_request(request):
            params = json.loads(request.text)["params"]
            return params[1] == -1

        def match_non_max_index_request(request):
            params = json.loads(request.text)["params"]
            return params[1] != -1

        with requests_mock.mock() as m:

            m.post(TestClient.NODES[0], json={
                "result": mock_history_max_index},
                   additional_matcher=match_max_index_request)
            m.post(TestClient.NODES[0], json={"result": mock_history},
                   additional_matcher=match_non_max_index_request)

            account = Account(self.client)
            history = list(account.history(account="hellosteem"))
            self.assertEqual(3, len(history))

            # check filter
            history = list(
                account.history(account="hellosteem", filter=["transfer"]))

            self.assertEqual(2, len(history))

            # check exclude
            history = list(
                account.history(account="hellosteem", exclude=["transfer"]))

            self.assertEqual(1, len(history))

            # check only_operation_data

            history = list(
                account.history(
                    account="hellosteem", only_operation_data=False))

            self.assertEqual(3, history[0][0])


if __name__ == '__main__':
    unittest.main()
