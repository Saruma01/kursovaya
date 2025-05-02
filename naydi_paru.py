import pygame
import random
import time
import os
from datetime import datetime
 
# Инициализация Pygame
pygame.init()
 
# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (155, 107, 214)
RED = (102, 161, 210)
GREEN = (132, 67, 214)
YELLOW = (80, 41, 130)
LIGHT_BLUE = (173, 216, 230)
PURPLE = (52, 5, 112)
PURPLEW = (73, 0, 163)
 
# Настройки шрифтов
font_small = pygame.font.SysFont('Biome', 20)
font_medium = pygame.font.SysFont('Biome', 30)
font_large = pygame.font.SysFont('Biome', 40)
 
# Константы
CARD_WIDTH = 100
CARD_HEIGHT = 100
MARGIN = 5
MIN_WIDTH, MIN_HEIGHT = 800, 600  # Минимальный размер окна
 
# Загрузка фоновых изображений
try:
    game_bg = pygame.image.load('C:\\Users\\Admin\\Documents\\kursovaya\\mond.jpg')  # Фон для игры
    menu_bg = pygame.image.load('C:\\Users\\Admin\\Documents\\kursovaya\\fontaine.jpg')  # Фон для меню и других экранов
    card_back = pygame.image.load('C:\\Users\\Admin\\Documents\\kursovaya\\card.jpg') # Рубашка карточки
except pygame.error as e:
    print(f"Ошибка загрузки фоновых изображений: {e}")
    game_bg = pygame.Surface((1, 1))
    game_bg.fill(GRAY)
    menu_bg = pygame.Surface((1, 1))
    menu_bg.fill(WHITE)
    card_back = pygame.Surface((1, 1))
    card_back.fill(BLUE)
# загрузка изображений для карточек
try:
    # загрузка
    card_images = [pygame.image.load(f'C:\\Users\\Admin\\Documents\\kursovaya\\cards\\image{i}.jpg') for i in range(1, 51)]
except pygame.error as e:
    print(f"Ошибка загрузки изображений карт: {e}")
    # Создаем простые цветные поверхности в случае ошибки
    card_images = [pygame.Surface((100, 100)) for _ in range(10)]
    for i, surf in enumerate(card_images):
        surf.fill((random.randint(50, 200), random.randint(50, 200), random.randint(50, 200)))

