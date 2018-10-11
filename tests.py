import datetime
import json
import unittest
import pytz

import requests_mock

import lightsteem.exceptions
from lightsteem.client import Client
from lightsteem.helpers.account import Account
from lightsteem.helpers.event_listener import EventListener
from lightsteem.helpers.amount import Amount

from tests_mockdata import mock_block_25926363, mock_dygp_result, \
    mock_block_25926364, mock_history, mock_history_max_index


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

    def test_vp_with_hf20(self):
        last_vote_time = datetime.datetime.utcnow() - datetime.timedelta(
            hours=24)

        utc = pytz.timezone('UTC')
        last_vote_time = utc.localize(last_vote_time)

        result = {
            'voting_manabar': {
                'current_mana': 7900,
                'last_update_time': int(last_vote_time.timestamp())
            }
        }

        with requests_mock.mock() as m:
            m.post(TestClient.NODES[0], json={"result": [result]})
            account = self.client.account('emrebeyler')

        self.assertEqual(99, account.vp())

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

    def test_rc(self):

        def match_get_accounts(request):
            method = json.loads(request.text)["method"]
            return method == "condenser_api.get_accounts"

        def match_find_rc_accounts(request):
            method = json.loads(request.text)["method"]
            return method == "rc_api.find_rc_accounts"

        last_update_time = datetime.datetime.utcnow() - datetime.timedelta(
            hours=24)
        last_update_timestamp = last_update_time.replace(
            tzinfo=datetime.timezone.utc).timestamp()

        result = {
            "rc_accounts": [{
                'account': 'emrebeyler',
                'rc_manabar': {
                    'current_mana': '750',
                    'last_update_time': last_update_timestamp
                },
                'max_rc_creation_adjustment': {
                    'amount': '1029141630',
                    'precision': 6,
                    'nai': '@@000000037'
                },
                'max_rc': '1000'
            }
            ]}

        with requests_mock.mock() as m:
            m.post(
                TestClient.NODES[0],
                json={"result": [{"foo": "bar"}]},
                additional_matcher=match_get_accounts)
            m.post(
                TestClient.NODES[0],
                json={"result": result},
                additional_matcher=match_find_rc_accounts)

            self.assertEqual(float(95), self.client.account(
                'emrebeyler').rc())

            self.assertEqual(float(75), self.client.account(
                'emrebeyler').rc(consider_regeneration=False))

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


class TestEventListener(unittest.TestCase):

    def setUp(self):
        self.client = Client(nodes=TestClient.NODES)

    def test_filtering(self):
        def match_dygp(request):
            params = json.loads(request.text)
            return 'get_dynamic_global_properties' in params["method"]

        def match_block_25926363(request):
            return '25926363' in request.text

        def match_block_25926364(request):
            return '25926364' in request.text

        with requests_mock.mock() as m:
            m.post(TestClient.NODES[0], json=mock_dygp_result,
                   additional_matcher=match_dygp)
            m.post(TestClient.NODES[0], json=mock_block_25926363,
                   additional_matcher=match_block_25926363)
            m.post(TestClient.NODES[0], json=mock_block_25926364,
                   additional_matcher=match_block_25926364)
            events = EventListener(
                self.client,
                start_block=25926363,
                end_block=25926364)

            # test filter
            ops = list(
                events.on('producer_reward', {"producer": "emrebeyler"}))
            self.assertEqual(1, len(ops))
            self.assertEqual("emrebeyler", ops[0]["op"][1]["producer"])

            # test condition
            ops = list(events.on(
                'comment', condition=lambda x: x["author"] == "jennybeans"))

            self.assertEqual(1, len(ops))
            self.assertEqual("jennybeans", ops[0]["op"][1]["author"])

            # test multiple filtering
            ops = list(events.on(
                ['withdraw_vesting_route', 'producer_reward']))
            self.assertEqual(2, len(ops))

            # test filter and condition together
            ops = list(events.on(
                ['transfer_to_vesting'],
                {'from': 'manimani'},
                condition=lambda x: x["to"] not in ["kstop1", "nodaji"])
            )

            self.assertEqual(0, len(ops))

            ops = list(events.on(
                ['transfer_to_vesting'],
                {'from': 'manimani'},
                condition=lambda x: x["to"] == "kstop1")
            )

            self.assertEqual(1, len(ops))


class TestAmountHelper(unittest.TestCase):

    def setUp(self):
        self.client = Client(nodes=TestClient.NODES)

    def test_standard_input(self):
        amount = Amount('1.942 SBD')
        self.assertEqual(float(1.942), float(amount.amount))
        self.assertEqual('SBD', amount.symbol)

    def test_asset_dict_input(self):
        amount = Amount.from_asset({
            'amount': '1029141630',
            'precision': 6,
            'nai': '@@000000037'
        })
        self.assertEqual(float('1029.141630'), float(amount.amount))
        self.assertEqual('VESTS', amount.symbol)

    def test_asset_dict_output(self):
        amount = Amount('0.010 STEEM')
        asset_dict = amount.asset
        self.assertEqual({
            "amount": "10",
            "precision": 3,
            "nai": "@@000000021"
        }, asset_dict)


if __name__ == '__main__':
    unittest.main()
