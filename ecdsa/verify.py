from ecdsa import VerifyingKey, BadSignatureError
vk = VerifyingKey.from_pem(open("public.pem").read())
with open("message", "rb") as f:
    message = f.read()
with open("signature", "rb") as f:
    sig = f.read()
try:
    vk.verify(sig, message)
    print ("good signature")
except BadSignatureError:
    print ("BAD SIGNATURE")
