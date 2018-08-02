import requests
import uuid

DEFAULT_NODES = ["https://api.steemit.com", ]

class Client:

    def __init__(self, nodes=None, batch_mode=False):
        self.nodes = nodes or DEFAULT_NODES
        self.api_type = "condenser_api"
        self.queue = []

    def __getattr__(self, attr):
        def callable(*args, **kwargs):
            return self.request(attr, *args, **kwargs)
        return callable

    def __call__(self, *args, **kwargs):
        # This is not really thread-safe
        # multi-threaded environments shouldn't share client instances
        self.api_type = args[0]

        return self

    def pick_node(self):
        return self.nodes[0]

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
            params = args[1]

        data = {
            "jsonrpc": "2.0",
            "method": f"{self.api_type}.{method_name}",
            "params": params,
            "id": kwargs.get("request_id") or self.pick_id_for_request(),
        }

        return data

    def request(self, *args, **kwargs):

        if kwargs.get("batch_data"):
            # if that's a batch call, don't do any formatting on data.
            # since it's already formatted for the app base.
            data = kwargs.get("batch_data")
        else:
            data = self.get_rpc_request_body(args, kwargs)

        if kwargs.get("batch"):
            self.queue.append(data)
            return

        response = requests.post(
            self.pick_node(),
            json=data,
        ).json()

        return response

    def process_batch(self):
        try:
            resp = self.request(batch_data=self.queue)
        finally:
            # flush the queue in case if any error happens
            self.queue = None
        return resp
