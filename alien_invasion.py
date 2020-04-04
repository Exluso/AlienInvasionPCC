import sys
import pygame
from time import sleep
from settings import Settings
from ship import Ship
from bullet import Bullet
from alien import Alien
from game_stats import GameStats
from button import Button


class AlienInvasion:
    """Overall class to manage game assets and behaviour."""

    def __init__(self):
        pygame.init()
        self.settings = Settings()
        self.screen = pygame.display.set_mode(
            (self.settings.screen_width, self.settings.screen_height))
        pygame.display.set_caption("Alien Invasion")
        self.stats = GameStats(self)
        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self._create_fleet()
        self.play_button = Button(self, "Play")

    def run_game(self):
        """Start the main loop for the game."""
        while True:
            # watch for keyboard and mouse events
            self._check_events()
            if self.stats.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()
            self._update_screen()

    def _create_fleet(self):
        """Create the fleet of aliens."""
        alien = Alien(self)
        # self.aliens.add(alien)
        alien_width, alien_height = alien.rect.size
        available_space_x = self.settings.screen_width - 2 * alien_width
        number_aliens_x = available_space_x // (2 * alien_width)
        # Determine the number of rows of aliens that fit on the screen
        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height - ship_height
                             - (3 * alien_height))
        number_rows = available_space_y // (2 * alien_height)

        # create the rows of aliens
        for row in range(number_rows):
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number, row)

    def _create_alien(self, alien_number, row):
        """Create an alien and place it in the row."""
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        alien.x = alien_width + (alien_number * (2 * alien_width))
        alien.y = alien_height + (row * (2 * alien_height))
        alien.rect.x, alien.rect.y = alien.x, alien.y
        self.aliens.add(alien)

    def _check_fleet_edges(self):
        """Reacts appropiately when any alien in the fleet reaches the edge"""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        """Drop the fleet down then make it moves in the opposite direction."""
        for alien in self.aliens.sprites():
            alien.rect.y += alien.settings.alien_drop_speed
        self.settings.fleet_direction *= -1

    def _check_events(self):
        """Respond to keypresses and mouse events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)

    def _check_play_button(self, mouse_pos):
        """Checks if the play_button was hit and if so starts the game."""
        if self.play_button.rect.collidepoint(mouse_pos)\
                and not self.stats.game_active:
            # Reset game stats
            self.stats.reset_stats()
            self.stats.game_active = True

            # get rid of old aliens and bullets
            self.bullets.empty()
            self.aliens.empty()

            # Create a new fleet and center the ship
            self._create_fleet()
            self.ship.center_ship()


    def _check_keydown_events(self, event):
        """Respond to keypresses."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_w:
            self.change_view()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()

    def _check_keyup_events(self, event):
        """Respond to key releases."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _fire_bullet(self):
        """Create a new bullet and add it tot he bullet group"""
        if len(self.bullets) < self.settings.bullet_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _update_bullets(self):
        """Update position of bullets and get rid of old bullets."""
        self.bullets.update()
        # get rid of bullets that have reached the top of the screen
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
        self._check_alien_bullet_collision()

    def _check_alien_bullet_collision(self):
        # Respond to alien bullet collision
        # Remove any bullet and alien that have collided
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens,
                                                True, True)
        if not self.aliens:
        # destroy bullet and create new fleet
            self.bullets.empty()
            self._create_fleet()

    def _update_aliens(self):
        """Check if the fleet is at an edge,
        then updates the position of all aliens in the fleet."""
        self._check_fleet_edges()
        self.aliens.update()
        self._check_alien_ship_collision()
        # look for alien reaching the bottom of the screen
        self._check_aliens_bottom()

    def _check_alien_ship_collision(self):
        """Respond to alien ship collision"""
        for alien in self.aliens.sprites():
            if pygame.sprite.spritecollideany(self.ship, self.aliens):
                self._ship_hit()

    def _check_aliens_bottom(self):
        """Che if any alien has reached the bottom of the screen."""
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                self._ship_hit()
                break

    def _ship_hit(self):
        """Respond to ship being hit by an alien"""
        if self.stats.ship_left > 0:
            # Decrement ships left
            self.stats.ship_left -= 1

            #Get rid of any left alien or bullet
            self.aliens.empty()
            self.bullets.empty()

            # create a new fleet and center the ship
            self._create_fleet()
            self.ship.center_ship()

            # Pause
            sleep(1)
        else:
            self.stats.game_active = False

    def _update_screen(self):
        """Update images on the screen and flip to the new screen."""
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme()
        for bullet in self.bullets:
            bullet.draw_bullet()
        self.aliens.draw(self.screen)
        # Draw the play button if the game is inactive
        if not self.stats.game_active:
            self.play_button.draw_button()

        pygame.display.flip()

    def change_view(self):
        """ Switches between full screen and windowed mode"""
        if not self.settings.full_screen:
            self.settings.full_screen = True
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            self.settings.screen_width = self.screen.get_rect().width
            self.settings.screen_height = self.screen.get_rect().height
        elif self.settings.full_screen:
            self.settings.full_screen = False
            self.settings.screen_width = 1200
            self.settings.screen_height = 800
            self.screen = pygame.display.set_mode(
                (self.settings.screen_width, self.settings.screen_height))

        pygame.display.flip()


if __name__ == "__main__":
    # make a game instance, and run the game.
    ai = AlienInvasion()
    ai.run_game()
