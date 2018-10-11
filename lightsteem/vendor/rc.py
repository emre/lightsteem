# flake8: noqa

import collections

"""
This file is vendorized from github/steemit/rc_demo
with a couple compability changes.
"""

STEEM_RC_REGEN_TIME = 60 * 60 * 24 * 5
STEEM_BLOCK_INTERVAL = 3


class CountOperationVisitor(object):

    def __init__(self, size_info, exec_info):
        self.market_op_count = 0
        self.new_account_op_count = 0
        self.state_bytes_count = 0
        self.execution_time_count = 0
        self.size_info = size_info
        self.exec_info = exec_info

    def get_authority_byte_count(self, auth):
        return (self.size_info.authority_base_size
                + self.size_info.authority_account_member_size * len(
                    auth["account_auths"])
                + self.size_info.authority_key_member_size * len(
                    auth["key_auths"])
                )

    def visit_account_create_operation(self, op):
        self.state_bytes_count += (
                self.size_info.account_object_base_size
                + self.size_info.account_authority_object_base_size
                + self.get_authority_byte_count(op["owner"])
                + self.get_authority_byte_count(op["active"])
                + self.get_authority_byte_count(op["posting"])
        )
        self.execution_time_count += self.exec_info.account_create_operation_exec_time

    def visit_account_create_with_delegation_operation(self, op):
        self.state_bytes_count += (
                self.size_info.account_object_base_size
                + self.size_info.account_authority_object_base_size
                + self.get_authority_byte_count(op["owner"])
                + self.get_authority_byte_count(op["active"])
                + self.get_authority_byte_count(op["posting"])
                + self.size_info.vesting_delegation_object_base_size
        )
        self.execution_time_count += self.exec_info.account_create_with_delegation_operation_exec_time

    def visit_account_witness_vote_operation(self, op):
        self.state_bytes_count += self.size_info.witness_vote_object_base_size
        self.execution_time_count += self.exec_info.account_witness_vote_operation_exec_time

    def visit_comment_operation(self, op):
        self.state_bytes_count += (
                self.size_info.comment_object_base_size
                + self.size_info.comment_object_permlink_char_size * len(
            op["permlink"].encode("utf8"))
                + self.size_info.comment_object_parent_permlink_char_size * len(
            op["parent_permlink"].encode("utf8"))
        )
        self.execution_time_count += self.exec_info.comment_operation_exec_time

    def visit_comment_payout_beneficiaries(self, bens):
        self.state_bytes_count += self.size_info.comment_object_beneficiaries_member_size * len(
            bens["beneficiaries"])

    def visit_comment_options_operation(self, op):
        for e in op["extensions"]:
            getattr(self, "visit_" + e["type"])(e["value"])
        self.execution_time_count += self.exec_info.comment_options_operation_exec_time

    def visit_convert_operation(self, op):
        self.state_bytes_count += self.size_info.convert_request_object_base_size
        self.execution_time_count += self.exec_info.convert_operation_exec_time

    def visit_create_claimed_account_operation(self, op):
        self.state_bytes_count += (
                self.size_info.account_object_base_size
                + self.size_info.account_authority_object_base_size
                + self.get_authority_byte_count(op["owner"])
                + self.get_authority_byte_count(op["active"])
                + self.get_authority_byte_count(op["posting"])
        )
        self.execution_time_count += self.exec_info.create_claimed_account_operation_exec_time

    def visit_decline_voting_rights_operation(self, op):
        self.state_bytes_count += self.size_info.decline_voting_rights_request_object_base_size
        self.execution_time_count += self.exec_info.decline_voting_rights_operation_exec_time

    def visit_delegate_vesting_shares_operation(self, op):
        self.state_bytes_count += max(
            self.size_info.vesting_delegation_object_base_size,
            self.size_info.vesting_delegation_expiration_object_base_size
        )
        self.execution_time_count += self.exec_info.delegate_vesting_shares_operation_exec_time

    def visit_escrow_transfer_operation(self, op):
        self.state_bytes_count += self.size_info.escrow_object_base_size
        self.execution_time_count += self.exec_info.escrow_transfer_operation_exec_time

    def visit_limit_order_create_operation(self, op):
        self.state_bytes_count += 0 if op[
            "fill_or_kill"] else self.size_info.limit_order_object_base_size
        self.execution_time_count += self.exec_info.limit_order_create_operation_exec_time
        self.market_op_count += 1

    def visit_limit_order_create2_operation(self, op):
        self.state_bytes_count += 0 if op[
            "fill_or_kill"] else self.size_info.limit_order_object_base_size
        self.execution_time_count += self.exec_info.limit_order_create2_operation_exec_time
        self.market_op_count += 1

    def visit_request_account_recovery_operation(self, op):
        self.state_bytes_count += self.size_info.account_recovery_request_object_base_size
        self.execution_time_count += self.exec_info.request_account_recovery_operation_exec_time

    def visit_set_withdraw_vesting_route_operation(self, op):
        self.state_bytes_count += self.size_info.withdraw_vesting_route_object_base_size
        self.execution_time_count += self.exec_info.set_withdraw_vesting_route_operation_exec_time

    def visit_vote_operation(self, op):
        self.state_bytes_count += self.size_info.comment_vote_object_base_size
        self.execution_time_count += self.exec_info.vote_operation_exec_time

    def visit_witness_update_operation(self, op):
        self.state_bytes_count += (
                self.size_info.witness_object_base_size
                + self.size_info.witness_object_url_char_size * len(
            op["url"].encode("utf8"))
        )
        self.execution_time_count += self.exec_info.witness_update_operation_exec_time

    def visit_transfer_operation(self, op):
        self.execution_time_count += self.exec_info.transfer_operation_exec_time
        self.market_op_count += 1

    def visit_transfer_to_vesting_operation(self, op):
        self.execution_time_count += self.exec_info.transfer_to_vesting_operation_exec_time
        self.market_op_count += 1

    def visit_transfer_to_savings_operation(self, op):
        self.execution_time_count += self.exec_info.transfer_to_savings_operation_exec_time

    def visit_transfer_from_savings_operation(self, op):
        self.state_bytes_count += self.size_info.savings_withdraw_object_byte_size
        self.execution_time_count += self.exec_info.transfer_from_savings_operation_exec_time

    def visit_claim_reward_balance_operation(self, op):
        self.execution_time_count += self.exec_info.claim_reward_balance_operation_exec_time

    def visit_withdraw_vesting_operation(self, op):
        self.execution_time_count += self.exec_info.withdraw_vesting_operation_exec_time

    def visit_account_update_operation(self, op):
        self.execution_time_count += self.exec_info.account_update_operation_exec_time

    def visit_account_witness_proxy_operation(self, op):
        self.execution_time_count += self.exec_info.account_witness_proxy_operation_exec_time

    def visit_cancel_transfer_from_savings_operation(self, op):
        self.execution_time_count += self.exec_info.cancel_transfer_from_savings_operation_exec_time

    def visit_change_recovery_account_operation(self, op):
        self.execution_time_count += self.exec_info.change_recovery_account_operation_exec_time

    def visit_claim_account_operation(self, op):
        self.execution_time_count += self.exec_info.claim_account_operation_exec_time

        if op["fee"] == "0.000 STEEM":
            self.new_account_op_count += 1

    def visit_custom_operation(self, op):
        self.execution_time_count += self.exec_info.custom_operation_exec_time

    def visit_custom_json_operation(self, op):
        self.execution_time_count += self.exec_info.custom_json_operation_exec_time

    def visit_custom_binary_operation(self, op):
        self.execution_time_count += self.exec_info.custom_binary_operation_exec_time

    def visit_delete_comment_operation(self, op):
        self.execution_time_count += self.exec_info.delete_comment_operation_exec_time

    def visit_escrow_approve_operation(self, op):
        self.execution_time_count += self.exec_info.escrow_approve_operation_exec_time

    def visit_escrow_dispute_operation(self, op):
        self.execution_time_count += self.exec_info.escrow_dispute_operation_exec_time

    def visit_escrow_release_operation(self, op):
        self.execution_time_count += self.exec_info.escrow_release_operation_exec_time

    def visit_feed_publish_operation(self, op):
        self.execution_time_count += self.exec_info.feed_publish_operation_exec_time

    def visit_limit_order_cancel_operation(self, op):
        self.execution_time_count += self.exec_info.limit_order_cancel_operation_exec_time

    def visit_witness_set_properties_operation(self, op):
        self.execution_time_count += self.exec_info.witness_set_properties_operation_exec_time

    def visit_claim_reward_balance2_operation(self, op):
        self.execution_time_count += self.exec_info.claim_reward_balance2_operation_exec_time

    def visit_smt_setup_operation(self, op):
        self.execution_time_count += self.exec_info.smt_setup_operation_exec_time

    def visit_smt_cap_reveal_operation(self, op):
        self.execution_time_count += self.exec_info.smt_cap_reveal_operation_exec_time

    def visit_smt_refund_operation(self, op):
        self.execution_time_count += self.exec_info.smt_refund_operation_exec_time

    def visit_smt_setup_emissions_operation(self, op):
        self.execution_time_count += self.exec_info.smt_setup_emissions_operation_exec_time

    def visit_smt_set_setup_parameters_operation(self, op):
        self.execution_time_count += self.exec_info.smt_set_setup_parameters_operation_exec_time

    def visit_smt_set_runtime_parameters_operation(self, op):
        self.execution_time_count += self.exec_info.smt_set_runtime_parameters_operation_exec_time

    def visit_smt_create_operation(self, op):
        self.execution_time_count += self.exec_info.smt_create_operation_exec_time

    def visit_allowed_vote_assets(self, op):
        pass

    def visit_recover_account_operation(self, op):
        pass

    def visit_pow_operation(self, op):
        pass

    def visit_pow2_operation(self, op):
        pass

    def visit_report_over_production_operation(self, op):
        pass

    def visit_reset_account_operation(self, op):
        pass

    def visit_set_reset_account_operation(self, op):
        pass

    # Virtual ops
    def visit_fill_convert_request_operation(self, op):
        pass

    def visit_author_reward_operation(self, op):
        pass

    def visit_curation_reward_operation(self, op):
        pass

    def visit_comment_reward_operation(self, op):
        pass

    def visit_liquidity_reward_operation(self, op):
        pass

    def visit_interest_operation(self, op):
        pass

    def visit_fill_vesting_withdraw_operation(self, op):
        pass

    def visit_fill_order_operation(self, op):
        pass

    def visit_shutdown_witness_operation(self, op):
        pass

    def visit_fill_transfer_from_savings_operation(self, op):
        pass

    def visit_hardfork_operation(self, op):
        pass

    def visit_comment_payout_update_operation(self, op):
        pass

    def visit_return_vesting_delegation_operation(self, op):
        pass

    def visit_comment_benefactor_reward_operation(self, op):
        pass

    def visit_producer_reward_operation(self, op):
        pass

    def visit_clear_null_account_balance_operation(self, op):
        pass


