import datetime
import math
import json

from dateutil.parser import parse

from lightsteem.exceptions import StopOuterIteration
from lightsteem.datastructures import Operation


class Account:

    def __init__(self, client, username=None):
        self.client = client
        self.username = username
        self.raw_data = None

        if username:
            self._pull_user_data(username)

    def _pull_user_data(self, username):
        accounts = self.client.get_accounts([username])
        if not len(accounts):
            raise ValueError("Username doesn't exist.")
        self.raw_data = accounts[0]

        return self

    def _get_account_history(self, account, index, limit,
                             order="desc", filter=None, exclude=None,
                             only_operation_data=True, start_at=None,
                             stop_at=None):

        if not filter:
            filter = []

        if not exclude:
            exclude = []
        order = -1 if order == "desc" else 1

        history = self.client.get_account_history(account, index, limit)
        for transaction in history[::order]:

            created_at = parse(transaction[1]["timestamp"])
            if start_at and order == -1 and created_at > start_at:
                continue

            if start_at and order != -1 and created_at < start_at:
                continue

            if stop_at and order == -1 and created_at < stop_at:
                raise StopOuterIteration

            if stop_at and order != -1 and created_at > stop_at:
                raise StopOuterIteration

            op_type, op_value = transaction[1]["op"]
            if op_type in exclude:
                continue

            if filter and op_type not in filter:
                continue

            yield op_value if only_operation_data else transaction

    def history(self, account=None, limit=1000,
                filter=None, exclude=None,
                order="desc", only_operation_data=True,
                start_at=None, stop_at=None):
        if not account:
            account = self.username

        # @todo: this can be faster with batch calls.
        # consider a way to implement it.
        max_index = self.client.get_account_history(account, -1, 0)[0][0]
        if not max_index:
            return

        if order == "desc":
            # Reverse history:
            # Loop until we process all ops
            last_processed_index = max_index
            while last_processed_index > 0:
                # Ex: if there are 10 ops left and the limit is 20,
                # change limit to 10.
                if last_processed_index - limit < 0:
                    limit = last_processed_index

                try:
                    for account_history in self._get_account_history(
                            account, index=last_processed_index,
                            limit=limit, filter=filter, exclude=exclude,
                            order=order,
                            only_operation_data=only_operation_data,
                            start_at=start_at, stop_at=stop_at):
                        yield account_history
                except StopOuterIteration as e:
                    # make sure the while loop is terminated
                    break

                # increment limit by one to prevent double hits.
                last_processed_index -= limit + 1
        else:
            last_processed_index = limit
            while last_processed_index < max_index + limit:
                try:
                    for account_history in self._get_account_history(
                            account, index=last_processed_index,
                            limit=limit, filter=filter, exclude=exclude,
                            order=order,
                            only_operation_data=only_operation_data,
                            start_at=start_at, stop_at=stop_at):
                        yield account_history
                except StopOuterIteration as e:
                    # make sure the while loop is terminated
                    break
                last_processed_index += limit + 1

    def _get_relationships(self, account, start_from="", type="blog",
                           limit=1000, method="get_followers"):

        start_from_key_map = {
            "get_followers": "follower",
            "get_following": "following",
        }

        relationships = getattr(self.client, method)(
            account, start_from, type, limit)

        if not len(relationships):
            return []

        last_user = relationships[-1][start_from_key_map[method]]
        relationships = [r[start_from_key_map[method]] for r in relationships]

        # if relationship count is equal to the limit, there
        # might be more. paginate.
        if len(relationships) >= limit:
            relationships += self._get_relationships(
                account,
                start_from=last_user,
                type=type,
                limit=limit,
                method=method)[1:]

        return relationships

    def followers(self, account=None):
        if not account:
            account = self.username

        return self._get_relationships(
            account,
            method="get_followers")

    def following(self, account=None):
        if not account:
            account = self.username

        return self._get_relationships(
            account,
            method="get_following"
        )

    def ignorers(self, account=None):
        if not account:
            account = self.username

        return self._get_relationships(
            account,
            type="ignore",
            method="get_followers"
        )

    def ignorings(self, account=None):
        if not account:
            account = self.username

        return self._get_relationships(
            account,
            type="ignore",
            method="get_following"
        )

    def vp(self, consider_regeneration=True, precision=2):

        if not consider_regeneration:
            # the voting power user has after the last vote they casted.
            return round(self.raw_data['voting_power'] / 100, precision)

        # the voting power user has after the last vote they casted and
        # recharging factors.

        last_vote_time = parse(self.raw_data['last_vote_time'])
        diff_in_seconds = (datetime.datetime.utcnow() -
                           last_vote_time).total_seconds()
        regenerated_vp = diff_in_seconds * 10000 / 86400 / 5
        total_vp = (self.raw_data['voting_power'] + regenerated_vp) / 100
        if total_vp > 100:
            total_vp = 100

        return round(total_vp, precision)

    def reputation(self, precision=2):
        rep = int(self.raw_data['reputation'])
        if rep == 0:
            return 25
        score = max([math.log10(abs(rep)) - 9, 0]) * 9 + 25
        if rep < 0:
            score = 50 - score
        return round(score, precision)

    def follow(self, account):
        op = Operation('custom_json', {
            'required_auths': [],
            'required_posting_auths': [self.username, ],
            'id': 'follow',
            'json': json.dumps(
                ["follow", {
                    "follower": self.username,
                    "following": account,
                    "what": ["blog", ],
                }]
            ),
        })

        return self.client.broadcast(op)

    def unfollow(self, account):
        op = Operation('custom_json', {
            'required_auths': [],
            'required_posting_auths': [self.username, ],
            'id': 'follow',
            'json': json.dumps(
                ["follow", {
                    "follower": self.username,
                    "following": account,
                    "what": [],
                }]
            ),
        })

        return self.client.broadcast(op)

    def ignore(self, account):
        op = Operation('custom_json', {
            'required_auths': [],
            'required_posting_auths': [self.username, ],
            'id': 'follow',
            'json': json.dumps(
                ["follow", {
                    "follower": self.username,
                    "following": account,
                    "what": ["ignore", ],
                }]
            ),
        })

        return self.client.broadcast(op)

    def unignore(self, account):
        return self.unfollow(account)
