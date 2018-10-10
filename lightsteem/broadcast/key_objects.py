from .utils import compat_bytes

from .base58 import Base58, ripemd160
from binascii import hexlify, unhexlify

import ecdsa
import hashlib

"""
This classes are mostly derived from
https://github.com/steemit/steem-python/blob/master/steembase/account.py
"""


class Address(object):
    """ Address class

        This class serves as an address representation for Public Keys.

        :param str address: Base58 encoded address (defaults to ``None``)
        :param str pubkey: Base58 encoded pubkey (defaults to ``None``)
        :param str prefix: Network prefix (defaults to ``GPH``)

        Example::

           Address("GPHFN9r6VYzBK8EKtMewfNbfiGCr56pHDBFi")

    """

    def __init__(self, address=None, pubkey=None, prefix="STM"):
        self.prefix = prefix
        if pubkey is not None:
            self._pubkey = Base58(pubkey, prefix=prefix)
            self._address = None
        elif address is not None:
            self._pubkey = None
            self._address = Base58(address, prefix=prefix)
        else:
            raise Exception("Address has to be initialized by either the " +
                            "pubkey or the address.")

    def derivesha256address(self):
        """ Derive address using ``RIPEMD160(SHA256(x))`` """
        pkbin = unhexlify(repr(self._pubkey))
        addressbin = ripemd160(hexlify(hashlib.sha256(pkbin).digest()))
        return Base58(hexlify(addressbin).decode('ascii'))

    def derivesha512address(self):
        """ Derive address using ``RIPEMD160(SHA512(x))`` """
        pkbin = unhexlify(repr(self._pubkey))
        addressbin = ripemd160(hexlify(hashlib.sha512(pkbin).digest()))
        return Base58(hexlify(addressbin).decode('ascii'))

    def __repr__(self):
        """ Gives the hex representation of the ``GrapheneBase58CheckEncoded``
            Graphene address.
        """
        return repr(self.derivesha512address())

    def __str__(self):
        """ Returns the readable Graphene address. This call is equivalent to
            ``format(Address, "GPH")``
        """
        return format(self, self.prefix)

    def __format__(self, _format):
        """  May be issued to get valid "MUSE", "PLAY" or any other Graphene compatible
            address with corresponding prefix.
        """
        if self._address is None:
            if _format.lower() == "btc":
                return format(self.derivesha256address(), _format)
            else:
                return format(self.derivesha512address(), _format)
        else:
            return format(self._address, _format)

    def __bytes__(self):
        """ Returns the raw content of the ``Base58CheckEncoded`` address """
        if self._address is None:
            return compat_bytes(self.derivesha512address())
        else:
            return compat_bytes(self._address)


class PublicKey(object):

    def __init__(self, pk, prefix="STM"):
        self.prefix = prefix
        self._pk = Base58(pk, prefix=prefix)
        self.address = Address(pubkey=pk, prefix=prefix)
        self.pubkey = self._pk

    def _derive_y_from_x(self, x, is_even):
        """ Derive y point from x point """
        curve = ecdsa.SECP256k1.curve
        # The curve equation over F_p is:
        #   y^2 = x^3 + ax + b
        a, b, p = curve.a(), curve.b(), curve.p()
        alpha = (pow(x, 3, p) + a * x + b) % p
        beta = ecdsa.numbertheory.square_root_mod_prime(alpha, p)
        if (beta % 2) == is_even:
            beta = p - beta
        return beta

    def compressed(self):
        """ Derive compressed public key """
        order = ecdsa.SECP256k1.generator.order()
        p = ecdsa.VerifyingKey.from_string(
            compat_bytes(self), curve=ecdsa.SECP256k1).pubkey.point
        x_str = ecdsa.util.number_to_string(p.x(), order)
        # y_str = ecdsa.util.number_to_string(p.y(), order)
        compressed = hexlify(
            compat_bytes(chr(2 + (p.y() & 1)), 'ascii') + x_str).decode(
            'ascii')
        return (compressed)

    def unCompressed(self):
        """ Derive uncompressed key """
        public_key = repr(self._pk)
        prefix = public_key[0:2]
        if prefix == "04":
            return public_key
        assert prefix == "02" or prefix == "03"
        x = int(public_key[2:], 16)
        y = self._derive_y_from_x(x, (prefix == "02"))
        key = '04' + '%064x' % x + '%064x' % y
        return key

    def point(self):
        """ Return the point for the public key """
        string = unhexlify(self.unCompressed())
        return ecdsa.VerifyingKey.from_string(
            string[1:], curve=ecdsa.SECP256k1).pubkey.point

    def __repr__(self):
        """ Gives the hex representation of the Graphene public key. """
        return repr(self._pk)

    def __str__(self):
        """ Returns the readable Graphene public key. This call is equivalent to
            ``format(PublicKey, "GPH")``
        """
        return format(self._pk, self.prefix)

    def __format__(self, _format):
        """ Formats the instance of:doc:`Base58 <base58>` according
        to ``_format`` """
        return format(self._pk, _format)

    def __bytes__(self):
        """ Returns the raw public key (has length 33)"""
        return compat_bytes(self._pk)


