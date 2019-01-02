#!/usr/bin/env python

import os, sys, string, time, traceback


import gnupg

gpg = gnupg.GPG() #gnupghome='/home/testgpguser/gpghome')
input_data = gpg.gen_key_input(
    name_email='testgpguser@mydomain.com',
    passphrase='my passphrase')
key = gpg.gen_key(input_data)

print key


from pprint import pprint

gpg = gnupg.GPG(gnupghome='/home/testgpguser/gpghome')
public_keys = gpg.list_keys()
private_keys = gpg.list_keys(True)
print 'public keys:'
pprint(public_keys)
print 'private keys:'
pprint(private_keys)



gpg = gnupg.GPG() #gnupghome='/home/testgpguser/gpghome')
unencrypted_string = 'Who are you? How did you get in my house?'
encrypted_data = gpg.encrypt(unencrypted_string, 'testgpguser@mydomain.com')
encrypted_string = str(encrypted_data)
decrypted_data = gpg.decrypt(encrypted_string, passphrase='my passphrase')

print 'ok: ', decrypted_data.ok
print 'status: ', decrypted_data.status
print 'stderr: ', decrypted_data.stderr
print 'decrypted string: ', decrypted_data.data

gpg = gnupg.GPG() #gnupghome='/home/testgpguser/gpghome')
ascii_armored_public_keys = gpg.export_keys(key)
ascii_armored_private_keys = gpg.export_keys(key, True)

with open('mykeyfile.asc', 'w') as f:
    f.write(ascii_armored_public_keys)
    f.write(ascii_armored_private_keys)

