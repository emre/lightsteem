from lightsteem.vendor.rc import (
    RCModel, STEEM_RC_REGEN_TIME, STEEM_BLOCK_INTERVAL
)

from lightsteem.helpers.amount import Amount


class ResourceCredit:

    def __init__(self, client):
        self.client = client

    def get_cost(self, operation):
        preffered_api_type = self.client.api_type
        keys = self.client.keys
        if not len(keys):
            # add a dummy key
            self.client.keys = [
                "5KQwrPbwdL6PhXujxW37FSSQZ1JiwsST4cqQzDeyXtP79zkvFD3"]
        try:
            tx = self.client.broadcast(operation, dry_run=True)
            signed_tx_hex = self.client.get_transaction_hex(tx)
            tx_size = len(bytes.fromhex(signed_tx_hex))

            self.client('condenser_api').get_dynamic_global_properties(
                batch=True)
            self.client('rc_api').get_resource_params(batch=True)
            self.client('rc_api').get_resource_pool(batch=True)

            chain_props, resource_params, resource_pool = self.client.\
                process_batch()

            resource_pool = resource_pool["resource_pool"]

            total_vesting_shares = int(
                Amount(chain_props["total_vesting_shares"]).amount)
            rc_regen = total_vesting_shares // (
                    STEEM_RC_REGEN_TIME // STEEM_BLOCK_INTERVAL)
            model = RCModel(resource_params=resource_params,
                            resource_pool=resource_pool, rc_regen=rc_regen)

            tx_cost = model.get_transaction_rc_cost(tx, tx_size)
            total_cost = sum(tx_cost["cost"].values())
            return total_cost
        finally:
            self.client.api_type = preffered_api_type
            self.client.keys = keys
