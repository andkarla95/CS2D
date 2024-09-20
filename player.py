import pygame

class Player:
    def __init__(self, x=50, y=50, width=20, height=20, color=(255, 0, 0)):
        self.rect = pygame.Rect(x, y, width, height)
        self.velocity = 5

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

    def render(self, screen):
        pygame.draw.rect(screen, (255, 0, 0), self.rect)
