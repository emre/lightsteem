import time


class TransactionListener:

    def __init__(self, client, blockchain_mode=None,
                 start_block=None, end_block=None,
                 only_ops=True):
        self.client = client
        self.blockchain_mode = blockchain_mode or "irreversible"
        self.start_block = start_block
        self.end_block = end_block
        self.only_ops = only_ops

    def get_last_block_height(self):
        props = self.client.get_dynamic_global_properties()
        if self.blockchain_mode == "irreversible":
            return props['last_irreversible_block_num']
        elif self.blockchain_mode == "head":
            return props['head_block_number']
        else:
            raise ValueError(
                "Invalid blockchain mode. It can be irreversible or head.")

    def get_ops(self, block_num):
        self.client.logger.info("Getting ops on %s", block_num)
        return block_num, self.client.get_ops_in_block(block_num, False)

    def get_block(self, block_num):
        self.client.logger.info("Getting block: %s", block_num)
        block_data = self.client.get_block(block_num)
        return block_data

    def listen(self, ops=True):
        current_block = self.start_block
        if not current_block:
            current_block = self.get_last_block_height()
        while True:
            while (self.get_last_block_height() - current_block) > 0:
                if self.end_block and current_block > self.end_block:
                    return
                if ops:
                    block_num, ops = self.get_ops(current_block)
                    for op in ops:
                        yield op
                else:
                    yield self.get_block(current_block)

                current_block += 1

            time.sleep(3)

    def listen_blocks(self):
        return self.listen(ops=False)


class EventListener:

    def __init__(self, client, blockchain_mode=None,
                 start_block=None, end_block=None):
        self.client = client
        self.transaction_listener = TransactionListener(
            self.client,
            blockchain_mode=blockchain_mode,
            start_block=start_block,
            end_block=end_block,
        )

    def on(self, op_type, filter_by=None, condition=None):

        # magically turn the op_type to a list if it's a single string.
        op_types = op_type if isinstance(op_type, list) else [op_type, ]
        for op_data in self.transaction_listener.listen():
            if 'op' not in op_data:
                continue
            operation_type, operation_value = op_data["op"][0:2]
            if operation_type not in op_types:
                continue

            # filter_by is a generic dict that can be changed on every op.
            if filter_by and not filter_by.items() <= operation_value.items():
                continue

            # condition result should be True, otherwise continue
            # and search for other operations.
            if condition and not condition(operation_value):
                continue

            yield op_data

    def stream_operations(self):
        for op_data in self.transaction_listener.listen():
            yield op_data

    def stream_blocks(self):
        for block in self.transaction_listener.listen_blocks():
            yield block