class Card:
    def __init__(self, value, row, col):
        self.value = value  # Теперь это индекс изображения (0-9)
        self.row = row
        self.col = col
        self.visible = False
        self.solved = False
        self.reveal_time = 0

    def draw(self, screen, x_offset, y_offset, card_width, card_height):
        x = self.col * (card_width + MARGIN) + MARGIN + x_offset
        y = self.row * (card_height + MARGIN) + MARGIN + y_offset
       
        if self.solved:
            return
           
        if self.visible:
            # Рисуем изображение вместо текста
            if 0 <= self.value < len(card_images):
                img = pygame.transform.scale(card_images[self.value], (card_width, card_height))
                screen.blit(img, (x, y))
            else:
                # Если изображение не найдено, рисуем прямоугольник с номером
                pygame.draw.rect(screen, WHITE, (x, y, card_width, card_height))
                text = font_medium.render(str(self.value), True, BLACK)
                text_rect = text.get_rect(center=(x + card_width//2, y + card_height//2))
                screen.blit(text, text_rect)
        else:
            if card_back:
                scaled_back = pygame.transform.scale(card_back, (card_width, card_height))
                screen.blit(scaled_back, (x, y))
            else:
                pygame.draw.rect(screen, BLUE, (x, y, card_width, card_height))

    def is_clicked(self, pos, x_offset, y_offset, card_width, card_height):
        x = self.col * (card_width + MARGIN) + MARGIN + x_offset
        y = self.row * (card_height + MARGIN) + MARGIN + y_offset
        return (x <= pos[0] <= x + card_width and 
                y <= pos[1] <= y + card_height and 
                not self.solved and not self.visible)
    

class GameStats:
    def __init__(self):
        self.games = [] # Список для хранения статистики игр
        self.filename = "memory_game_stats.txt" # Имя файла для сохранения статистики
        self.load_stats() # Загрузка статистики при инициализации
 
    def add_game(self, date_time, rows, cols, moves, duration):
        self.games.append({ # Добавление статистики текущей игры
            "date_time": date_time,
            "rows": rows,
            "cols": cols,
            "moves": moves,
            "duration": duration
        })
        self.save_stats() # Сохранение статистики в файл
 
    def save_stats(self):
        with open(self.filename, "w") as f: # Открытие файла для записи (перезапись)
            for game in self.games: # Запись статистики каждой игры в новую строку
                f.write(f"{game['date_time']},{game['rows']},{game['cols']},"
                            f"{game['moves']},{game['duration']}\n")
 
    def load_stats(self):
        if os.path.exists(self.filename): # Проверка существования файла
            with open(self.filename, "r") as f: # Открытие файла для чтения
                for line in f: # Чтение каждой строки
                    parts = line.strip().split(',') # Разделение строки по запятой
                    if len(parts) == 5: # Проверка количества элементов
                        self.games.append({ # Добавление статистики в список
                            "date_time": parts[0],
                            "rows": int(parts[1]),
                            "cols": int(parts[2]),
                            "moves": int(parts[3]),
                            "duration": int(parts[4])
                        })
 
class Game:
    def __init__(self, rows, cols):
        self.rows = rows # Количество строк
        self.cols = cols # Количество столбцов
        self.cards = [] # Список карточек на поле
        self.selected = [] # Список выбранных (открытых) карточек
        self.moves = 0 # Счетчик ходов
        self.solved_pairs = 0 # Счетчик найденных пар
        self.total_pairs = (rows * cols) // 2 # Общее количество пар
        self.start_time = time.time() # Время начала игры
        self.game_over = False # Флаг завершения игры
        self.waiting = False # Флаг ожидания после неправильного хода
        self.wait_start = 0 # Время начала ожидания
        self.generate_board() # Генерация игрового поля при создании объекта Game
       

    def generate_board(self):
    # Проверяем, достаточно ли изображений для данного размера поля
        if self.total_pairs > len(card_images):
            raise ValueError(f"Недостаточно изображений карточек. Нужно минимум {self.total_pairs}, доступно {len(card_images)}")
    
    # Выбираем случайные уникальные изображения для пар
        selected_images = random.sample(range(len(card_images)), self.total_pairs)
    
    # Создаем пары (каждое изображение встречается дважды)
        values = selected_images * 2
        random.shuffle(values)
        
        # Создаем карточки
        self.cards = []
        for i in range(self.rows * self.cols):
            row = i // self.cols
            col = i % self.cols
            self.cards.append(Card(values[i], row, col))
 
    def handle_click(self, pos, x_offset, y_offset, card_width, card_height):
        if self.waiting or self.game_over: # Игнорирование кликов во время ожидания или после завершения
            return
        for card in self.cards: # Перебор всех карточек
            if card.is_clicked(pos, x_offset, y_offset, card_width, card_height): # Проверка клика по карточке
                card.visible = True # Открытие карточки
                self.selected.append(card) # Добавление в список выбранных
                if len(self.selected) == 2: # Если выбраны две карточки
                    self.moves += 1 # Увеличение счетчика ходов
                    if self.selected[0].value == self.selected[1].value: # Проверка на совпадение
                        for c in self.selected: # Отметка как решенные
                            c.solved = True
                        self.solved_pairs += 1 # Увеличение счетчика решенных пар
                        self.selected = [] # Очистка списка выбранных
                        if self.solved_pairs == self.total_pairs: # Проверка на завершение игры
                            self.game_over = True
                    else: # Если не совпали
                        self.waiting = True # Установка флага ожидания
                        self.wait_start = time.time() # Запись времени начала ожидания
                break
 
    def update(self):
        if self.waiting and time.time() - self.wait_start > 1: # Проверка окончания времени ожидания
            for card in self.selected: # Скрытие выбранных карточек
                card.visible = False
            self.selected = [] # Очистка списка выбранных
            self.waiting = False # Сброс флага ожидания
 
    def draw(self, screen, x_offset, y_offset, card_width, card_height, width, height):
        scaled_bg = pygame.transform.scale(game_bg, (width, height)) # Масштабирование фонового изображения
        screen.blit(scaled_bg, (0, 0)) # Отображение фона
       
        info_text = font_medium.render( # Отображение информации об игре
            f"Ходы: {self.moves} | Найдено пар: {self.solved_pairs}/{self.total_pairs}",
            True, WHITE
        )
        screen.blit(info_text, (10, 10))
       
        # Измененная позиция кнопки "Назад" (правый верхний угол)
        back_btn = pygame.Rect(width - 110, 10, 100, 40) # Создание кнопки "Назад"
        pygame.draw.rect(screen, YELLOW, back_btn) # Рисование кнопки
        pygame.draw.rect(screen, BLACK, back_btn, 2) # Рисование обводки кнопки
        back_text = font_small.render("Назад", True, WHITE) # Рендер текста кнопки
        screen.blit(back_text, back_text.get_rect(center=back_btn.center)) # Отображение текста по центру
   
        for card in self.cards: # Отрисовка всех карточек
            card.draw(screen, x_offset, y_offset, card_width, card_height)
 
 
def show_stats_screen(screen, width, height, stats):
    # Рисуем меню-фон
    scaled_bg = pygame.transform.scale(menu_bg, (width, height)) # Масштабирование фонового изображения
    screen.blit(scaled_bg, (0, 0)) # Отображение фона
    title = font_large.render("Статистика игр", True, WHITE) # Отображение заголовка
    screen.blit(title, (width // 2 - title.get_width() // 2, 30)) # Центрирование заголовка
 
    back_btn = pygame.Rect(20, 20, 100, 40) # Кнопка "Назад"
    pygame.draw.rect(screen, YELLOW, back_btn) # Рисование кнопки
    pygame.draw.rect(screen, BLACK, back_btn, 2) # Рисование обводки кнопки
    back_text = font_small.render("Назад", True, WHITE) # Рендер текста
    screen.blit(back_text, (back_btn.x + back_btn.width // 2 - back_text.get_width() // 2,
                            back_btn.y + back_btn.height // 2 - back_text.get_height() // 2)) # Отображение текста по центру
 
    if not stats.games: # Если нет данных статистики
        no_stats = font_medium.render("Нет данных о прошлых играх", True, WHITE) # Вывод сообщения
        screen.blit(no_stats, (width // 2 - no_stats.get_width() // 2, height // 2)) # Центрирование сообщения
    else: # Если статистика есть
        headers = ["Дата и время", "Размер", "Ходы", "Время (сек)"] # Заголовки таблицы
        for i, header in enumerate(headers): # Отображение заголовков
            text = font_small.render(header, True, PURPLE)
            screen.blit(text, (50 + i * 200, 100))
 
        for i, game in enumerate(stats.games[-10:]): # Отображение последних 10 записей статистики
            date_text = font_small.render(game['date_time'], True, WHITE)
            size_text = font_small.render(f"{game['rows']}x{game['cols']}", True, WHITE)
            moves_text = font_small.render(str(game['moves']), True, WHITE)
            time_text = font_small.render(str(game['duration']), True, WHITE)
            screen.blit(date_text, (50, 130 + i * 30))
            screen.blit(size_text, (250, 130 + i * 30))
            screen.blit(moves_text, (450, 130 + i * 30))
            screen.blit(time_text, (650, 130 + i * 30))
 
    pygame.display.flip() # Обновление экрана
 
    while True: # Основной цикл экрана статистики
        for event in pygame.event.get(): # Обработка событий
            if event.type == pygame.QUIT: # Выход из игры
                pygame.quit()
                return False
            if event.type == pygame.MOUSEBUTTONDOWN: # Обработка клика мыши
                if back_btn.collidepoint(event.pos): # Если нажата кнопка "Назад"
                    return True
            if event.type == pygame.VIDEORESIZE: # Обработка изменения размера окна
                width, height = max(event.size[0], MIN_WIDTH), max(event.size[1], MIN_HEIGHT)
                screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
                return show_stats_screen(screen, width, height, stats)
 
def show_game_over_screen(screen, width, height, moves, duration):
    # Рисуем меню-фон
    scaled_bg = pygame.transform.scale(menu_bg, (width, height)) # Масштабирование фона
    screen.blit(scaled_bg, (0, 0)) # Отображение фона
    victory_text = font_large.render("Победа!", True, GREEN) # Отображение сообщения о победе
    screen.blit(victory_text, (width // 2 - victory_text.get_width() // 2, height // 2 - 100)) # Центрирование сообщения
 
    stats_text = f"Время: {duration} сек. | Ходы: {moves}" # Формирование текста статистики
    stats_surface = font_medium.render(stats_text, True, BLACK) # Рендер текста статистики
    screen.blit(stats_surface, (width // 2 - stats_surface.get_width() // 2, height // 2 - 30)) # Центрирование статистики
 
    # Увеличиваем размер кнопок
    restart_btn = pygame.Rect(width // 2 - 250, height // 2 + 30, 220, 60) # Кнопка "Начать сначала"
    pygame.draw.rect(screen, BLUE, restart_btn) # Рисование кнопки
    pygame.draw.rect(screen, BLACK, restart_btn, 2) # Рисование обводки
    restart_text = font_medium.render("Начать сначала", True, WHITE) # Рендер текста
    screen.blit(restart_text, (restart_btn.x + restart_btn.width // 2 - restart_text.get_width() // 2,
                              restart_btn.y + restart_btn.height // 2 - restart_text.get_height() // 2)) # Центрирование текста
 
    menu_btn = pygame.Rect(width // 2 + 30, height // 2 + 30, 220, 60) # Кнопка "Вернуться в меню"
    pygame.draw.rect(screen, YELLOW, menu_btn) # Рисование кнопки
    pygame.draw.rect(screen, BLACK, menu_btn, 2) # Рисование обводки
    menu_text = font_medium.render("Вернуться в меню", True, WHITE) # Рендер текста
    screen.blit(menu_text, (menu_btn.x + menu_btn.width // 2 - menu_text.get_width() // 2,
                            menu_btn.y + menu_btn.height // 2 - menu_text.get_height() // 2)) # Центрирование текста
 
    pygame.display.flip() # Обновление экрана
 
    while True: # Основной цикл экрана завершения игры
        for event in pygame.event.get(): # Обработка событий
            if event.type == pygame.QUIT: # Выход из игры
                pygame.quit()
                return None
            if event.type == pygame.MOUSEBUTTONDOWN: # Обработка кликов мыши
                if restart_btn.collidepoint(event.pos): # Если нажата кнопка "Начать сначала"
                    return "restart"
                if menu_btn.collidepoint(event.pos): # Если нажата кнопка "Вернуться в меню"
                    return "menu"
            if event.type == pygame.VIDEORESIZE: # Обработка изменения размера окна
                width, height = max(event.size[0], MIN_WIDTH), max(event.size[1], MIN_HEIGHT)
                screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
                return show_game_over_screen(screen, width, height, moves, duration)
 
def get_custom_size(screen, width, height):
     # Рисуем меню-фон
    scaled_bg = pygame.transform.scale(menu_bg, (width, height)) # Масштабирование фона
    screen.blit(scaled_bg, (0, 0)) # Отображение фона
    input_box = pygame.Rect(width // 2 - 100, height // 2 - 25, 200, 50) # Создание поля ввода
    color_inactive = pygame.Color(165, 92, 255) # Цвет неактивного поля
    color_active = pygame.Color(73, 0, 163) # Цвет активного поля
    color = color_inactive # Установка начального цвета
    active = False # Флаг активности поля ввода
    text = '' # Введенный текст
    font = font_medium # Используемый шрифт
    label = font.render("Введите размер (например, 4x4):", True,PURPLEW) # Подсказка
    error_message = None # Сообщение об ошибке
    
    back_btn = pygame.Rect(20, 20, 100, 40) # Кнопка "Назад"
    back_text = font_small.render("Назад", True, WHITE) # Рендер текста
 
    while True: # Основной цикл ввода размера
        for event in pygame.event.get(): # Обработка событий
            if event.type == pygame.QUIT: # Выход из игры
                pygame.quit()
                return None, None
            if event.type == pygame.MOUSEBUTTONDOWN: # Обработка клика мыши
                if input_box.collidepoint(event.pos): # Если клик по полю ввода
                    active = not active # Переключение активности
                else: # Если клик вне поля ввода
                    active = False # Деактивация поля
                color = color_active if active else color_inactive # Обновление цвета поля
               
                if back_btn.collidepoint(event.pos): # Обработка кнопки "Назад"
                    return None, None  # Возвращаем None для выхода в меню
                   
            if event.type == pygame.KEYDOWN: # Обработка нажатий клавиш
                if active: # Если поле ввода активно
                    if event.key == pygame.K_RETURN: # Если нажат Enter
                        try: # Попытка распарсить введенный размер
                            parts = text.split('x')
                            if len(parts) != 2:
                                raise ValueError("Неправильный формат")
                            rows, cols = map(int, parts)
                            if rows <= 0 or cols <= 0:
                                error_message = "Размеры должны быть положительными"
                            elif (rows * cols) % 2 != 0:
                                error_message = "Общее количество карточек должно быть четным"
                            elif rows * cols > 100:
                                error_message = "Слишком большое поле (макс. 100 карточек)"
                            else:
                                return rows, cols # Возврат введенных размеров
                        except ValueError:
                            error_message = "Неправильный формат. Введите, например, 4x4"
                            text = '' # Очистка поля ввода при ошибке
                    elif event.key == pygame.K_BACKSPACE: # Обработка Backspace
                            text = text[:-1] # Удаление последнего символа
                            error_message = None # Сброс сообщения об ошибке
                    else: # Ввод текста
                        text += event.unicode # Добавление введенного символа
                        error_message = None # Сброс сообщения об ошибке
            if event.type == pygame.VIDEORESIZE: # Обработка изменения размера окна
                width, height = max(event.size[0], MIN_WIDTH), max(event.size[1], MIN_HEIGHT)
                screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
                return get_custom_size(screen, width, height)
           
        pygame.draw.rect(screen, YELLOW, back_btn) # Рисование кнопки "Назад"
        pygame.draw.rect(screen, BLACK, back_btn, 2) # Рисование обводки
        screen.blit(back_text, (back_btn.x + back_btn.width // 2 - back_text.get_width() // 2,
                               back_btn.y + back_btn.height // 2 - back_text.get_height() // 2)) # Отображение текста
        
        screen.blit(label, (width // 2 - label.get_width() // 2, height // 2 - 70)) # Отображение подсказки
        txt_surface = font.render(text, True, color) # Рендер введенного текста
        width_txt = max(200, txt_surface.get_width() + 10) # Определение ширины поля ввода
        input_box.w = width_txt # Установка ширины поля ввода
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5)) # Отображение текста в поле
        pygame.draw.rect(screen, color, input_box, 2) # Рисование поля ввода
        if error_message: # Отображение сообщения об ошибке
            error_surface = font_small.render(error_message, True, RED)
            screen.blit(error_surface, (width // 2 - error_surface.get_width() // 2, height // 2 + 40))
        pygame.display.flip() # Обновление экрана
 
def show_menu(screen, width, height, stats):
    # Рисуем меню-фон
    scaled_bg = pygame.transform.scale(menu_bg, (width, height)) # Масштабирование фона
    screen.blit(scaled_bg, (0, 0)) # Отображение фона
   
    title = font_large.render("Найди пару", True, BLACK) # Отображение заголовка
    screen.blit(title, (width // 2 - title.get_width() // 2, 50)) # Центрирование заголовка
 
    buttons = [] # Список кнопок меню
    sizes = [(2, 4), (3, 4), (4, 4), (4, 5), (4, 6)] # Предустановленные размеры поля
    button_height = 50
    button_width = 200
    button_margin = 20
    total_button_height = len(sizes) * (button_height + button_margin) + 2 * (button_height + button_margin) # Расчет общей высоты кнопок
    start_y = (height - total_button_height) // 2 # Расчет начальной y-координаты для центрирования
 
    for i, (rows, cols) in enumerate(sizes): # Создание кнопок для размеров
        btn_text = font_medium.render(f"{rows}x{cols}", True, WHITE) # Рендер текста кнопки
        btn_x = width // 2 - button_width // 2 # Вычисление x-координаты кнопки
        btn_y = start_y + i * (button_height + button_margin) # Вычисление y-координаты кнопки
        btn = pygame.Rect(btn_x, btn_y, button_width, button_height) # Создание объекта Rect для кнопки
        buttons.append((btn, rows, cols)) # Добавление кнопки в список
        pygame.draw.rect(screen, BLUE, btn) # Рисование кнопки
        pygame.draw.rect(screen, BLACK, btn, 2) # Рисование обводки
        screen.blit(btn_text, (btn.x + btn.width // 2 - btn_text.get_width() // 2,
                               btn.y + btn.height // 2 - btn_text.get_height() // 2)) # Центрирование текста
 
    custom_text = font_medium.render("Свой размер", True, WHITE) # Кнопка "Свой размер"
    custom_btn = pygame.Rect(width // 2 - button_width // 2,
                             start_y + len(sizes) * (button_height + button_margin),
                             button_width, button_height)
    pygame.draw.rect(screen, YELLOW, custom_btn) # Рисование кнопки
    pygame.draw.rect(screen, BLACK, custom_btn, 2) # Рисование обводки
    screen.blit(custom_text, (custom_btn.x + custom_btn.width // 2 - custom_text.get_width() // 2,
                               custom_btn.y + custom_btn.height // 2 - custom_text.get_height() // 2)) # Центрирование текста
 
    stats_text = font_medium.render("Статистика", True, WHITE) # Кнопка "Статистика"
    stats_btn = pygame.Rect(width // 2 - button_width // 2,
                             start_y + (len(sizes) + 1) * (button_height + button_margin),
                             button_width, button_height)
    pygame.draw.rect(screen, PURPLE, stats_btn) # Рисование кнопки
    pygame.draw.rect(screen, BLACK, stats_btn, 2) # Рисование обводки
    screen.blit(stats_text, (stats_btn.x + stats_btn.width // 2 - stats_text.get_width() // 2,
                              stats_btn.y + stats_btn.height // 2 - stats_text.get_height() // 2)) # Центрирование текста
 
    exit_text = font_medium.render("Выход", True, WHITE) # Кнопка "Выход"
    exit_btn = pygame.Rect(width - button_width - 20, 20, button_width, button_height)
    pygame.draw.rect(screen, RED, exit_btn) # Рисование кнопки
    pygame.draw.rect(screen, BLACK, exit_btn, 2) # Рисование обводки
    screen.blit(exit_text, (exit_btn.x + exit_btn.width // 2 - exit_text.get_width() // 2,
                            exit_btn.y + exit_btn.height // 2 - exit_text.get_height() // 2)) # Центрирование текста
 
    pygame.display.flip() # Обновление экрана
 
    while True: # Основной цикл меню
        for event in pygame.event.get(): # Обработка событий
            if event.type == pygame.QUIT: # Выход из игры
                pygame.quit()
                return None, None
            if event.type == pygame.MOUSEBUTTONDOWN: # Обработка клика мыши
                for btn, rows, cols in buttons: # Обработка нажатия на кнопки размеров
                    if btn.collidepoint(event.pos):
                        return rows, cols
                if custom_btn.collidepoint(event.pos): # Обработка кнопки "Свой размер"
                    custom_size = get_custom_size(screen, width, height)
                    if custom_size != (None, None):  # Проверяем, что не нажата кнопка "Назад"
                        return custom_size
                    else:
                        return show_menu(screen, width, height, stats)
                if stats_btn.collidepoint(event.pos): # Обработка кнопки "Статистика"
                    if not show_stats_screen(screen, width, height, stats):
                        return None, None
                    return show_menu(screen, width, height, stats)
                if exit_btn.collidepoint(event.pos): # Обработка кнопки "Выход"
                    pygame.quit()
                    return None, None
            if event.type == pygame.VIDEORESIZE: # Обработка изменения размера окна
                width, height = max(event.size[0], MIN_WIDTH), max(event.size[1], MIN_HEIGHT)
                screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
                return show_menu(screen, width, height, stats)
 
def calculate_board_offset(width, height, rows, cols):
    board_width = cols * (CARD_WIDTH + MARGIN) + MARGIN # Расчет общей ширины игрового поля
    board_height = rows * (CARD_HEIGHT + MARGIN) + MARGIN # Расчет общей высоты игрового поля
    x_offset = max((width - board_width) // 2, 0) # Расчет смещения по x для центрирования
    y_offset = max((height - board_height) // 2 + 50, 50) # Расчет смещения по y для центрирования
    return x_offset, y_offset
 
def calculate_board_size(width, height, rows, cols):
    max_card_width = (width - MARGIN * (cols + 1)) // cols # Максимально возможная ширина карточки
    max_card_height = (height - MARGIN * (rows + 1) - 50) // rows # Максимально возможная высота карточки
    card_size = min(max_card_width, max_card_height) # Выбор наименьшего размера для квадратных карточек
    
    board_width = cols * (card_size + MARGIN) + MARGIN # Расчет фактической ширины игрового поля
    board_height = rows * (card_size + MARGIN) + MARGIN # Расчет фактической высоты игрового поля
    x_offset = (width - board_width) // 2 # Расчет смещения по x
    y_offset = (height - board_height) // 2 + 50 # Расчет смещения по y
    
    return x_offset, y_offset, card_size, card_size
 
def main():
    pygame.display.set_caption("Найди пару") # Установка заголовка окна
    screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE) # Создание основного экрана
    clock = pygame.time.Clock() # Создание объекта Clock для контроля FPS
    stats = GameStats() # Создание объекта для хранения статистики
 
    while True: # Основной цикл игры
        width, height = screen.get_size() # Получение текущих размеров окна
        rows_cols = show_menu(screen, width, height, stats) # Отображение меню и получение выбора размера
        if not rows_cols: # Если пользователь вышел из меню
            break
        
        rows, cols = rows_cols # Получение выбранных размеров
        game = Game(rows, cols) # Создание объекта игры
        running = True # Флаг игрового цикла
        
        while running: # Игровой цикл
            width, height = screen.get_size() # Получение текущих размеров окна
            x_offset, y_offset, card_width, card_height = calculate_board_size(width, height, rows, cols) # Расчет размеров и смещений для карточек
            
            for event in pygame.event.get(): # Обработка событий
                if event.type == pygame.QUIT: # Обработка закрытия окна
                    running = False
                    pygame.quit()
                    return
                if event.type == pygame.MOUSEBUTTONDOWN: # Обработка клика мыши
                    pos = pygame.mouse.get_pos() # Получение позиции клика
                    # Обновленная проверка позиции кнопки "Назад"
                    if pygame.Rect(width - 110, 10, 100, 40).collidepoint(pos):
                        running = False
                    else: # Обработка клика по карточке
                        game.handle_click(pos, x_offset, y_offset, card_width, card_height)
                if event.type == pygame.VIDEORESIZE: # Обработка изменения размера окна
                    width, height = max(event.size[0], MIN_WIDTH), max(event.size[1], MIN_HEIGHT)
                    screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
 
            game.update() # Обновление состояния игры
            scaled_bg = pygame.transform.scale(game_bg, (width, height)) # Масштабирование фона
            screen.blit(scaled_bg, (0, 0)) # Отображение фона
            game.draw(screen, x_offset, y_offset, card_width, card_height, width, height) # Отрисовка игрового поля
            pygame.display.flip() # Обновление экрана
            clock.tick(30) # Контроль FPS
 
            if game.game_over: # Обработка завершения игры
                duration = int(time.time() - game.start_time) # Расчет времени игры
                stats.add_game(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), rows, cols, game.moves, duration) # Сохранение статистики
                result = show_game_over_screen(screen, width, height, game.moves, duration) # Отображение экрана завершения
                if result == "restart": # Перезапуск игры
                    game = Game(rows, cols)
                elif result == "menu": # Возврат в меню
                    running = False
                else: # Выход из игры
                    pygame.quit()
                    return
 
    pygame.quit() # Завершение Pygame
 
if __name__ == "__main__":
    main() # Запуск основной функции