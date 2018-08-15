
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

Example: Creating a transfer
---------------------

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


.. important ::
    Since, lightsteem doesn't introduce any encapsulation on operations, you are responsible to create operation data yourself. To find out the specs for each operation, you may review the block explorers for raw data or the source code of steemd.



