import socket
import tqdm
import struct
import argparse


#BLOCK = 1 << 20  # 1MB
BLOCK = 1024

def rdata2(rfile):
    data = rfile.read(BLOCK)
    return data

def rdata(rfile):
    ldata = rfile.read(2)
    xlen = struct.unpack("!h", ldata)  #.encode("cp437"))
    #data = rfile.read(BLOCK if remaining > BLOCK else remaining)
    #print("xlen", xlen)
    data = rfile.read(xlen[0])
    return data


def main(args):

    print(args)

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

    #parser.add_argument('integers', metavar='N', type=int, nargs='+',
    #                    help='an integer for the accumulator')
    #
    parser.add_argument("-p", '--port', dest='port', type=int,
                        default=9999,
                        help='connect to port (default: 9999)')

    parser.add_argument("-t", '--host', dest='host',  nargs='?',
                        default="localhost",
                        help='connect to host (default: localhost)')

    parser.add_argument("-f", '--file', dest='file',  nargs='?',
                        help='download file')

    args = parser.parse_args()
    #print (args.accumulate(args.integers)  )
    main(args)