import socket
import threading
import socketserver
import time

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
        while True:
            data = self.request.recv(1024)
            cur_thread = threading.current_thread()
            #response = "{}: {}".format(cur_thread.name, data)
            #self.request.sendall(response.encode("utf-8"))
            #self.request.sendall(b"OK")
            if not data:
                break

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

def client(ip, port, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))

    prog = 0   ; chunk = 1000
    try:
        while True:
            sock.sendall(message[prog:prog + chunk])
            prog += chunk
            #response = sock.recv(1024)
            #print ("Received: {} {}".format(prog, response[:10]))
            if prog >= len(message):
                    break

    finally:
        sock.close()

if __name__ == "__main__":
    # Port 0 means to select an arbitrary unused port
    HOST, PORT = "localhost", 0

    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    ip, port = server.server_address

    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = threading.Thread(target=server.serve_forever)
    # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    server_thread.start()
    print ("Server loop running in thread:", server_thread.name)

    ttt = time.time()
    size = 1000 * 1000 * 10
    client(ip, port, b"a" * size)
    ddd = time.time() - ttt
    print("time: %.2f %.0f kbs" % (ddd, (size/1000) / ddd))
    #client(ip, port, b"Hello World 2")
    #client(ip, port, b"Hello World 3")

    server.shutdown()

    server.server_close()
