import socket
import threading
from player import Player

players = {}  # Dictionary to hold player objects

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")  # Debugging line
    player = Player()  # Create a new player for this client
    players[addr] = player  # Add player to the global state

    while True:
        try:
            # Receive player data (position, etc.)
            data = conn.recv(1024).decode()
            if not data:
                print(f"[DISCONNECT] {addr} disconnected.")  # Debugging line
                break

            print(f"[RECEIVED] Data from {addr}: {data}")  # Debugging line

            # Update player's position
            player.update_position(eval(data))  # Convert received string to tuple
            
            # Broadcast game state to all players
            for player_conn in players:
                conn.sendall(str(players).encode())

        except Exception as e:
            print(f"[ERROR] Error handling client {addr}: {e}")  # Debugging line
            break

    conn.close()
    del players[addr]
    print(f"[CLOSED] Connection closed for {addr}.")  # Debugging line

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        server.bind(('192.168.39.25', 5555))
        print("[STARTING] Server is starting...")  # Debugging line
    except socket.error as e:
        print(f"[ERROR] Binding failed: {e}")  # Debugging line
        return
    
    server.listen()
    print(f"[LISTENING] Server is listening on port 5555...")  # Debugging line

    while True:
        conn, addr = server.accept()
        print(f"[CONNECTION] Connected to {addr}")  # Debugging line
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

if __name__ == "__main__":
    main()
