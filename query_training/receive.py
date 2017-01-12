from multiprocessing.connection import Client

address = ('localhost', 7979)

conn = Client(address)
while True:
    conn.recv_bytes(2048)