class SizeInfo(object):
    pass


class ExecInfo(object):
    pass


class ResourceCounter(object):
    def __init__(self, resource_params):
        self.resource_params = resource_params
        self.resource_name_to_index = {}
        self._size_info = None
        self._exec_info = None

        self.resource_names = self.resource_params["resource_names"]
        self.STEEM_NUM_RESOURCE_TYPES = len(self.resource_names)
        for i, resource_name in enumerate(self.resource_names):
            self.resource_name_to_index[resource_name] = i
        self._size_info = SizeInfo()
        for k, v in self.resource_params["size_info"][
            "resource_state_bytes"].items():
            setattr(self._size_info, k, v)
        self._exec_info = ExecInfo()
        for k, v in self.resource_params["size_info"][
            "resource_execution_time"].items():
            setattr(self._exec_info, k, v)
        return

    def __call__(self, tx=None, tx_size=-1):
        result = collections.OrderedDict(
            (("resource_count", collections.OrderedDict((
                ("resource_history_bytes", 0),
                ("resource_new_accounts", 0),
                ("resource_market_bytes", 0),
                ("resource_state_bytes", 0),
                ("resource_execution_time", 0),
            ))),)
        )

        resource_count = result["resource_count"]
        resource_count["resource_history_bytes"] += tx_size

        vtor = CountOperationVisitor(self._size_info, self._exec_info)
        for op in tx["operations"]:
            getattr(vtor, "visit_" + op[0] + "_operation")(op[1])
        resource_count["resource_new_accounts"] += vtor.new_account_op_count

        if vtor.market_op_count > 0:
            resource_count["resource_market_bytes"] += tx_size

        resource_count["resource_state_bytes"] += (
                self._size_info.transaction_object_base_size
                + self._size_info.transaction_object_byte_size * tx_size
                + vtor.state_bytes_count)

        # resource_count["resource_execution_time"] += vtor.execution_time_count
        return result


