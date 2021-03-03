from ecdsa import SigningKey, NIST384p
sk = SigningKey.generate(curve=NIST384p)
sk_string = sk.to_string()
sk2 = SigningKey.from_string(sk_string, curve=NIST384p)
print(sk_string.hex())
print(sk2.to_string().hex())

