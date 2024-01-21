import socket
import os
import threading
import sys

#BLOCK = 128 << 10 # 128KB
BLOCK = 1024

class  write_parm():

    def __init__(self, *argx):
        (self.cargs) = argx
        pass

class  serve_writer():

    def __init__(self, *argx):
        parms = write_parm(argx)
        writer_thread = threading.Thread(target=self.run, args=(parms,))
        writer_thread.start()

    def run(self, *argx):

        #print(argx[0].cargs)

        wfile, fullname = argx[0].cargs[0]
        #print("writer")

        try:
            file_size = os.path.getsize(fullname)
            wfile.write(f'{file_size}\n'.encode())
            print(f'Sending {fullname}...')
            with open(fullname, 'rb') as file:
                while data := file.read(BLOCK):
                    wfile.write(data)

            wfile.flush() # make sure anything remaining in makefile buffer is sent.
            print(f' Complete ({file_size} bytes).')
        except:
            print(sys.exc_info())

class serve_one():

    def __init__(self, *argx):
        self.cnt = 0
        server_thread = threading.Thread(target=self.run, args=argx)
        server_thread.start()

    def run(self, *argx):

        self.client, addr = argx
        try:
            with (self.client,
                  self.client.makefile('wb') as wfile,
                  self.client.makefile('rb') as rfile):

                while True:
                    self.cnt += 1
                    print("cycle", self.cnt)

                    filename = rfile.readline()
                    if not filename: return

                    fullname = os.path.join('Server_files', filename.decode().rstrip('\n'))

                    serve_writer(wfile, fullname)
                    while True:
                        rdata = rfile.readline()
                        #print("reading", rdata, end=" ")
                        if not rdata:
                            break
                        if  rdata == b"\n":
                            break

                        #print(rdata)

        except ConnectionResetError:
            print('Client aborted.')
        except:
            print(sys.exc_info())

        print("ended thread")

with socket.socket() as server:
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server.bind(('', 9999))
    server.listen()
    while True:
        client, addr = server.accept()
        serve_one(client, addr)

