class GameStats():
    """ A class to handle statistics"""
    def __init__(self, ai_game):
        """Initialize game_stats"""
        self.settings = ai_game.settings
        self.reset_stats()
        self.game_active = True

    def reset_stats(self):
        """Initialize statistic that can change during the game."""
        self.ship_left = self.settings.ship_limit