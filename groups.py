from settings import *

class AllSprites(pygame.sprite.Group):
    '''
    Класс AllSprites наследуется от pygame.sprite.Group и предназначен для управления группой спрайтов, которые будут отображаться на экране.
    Он также реализует логику камеры, чтобы следить за игроком и корректно отображать спрайты.

    :param width: Ширина уровня в тайлах.
    :type width: int
    :param height: Высота уровня в тайлах.
    :type height: int
    '''
    def __init__(self, width, height):
        '''
        :param width: Ширина уровня в тайлах.
        :type width: int
        :param height: Высота уровня в тайлах.
        :type height: int
        '''
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = vector() #смещение камеры
        self.width, self.height = width * TILE_SIZE, height * TILE_SIZE
        self.borders = {
			'left': 0,
			'right': -self.width + WIN_WIDTH,
			'bottom': -self.height + WIN_HEIGHT,
			'top': 0}
    
    def camera_constraint(self):
        '''
        Проверяет и устанавливает смещение камеры для левой, правой, верхней и нижней границ.
        '''
        self.offset.x = self.offset.x if self.offset.x < self.borders['left'] else self.borders['left']
        self.offset.x = self.offset.x if self.offset.x > self.borders['right'] else self.borders['right'] 
        self.offset.y = self.offset.y if self.offset.y > self.borders['bottom'] else self.borders['bottom']
        self.offset.y = self.offset.y if self.offset.y < self.borders['top'] else self.borders['top']
          
    def draw(self, target_pos):
        '''
        Отрисовывает все спрайты на экране с учетом смещения камеры.

        :param target_pos: Позиция target'а, за которой следует камера.
        :type target_pos: tuple
        '''
        self.offset.x = -(target_pos[0] - WIN_WIDTH / 2) # такое смещение по x, чтобы игрок был по центру экрана
        self.offset.y = -(target_pos[1] - WIN_HEIGHT / 2) # такое смещение по y, чтобы игрок был по центру экрана
        self.camera_constraint()

        for sprite in sorted(self, key = lambda sprite: sprite.z):
        # сортирует спрайты по слоям, чем больше значение z тем выше слой
            offset_pos = sprite.rect.topleft + self.offset
            self.display_surface.blit(sprite.image, offset_pos)