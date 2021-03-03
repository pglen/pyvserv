from ecdsa import ECDH, NIST256p

ecdh = ECDH(curve=NIST256p)
ecdh.generate_private_key()
local_public_key = ecdh.get_public_key()
#send `local_public_key` to remote party and receive `remote_public_key` from remote party
with open("remote_public_key.pem") as e:
    remote_public_key = e.read()
ecdh.load_received_public_key_pem(remote_public_key)
secret = ecdh.generate_sharedsecret_bytes()
