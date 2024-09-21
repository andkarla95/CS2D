import socket
import threading
import time
import pygame
import json
from player import Player
from bullet import Bullet  # Import the Bullet class

pygame.init()
players = {}  # Dictionary to hold player objects
bullets = []  # List to hold all active bullets
lock = threading.Lock()  # To handle synchronization when modifying the players and bullets

# Function to handle bullet creation when a player shoots
def handle_shoot(player, direction):
    bullet = Bullet(player.rect.centerx, player.rect.centery, direction)
    with lock:
        bullets.append(bullet)

# Function to update the position of all bullets
def update_bullets():
    global bullets
    with lock:
        for bullet in bullets:
            bullet.update()
        # Remove inactive bullets (e.g., those that are off-screen)
        bullets = [bullet for bullet in bullets if bullet.active]

# Function to broadcast the game state (players and bullets) to all clients
def broadcast_state():
    while True:
        try:
            with lock:
                # Convert player address tuples to strings (IP:Port)
                game_state = {
                    "players": {f"{addr[0]}:{addr[1]}": (player.rect.x, player.rect.y) for addr, player in players.items()},
                    "bullets": [(bullet.x, bullet.y) for bullet in bullets if bullet.active]
                }

            # Send the game state as a JSON string
            game_state_json = json.dumps(game_state)
            for addr, player in list(players.items()):
                try:
                    player.conn.sendall(game_state_json.encode())
                except Exception as e:
                    print(f"[ERROR] Unable to send game state to {addr}: {e}")
                    with lock:
                        del players[addr]

        except Exception as e:
            print(f"[BROADCAST ERROR]: {e}")

        # Update bullet positions before broadcasting the next state
        update_bullets()

        # Small delay to control the update rate (e.g., 20 times per second)
        time.sleep(0.05)


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
            # Receive data from the client (e.g., player position, shooting command)
            data = conn.recv(1024).decode()
            if not data:
                print(f"[DISCONNECT] {addr} disconnected.")
                break

            print(f"[DEBUG] Received data from {addr}: {data}")  # Debugging line

            if data.startswith("SHOOT"):
                # Debugging
                print(f"[DEBUG] Handling shoot event for {addr}: {data}")
                
                # Extract shooting direction from the data (assumed to be in the format "SHOOT,x,y")
                _, target_x, target_y = data.split(',')
                direction = (float(target_x) - player.rect.centerx, float(target_y) - player.rect.centery)
                direction = pygame.Vector2(direction).normalize()  # Normalize direction
                handle_shoot(player, direction)  # Handle shooting
            else:
                # Otherwise, update player position (assuming data is position tuple)
                position = eval(data)
                player.update_position(position)

        except Exception as e:
            print(f"[ERROR] Error handling client {addr}: {e}")
            break

    # Remove the player from the global state when they disconnect
    with lock:
        del players[addr]
    conn.close()
    print(f"[CLOSED] Connection closed for {addr}.")


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        server.bind(('192.168.255.25', 5555))  # Use the correct IP address of the server machine
        print("[STARTING] Server is starting...")
    except socket.error as e:
        print(f"[ERROR] Binding failed: {e}")
        return
    
    server.listen()
    print(f"[LISTENING] Server is listening on port 5555...")

    # Start a separate thread to broadcast the game state (players and bullets) to all clients
    broadcast_thread = threading.Thread(target=broadcast_state, daemon=True)
    broadcast_thread.start()

    while True:
        conn, addr = server.accept()
        print(f"[CONNECTION] Connected to {addr}")
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

if __name__ == "__main__":
    main()
