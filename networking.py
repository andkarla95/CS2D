import socket

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = '192.168.39.25'  # Server IP address
        self.port = 5555
        self.addr = (self.server, self.port)
        self.connect()

    def connect(self):
        try:
            self.client.connect(self.addr)
        except:
            pass

    def send(self, data):
        try:
            self.client.send(str(data).encode())
        except socket.error as e:
            print(e)

    def receive(self):
        try:
            return self.client.recv(1024).decode()  # Receive game state from the server
        except:
            return None
