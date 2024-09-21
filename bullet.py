import pygame

class Bullet:
    def __init__(self, x, y, direction, owner, speed=6, color=(255, 255, 255), radius=5, damage=10):
        self.x = x
        self.y = y
        self.direction = direction  # Aiming direction (a vector)
        self.owner = owner  # The player who fired the bullet
        self.speed = speed
        self.color = color
        self.radius = radius
        self.active = True  # To track if the bullet is still active (for collision or off-screen)
        self.damage = damage
        self.immunity_frames = 10  # Number of frames bullet is immune to hit the owner after firing

    def update(self):
        """
        Update the bullet's position based on its direction and speed.
        """
        self.x += self.direction[0] * self.speed
        self.y += self.direction[1] * self.speed

        # Decrease immunity frame counter (if > 0)
        if self.immunity_frames > 0:
            self.immunity_frames -= 1

        # Deactivate the bullet if it goes off-screen (simple bounds check)
        if self.x < 0 or self.x > 800 or self.y < 0 or self.y > 600:  # Assuming screen size 800x600
            self.active = False

    def render(self, screen):
        """
        Draw the bullet on the screen.
        """
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
