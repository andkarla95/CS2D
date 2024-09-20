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
    player = Player()
    
    network = Network()  # Networking to connect to the server
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Get player input (WASD) and send to the server
        player.handle_input()
        network.send(player.get_position())  # Send player position to server
        
        # Get updated game state from the server
        game_state = network.receive()  # Get updated state
        # Render the game
        screen.fill((0, 0, 0))  # Clear screen
        player.render(screen)
        # Render other players from game_state
        
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