def compute_rc_cost_of_resource(curve_params=None, current_pool=0,
                                resource_count=0, rc_regen=0):
    if resource_count <= 0:
        if resource_count < 0:
            return -compute_rc_cost_of_resource(curve_params, current_pool,
                                                -resource_count, rc_regen)
        return 0
    num = rc_regen
    num *= int(curve_params["coeff_a"])
    num >>= int(curve_params["shift"])
    num += 1
    num *= resource_count

    denom = int(curve_params["coeff_b"])
    denom += max(current_pool, 0)

    num_denom = num // denom
    return num_denom + 1


def rd_compute_pool_decay(
        decay_params,
        current_pool,
        dt,
):
    if current_pool < 0:
        return -rd_compute_pool_decay(decay_params, -current_pool, dt)
    decay_amount = int(decay_params["decay_per_time_unit"]) * dt
    decay_amount *= current_pool
    decay_amount >>= int(decay_params["decay_per_time_unit_denom_shift"])
    result = decay_amount
    return min(result, current_pool)


class RCModel(object):
    def __init__(self, resource_params=None, resource_pool=None, rc_regen=0):
        self.resource_params = resource_params
        self.resource_pool = resource_pool
        self.rc_regen = rc_regen
        self.count_resources = ResourceCounter(resource_params)
        self.resource_names = self.resource_params["resource_names"]

    def get_transaction_rc_cost(self, tx=None, tx_size=-1):
        usage = self.count_resources(tx, tx_size)

        total_cost = 0

        cost = collections.OrderedDict()
        for resource_name in self.resource_params["resource_names"]:
            params = self.resource_params["resource_params"][resource_name]
            pool = int(self.resource_pool[resource_name]["pool"])

            usage["resource_count"][resource_name] *= \
            params["resource_dynamics_params"]["resource_unit"]
            cost[resource_name] = compute_rc_cost_of_resource(
                params["price_curve_params"], pool,
                usage["resource_count"][resource_name], self.rc_regen)
            total_cost += cost[resource_name]
        # TODO: Port get_resource_user()
        return collections.OrderedDict((("usage", usage), ("cost", cost)))

    def apply_rc_pool_dynamics(self, count):
        block_info = collections.OrderedDict((
            ("dt", collections.OrderedDict()),
            ("decay", collections.OrderedDict()),
            ("budget", collections.OrderedDict()),
            ("usage", collections.OrderedDict()),
            ("adjustment", collections.OrderedDict()),
            ("pool", collections.OrderedDict()),
            ("new_pool", collections.OrderedDict()),
        ))

        for resource_name in self.resource_params["resource_names"]:
            params = self.resource_params["resource_params"][resource_name][
                "resource_dynamics_params"]
            pool = int(self.resource_pool[resource_name]["pool"])
            dt = 1

            block_info["pool"][resource_name] = pool
            block_info["dt"][resource_name] = dt
            block_info["budget"][resource_name] = int(
                params["budget_per_time_unit"]) * dt
            block_info["usage"][resource_name] = count[resource_name] * params[
                "resource_unit"]
            block_info["decay"][resource_name] = rd_compute_pool_decay(
                params["decay_params"],
                pool - block_info["usage"][resource_name], dt)

            block_info["new_pool"][resource_name] = pool - block_info["decay"][
                resource_name] + block_info["budget"][resource_name] - \
                                                    block_info["usage"][
                                                        resource_name]
        return block_info