class PrivateKey(object):
    def __init__(self, wif=None, prefix="STM"):
        if wif is None:
            import os
            self._wif = Base58(hexlify(os.urandom(32)).decode('ascii'))
        elif isinstance(wif, Base58):
            self._wif = wif
        else:
            self._wif = Base58(wif)
        # compress pubkeys only
        self._pubkeyhex, self._pubkeyuncompressedhex = self.compressedpubkey()
        self.pubkey = PublicKey(self._pubkeyhex, prefix=prefix)
        self.uncompressed = PublicKey(
            self._pubkeyuncompressedhex, prefix=prefix)
        self.uncompressed.address = Address(
            pubkey=self._pubkeyuncompressedhex, prefix=prefix)
        self.address = Address(pubkey=self._pubkeyhex, prefix=prefix)

    def compressedpubkey(self):
        """ Derive uncompressed public key """
        secret = unhexlify(repr(self._wif))
        order = ecdsa.SigningKey.from_string(
            secret, curve=ecdsa.SECP256k1).curve.generator.order()
        p = ecdsa.SigningKey.from_string(
            secret, curve=ecdsa.SECP256k1).verifying_key.pubkey.point
        x_str = ecdsa.util.number_to_string(p.x(), order)
        y_str = ecdsa.util.number_to_string(p.y(), order)
        compressed = hexlify(
            chr(2 + (p.y() & 1)).encode('ascii') + x_str
        ).decode('ascii')
        uncompressed = hexlify(
            chr(4).encode('ascii') + x_str + y_str).decode(
            'ascii')
        return [compressed, uncompressed]

    def __format__(self, _format):
        """ Formats the instance of:doc:`Base58 <base58>` according to
            ``_format``
        """
        return format(self._wif, _format)

    def __repr__(self):
        """ Gives the hex representation of the Graphene private key."""
        return repr(self._wif)

    def __str__(self):
        """ Returns the readable (uncompressed wif format) Graphene private key. This
            call is equivalent to ``format(PrivateKey, "WIF")``
        """
        return format(self._wif, "WIF")

    def __bytes__(self):
        """ Returns the raw private key """
        return compat_bytes(self._wif)


class PasswordKey(object):
    """ This class derives a private key given the account name, the
        role and a password. It leverages the technology of Brainkeys
        and allows people to have a secure private key by providing a
        passphrase only.
    """

    def __init__(self, account, password, role="active"):
        self.account = account
        self.role = role
        self.password = password

    def get_private(self):
        """ Derive private key from the brain key and the current sequence
            number
        """
        a = compat_bytes(self.account + self.role + self.password, 'utf8')
        s = hashlib.sha256(a).digest()
        return PrivateKey(hexlify(s).decode('ascii'))

    def get_public(self):
        return self.get_private().pubkey

    def get_private_key(self):
        return self.get_private()

    def get_public_key(self):
        return self.get_public()
