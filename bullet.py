import pygame

class Bullet:
    def __init__(self, x, y, direction, speed=10, color=(255, 255, 255), radius=5):
        self.x = x
        self.y = y
        self.direction = direction  # Aiming direction (a vector)
        self.speed = speed
        self.color = color
        self.radius = radius
        self.active = True  # To track if the bullet is still active (for collision or off-screen)

    def update(self):
        """
        Update the bullet's position based on its direction and speed.
        """
        self.x += self.direction[0] * self.speed
        self.y += self.direction[1] * self.speed

        # Deactivate the bullet if it goes off-screen (simple bounds check)
        if self.x < 0 or self.x > 800 or self.y < 0 or self.y > 600:  # Assuming screen size 800x600
            self.active = False

    def render(self, screen):
        """
        Draw the bullet on the screen.
        """
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
