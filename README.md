# lightsteem

A light python client to interact with the STEEM blockchain.


#### Current state of python libraries for steem

One of the Python's idioms:

> Simple is better than complex.

Current STEEM libraries on python are **complicated**. They have enormous amount
of encapsulation and they try to solve everything inside the library.

lightsteem's standing here just providing a simple interface to STEEM nodes. It's
simple and stupid. You ask something, you get something.

This comes with a tradeoff, though. User of the library is responsible to consider

- Node failovers
- Exception handling
- Retry mechanisms

#### What's supported?

lightsteem is designed for appbase nodes. Every call supported by the appbase is
accessible via the ```Client``` interface. It also supports jussi's batch calls.

#### Installation

```
$ (sudo) pip install lightsteem
```

#### Usage

```python
from lightsteem.client import Client

client = Client()

print(c.get_dynamic_global_properties())
```

By default, client uses condenser_api to make the calls. If you
want to change the api, just call the client instance
with the api name.

Example:

```python

from lightsteem.client import Client

client = Client()

accounts = c('account_by_key_api').get_key_references({
    "keys":["STM5jZtLoV8YbxCxr4imnbWn61zMB24wwonpnVhfXRmv7j6fk3dTH"]
})

print(accounts)
```


#### Roadmap and potential feature ideas

- Support for broadcasting (Read-only methods supported at the moment.)
- Block streaming helpers
- Account helpers
- Formatting helpers (Ex: Reputation)
- Amount helpers
