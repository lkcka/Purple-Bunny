from pygame.time import get_ticks

class Timer:
	'''
	Класс для создания таймеров, которые могут выполнять определенные действия через заданный промежуток времени.
    Таймер может быть одноразовым или повторяющимся.
	'''
	def __init__(self, duration, func = None, repeat = False):
		'''
        Инициализирует таймер.

        :param duration: Продолжительность таймера в миллисекундах.
        :type duration: int
        :param func: Функция, которая будет выполнена по истечении времени таймера. По умолчанию None.
        :type func: function
        :param repeat: Флаг, указывающий, должен ли таймер повторяться. По умолчанию False.
        :type repeat: bool
        '''
		self.duration = duration
		self.func = func
		self.start_time = 0
		self.active = False
		self.repeat = repeat

	def activate(self):
		'''
        Активирует таймер. Устанавливает флаг `active` в `True` и записывает текущее время в `start_time`.
        '''
		self.active = True
		self.start_time = get_ticks()

	def deactivate(self):
		'''
		Деактивирует таймер. Устанавливает флаг `active` в `False` и сбрасывает `start_time` в `0`.
        Если таймер повторяющийся (`repeat` равно `True`), он автоматически активируется снова.
		'''
		self.active = False
		self.start_time = 0
		if self.repeat:
			self.activate()

	def update(self):
		'''
		Вызывается в основном цикле игры, проверяет, истекло ли время таймера.
        Если время истекло, выполняет заданную функцию (если есть) и деактивирует таймер.
		'''
		current_time = get_ticks()
		if current_time - self.start_time >= self.duration:
			if self.func and self.start_time != 0:
				self.func()
			self.deactivate()