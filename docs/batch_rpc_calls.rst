
Batch RPC Calls
=================================

Appbase nodes support multiple RPC calls in one HTTP request. (Maximum is 50.). If you want
to take advantage of this:


.. code-block:: python


    from lightsteem.client import Client

    c = Client()

    c.get_block(24858937, batch=True)
    c.get_block(24858938, batch=True)

    blocks = c.process_batch()

    print(blocks)

This will create one request, but you will have two block details.

.. important ::
    This feature is not thread-safe. Every instance has a simple queue (list) as their property, and it's flushed every time the ``process_batch``` called.
