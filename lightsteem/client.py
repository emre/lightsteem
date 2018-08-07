import uuid

import requests
from requests.adapters import HTTPAdapter

DEFAULT_NODES = ["https://api.steemit.com", ]
MAX_RETRIES = 5


class Client:

    def __init__(self, nodes=None, max_retries=5,
                 connect_timeout=3, read_timeout=30):
        self.nodes = nodes or DEFAULT_NODES
        self.api_type = "condenser_api"
        self.queue = []
        self.max_retries = max_retries
        self.connect_timeout = connect_timeout
        self.read_timeout = read_timeout

        self.current_node = self.nodes[0]

    def __getattr__(self, attr):
        def callable(*args, **kwargs):
            return self.request(attr, *args, **kwargs)

        return callable

    def __call__(self, *args, **kwargs):
        # This is not really thread-safe
        # multi-threaded environments shouldn't share client instances
        self.api_type = args[0]

        return self

    def get_requests_session(self):
        session = requests.Session()
        adapter = HTTPAdapter(
            max_retries=self.max_retries
        )
        session.mount('https://', adapter)
        session.mount('http://', adapter)

        return session

    def next_node(self):
        return next(self.nodes)

    def pick_id_for_request(self):
        return str(uuid.uuid4())

    def get_rpc_request_body(self, args, kwargs):
        method_name = args[0]
        if len(args) == 1:
            # condenser_api expects an empty list
            # while other apis expects an empty dict if no arguments
            # sent by the user.
            params = [] if self.api_type == "condenser_api" else {}
        else:
            params = args[1:] if self.api_type == "condenser_api" else args[1]

        data = {
            "jsonrpc": "2.0",
            "method": f"{self.api_type}.{method_name}",
            "params": params,
            "id": kwargs.get("request_id") or self.pick_id_for_request(),
        }

        return data

    def request(self, *args, **kwargs):

        batch_data = kwargs.get("batch_data")
        if batch_data:
            # if that's a batch call, don't do any formatting on data.
            # since it's already formatted for the app base.
            data = batch_data
        else:
            data = self.get_rpc_request_body(args, kwargs)

        if kwargs.get("batch"):
            self.queue.append(data)
            return

        session = self.get_requests_session()
        response = session.post(
            self.current_node,
            json=data,
            timeout=(self.connect_timeout, self.read_timeout)
        ).json()

        response_dict = response["result"]
        if 'request_id' in kwargs and isinstance(response_dict, dict):
            response_dict.update({
                "request_id": response
            })

        return response_dict

    def process_batch(self):
        try:
            resp = self.request(batch_data=self.queue)
        finally:
            # flush the queue in case if any error happens
            self.queue = None
        return resp
