import hashlib
import base64
import json
import typing

from Crypto.Cipher import AES
from fastapi import Request, Response
from fastapi.routing import APIRoute


class AESCipher(object):
    def __init__(self, key):
        self.bs = AES.block_size
        self.key = hashlib.sha256(AESCipher.str_to_bytes(key)).digest()

    @staticmethod
    def str_to_bytes(data):
        u_type = type(b"".decode('utf8'))
        if isinstance(data, u_type):
            return data.encode('utf8')
        return data

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s) - 1:])]

    def decrypt(self, enc):
        iv = enc[:AES.block_size]
        _cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(_cipher.decrypt(enc[AES.block_size:]))

    def decrypt_string(self, enc):
        enc = base64.b64decode(enc)
        return self.decrypt(enc).decode('utf8')


class DecryptRequest(Request):

    # async def body(self):
    #     if not hasattr(self, "_body"):
    #         body = await super().body()
    #         if b'{"encrypt":' in body:
    #             b_json = json.loads(body)
    #             b_json = AESCipher("MwmwyPiUgih8SFwihnBVsfrBaLr3IIKy").decrypt_string(b_json['encrypt'])
    #             body = json.dumps(b_json).encode('utf8')
    #         self._body = body
    #     return self._body

    async def json(self) -> typing.Any:
        if not hasattr(self, "_json"):
            b_json = await super().json()
            print(f"decrypt, {b_json}")
            if 'encrypt' in b_json:
                b_json = AESCipher("MwmwyPiUgih8SFwihnBVsfrBaLr3IIKy").decrypt_string(b_json['encrypt'])
            self._json = json.loads(b_json)
        return self._json


class DecryptRoute(APIRoute):
    def get_route_handler(self) -> typing.Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            request = DecryptRequest(request.scope, request.receive)
            return await original_route_handler(request)

        return custom_route_handler


if __name__ == '__main__':
    encrypt = "OeuqzUt323iQYvxbFkaGnSqQqySyn4ObRalbvKzQ+zx/db39bin70BmuqmiloFoRNVewijQCdCZDgF1m0gwyHw9In3O8WNrtyDzFlscWF8SObMfvKmSZdYAB2yBRaWoBM0sRnhYjb6IQ78LGl4TQSrX+gw2KnEl2zEZdekl8atFlgCXlKzZZdFnaD4WIqQsp"
    cipher = AESCipher("MwmwyPiUgih8SFwihnBVsfrBaLr3IIKy")
    print("明文:\n{}".format(cipher.decrypt_string(encrypt)))
