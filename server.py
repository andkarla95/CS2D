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
    bullet = Bullet(player.rect.centerx, player.rect.centery, direction, owner=player)  # Pass the player as the owner
    with lock:
        bullets.append(bullet)

# Function to update the position of all bullets
def update_bullets():
    global bullets
    with lock:
        for bullet in bullets:
            bullet.update()

            # Check for collision with each player (except the owner within immunity period)
            for addr, player in players.items():
                if player != bullet.owner or bullet.immunity_frames == 0:  # Ignore owner for first few frames
                    if player.rect.collidepoint(bullet.x, bullet.y):  # Bullet hits the player
                        player.hp -= bullet.damage  # Reduce player HP by bullet damage
                        print(f"[DEBUG] Player {addr} hit! HP: {player.hp}")  # Debugging line
                        bullet.active = False  # Deactivate bullet after collision

                        if not player.is_alive():
                            print(f"[DEBUG] Player {addr} is dead.")  # Debugging line
                            del players[addr]  # Remove the player when HP reaches 0
                            break

        # Remove inactive bullets (e.g., off-screen or after a collision)
        bullets = [bullet for bullet in bullets if bullet.active]

# Function to broadcast the game state (players and bullets) to all clients
def broadcast_state():
    while True:
        try:
            with lock:
                # Include HP in the player data
                game_state = {
                    "players": {f"{addr[0]}:{addr[1]}": (player.rect.x, player.rect.y, player.hp) for addr, player in players.items()},
                    "bullets": [(bullet.x, bullet.y) for bullet in bullets if bullet.active]
                }

            # Send the game state as a JSON string with a newline as a separator
            game_state_json = json.dumps(game_state) + "\n"
            for addr, player in list(players.items()):
                try:
                    player.conn.sendall(game_state_json.encode())
                except Exception as e:
                    print(f"[ERROR] Unable to send game state to {addr}: {e}")
                    with lock:
                        del players[addr]

        except Exception as e:
            print(f"[BROADCAST ERROR]: {e}")

        update_bullets()
        time.sleep(0.01)




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
                data = data.split("(")[0]
                data = "S" + data.split("S")[1]
                # Debugging
                print(f"[DEBUG] Handling shoot event for {addr}: {data}")
                
                # Extract shooting direction from the data (assumed to be in the format "SHOOT,x,y")
                _, target_x, target_y = data.split(',')
                direction = (float(target_x) - player.rect.centerx, float(target_y) - player.rect.centery)
                direction = pygame.Vector2(direction).normalize()  # Normalize direction
                handle_shoot(player, direction)  # Handle shooting
            else:
                # Otherwise, update player position (assuming data is position tuple)
                position = eval(data.split(")")[0] +")")
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
        server.bind(('192.168.244.25', 5555))  # Use the correct IP address of the server machine
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
