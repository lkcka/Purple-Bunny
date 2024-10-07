from settings import *
from sprites import Sprite, AnimatedSprite, MovingSprite, Item, ParticleEffectSprite
from player import Player
from groups import AllSprites
from enemies import Slime
from data import Data

class Level:
    '''
    Класс Level представляет собой уровень игры. Он управляет всеми спрайтами, столкновениями, взаимодействиями и обновлением состояния уровня.
    '''
    def __init__(self, tmx_map, level_frames, data, switch_stage):
        '''
        :param tmx_map: Объект карты уровня, созданный с помощью библиотеки pytmx.
        :type tmx_map: pytmx.TiledMap
        :param level_frames: Словарь с кадрами анимации для различных объектов уровня.
        :type level_frames: dict
        :param data: Объект класса Data, содержащий данные игры (например, количество монет и здоровье).
        :type data: Data
        :param switch_stage: Функция для переключения на следующий уровень.
        :type switch_stage: function
        '''
        self.display_surface = pygame.display.get_surface()
        self.data = data
        self.switch_stage = switch_stage

        # level data
        self.level_width = tmx_map.width * TILE_SIZE
        self.level_bottom = tmx_map.height * TILE_SIZE

        #groups
        self.all_sprites = AllSprites(
            width = self.level_width,
            height = self.level_bottom
        )
        self.collision_sprites = pygame.sprite.Group() # все сталкивающиеся спрайты
        self.semi_collision_sprites = pygame.sprite.Group()
        self.damage_sprites = pygame.sprite.Group()
        self.slime_sprites = pygame.sprite.Group()
        self.item_sprites = pygame.sprite.Group()

        self.setup(tmx_map, level_frames)

        self.particle_frames = level_frames['particle']

    def setup(self, tmx_map, level_frames):
        '''
        Настраивает уровень, создавая спрайты для тайлов, объектов, движущихся объектов, врагов и предметов.

        :param tmx_map: Объект карты уровня.
        :type tmx_map: pytmx.TiledMap
        :param level_frames: Словарь с кадрами анимации для различных объектов уровня.
        :type level_frames: dict
        '''
        # тайлы
        for layer in ['Sky', 'Cloud', 'Lake', 'Terrain', 'Decoration']:
            for x, y, surf in tmx_map.get_layer_by_name(layer).tiles():
                groups = [self.all_sprites]
                if layer == 'Terrain': 
                    groups.append(self.collision_sprites)
                match layer:
                    case 'Sky': z = Z_LAYERS['background']
                    case 'Cloud': z = Z_LAYERS['background'] 
                    case 'Lake': z = Z_LAYERS['water']
                    case _: z = Z_LAYERS['main']
                Sprite((x * TILE_SIZE, y * TILE_SIZE), surf, groups, z)
    
        # объекты
        for obj in tmx_map.get_layer_by_name('Object'):
            if obj.name == 'player':
                self.player = Player(
                    pos = (obj.x, obj.y), 
                    groups = self.all_sprites, 
                    collision_sprites = self.collision_sprites, 
                    semi_collision_sprites = self.semi_collision_sprites,
                    frames = level_frames['player'],
                    data = self.data)
            elif obj.name != 'doors':
                frames = level_frames[obj.name]
                AnimatedSprite((obj.x, obj.y), frames, self.all_sprites, z = Z_LAYERS['background details'])
            if obj.name == 'doors':
                self.level_finish_rect = pygame.FRect((obj.x, obj.y), (obj.width, obj.height))
                frames = level_frames[obj.name]
                Sprite((obj.x, obj.y), frames[0], groups, z = Z_LAYERS['background tiles'])
                    
        # движущиеся объекты
        for obj in tmx_map.get_layer_by_name('Moving Objects'):
            frames = level_frames[obj.name]
            groups = (self.all_sprites, self.semi_collision_sprites) if obj.properties['platform'] else (self.all_sprites, self.damage_sprites)
            # горизонтальное движение
            if obj.width > obj.height: 
                move_dir = 'x'
                start_pos = (obj.x, obj.y + obj.height / 2)
                end_pos = (obj.x + obj.width, obj.y + obj.height / 2)
            # вертикальное движение
            else:
                move_dir = 'y'
                start_pos = (obj.x + obj.width / 2, obj.y)
                end_pos = (obj.x + obj.width / 2, obj.y + obj.height)
            speed = obj.properties['speed']
            MovingSprite(frames, groups, start_pos, end_pos, move_dir, speed)

        # враги
        for obj in tmx_map.get_layer_by_name('Enemies'):
            if obj.name == 'slime':
                Slime((obj.x, obj.y), level_frames['slime'], (self.all_sprites, self.damage_sprites, self.slime_sprites), self.collision_sprites)

        # предметы
        for obj in tmx_map.get_layer_by_name('Items'):
            Item(obj.name, (obj.x, obj.y), level_frames['items'][obj.name], (self.all_sprites, self.item_sprites), self.data)

    def hit_collision(self):
        '''
        Проверяет столкновения игрока с врагами и наносит урон, если столкновение произошло.
        '''
        for sprite in self.damage_sprites:
            if sprite.rect.colliderect(self.player.hitbox_rect):
                self.player.get_damaged()

    def item_collision(self):
        '''
        Проверяет столкновения игрока с предметами и активирует их, если столкновение произошло.
        '''
        if self.item_sprites:
            item_sprites = pygame.sprite.spritecollide(self.player, self.item_sprites, True)
            if item_sprites:
                item_sprites[0].activate()
                ParticleEffectSprite((item_sprites[0].rect.topleft), self.particle_frames, self.all_sprites)

    def attack_collision(self):
        '''
        Проверяет столкновения игрока с врагами при атаке и уничтожает врагов, если столкновение произошло.
        '''
        for target in self.slime_sprites.sprites():
            facing_target = self.player.rect.centerx < target.rect.centerx and self.player.facing_right or \
                            self.player.rect.centerx > target.rect.centerx and not self.player.facing_right
            if target.rect.colliderect(self.player.rect) and self.player.attacking and facing_target:
                target.kill()

    def check_constraint(self):
        '''
        Проверяет ограничения игрока на уровне.
        '''
        # левая и правая границы
        if self.player.hitbox_rect.left <= 0:
            self.player.hitbox_rect.left = 0
        if self.player.hitbox_rect.right >= self.level_width:
            self.player.hitbox_rect.right = self.level_width

        # нижняя граница
        if self.player.hitbox_rect.bottom > self.level_bottom:
            pygame.quit()
            sys.exit()

        # завершение уровня
        if self.player.hitbox_rect.colliderect(self.level_finish_rect):
            self.data.current_level += 1
            self.switch_stage(self.data.current_level)

    def run(self, dt):
        '''
        Запускает обновление и отрисовку уровня.
        '''
        self.display_surface.fill((44, 156, 213))
        
        self.all_sprites.update(dt)
        self.hit_collision()
        self.item_collision()
        self.attack_collision()
        self.check_constraint()

        self.all_sprites.draw(self.player.hitbox_rect.center)