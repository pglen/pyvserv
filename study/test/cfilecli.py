import socket
import tqdm
import struct
#BLOCK = 1 << 20  # 1MB
BLOCK = 1024

with socket.socket() as client:
    client.connect(('localhost', 9999))

    with (client.makefile('rb') as rfile,
          client.makefile('wb') as wfile):

        while True:
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
                    ldata = rfile.read(2)
                    xlen = struct.unpack("!h", ldata)  #.encode("cp437"))
                    #data = rfile.read(BLOCK if remaining > BLOCK else remaining)
                    #print("xlen", xlen)
                    data = rfile.read(xlen[0])
                    file.write(data)
                    progress.update(len(data))
                    remaining -= len(data)
                    #
                    wfile.write(b"OK\n")
                wfile.write(b"\n")
                wfile.flush()

