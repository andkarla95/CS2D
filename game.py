import pygame
import sys
from player import Player
from networking import Network

# Configuration
WIDTH, HEIGHT = 800, 600
FPS = 60

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    
    player = Player(color=(255, 0, 0))  # Local player in red
    network = Network()  # Networking to connect to the server
    
    running = True
    other_players = {}  # To store other players' positions

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Get player input (WASD) and send the position to the server
        player.handle_input()
        network.send(player.get_position())  # Send local player's position to the server

        # Get the game state (positions of all players) from the server
        game_state = network.receive()
        if game_state:
            other_players = eval(game_state)  # Convert received string to dictionary
        
        # Render the game
        screen.fill((0, 0, 0))  # Clear the screen
        
        # Render other players
        for addr, pos in other_players.items():
            if addr != network.addr:  # Do not draw the local player from the received state
                pygame.draw.rect(screen, (0, 0, 255), pygame.Rect(pos[0], pos[1], 20, 20))  # Blue for other players

        # Render local player (red)
        player.render(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
