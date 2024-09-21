import pygame
import sys
from player import Player
from networking import Network
import json

# Configuration
WIDTH, HEIGHT = 800, 600
FPS = 120

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    
    player = Player(color=(255, 0, 0))  # Local player in red
    network = Network()  # Networking to connect to the server
    
    running = True
    other_players = {}  # To store other players' positions
    bullets = []  # To store bullet positions received from the server

    while running:
        shoot_message = ""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Shoot a bullet toward the mouse click
                target_x, target_y = pygame.mouse.get_pos()
                # Send a "SHOOT" message to the server
                shoot_message = f"SHOOT,{target_x},{target_y}"
                # network.send(shoot_message)

        # Get player input (WASD) and send the position to the server
        player.handle_input()
        if shoot_message.startswith("SHOOT"):
            network.send(shoot_message)
        else:
            network.send(player.get_position())  # Send local player's position to the server

        # Get the game state (positions of all players and bullets) from the server
        game_state = network.receive()
        if game_state:
            try:
                game_data = json.loads(game_state)  # Use json.loads() to safely parse the game state
                other_players = game_data["players"]
                bullets = game_data["bullets"]
            except Exception as e:
                print(f"[ERROR] Could not evaluate game state: {e}")

        # Render the game
        screen.fill((0, 0, 0))  # Clear the screen
        
        # Render other players (use string-based player addresses)
        # Render other players
        for addr, data in other_players.items():
            if addr != f"{network.addr[0]}:{network.addr[1]}":  # Don't render the local player
                pos_x, pos_y, hp = data  # Include HP
                pygame.draw.rect(screen, (0, 0, 255), pygame.Rect(pos_x, pos_y, 20, 20))  # Blue for other players
                # Render HP above the player
                font = pygame.font.SysFont(None, 24)
                hp_text = font.render(f"HP: {hp}", True, (255, 255, 255))
                screen.blit(hp_text, (pos_x, pos_y - 20))

        for bullet_pos in bullets:
            pygame.draw.circle(screen, (255, 255, 255), (int(bullet_pos[0]), int(bullet_pos[1])), 5)

        # Render local player (red)
        player.render(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
