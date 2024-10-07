class Data:
    '''
    Класс представляет собой модель данных для игры, управляющую количеством монет и здоровьем игрока.
    Он также взаимодействует с объектом UI для обновления отображения этих данных на экране.
    '''
    def __init__(self, ui):
        '''
        Инициализирует объект Data.

        Аргументы:
        - ui (UI): Объект класса UI, отвечающий за отображение данных на экране.
        '''
        self.ui = ui
        self._coins = 0
        self._health = 3
        self.ui.create_hearts(self._health)
    
        self.current_level = 0

    @property
    def coins(self):
        '''
        Возвращает текущее количество монет.

        Возвращает:
        - int: Количество монет.
        '''
        return self._coins
    
    @coins.setter
    def coins(self, value):
        '''
        Устанавливает новое количество монет и обновляет отображение на экране.
        Если количество монет >= 10, игрок получает 1 хп.

        Аргументы:
        - value (int): Новое количество монет.
        '''
        self._coins = value
        if self.coins >= 10:
            self.coins -= 10
            self.health += 1
        self.ui.show_coins(self.coins)

    @property
    def health(self):
        '''
        Возвращает текущее количество хп.

        Возвращает:
        - int: Количество хп.
        '''
        return self._health
    
    @health.setter
    def health(self, value):
        '''
        Устанавливает новое количество хп и обновляет отображение на экране.

        Аргументы:
        - value (int): Новое количество хп.
        '''
        self._health = value
        self.ui.create_hearts(value)