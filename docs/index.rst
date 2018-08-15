
lightsteem
=================================

Lightsteem is a **light** python client to interact with the STEEM blockchain.
It's simple and stupid. It doesn't interfere the process between the developer
and the STEEM node.

.. figure::  https://steemitimages.com/0x0/https://cdn.steemitimages.com/DQmV9ziht8AJYi3YhqR1gjKT96pCAe6FMiEAD7TC8nE5r13/Screen%20Shot%202018-08-07%20at%207.14.36%20PM.png
   :width: 600

Features
----------
- No hard-coded methods. All potential future appbase methods are automatically supported.
- Retry and Failover support for node errors and timeouts. See :doc:`/retryandfailover`.


Limitations
------------
- No support for pre-appbase nodes.
- No magic methods and encapsulation over well-known blockchain objects. (Comment, Post, Account, etc.)

Installation
-------------

Lightsteem requires python3.6 and above. Even though it's easy to make it compatible
with lower versions, it's doesn't have support by design to keep the library simple.

You can install the library by typing to your console:

.. code-block:: bash

    $ (sudo) pip install lightsteem

After that, you can continue with  :doc:`/gettingstarted`.

Documentation Pages
-----------

.. toctree::
   :maxdepth: 3

   gettingstarted
   retryandfailover
   broadcasting
   batch_rpc_calls