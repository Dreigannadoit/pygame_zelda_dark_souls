import pygame
import sys

from level import Level
from settings import *

# Project By Robert Bamba
class Game:
    def __init__(self):

        # general setup
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGTH))
        pygame.display.set_caption('Beach face')
        self.clock = pygame.time.Clock()

        self.level = Level()

        # bg music
        main_sound = pygame.mixer.Sound('./audio/main.ogg')
        main_sound.set_volume(0.4)
        main_sound.play(loops = -1)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c:
                        self.level.toggle_menu()

            self.screen.fill(WATER_COLOR)
            self.level.run()
            pygame.display.update()
            self.clock.tick(FPS)

if __name__ == '__main__':
    game = Game()
    game.run()



