import pygame

class Player:
    def __init__(self, x=50, y=50, width=20, height=20, color=(255, 0, 0), hp=100):
        self.rect = pygame.Rect(x, y, width, height)
        self.velocity = 2
        self.color = color
        self.hp = hp  # Add health to the player

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.rect.y -= self.velocity
        if keys[pygame.K_s]:
            self.rect.y += self.velocity
        if keys[pygame.K_a]:
            self.rect.x -= self.velocity
        if keys[pygame.K_d]:
            self.rect.x += self.velocity

    def get_position(self):
        return self.rect.x, self.rect.y

    def update_position(self, position):
        self.rect.x, self.rect.y = position
                # Keep the player within the screen bounds (assuming screen size 800x600)
        if self.rect.x < 0:
            self.rect.x = 0
        elif self.rect.x + self.rect.width > 800:
            self.rect.x = 800 - self.rect.width

        if self.rect.y < 0:
            self.rect.y = 0
        elif self.rect.y + self.rect.height > 600:
            self.rect.y = 600 - self.rect.height
    
    def is_alive(self):
        return self.hp > 0

    def render(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)  # Render using the player's color
