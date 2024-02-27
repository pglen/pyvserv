from ecies.utils import generate_key
from ecies import encrypt, decrypt
from coincurve.keys import PrivateKey, PublicKey, PublicKeyXOnly
from coincurve.utils import bytes_to_int, int_to_bytes_padded, verify_signature

import time, base64

def wrap(xkey):
    ret = "-----BEGIN PUBLIC KEY-----\n"
    ret += base64.b64encode(xkey).decode()
    ret += "\n-----END PUBLIC KEY-----\n"
    return ret

def unwrap(xkey):
    #print(xkey[27:-24])
    ret = base64.b64decode(xkey[27:-24])
    return ret

ecc_k = generate_key()
sk_hex = ecc_k.to_hex()  # hex string
print(sk_hex)
sk_pem = ecc_k.to_pem()
print(sk_pem.decode())

pk_bin = ecc_k.public_key.format()
print(pk_bin)

wrpd = wrap(pk_bin)
print(wrpd)
#print(unwrap(wrpd))

#data = b'this is a test'
data = \
b"this is a test " * 30

print("org:", data)

ttt = time.time()
#eee = encrypt(pk_bin, data)
eee = encrypt(unwrap(wrpd), data)
print("enc %.3f" % ((time.time() - ttt) * 1000) )

ttt = time.time()
bbb = decrypt(PrivateKey.from_pem(sk_pem).to_hex(), eee)
print("dec %.3f" % ((time.time() - ttt) * 1000) )

#print ("cyph:", eee)
print("decr:", bbb)

# EOF
