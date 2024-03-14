from __future__ import print_function

import socket
import os
import threading
import sys
import struct
import argparse

from Crypto import Random
from Crypto.Hash import SHA512
from Crypto.Cipher import AES

base = os.path.dirname(os.path.realpath(__file__))

#sys.path.append(os.path.join(base, '../bluepy'))
#import bluepy

from cfilecomm import *

#iv = Random.new().read(AES.block_size)
#cipher = AES.new(key, AES.MODE_ECB)
#cipher = None #AES.new(key, AES.MODE_CTR)
#cipher = AES.new(key, AES.MODE_ECB, iv)
#cipher = AES.new(key, AES.MODE_CTR,
#                        use_aesni=True, nonce = b'12345678')

class  serve_writer():

    def __init__(self, *argx):
        self.parms = argx
        writer_thread = threading.Thread(target=self.run)
        writer_thread.start()

    def swrite2(self, wfile, data):
        ret = wfile.write(data)
        return ret

    def swrite(self, wfile, data):
        #datac = bluepy.encrypt(data, "1234")
        #datac = data[:]
        #ddd = cipher.encrypt(data)
        datac = self.cipher.encrypt(data)
        #print(len(cipher.nonce), cipher.nonce)
        #datac = iv + cipher.encrypt(data)

        data2 = struct.pack("!h", len(datac)) + datac
        ret = wfile.write(data2)
        return ret

    def run(self, *parms):
        wfile, fullname, args = self.parms
        try:
            file_size = os.path.getsize(fullname)
            wfile.write(f'{file_size}\n'.encode())
            if args.verbose:
                print(f'Sending {fullname} ... ', end="")
                sys.stdout.flush()
            self.cipher = AES.new(key, AES.MODE_CTR,
                        use_aesni=True, nonce = b'12345678')

            #wfile.write(nonce + b'\n')

            with open(fullname, 'rb') as file:
                while data := file.read(BLOCK):
                    self.swrite(wfile, data)
                    if len(data) < BLOCK:
                        break

            # make sure anything remaining in makefile buffer is sent.
            wfile.flush()
            if args.verbose:
                print(f' Complete ({file_size} bytes).')
        except:
            print(sys.exc_info())

# Execute one server cycle

class serve_one():

    def __init__(self, *argx):
        self.cnt = 0
        self.argx = argx
        server_thread = threading.Thread(target=self.run)
        server_thread.start()

    def run(self, *argx):

        self.client, self.addr, self.args =  self.argx
        try:
            with (self.client,
                  self.client.makefile('wb') as self.wfile,
                  self.client.makefile('rb') as self.rfile):

                while True:
                    self.cnt += 1
                    #print("cycle", self.cnt)

                    filename = self.rfile.readline()
                    if not filename: return

                    fullname = os.path.join('server_files',
                                    filename.decode().rstrip('\n'))

                    serve_writer(self.wfile, fullname, self.args)

                    while True:
                        rdata = self.rfile.readline()
                        if self.args.verbose > 1:
                            print(rdata, end=" ")
                            sys.stdout.flush()

                        if not rdata:
                            break
                        if  rdata == b"\n":
                            break

                        #print(rdata)

        except ConnectionResetError:

            print(sys.exc_info())
            print('Client aborted.')
        except:
            print(sys.exc_info())

        print("ended thread")

def server(args):
    with socket.socket() as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        server.bind(('', args.port))
        server.listen()
        while True:
            client, addr = server.accept()
            client.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            serve_one(client, addr, args)

def main(args):
    server(args)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Process some integers.')

    parser.add_argument("-p", '--port', dest='port', type=int,
                        default=9999,
                        help='Connect to port (default: 9999)')

    parser.add_argument("-v", '--verbose', dest='verbose',
                        default=0,  action='count',
                        help='verbocity on (default: off)')

    parser.add_argument("-f", '--file', dest='file',  nargs='?',
                        help='download file')

    args = parser.parse_args()
    main(args)







