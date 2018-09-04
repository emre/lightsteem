
class RPCNodeException(Exception):
    def __init__(self, message, code=None, raw_body=None):
        super().__init__(message)
        self.code = code
        self.raw_body = raw_body


class StopOuterIteration(Exception):
    pass
