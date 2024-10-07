from settings import *
from timer import Timer

class Player(pygame.sprite.Sprite):
    '''
    Класс игрока.
    '''
    def __init__(self, pos, groups, collision_sprites, semi_collision_sprites, frames, data):
        '''
        Инициализирует объект игрока.

        :param pos: Позиция игрока.
        :param groups: Группы, к которым принадлежит игрок.
        :param collision_sprites: Список объектов, с которыми возможны полные коллизии.
        :param semi_collision_sprites: Список объектов, с которыми возможны частичные коллизии (например, платформы).
        :param frames: Словарь кадров для анимаций игрока.
        :param data: Дополнительные данные о состоянии игрока (например, здоровье).
        '''
        super().__init__(groups)
        self.z = Z_LAYERS['main']
        self.data = data

        # image
        self.frames, self.frame_index = frames, 0
        self.state, self.facing_right = 'Idle', True
        self.image = self.frames[self.state][self.frame_index]

        # rects
        self.rect = self.image.get_frect(topleft = pos)
        self.hitbox_rect = self.rect.inflate(-14, 0)
        self.old_rect = self.hitbox_rect.copy()

        # движение
        self.direction = vector()
        self.speed = 200
        self.gravity = 1300
        self.jump = False
        self.jump_height = 500
        self.attacking = False
        self.damaged = False

        # столкновения
        self.collision_sprites = collision_sprites
        self.semi_collision_sprites = semi_collision_sprites
        self.on_surface = {'floor': False, 'left': False, 'right': False}
        self.platform = None

        # таймер
        self.timers = {
            'wall jump': Timer(200),
            'wall slide block': Timer (200),
            'platform skip': Timer(100),
            'attack block': Timer(500),
            'hit': Timer(600)
        }

    def attack(self):
        '''
        Обрабатывает атаку игрока. Атака возможна только если таймер атаки не активен.
        '''
        if not self.timers['attack block'].active:
            self.attacking = True
            self.frame_index = 0
            self.timers['attack block'].activate()

    def input(self):
        '''
        Обрабатывает пользовательский ввод для перемещения, прыжков и атак.
        '''
        keys = pygame.key.get_pressed()
        input_vector = vector(0, 0)
        if not self.timers['wall jump'].active:
            
            if keys[pygame.K_RIGHT]:
                input_vector.x += 1
                self.facing_right = True
            
            if keys[pygame.K_LEFT]:
                input_vector.x -= 1
                self.facing_right = False
            
            if keys[pygame.K_DOWN]:
                self.timers['platform skip'].activate()
            
            if keys[pygame.K_SPACE]:
                self.attack()

            self.direction.x = input_vector.normalize().x if input_vector else input_vector.x
        
        if keys[pygame.K_UP]:
            self.jump = True

    def move(self, dt):
        '''
        Обрабатывает движение игрока с учетом столкновений и гравитации.
        '''
        # hotizontal
        self.hitbox_rect.x += self.direction.x * self.speed * dt
        self.collision('horizontal')

        # vertical
        if not self.on_surface['floor'] and any((self.on_surface['left'], self.on_surface['right'])) and not self.timers['wall slide block'].active:
            self.direction.y = 0
            self.hitbox_rect.y += self.gravity / 10 * dt

        else:
        # объяснение со Stack Overflow:
        # применяем разделение гравитации на два этапа, чтобы исправить неточности, возникающие при редком обновлении состояния игры 
        # этот подход компенсирует проблему с неправильным расчетом ускорения на длинных промежутках времени между кадрами 
            self.direction.y += self.gravity / 2 * dt
            self.hitbox_rect.y += self.direction.y * dt
            self.direction.y += self.gravity / 2 * dt

        if self.jump:
            if self.on_surface['floor']:
                self.direction.y = -self.jump_height
                self.timers['wall slide block'].activate()
                self.hitbox_rect.bottom -= 1 #чтобы прыгать на двигающейся горизонтально платформе
            elif any((self.on_surface['right'], self.on_surface['left'])) and not self.timers['wall slide block'].active:
                self.timers['wall jump'].activate()
                self.direction.y = -self.jump_height
                self.direction.x = 1 if self.on_surface['left'] else -1
            self.jump = False  
        
        self.collision('vertical')
        self.semi_collision()
        self.rect.center = self.hitbox_rect.center

    # если игрок стоит на платформе, то передвигаем игрока в направлении платформы со скоростью движения платформы
    def platform_move(self, dt):
        '''
        Обрабатывает перемещение игрока вместе с платформой, если он на ней находится.

        :param dt: Время, прошедшее с последнего обновления.
        '''
        if self.platform:
            self.hitbox_rect.topleft += self.platform.direction * self.platform.speed * dt
        
    def check_contact(self):
        '''
        Проверяет контакт игрока с поверхностями и платформами
        '''
        floor_rect = pygame.Rect(self.hitbox_rect.bottomleft, (self.hitbox_rect.width, 2))
        right_rect = pygame.Rect(self.hitbox_rect.topright + vector(0,self.hitbox_rect.height/4), (2, self.hitbox_rect.height / 2))
        left_rect = pygame.Rect(self.hitbox_rect.topleft + vector(-2,self.hitbox_rect.height/4), (2, self.hitbox_rect.height / 2))
    
        
        collide_rects = [sprite.rect for sprite in self.collision_sprites]
        semi_collide_rect = [sprite.rect for sprite in self.semi_collision_sprites]


        # collisions
        self.on_surface['floor'] = True if floor_rect.collidelist(collide_rects) >= 0 or floor_rect.collidelist(semi_collide_rect) >= 0 and self.direction.y >= 0 else False
        self.on_surface['right'] = True if right_rect.collidelist(collide_rects) >= 0 else False
        self.on_surface['left'] = True if left_rect.collidelist(collide_rects) >= 0 else False

        # движение игрока на передвигающейся платформе
        self.platform = None
        sprites = self.collision_sprites.sprites() + self.semi_collision_sprites.sprites()
        for sprite in [sprite for sprite in sprites if hasattr(sprite, 'moving')]:
            if sprite.rect.colliderect(floor_rect):
                self.platform = sprite

    def collision(self, axis):
        '''
        Обрабатывает столкновения игрока с объектами в зависимости от оси.

        :param axis: Ось столкновения ('horizontal' или 'vertical').
        '''
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hitbox_rect): #проверка коллизий между объектами, где self.rect - игрок
                if axis == 'horizontal':
                    # left
                    if self.hitbox_rect.left <= sprite.rect.right and int(self.old_rect.left) >= int(sprite.old_rect.right): # если левое плечо игрока ушло за правый край стены
                        self.hitbox_rect.left = sprite.rect.right # то левое плечо должно находится вровень к правой стене
                    
                    # right
                    if self.hitbox_rect.right >= sprite.rect.left and int(self.old_rect.right) <= int(sprite.old_rect.left):
                        self.hitbox_rect.right = sprite.rect.left

                else: # vertical collision
                    # bottom
                    if self.hitbox_rect.bottom >= sprite.rect.top and int(self.old_rect.bottom) <= int(sprite.old_rect.top):
                        self.hitbox_rect.bottom = sprite.rect.top
                        
                    # top
                    if self.hitbox_rect.top <= sprite.rect.bottom and int(self.old_rect.top) >= int(sprite.old_rect.bottom):
                        self.hitbox_rect.top = sprite.rect.bottom
                        if hasattr(sprite, 'moving'):
                            self.hitbox_rect.top += 6 # для того, чтобы головой не проникать внутрь движущейся платформы
                    self.direction.y = 0

    def semi_collision(self):
        '''
        Обрабатывает столкновения игрока с движущимися платформами.
        '''
        if not self.timers['platform skip'].active:
            for sprite in self.semi_collision_sprites:
                if sprite.rect.colliderect(self.hitbox_rect):
                    if self.hitbox_rect.bottom >= sprite.rect.top and int(self.old_rect.bottom) <= sprite.old_rect.top:
                            self.hitbox_rect.bottom = sprite.rect.top
                            if self.direction.y > 0: # так игрок не липнет моментально к полу полу после запрыгивания на платформу
                                self.direction.y = 0
                        
    def update_timers(self):
        for timer in self.timers.values():
            timer.update()

    def animate(self, dt):
        '''
        Обрабатывает анимацию игрока в зависимости от его состояния.
        '''
        self.frame_index += ANIMATION_SPEED * dt
        if self.state == 'Attack1' and self.frame_index >= len(self.frames[self.state]):
            self.state = 'Idle'
        self.image = self.frames[self.state][int(self.frame_index % len(self.frames[self.state]))]        
        self.image = self.image if self.facing_right else pygame.transform.flip(self.image, flip_x = True, flip_y = False)

        if self.attacking and self.frame_index > len(self.frames[self.state]):
            self.attacking = False
        if self.damaged and self.frame_index > len(self.frames[self.state]):
            self.damaged = False

    def get_state(self):
        '''
        Определяет текущее в зависимости от взаимодействий с окружением.
        '''
        if self.on_surface['floor']:
            if self.attacking:
                self.state = 'Attack1'
            elif self.damaged:
                self.state = 'Hurt'
            else:
                self.state = 'Idle' if self.direction.x == 0 else 'Walk'
        else:
            if any((self.on_surface['left'],self.on_surface['right'])):
                self.state = 'Wall'
            elif self.damaged:
                self.state = 'Hurt'
            else:
                self.state = 'Jump'

    def get_damaged(self):
        '''
        Обрабатывает получение урона игроком
        '''
        if not self.timers['hit'].active:
            self.damaged = True
            self.data.health -= 1
            self.frame_index = 0
            print(self.data.health)
            self.timers['hit'].activate()

    def update(self, dt):
        self.old_rect = self.hitbox_rect.copy()
        self.update_timers()
        
        self.input()
        self.move(dt)
        self.platform_move(dt)
        self.check_contact()

        self.get_state()
        self.animate(dt)