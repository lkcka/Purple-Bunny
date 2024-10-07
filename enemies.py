from settings import *
from random import choice

class Slime(pygame.sprite.Sprite):
    '''
    Класс Slime представляет собой врага в игре. Он перемещается по горизонтали и меняет направление при столкновении с препятствиями.
    '''
    def __init__(self, pos, frames, groups, collision_sprites):
        '''
        Инициализирует объект Slime.

        Аргументы:
        - pos (tuple): Начальная позиция спрайта (x, y).
        - frames (list): Список кадров анимации.
        - groups (list): Список групп спрайтов, к которым принадлежит этот спрайт.
        - collision_sprites (list): Список спрайтов, с которыми может столкнуться Slime.
        '''
        super().__init__(groups)
        self.frames, self.frame_index = frames, 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_frect(topleft = pos)
        self.z = Z_LAYERS['main']
        self.speed = 20

        self.direction = choice((-1,1))
        self.collision_rects = [sprite.rect for sprite in collision_sprites]

    def update(self, dt):
        # анимация
        self.frame_index += ANIMATION_SPEED * dt
        self.image = self.frames[int(self.frame_index % len(self.frames))]
        self.image = pygame.transform.flip(self.image, True, False) if self.direction < 0 else self.image    
        
        # движение
        self.rect.x += self.direction * self.speed * dt

        # изменение направления
        floor_rect_right = pygame.FRect(self.rect.bottomright, (1,1))
        floor_rect_left = pygame.FRect(self.rect.bottomleft, (-1,1))
        wall_rect_right = pygame.FRect(self.rect.midright, (1, 1))
        wall_rect_left = pygame.FRect(self.rect.midleft, (-1, 1))


        # check 
        if floor_rect_right.collidelist(self.collision_rects) < 0 and self.direction > 0 or \
                floor_rect_left.collidelist(self.collision_rects) < 0 and self.direction < 0 or \
                wall_rect_right.collidelist(self.collision_rects) >= 0 and self.direction > 0 or \
                wall_rect_left.collidelist(self.collision_rects) >= 0 and self.direction < 0:
            self.direction *= -1