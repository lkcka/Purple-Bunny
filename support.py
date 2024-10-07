from settings import * 
from os import walk
from os.path import join

def import_image(*path, alpha = True, format = 'png'):
	'''
    Импортирует изображение из указанного пути и преобразует его в формат, подходящий для pygame.

    Аргументы:
    *path (str): Переменное количество аргументов, представляющих путь к изображению.
    alpha (bool): Если True, изображение будет преобразовано с учетом альфа-канала (прозрачность).
                  Если False, изображение будет преобразовано без учета альфа-канала.
                  По умолчанию True.
    format (str): Формат изображения (например, 'png', 'jpg'). По умолчанию 'png'.

    Возвращает:
    pygame.Surface: Загруженное и преобразованное изображение.
    '''
	full_path = join(*path) + f'.{format}'
	return pygame.image.load(full_path).convert_alpha() if alpha else pygame.image.load(full_path).convert()

def import_folder(*path):
	'''
    Импортирует все изображения из указанной папки и возвращает их в виде списка.

    Аргументы:
    *path (str): Переменное количество аргументов, представляющих путь к папке с изображениями.

    Возвращает:
    list: Список загруженных и преобразованных изображений.
    '''
	frames = []
	for folder_path, sub_folders, image_names in walk(join(*path)):
		for image_name in sorted(image_names, key = lambda name: int(name.split('.')[0])):
			full_path = join(folder_path, image_name)
			frames.append(pygame.image.load(full_path).convert_alpha())
	return frames 

def import_sub_folders(*path):
	'''
    Импортирует изображения из всех подпапок указанной директории и возвращает их в виде словаря,
    где ключами являются имена подпапок.

    Аргументы:
    *path (str): Переменное количество аргументов, представляющих путь к директории с подпапками.

    Возвращает:
    dict: Словарь, где ключи — имена подпапок, а значения — списки загруженных и преобразованных изображений.
    '''
	frame_dict = {}
	for folder_path, sub_folders, image_names in walk(join(*path)): 
		if sub_folders:
			for sub_folder in sub_folders:
				frame_dict[sub_folder] = import_folder(*path, sub_folder)
	return frame_dict