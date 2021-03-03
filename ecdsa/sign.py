from ecdsa import SigningKey
with open("private.pem") as f:
    sk = SigningKey.from_pem(f.read())
with open("message", "rb") as f:
    message = f.read()
sig = sk.sign(message)
with open("signature", "wb") as f:
    f.write(sig)
