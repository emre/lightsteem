
Helpers
=================================

Lightsteem has a target to define helper classes for well known blockchain objects. This is
designed in that way to prevent code repeat on client (library user) side.

It's possible to use lightsteem for just a client. However, if you need to get an
account's history, or get followers of account, you may use the helpers module.

Account helper
=================================

This class defines an Account in the STEEM blockchain.

.. code-block:: python

    from lightsteem.client import Client
    c = Client()
    account = c.get_account('emrebeyler')

When you execute that script in your REPL, lightsteem makes a RPC call to get the account data
from the blockchain. Once you initialized the Account instance, you have access to these helper methods:

Getting account history
-----------------------------------

With this method, you can traverse entire history of a STEEM account.

.. function:: history(self, account=None, limit=1000, filter=None, exclude=None,
                        order="desc", only_operation_data=True,
                        start_at=None, stop_at=None):

    :param account: (string) The username.
    :param limit: (integer) Batch size per call.
    :param filter: (list:string) Operation types to filter
    :param exclude: (list:s tring) Operation types to exclude
    :param order: (string) asc or desc.
    :param only_operation_data: (bool) If false, returns in the raw format. (Includes transaction information.)
    :param start_at: (datetime.datetime) Starts after that time to process ops.
    :param stop_at: (datetime.datetime) Stops at that time while processing ops.

account_history is an important call for the STEEM applications. A few use cases:

- Getting incoming delegations
- Filtering transfers on specific accounts
- Getting author, curation rewards

etc.

**Example: Get all incoming STEEM of binance account in the last 7 days**

.. code-block:: python

    import datetime

    from lightsteem.client import Client
    from lightsteem.helpers.amount import Amount

    client = Client()
    account = client.account('deepcrypto8')

    one_week_ago = datetime.datetime.utcnow() -
        datetime.timedelta(days=7)
    total_steem = 0
    for op in account.history(
            stop_at=one_week_ago,
            filter=["transfer"]):

        if op["to"] != "deepcrypto8":
            continue

        total_steem += Amount(op["amount"]).amount

    print("Total STEEM deposited to Binance", total_steem)


Getting account followers
-----------------------------------

.. code-block:: python

    from lightsteem.client import Client

    client = Client()
    account = client.account('deepcrypto8')

    print(account.followers())

Output will be a list of usernames. (string)


Getting account followings
-----------------------------------

.. code-block:: python

    from lightsteem.client import Client

    client = Client()
    account = client.account('emrebeyler')

    print(account.following())

Output will be a list of usernames. (string)

Getting account ignorers (Muters)
-----------------------------------

.. code-block:: python

    from lightsteem.client import Client

    client = Client()
    account = client.account('emrebeyler')

    print(account.ignorers())


Getting account ignorings (Muted list)
-----------------------------------

.. code-block:: python

    from lightsteem.client import Client

    client = Client()
    account = client.account('emrebeyler')

    print(account.ignorings())

Getting voting power
-----------------------------------

This helper method determines the account's voting power. In default, It considers
account's regenerated VP. (Actual VP)

If you want the VP at the time the last vote casted, you can pass consider_regeneration=False.

.. code-block:: python

    from lightsteem.client import Client

    client = Client()
    account = client.account('emrebeyler')

    print(account.vp())
    print(account.vp(consider_regeneration=False))

Getting resource credits
-----------------------------------
This helper method determines the account's resource credits in percent. In default, It considers
account's regenerated RC. (Actual RC)

If you want the Rc at the time the last vote casted, you can pass consider_regeneration=False.

.. code-block:: python

    from lightsteem.client import Client

    client = Client()
    account = client.account('emrebeyler')

    print(account.rc())
    print(account.rc(consider_regeneration=False))



Getting account reputation
-----------------------------------

.. code-block:: python

    from lightsteem.client import Client

    client = Client()
    account = client.account('emrebeyler')

    print(account.reputation())

Default precision is 2. You can set it by passing precision=N parameter.

Amount helper
=================================

A simple class to convert "1234.1234 STEEM" kind of values to Decimal.

.. code-block:: python

    from lightsteem.helpers.amount import Amount

    amount = Amount("42.5466 STEEM")

    print(amount.amount)
    print(amount.symbol)

EventListener Helper
=================================

EventListener is a helper class to listen specific operations (events) on the
blockchain.

**Stream blockchain for the incoming transfers related to a specific account**

.. code-block:: python

    from lightsteem.helpers.event_listener import EventListener
    from lightsteem.client import Client

    client = Client()
    events = EventListener(client)

    for transfer in events.on('transfer', filter_by={"to": "emrebeyler"}):
        print(transfer)



**Stream for incoming vote actions**

.. code-block:: python

    events = EventListener(client)

    for witness_vote in events.on('account_witness_vote', filter_by={"witness": "emrebeyler"}):
        print(witness_vote)


**Conditions via callables**

Stream for the comments and posts tagged with utopian-io.

.. code-block:: python

    from lightsteem.client import Client
    from lightsteem.helpers.event_listener import EventListener

    import json

    c = Client()
    events = EventListener(c)

    def filter_tags(comment_body):
        if not comment_body.get("json_metadata"):
            return False

        try:
            tags = json.loads(comment_body["json_metadata"])["tags"]
        except KeyError:
            return False
        return "utopian-io" in tags


    for op in events.on("comment", condition=filter_tags):
        print(op)

EventListener class also has

- start_block
- end_block

params that you can limit the streaming process into specific blocks.


ResourceCredits Helper
=================================

ResourceCredits class has a simple helper function to get RC costs on specific
operations.

For example, if you want to learn about how much resource credit will be exhausted
for an **account_claim** operation:

.. code-block:: python

    from lightsteem.client import Client
    from lightsteem.datastructures import Operation

    client = Client(keys=[<your_active_key>])

    op = Operation(
        'claim_account',
        {
            "creator": "emrebeyler",
            "fee": "0.000 STEEM",
            "extensions": [],
        }
    )

    print(client.rc().get_cost(op))

