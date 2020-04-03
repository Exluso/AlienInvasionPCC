import pygame
from pygame.sprite import Sprite

class Alien(Sprite):
    """A Class to represent a single alien in the fleet."""

    def __init__(self, ai_game):
        "initialize the alien and sets its starting position"
        super().__init__()
        self.screen = ai_game.screen

        # load the alien image and set its rect attributte
        self.image = pygame.image.load("images/alien.bmp")
        self.rect = self.image.get_rect()

        # Start each new alien near the top left of the screen
        self.rect.x = self.rect.width
        self.rect.y = self.rect.height

        # Store the alien exact horizontal position
        self.x = float(self.rect.x)
