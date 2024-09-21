import socket

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = '192.168.244.25'  # Replace with your server IP
        self.port = 5555
        self.addr = (self.server, self.port)
        self.connect()

    def connect(self):
        try:
            self.client.connect(self.addr)
        except Exception as e:
            print(f"[ERROR] Could not connect to server: {e}")

    def send(self, data):
        try:
            self.client.send(str(data).encode())
        except socket.error as e:
            print(e)

    def receive(self):
        buffer = ""  # Buffer to store incoming data
        try:
            while True:
                data = self.client.recv(1024).decode()  # Receive up to 1024 bytes
                buffer += data
                if "\n" in buffer:  # Check if a complete JSON object has been received
                    message, buffer = buffer.split("\n", 1)  # Extract the message and leave any remaining data
                    return message
        except Exception as e:
            print(f"[ERROR] Receiving data: {e}")
            return None
