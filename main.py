from settings import *
from support import *
from level import Level
from data import Data
from ui import UI
from pytmx.util_pygame import load_pygame
from os.path import join


class Game:
    '''
    Класс Game представляет собой основной класс игры. Он инициализирует все необходимые компоненты
    '''
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
        pygame.display.set_caption('Purple Bunny Game')
        self.clock = pygame.time.Clock()
        self.import_assets()

        self.ui = UI(self.font, self.ui_frames)
        self.data = Data(self.ui)
        self.tmx_maps = {0: load_pygame('Levels/level1.tmx'),
                         1: load_pygame('Levels/level2.tmx')}
        self.current_stage = Level(self.tmx_maps[self.data.current_level], self.level_frames, self.data, self.switch_stage)

    def import_assets(self):
        self.level_frames = {
            'doors': import_folder('Assets/Doors'),
            'saw': import_folder('Assets/Saw'),
            'player': import_sub_folders('Assets/Player'),
            'flying platform': import_folder('Assets/Flying_platform'),
            'slime': import_folder('Assets/Slime'),
            'items': import_sub_folders('Assets/Items'),
            'particle': import_folder('Assets/Particle')
        }

        self.font = pygame.font.Font('Assets/Font/1.ttf', 30)
        self.ui_frames = {
            'heart': import_folder('Assets/UI/Heart'),
            'coin': import_image('Assets/UI/Coin')
        }

    def switch_stage(self, current_level = 0):
        '''
        Переключает на следующий уровень.

        :param current_level: Текущий уровень, по умолчанию 0.
        :type current_level: int
        '''
        self.current_stage = Level(self.tmx_maps[self.data.current_level], self.level_frames, self.data, self.switch_stage)

    def check_game_over(self):
        if self.data.health <= 0:
            pygame.quit()
            sys.exit()

    def run(self):
        while True:
            dt = self.clock.tick() / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
            self.check_game_over()
            self.current_stage.run(dt)
            self.ui.update(dt)

            pygame.display.update()

if __name__ == '__main__':
    game = Game()  
    game.run()