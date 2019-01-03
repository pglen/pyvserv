#!/usr/bin/env python

import os, sys, string, time, traceback
import gnupg

gpg = gnupg.GPG() #gnupghome=os.environ['HOME'])
input_data = gpg.gen_key_input(
    name_email='testgpguser@mydomain.com',
    passphrase='1234')
    
key = gpg.gen_key(input_data)
print key

from pprint import pprint

'''
public_keys = gpg.list_keys()
private_keys = gpg.list_keys(True)
print 'public keys:'
pprint(public_keys)
print 'private keys:'
pprint(private_keys)
'''

unencrypted_string = 'Who are you? How did you get in my house?'
encrypted_data = gpg.encrypt(unencrypted_string, 'testgpguser@mydomain.com')
encrypted_string = str(encrypted_data)
decrypted_data = gpg.decrypt(encrypted_string, passphrase='1234')

print 'ok: ', decrypted_data.ok
print 'status: ', decrypted_data.status
print 'stderr: ', decrypted_data.stderr
print 'decrypted string: ', decrypted_data.data

input_data2 = gpg.gen_key_input(key_type="RSA", key_length=1024, passphrase='1234')
key2 = gpg.gen_key(input_data2)

print "key2", key2

ascii_armored_public_keys = gpg.export_keys((key2))
ascii_armored_private_keys = gpg.export_keys((key2), True)

with open('mykeyfile.asc', 'w') as f:
    f.write(ascii_armored_public_keys)
    f.write(ascii_armored_private_keys)


