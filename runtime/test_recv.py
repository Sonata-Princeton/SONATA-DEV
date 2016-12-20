from multiprocessing.connection import Client


conn = Client(('localhost', 8989))
while True:
    line = conn.recv_bytes()
    print line
