import socket
import tqdm
import struct
import argparse
import os
import sys

base = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(base, '../bluepy'))

import bluepy

from Crypto import Random
from Crypto.Cipher import AES

#BLOCK = 1 << 20  # 1MB
BLOCK = 1024

def rdata2(rfile, remaining):
    #data = rfile.read(BLOCK)
    data = rfile.read(BLOCK if remaining > BLOCK else remaining)
    return data

key = b'Sixteen byte key'
iv = Random.new().read(AES.block_size)
cipher = AES.new(key, AES.MODE_CFB, iv)

def rdata(rfile):
    ldata = rfile.read(2)
    xlen = struct.unpack("!h", ldata)  #.encode("cp437"))
    #print("xlen", xlen)
    data2 = rfile.read(xlen[0])
    #data = bluepy.decrypt(data2, "1234")
    #data = data2[:]

    data = iv + cipher.decrypt(data2)

    return data

def main(args):

    #print(args)

    with socket.socket() as client:

        client.connect((args.host, args.port))

        client.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        with (client.makefile('rb') as rfile,
              client.makefile('wb') as wfile):

            while True:
                if  args.file:
                    file_name = args.file
                else:
                    file_name = input('File name (just ENTER to quit): ')

                if not file_name: break
                wfile.write(f'{file_name}\n'.encode())
                wfile.flush() # make sure makefile buffer is fully sent
                file_size = int(rfile.readline().decode())

                with (tqdm.tqdm(unit='B',
                                unit_scale=True,
                                unit_divisor=1000,
                                total=file_size) as progress,
                      open(file_name, 'wb') as file):

                    remaining = file_size
                    while remaining:

                        #data = rdata2(rfile, remaining)
                        data = rdata(rfile)
                        if not data:
                            break

                        file.write(data)

                        progress.update(len(data))
                        remaining -= len(data)
                        #
                        wfile.write(b"OK\n")
                    wfile.write(b"\n")
                    wfile.flush()
                if  args.file:
                    break

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Process some integers.')

    parser.add_argument("-p", '--port', dest='port', type=int,
                        default=9999,
                        help='Connect to port (default: 9999)')

    parser.add_argument("-v", '--verbose', dest='verbose',
                        default=0,  action='count',
                        help='verbocity on (default: off)')

    parser.add_argument("-t", '--host', dest='host',  nargs='?',
                        default="localhost",
                        help='Connect to host (default: localhost)')

    parser.add_argument("-f", '--file', dest='file',  nargs='?',
                        help='download file')

    args = parser.parse_args()
    main(args)






