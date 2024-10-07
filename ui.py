from settings import *
from sprites import Heart
from timer import Timer

class UI:
    '''
    Класс UI отвечает за отображение данных на экране, таких как количество монет и здоровье игрока.
    '''
    def __init__(self, font, frames):
        '''
        Инициализирует объект UI.

        Аргументы:
        - font (pygame.font.Font): Шрифт для отображения текста.
        - frames (dict): Словарь с изображениями для сердец и монет.
        '''
        self.display_surface = pygame.display.get_surface()
        self.sprites = pygame.sprite.Group()
        self.font = font

        # health
        self.heart_frames = frames['heart']
        self.heart_surf_width = self.heart_frames[0].get_width()
        self.heart_padding = 0
        self.create_hearts(3)

        # coins
        self.coin_amount = 0
        self.coin_timer = Timer(1000)
        self.coin_surf = frames['coin']

    def create_hearts(self, amount):
        '''
        Создает и отображает на экране указанное количество сердец.

        Аргументы:
        - amount (int): Количество сердец для отображения.
        '''
        for sprite in self.sprites:
            sprite.kill()
        for heart in range(amount):
            x = 10 + heart * (self.heart_surf_width + self.heart_padding)
            y = 10
            Heart((x, y), self.heart_frames, self.sprites)

    def display_text(self):
        if self.coin_timer.active:
            text_surf = self.font.render(str(self.coin_amount), False, 'white')
            text_rect = text_surf.get_frect(topleft = (40, 50))
            self.display_surface.blit(text_surf, text_rect)

            coin_rect = self.coin_surf.get_frect(topleft = (5, 50))
            self.display_surface.blit(self.coin_surf, coin_rect)

    def show_coins(self, amount):
        '''
        Обновляет количество монет и активирует таймер для отображения.

        Параметры:
        - amount (int): Новое количество монет.
        '''
        self.coin_amount = amount
        self.coin_timer.activate()

    def update(self, dt):
        self.coin_timer.update()
        self.sprites.update(dt)
        self.sprites.draw(self.display_surface)
        self.display_text()