import os
import ecdsa
import base64
import hashlib
import binascii


class Signature(object):
    """Class Signature would be use for the corporate providers monobank API"""
    def __init__(self, priv_key):
        self.priv_key = priv_key
        self.sk = self._load()

    def key_id(self):
        """Returns monobank X-Key-Id"""
        public_key = self.sk.get_verifying_key()
        public_key_b64 = base64.b64encode(public_key.to_der())

        uncompressed_public_key = bytearray([0x04]) + (bytearray(public_key.to_string()))
        digests = hashlib.sha1()
        digests.update(uncompressed_public_key)
        return binascii.hexlify(digests.digest())

    def sign(self, str_to_sign):
        """Signs string str_to_sign with private key, and hash sha256"""
        sign = self.sk.sign(str_to_sign.encode(), hashfunc=hashlib.sha256)
        return base64.b64encode(sign)

    def _load(self):
        if "PRIVATE KEY-----" in self.priv_key:
            raw = self.priv_key
        elif os.path.exists(self.priv_key):
            with open(self.priv_key) as f:
                raw = f.read()
        else:
            raise Exception("Cannot load private key")
        return ecdsa.SigningKey.from_pem(raw)
