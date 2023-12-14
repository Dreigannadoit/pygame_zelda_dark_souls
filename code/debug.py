import pygame
from settings import *

pygame.init()
font = pygame.font.Font(None, 30)


def debug(info, y=HEIGTH - 30, x=WIDTH - (WIDTH / 1.23)):
    display_surface = pygame.display.get_surface()
    debug_surf = font.render(str(info), True, 'White')
    debug_rect = debug_surf.get_rect(topleft=(x, y))
    pygame.draw.rect(display_surface, 'DarkBlue', debug_rect.inflate(5, 5))
    display_surface.blit(debug_surf, debug_rect)


def FPS_show(info, y=HEIGTH - 55, x=WIDTH - (WIDTH / 1.8)):
    display_surface = pygame.display.get_surface()
    debug_surf = font.render(str(info), True, 'White')
    debug_rect = debug_surf.get_rect(topleft=(x, y))
    pygame.draw.rect(display_surface, 'DarkBlue', debug_rect.inflate(5, 5))
    display_surface.blit(debug_surf, debug_rect)
