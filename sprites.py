from settings import *

class Sprite(pygame.sprite.Sprite):
    '''
    Базовый класс для всех спрайтов в игре.

    Аргументы:
    - pos (tuple): Начальная позиция спрайта (x, y).
    - surf (pygame.Surface): Поверхность изображения спрайта. По умолчанию создается пустая поверхность размером TILE_SIZE x TILE_SIZE.
    - groups (list): Список групп спрайтов, к которым принадлежит этот спрайт. По умолчанию None.
    - z (int): Значение z-слоя для отрисовки спрайта. По умолчанию Z_LAYERS['main'].
    '''
    def __init__(self, pos, surf = pygame.Surface((TILE_SIZE, TILE_SIZE)), groups = None, z = Z_LAYERS['main']):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft = pos)
        self.old_rect = self.rect.copy()
        self.z = z

class AnimatedSprite(Sprite):
    '''
    Класс для анимированных спрайтов.

    Аргументы:
    - pos (tuple): Начальная позиция спрайта (x, y).
    - frames (list): Список кадров анимации.
    - groups (list): Список групп спрайтов, к которым принадлежит этот спрайт.
    - z (int): Значение z-слоя для отрисовки спрайта. По умолчанию Z_LAYERS['main'].
    - animation_speed (float): Скорость анимации. По умолчанию ANIMATION_SPEED.
    '''
    def __init__(self, pos, frames, groups, z = Z_LAYERS['main'], animation_speed = ANIMATION_SPEED):
        self.frames, self.frame_index = frames, 0
        super().__init__(pos, self.frames[self.frame_index], groups, z)
        self.animation_speed = animation_speed

    def animate(self, dt):
        self.frame_index += self.animation_speed * dt
        self.image = self.frames[int(self.frame_index % len(self.frames))]
    
    def update(self, dt):
        self.animate(dt)

class Item(AnimatedSprite):
    '''
    Класс для предметов в игре (для монет и зелий).

    Аргументы:
    - item_type (str): Тип предмета ('coin' или 'potion').
    - pos (tuple): Начальная позиция предмета (x, y).
    - frames (list): Список кадров анимации.
    - groups (list): Список групп спрайтов, к которым принадлежит этот предмет.
    - data (Data): Объект класса Data, содержащий данные игры.
    '''
    def __init__(self, item_type, pos, frames, groups, data):
        super().__init__(pos, frames, groups, z= Z_LAYERS['background details'])
        self.item_type = item_type
        self.data = data

    def activate(self):
        if self.item_type == 'coin':
            self.data.coins += 1
        if self.item_type == 'potion':
            self.data.health += 1

class ParticleEffectSprite(AnimatedSprite):
    '''
    Класс для эффектов частиц в игре.

    Аргументы:
    - pos (tuple): Начальная позиция эффекта (x, y).
    - frames (list): Список кадров анимации.
    - groups (list): Список групп спрайтов, к которым принадлежит этот эффект.
    '''
    def __init__(self, pos, frames, groups):
        super().__init__(pos, frames, groups)
        self.z = Z_LAYERS['frontground']

    def animate(self, dt):
        self.frame_index += self.animation_speed * dt
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
        else:
            self.kill()

class MovingSprite(AnimatedSprite):
    '''
    Класс для движущихся спрайтов.

    Аргументы:
    - frames (list): Список кадров анимации.
    - groups (list): Список групп спрайтов, к которым принадлежит этот спрайт.
    - start_pos (tuple): Начальная позиция спрайта (x, y).
    - end_pos (tuple): Конечная позиция спрайта (x, y).
    - move_dir (str): Направление движения ('x' или 'y').
    - speed (float): Скорость движения.
    '''
    def __init__(self, frames, groups, start_pos, end_pos, move_dir, speed):
        super().__init__(start_pos, frames, groups)
        if move_dir == 'x':
            self.rect.midleft = start_pos
        else:
            self.rect.midtop = start_pos
        self.start_pos = start_pos
        self.end_pos = end_pos
        
        # движение
        self.moving = True
        self.speed = speed
        self.direction = vector(1,0) if move_dir == 'x' else vector (0, 1)
        self.move_dir = move_dir
    
    def check_border(self):
        # горизонтальная граница
        if self.move_dir == 'x':
            if self.rect.right >= self.end_pos[0] and self.direction.x == 1:
                self.direction.x = -1
                self.rect.right = self.end_pos[0]
            if self.rect.left <= self.start_pos[0] and self.direction.x == -1:
                self.direction.x = 1
                self.rect.left = self.start_pos[0]
        
        # вертикальная граница
        else:
            if self.rect.bottom >= self.end_pos[1] and self.direction.y == 1:
                self.direction.y = -1
                self.rect.bottom = self.end_pos[1]
            if self.rect.top <= self.start_pos[1] and self.direction.y == -1:
                self.direction.y = 1
                self.rect.top = self.start_pos[1]

    def update(self, dt):
        self.old_rect = self.rect.copy()
        self.rect.topleft += self.direction * self.speed * dt
        self.check_border()

        self.animate(dt)

# UI
class Heart(AnimatedSprite):
    '''
    Класс для спрайтов сердец, отображающих здоровье игрока.

    Аргументы:
    - pos (tuple): Начальная позиция сердечка (x, y).
    - frames (list): Список кадров анимации.
    - groups (list): Список групп спрайтов, к которым принадлежит это сердечко.
    '''
    def __init__(self, pos, frames, groups):
        super().__init__(pos, frames, groups)
        self.active = False
    