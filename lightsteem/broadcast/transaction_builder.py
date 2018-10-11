import array
import hashlib
import struct
import time
from binascii import hexlify
from binascii import unhexlify
from collections import OrderedDict
from datetime import timedelta

import ecdsa
from dateutil.parser import parse

from .chains import known_chains
from .key_objects import PrivateKey
from .utils import compat_bytes

try:
    import secp256k1
    USE_SECP256K1 = True
except ImportError:
    USE_SECP256K1 = False


class TransactionBuilder:

    def __init__(self, client):
        self.client = client
        self.transaction = OrderedDict()
        self.message = None
        self.digest = None

    def prepare(self):
        properties = self.client.get_dynamic_global_properties()
        ref_block_num = properties["head_block_number"] - 3 & 0xFFFF
        ref_block = self.client.get_block(properties["head_block_number"] - 2)
        ref_block_prefix = struct.unpack_from("<I", unhexlify(
            ref_block["previous"]), 4)[0]
        expiration = (
                parse(properties["time"]) + timedelta(seconds=30)
        ).strftime('%Y-%m-%dT%H:%M:%S%Z')
        self.transaction["ref_block_num"] = ref_block_num
        self.transaction["ref_block_prefix"] = ref_block_prefix
        self.transaction["expiration"] = expiration

        return self

    def get_known_chains(self):
        return known_chains

    def get_chain_params(self, chain):
        chains = self.get_known_chains()
        if isinstance(chain, str) and chain in chains:
            chain_params = chains[chain]
        elif isinstance(chain, dict):
            chain_params = chain
        else:
            raise Exception("Invalid chain")

        return chain_params

    def derive_digest(self, chain, hex):
        chain_params = self.get_chain_params(chain)
        self.chainid = chain_params["chain_id"]
        self.message = unhexlify(self.chainid + hex[0:-2])
        self.digest = hashlib.sha256(self.message).digest()

    def recover_public_key(self, digest, signature, i):
        curve = ecdsa.SECP256k1.curve
        G = ecdsa.SECP256k1.generator
        order = ecdsa.SECP256k1.order
        yp = (i % 2)
        r, s = ecdsa.util.sigdecode_string(signature, order)
        x = r + (i // 2) * order
        alpha = ((x * x * x) + (curve.a() * x) + curve.b()) % curve.p()
        beta = ecdsa.numbertheory.square_root_mod_prime(alpha, curve.p())
        y = beta if (beta - yp) % 2 == 0 else curve.p() - beta
        R = ecdsa.ellipticcurve.Point(curve, x, y, order)
        e = ecdsa.util.string_to_number(digest)
        Q = ecdsa.numbertheory.inverse_mod(r, order) * (s * R +
                                                        (-e % order) * G)
        if not ecdsa.VerifyingKey.from_public_point(
                Q, curve=ecdsa.SECP256k1).verify_digest(
                    signature, digest, sigdecode=ecdsa.util.sigdecode_string):
            return None
        return ecdsa.VerifyingKey.from_public_point(Q, curve=ecdsa.SECP256k1)

    def compressed_pubkey(self, pk):
        order = pk.curve.generator.order()
        p = pk.pubkey.point
        x_str = ecdsa.util.number_to_string(p.x(), order)
        return compat_bytes(chr(2 + (p.y() & 1)), 'ascii') + x_str

    def recover_pubkey_parameter(self, digest, signature, pubkey):
        for i in range(0, 4):
            if USE_SECP256K1:
                sig = pubkey.ecdsa_recoverable_deserialize(signature, i)
                p = secp256k1.PublicKey(
                    pubkey.ecdsa_recover(self.message, sig))
                if p.serialize() == pubkey.serialize():
                    return i
            else:
                p = self.recover_public_key(digest, signature, i)
                if (p.to_string() == pubkey.to_string()
                        or self.compressed_pubkey(p) == pubkey.to_string()):
                    return i
        return None

    def _is_canonical(self, sig):
        return (not (sig[0] & 0x80)
                and not (sig[0] == 0 and not (sig[1] & 0x80))
                and not (sig[32] & 0x80)
                and not (sig[32] == 0 and not (sig[33] & 0x80)))

    def broadcast(self, operations, chain=None, dry_run=False):
        preferred_api_type = self.client.api_type
        if not isinstance(operations, list):
            operations = [operations, ]

        self.prepare()

        op_list = []
        for operation in operations:
            op_list.append(
                [operation.op_id, operation.op_data],
            )

        self.transaction["operations"] = op_list
        self.transaction["extensions"] = []
        self.transaction["signatures"] = []

        tx_hex = self.client.get_transaction_hex(self.transaction)
        self.derive_digest(chain, tx_hex)

        sigs = []
        for wif in self.client.keys:
            p = compat_bytes(PrivateKey(wif))
            i = 0
            if USE_SECP256K1:
                ndata = secp256k1.ffi.new("const int *ndata")
                ndata[0] = 0
                while True:
                    ndata[0] += 1
                    privkey = secp256k1.PrivateKey(p, raw=True)
                    sig = secp256k1.ffi.new(
                        'secp256k1_ecdsa_recoverable_signature *')
                    signed = secp256k1.lib.secp256k1_ecdsa_sign_recoverable(
                        privkey.ctx, sig, self.digest, privkey.private_key,
                        secp256k1.ffi.NULL, ndata)
                    assert signed == 1
                    signature, i = privkey.ecdsa_recoverable_serialize(sig)
                    if self._is_canonical(signature):
                        i += 4
                        i += 27
                        break
            else:
                cnt = 0
                sk = ecdsa.SigningKey.from_string(p, curve=ecdsa.SECP256k1)
                while 1:
                    cnt += 1
                    if not cnt % 20:
                        print("Still searching for a canonical signature. "
                              "Tried %d times already!" % cnt)

                    k = ecdsa.rfc6979.generate_k(
                        sk.curve.generator.order(),
                        sk.privkey.secret_multiplier,
                        hashlib.sha256,
                        hashlib.sha256(
                            self.digest + struct.pack("d", time.time(
                            ))
                        ).digest())

                    sigder = sk.sign_digest(
                        self.digest, sigencode=ecdsa.util.sigencode_der, k=k)

                    r, s = ecdsa.util.sigdecode_der(sigder,
                                                    sk.curve.generator.order())
                    signature = ecdsa.util.sigencode_string(
                        r, s, sk.curve.generator.order())

                    sigder = array.array('B', sigder)
                    lenR = sigder[3]
                    lenS = sigder[5 + lenR]
                    if lenR is 32 and lenS is 32:
                        i = self.recover_pubkey_parameter(
                            self.digest, signature, sk.get_verifying_key())
                        i += 4
                        i += 27
                        break

            sigstr = struct.pack("<B", i)
            sigstr += signature
            sigs.append(hexlify(sigstr).decode('ascii'))

        self.transaction["signatures"] = sigs
        self.client.api_type = preferred_api_type

        if dry_run:
            return self.transaction

        return self.client.broadcast_transaction(self.transaction)
