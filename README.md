### lightsteem <img src="https://travis-ci.org/emre/lightsteem.svg?branch=master">

A light python client to interact with the STEEM blockchain. It's simple and stupid. You ask something, you get something.

#### What's supported?

lightsteem is designed for appbase nodes. Every call supported by the appbase is
accessible via the ```Client``` interface. It also supports jussi's batch calls.

#### Documentation

See [lightsteem.readthedocs.io](https://lightsteem.readthedocs.io/en/latest/).

#### Notes

- You can see the list of api types at [Steem Developers Portal](https://developers.steem.io/apidefinitions/#apidefinitions-condenser-api)

Consider using condenser_api methods until the other apis becomes stable. A warning from the official portal:

> While the condenser_api.* calls are ready for use, all other appbase methods are currently works in progress and may change, or be unsuitable for production use.

