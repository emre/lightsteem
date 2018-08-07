### lightsteem

A light python client to interact with the STEEM blockchain. It's simple and stupid. You ask something, you get something.

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

print(client.get_dynamic_global_properties())
```

By default, client uses **condenser_api** to make the calls. If you
want to change the api, just call the client instance
with the api name.

#### Examples

##### Get Account History
```python
from lightsteem.client import Client

c = Client()

history = c.get_account_history("emrebeyler", 1000, 10)

for op in history:
    print(op)
```


##### Get accounts by key (account_by_key_api)

```python

from lightsteem.client import Client

client = Client()

accounts = client('account_by_key_api').get_key_references({
    "keys":["STM5jZtLoV8YbxCxr4imnbWn61zMB24wwonpnVhfXRmv7j6fk3dTH"]
})

print(accounts)
```

##### Get last 10 posts of a user (tags_api)

```python
from lightsteem.client import Client

c = Client()

posts = c('tags_api').get_discussions_by_blog({"tag": "ned", "limit": 10})
for p in posts["discussions"]:
    print(p["title"])
```

##### Get block detail (block_api)

```python
from lightsteem.client import Client

c = Client()

block = c('block_api').get_block({"block_num": 24858937})

print(block)
```

#### Get current reserve ratio (witness_api)

```python
from lightsteem.client import Client

c = Client()

ratio = c('witness_api').get_reserve_ratio()

print(ratio)
```

##### Get list of supported methods by RPC node (jsonrpc)

```python
from lightsteem.client import Client

c = Client()

methods = c('jsonrpc').get_methods()

print(methods)

```

##### Get vesting delegations of an account (database_api)

```python
from lightsteem.client import Client

c = Client()

outgoing_delegations = c('database_api').find_vesting_delegations({"account": "emrebeyler"})

print(outgoing_delegations)

```

#### Batch calls

If a JUSSI instance is set on the appbase node, you can enjoy batch calls. 

```python
from lightsteem.client import Client

c = Client()

c.get_block(24858937, batch=True)
c.get_block(24858938, batch=True)

blocks = c.process_batch()

print(blocks)

```

#### Notes

- You can see the list of api types at [Steem Developers Portal](https://developers.steem.io/apidefinitions/#apidefinitions-condenser-api)

Consider using condenser_api methods until the other apis becomes stable. A warning from the official portal:

> While the condenser_api.* calls are ready for use, all other appbase methods are currently works in progress and may change, or be unsuitable for production use.

