import socket
import threading
import time
from player import Player

players = {}  # Dictionary to hold player objects
lock = threading.Lock()  # To handle synchronization when modifying the players dictionary

def broadcast_state():
    """
    This function sends the current game state (positions of all players)
    to all connected clients at regular intervals.
    """
    while True:
        # Send the state to all connected clients
        try:
            with lock:  # Acquire lock once before generating the game state
                game_state = {addr: (player.rect.x, player.rect.y) for addr, player in players.items()}

            # Broadcast the state to all connected clients
            for addr, player in list(players.items()):  # Use list to safely iterate while modifying
                try:
                    player.conn.sendall(str(game_state).encode())  # Consider switching to a more efficient format
                except Exception as e:
                    print(f"[ERROR] Unable to send game state to {addr}: {e}")
                    # Handle disconnected clients by removing them
                    with lock:
                        del players[addr]

        except Exception as e:
            print(f"[BROADCAST ERROR]: {e}")

        # Small sleep to avoid overwhelming the network (adjust this value to balance latency vs performance)
        time.sleep(0.01)  # 50ms interval = 20 updates per second

def handle_client(conn, addr):
    """
    This function is run in a thread for each client connection. 
    It handles the reception of data from the client and updates the player's state.
    """
    print(f"[NEW CONNECTION] {addr} connected.")  # Debugging line
    player = Player()  # Create a new player for this client
    player.conn = conn  # Store the client's connection in the player object
    
    with lock:
        players[addr] = player  # Add player to the global state

    while True:
        try:
            # Receive player data (position, etc.)
            data = conn.recv(1024).decode()
            if not data:
                print(f"[DISCONNECT] {addr} disconnected.")  # Debugging line
                break

            print(f"[RECEIVED] Data from {addr}: {data}")  # Debugging line

            # Update player's position (assuming data is a tuple of (x, y))
            with lock:
                player.update_position(eval(data))  # Convert received string to tuple
            
        except Exception as e:
            print(f"[ERROR] Error handling client {addr}: {e}")  # Debugging line
            break

    # Remove the player from the global state
    with lock:
        del players[addr]

    conn.close()
    print(f"[CLOSED] Connection closed for {addr}.")  # Debugging line

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        server.bind(('192.168.39.25', 5555))  # Use the correct IP address of the server machine
        print("[STARTING] Server is starting...")  # Debugging line
    except socket.error as e:
        print(f"[ERROR] Binding failed: {e}")  # Debugging line
        return
    
    server.listen()
    print(f"[LISTENING] Server is listening on port 5555...")  # Debugging line

    # Start a separate thread to broadcast the game state to all clients
    broadcast_thread = threading.Thread(target=broadcast_state, daemon=True)
    broadcast_thread.start()

    while True:
        conn, addr = server.accept()
        print(f"[CONNECTION] Connected to {addr}")  # Debugging line
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

if __name__ == "__main__":
    main()
