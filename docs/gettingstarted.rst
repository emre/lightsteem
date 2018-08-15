
Getting Started
=================================

Client class is the primary class you will work with.


.. code-block:: python

    from lightsteem.client import Client

    client = Client()


Appbase nodes support different `api namespaces <https://developers.steem.io/apidefinitions/#apidefinitions-condenser-api>`_.

Client class uses **condenser_api** as default. Follow the official developer portal's `api definitions <https://developers.steem.io/apidefinitions/>`_
to explore available methods.

Examples
""""""""

**Get Dynamic Global Properties**

.. code-block:: python

    props = client.get_dynamic_global_properties()

    print(props)

**Get Current Reserve Ratio**

.. code-block:: python

    ratio = c('witness_api').get_reserve_ratio()

    print(ratio)


**Get @emrebeyler's account history**

.. code-block:: python

    history = c.get_account_history("emrebeyler", 1000, 10)

    for op in history:
        print(op)

It's the same convention for every api type and every call on appbase nodes.

.. important ::
    Since, api_type is set when the client instance is called, it is not thread-safe to share Client instances between threads.


Optional parameters of Client
"""""""""

Even though, you don't need to pass any parameters to the ``Client``, you have some options
to choose.


.. function:: __init__(self, nodes=None, keys=None, connect_timeout=3,
                 read_timeout=30, loglevel=logging.ERROR, chain=None)

   :param nodes: A list of appbase nodes. (Defaults: ``api.steemit.com``, ``appbase.buildteam.io``.)
   :param keys: A list of private keys.
   :param connect_timeout: Integer. Connect timeout for nodes. (Default:3 seconds.)
   :param read_timeout: Integer. Read timeout for nodes. (Default: 30 seconds.)
   :param loglevel: Integer. (Ex: logging.DEBUG)
   :param chain: String. The blockhain we're working with. (Default: STEEM)


See :doc:`/broadcasting` to find out how to broadcast transactions into the blockchain.