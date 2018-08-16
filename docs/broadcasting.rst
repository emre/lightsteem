
Broadcasting Transactions
=================================

Since Lightsteem supports transaction signing out of the box, you only need to
define the operations you want to broadcast.

A typical transaction on STEEM blockchain consists of these fields:

.. code-block:: javascript

    {
        "ref_block_num": "..",
        "ref_block_prefix": "..",
        "expiration": "..",
        "operations": [OperationObject, ],
        "extensions": [],
        "signatures": [Signature1,],
    }

As a library user, you don't need to build the all these information yourself. Since all keys except ``operations``
can be generated automatically, Lightsteem only asks for a list of operations.

Example: Account Witness Vote
-----------------------------------

.. code-block:: python

    from lightsteem.client import Client
    from lightsteem.datastructures import Operation

    c = Client(
        keys=["<private_key>",])

    op = Operation('account_witness_vote', {
            'account': '<your_account>',
            'witness': 'emrebeyler',
            'approve': True,
        })

    c.broadcast(op)


Example: Voting for a Post
-----------------------------

This will vote with a %1. Percent / 100 = Weight. If you want to downvote,
use negative weight.

.. code-block:: python


    from lightsteem.client import Client
    from lightsteem.datastructures import Operation

    client = Client(
        keys=["<private_key>"]
    )

    op = Operation('vote', {
        "voter": "emrebeyler",
        "author": "emrebeyler",
        "permlink": "re-hitenkmr-actifit-ios-app-development-contribution-20180816t105311829z",
        "weight": 100,
    })

    client.broadcast(op)

Example: Creating a Post (main Comment)
-----------------------------

.. code-block:: python

    import json

    from lightsteem.client import Client
    from lightsteem.datastructures import Operation

    client = Client(
        keys=["<posting_key>"]
    )

    post = Operation('comment', {
        "parent_author": None,
        "parent_permlink": "steemit",
        "author": "emrebeyler",
        "permlink": "api-steemit-is-down",
        "title": "api.steemit.com is down",
        "body": "Body of the post",
        "json_metadata": json.dumps({"tags": "steemit steem lightsteem"})
    })

    resp =client.broadcast(post)

    print(resp)

Posts are actually Comment objects and same with replies. This example
creates a main comment (Post) on the blockchain.

Notes:

- parent_author should be None for posts.
- parent_permlink should be the first tag you use in the post.

If you fill parent_author and parent_permlink with actual post information, you will
have a reply. (comment)


Example: Creating a transfer
-----------------------------

.. code-block:: python


    from lightsteem.client import Client
    from lightsteem.datastructures import Operation


    c = Client(
        keys=["active_key",])

    op = Operation('transfer', {
                'from': 'emrebeyler',
                'to': '<receiver_1>',
                'amount': '0.001 SBD',
                'memo': 'test1!'
            })

    c.broadcast(ops)


Example: Bundling Operations
---------------------------


It's also possible to bundle multiple operations into one transaction:

.. code-block:: python

    from lightsteem.client import Client
    from lightsteem.datastructures import Operation


    c = Client(
        keys=["active_key",])

    ops = [
        Operation('transfer', {
            'from': 'emrebeyler',
            'to': '<receiver_1>',
            'amount': '0.001 SBD',
            'memo': 'test1!'
        }),
        Operation('transfer', {
            'from': 'emrebeyler',
            'to': '<receiver_2>',
            'amount': '0.001 SBD',
            'memo': 'test2!'
        }),

    ]

    c.broadcast(ops)


Example: Using convert function for SBDs
---------------------------------------------------------------------------------

.. code-block:: python

    from lightsteem.client import Client
    from lightsteem.datastructures import Operation

    client = Client(
        keys=["<active_key>"]
    )
    client.broadcast(
        Operation('convert', {
            "owner": "emrebeyler,
            "amount": "0.500 SBD",
            "requestid": 1,
        })
    )

Note: requestid and the owner is unique together.

.. important ::
    Since, lightsteem doesn't introduce any encapsulation on operations, you are responsible to create operation data yourself. To find out the specs for each operation, you may review the block explorers for raw data or the source code of steemd.



