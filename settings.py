import pygame, sys
from pygame.math import Vector2 as vector

WIN_WIDTH, WIN_HEIGHT = 800, 400
TILE_SIZE = 32
ANIMATION_SPEED = 6

Z_LAYERS = {
    'background': 0,
    'clouds': 1,
    'background tiles': 2,
    'background details': 3,
    'main': 4,
    'water': 5,
    'frontground': 6
} 



