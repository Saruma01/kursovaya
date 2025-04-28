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
    card_back = pygame.image.load('C:\\Users\\Admin\\Documents\\kursovaya\\card.jpg')
except pygame.error as e:
    print(f"Ошибка загрузки фоновых изображений: {e}")
    game_bg = pygame.Surface((1, 1))
    game_bg.fill(GRAY)
    menu_bg = pygame.Surface((1, 1))
    menu_bg.fill(WHITE)
    card_back = pygame.Surface((1, 1))
    card_back.fill(BLUE)

class Card:
    def __init__(self, value, row, col):
        self.value = value
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
        self.games = []
        self.filename = "memory_game_stats.txt"
        self.load_stats()

    def add_game(self, date_time, rows, cols, moves, duration):
        self.games.append({
            "date_time": date_time,
            "rows": rows,
            "cols": cols,
            "moves": moves,
            "duration": duration
        })
        self.save_stats()

    def save_stats(self):
        with open(self.filename, "w") as f:
            for game in self.games:
                f.write(f"{game['date_time']},{game['rows']},{game['cols']},"
                        f"{game['moves']},{game['duration']}\n")

    def load_stats(self):
        if os.path.exists(self.filename):
            with open(self.filename, "r") as f:
                for line in f:
                    parts = line.strip().split(',')
                    if len(parts) == 5:
                        self.games.append({
                            "date_time": parts[0],
                            "rows": int(parts[1]),
                            "cols": int(parts[2]),
                            "moves": int(parts[3]),
                            "duration": int(parts[4])
                        })

class Game:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.cards = []
        self.selected = []
        self.moves = 0
        self.solved_pairs = 0
        self.total_pairs = (rows * cols) // 2
        self.start_time = time.time()
        self.game_over = False
        self.waiting = False
        self.wait_start = 0
        self.generate_board()

    def generate_board(self):
        values = [num for num in random.sample(range(10, 100), self.total_pairs) for _ in (0, 1)]
        random.shuffle(values)
        self.cards = [Card(values[i], row, col) 
                     for row in range(self.rows) 
                     for col in range(self.cols) 
                     for i in [row*self.cols + col]]

    def handle_click(self, pos, x_offset, y_offset, card_width, card_height):
        if self.waiting or self.game_over:
            return
        for card in self.cards:
            if card.is_clicked(pos, x_offset, y_offset, card_width, card_height):
                card.visible = True
                self.selected.append(card)
                if len(self.selected) == 2:
                    self.moves += 1
                    if self.selected[0].value == self.selected[1].value:
                        for c in self.selected:
                            c.solved = True
                        self.solved_pairs += 1
                        self.selected = []
                        if self.solved_pairs == self.total_pairs:
                            self.game_over = True
                    else:
                        self.waiting = True
                        self.wait_start = time.time()
                break

    def update(self):
        if self.waiting and time.time() - self.wait_start > 1:
            for card in self.selected:
                card.visible = False
            self.selected = []
            self.waiting = False

    def draw(self, screen, x_offset, y_offset, card_width, card_height, width, height):
        scaled_bg = pygame.transform.scale(game_bg, (width, height))
        screen.blit(scaled_bg, (0, 0))
        
        info_text = font_medium.render(
            f"Ходы: {self.moves} | Найдено пар: {self.solved_pairs}/{self.total_pairs}", 
            True, WHITE
        )
        screen.blit(info_text, (10, 10))
        
        # Измененная позиция кнопки "Назад" (правый верхний угол)
        back_btn = pygame.Rect(width - 110, 10, 100, 40)  # X: ширина экрана - 110 (100 ширина + 10 отступ)
        pygame.draw.rect(screen, YELLOW, back_btn)
        pygame.draw.rect(screen, BLACK, back_btn, 2)
        back_text = font_small.render("Назад", True, WHITE)
        screen.blit(back_text, back_text.get_rect(center=back_btn.center))
    
        for card in self.cards:
            card.draw(screen, x_offset, y_offset, card_width, card_height)


def show_stats_screen(screen, width, height, stats):
    # Рисуем меню-фон
    scaled_bg = pygame.transform.scale(menu_bg, (width, height))
    screen.blit(scaled_bg, (0, 0))
    title = font_large.render("Статистика игр", True, WHITE)
    screen.blit(title, (width // 2 - title.get_width() // 2, 30))

    back_btn = pygame.Rect(20, 20, 100, 40)
    pygame.draw.rect(screen, YELLOW, back_btn)
    pygame.draw.rect(screen, BLACK, back_btn, 2)
    back_text = font_small.render("Назад", True, WHITE)
    screen.blit(back_text, (back_btn.x + back_btn.width // 2 - back_text.get_width() // 2,
                           back_btn.y + back_btn.height // 2 - back_text.get_height() // 2))

    if not stats.games:
        no_stats = font_medium.render("Нет данных о прошлых играх", True, WHITE)
        screen.blit(no_stats, (width // 2 - no_stats.get_width() // 2, height // 2))
    else:
        headers = ["Дата и время", "Размер", "Ходы", "Время (сек)"]
        for i, header in enumerate(headers):
            text = font_small.render(header, True, PURPLE)
            screen.blit(text, (50 + i * 200, 100))

        for i, game in enumerate(stats.games[-10:]):
            date_text = font_small.render(game['date_time'], True, WHITE)
            size_text = font_small.render(f"{game['rows']}x{game['cols']}", True, WHITE)
            moves_text = font_small.render(str(game['moves']), True, WHITE)
            time_text = font_small.render(str(game['duration']), True, WHITE)
            screen.blit(date_text, (50, 130 + i * 30))
            screen.blit(size_text, (250, 130 + i * 30))
            screen.blit(moves_text, (450, 130 + i * 30))
            screen.blit(time_text, (650, 130 + i * 30))

    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_btn.collidepoint(event.pos):
                    return True
            if event.type == pygame.VIDEORESIZE:
                width, height = max(event.size[0], MIN_WIDTH), max(event.size[1], MIN_HEIGHT)
                screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
                return show_stats_screen(screen, width, height, stats)

def show_game_over_screen(screen, width, height, moves, duration):
    # Рисуем меню-фон
    scaled_bg = pygame.transform.scale(menu_bg, (width, height))
    screen.blit(scaled_bg, (0, 0))
    victory_text = font_large.render("Победа!", True, GREEN)
    screen.blit(victory_text, (width // 2 - victory_text.get_width() // 2, height // 2 - 100))

    stats_text = f"Время: {duration} сек. | Ходы: {moves}"
    stats_surface = font_medium.render(stats_text, True, BLACK)
    screen.blit(stats_surface, (width // 2 - stats_surface.get_width() // 2, height // 2 - 30))

    # Увеличиваем размер кнопок
    restart_btn = pygame.Rect(width // 2 - 250, height // 2 + 30, 220, 60)  # Шире и выше
    pygame.draw.rect(screen, BLUE, restart_btn)
    pygame.draw.rect(screen, BLACK, restart_btn, 2)
    restart_text = font_medium.render("Начать сначала", True, WHITE)
    screen.blit(restart_text, (restart_btn.x + restart_btn.width // 2 - restart_text.get_width() // 2,
                              restart_btn.y + restart_btn.height // 2 - restart_text.get_height() // 2))

    menu_btn = pygame.Rect(width // 2 + 30, height // 2 + 30, 220, 60)  # Шире и выше
    pygame.draw.rect(screen, YELLOW, menu_btn)
    pygame.draw.rect(screen, BLACK, menu_btn, 2)
    menu_text = font_medium.render("Вернуться в меню", True, WHITE)
    screen.blit(menu_text, (menu_btn.x + menu_btn.width // 2 - menu_text.get_width() // 2,
                            menu_btn.y + menu_btn.height // 2 - menu_text.get_height() // 2))

    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            if event.type == pygame.MOUSEBUTTONDOWN:
                if restart_btn.collidepoint(event.pos):
                    return "restart"
                if menu_btn.collidepoint(event.pos):
                    return "menu"
            if event.type == pygame.VIDEORESIZE:
                width, height = max(event.size[0], MIN_WIDTH), max(event.size[1], MIN_HEIGHT)
                screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
                return show_game_over_screen(screen, width, height, moves, duration)

def get_custom_size(screen, width, height):
     # Рисуем меню-фон
    scaled_bg = pygame.transform.scale(menu_bg, (width, height))
    screen.blit(scaled_bg, (0, 0))
    input_box = pygame.Rect(width // 2 - 100, height // 2 - 25, 200, 50)
    color_inactive = pygame.Color(165, 92, 255)
    color_active = pygame.Color(73, 0, 163)
    color = color_inactive
    active = False
    text = ''
    font = font_medium
    label = font.render("Введите размер (например, 4x4):", True,PURPLEW)
    error_message = None
    
    back_btn = pygame.Rect(20, 20, 100, 40)
    back_text = font_small.render("Назад", True, WHITE)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None, None
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive
                
                if back_btn.collidepoint(event.pos):
                    return None, None  # Возвращаем None для выхода в меню
                    
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        try:
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
                                return rows, cols
                        except ValueError:
                            error_message = "Неправильный формат. Введите, например, 4x4"
                        text = ''
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                        error_message = None
                    else:
                        text += event.unicode
                        error_message = None
            if event.type == pygame.VIDEORESIZE:
                width, height = max(event.size[0], MIN_WIDTH), max(event.size[1], MIN_HEIGHT)
                screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
                return get_custom_size(screen, width, height)
            
        pygame.draw.rect(screen, YELLOW, back_btn)
        pygame.draw.rect(screen, BLACK, back_btn, 2)
        screen.blit(back_text, (back_btn.x + back_btn.width // 2 - back_text.get_width() // 2,
                               back_btn.y + back_btn.height // 2 - back_text.get_height() // 2))
        
        screen.blit(label, (width // 2 - label.get_width() // 2, height // 2 - 70))
        txt_surface = font.render(text, True, color)
        width_txt = max(200, txt_surface.get_width() + 10)
        input_box.w = width_txt
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        pygame.draw.rect(screen, color, input_box, 2)
        if error_message:
            error_surface = font_small.render(error_message, True, RED)
            screen.blit(error_surface, (width // 2 - error_surface.get_width() // 2, height // 2 + 40))
        pygame.display.flip()

def show_menu(screen, width, height, stats):
    # Рисуем меню-фон
    scaled_bg = pygame.transform.scale(menu_bg, (width, height))
    screen.blit(scaled_bg, (0, 0))
    
    title = font_large.render("Найди пару", True, BLACK)
    screen.blit(title, (width // 2 - title.get_width() // 2, 50))

    buttons = []
    sizes = [(2, 4), (3, 4), (4, 4), (4, 5), (4, 6)]
    button_height = 50
    button_width = 200
    button_margin = 20
    total_button_height = len(sizes) * (button_height + button_margin) + 2 * (button_height + button_margin)
    start_y = (height - total_button_height) // 2

    for i, (rows, cols) in enumerate(sizes):
        btn_text = font_medium.render(f"{rows}x{cols}", True, WHITE)
        btn_x = width // 2 - button_width // 2
        btn_y = start_y + i * (button_height + button_margin)
        btn = pygame.Rect(btn_x, btn_y, button_width, button_height)
        buttons.append((btn, rows, cols))
        pygame.draw.rect(screen, BLUE, btn)
        pygame.draw.rect(screen, BLACK, btn, 2)
        screen.blit(btn_text, (btn.x + btn.width // 2 - btn_text.get_width() // 2,
                               btn.y + btn.height // 2 - btn_text.get_height() // 2))

    custom_text = font_medium.render("Свой размер", True, WHITE)
    custom_btn = pygame.Rect(width // 2 - button_width // 2,
                             start_y + len(sizes) * (button_height + button_margin),
                             button_width, button_height)
    pygame.draw.rect(screen, YELLOW, custom_btn)
    pygame.draw.rect(screen, BLACK, custom_btn, 2)
    screen.blit(custom_text, (custom_btn.x + custom_btn.width // 2 - custom_text.get_width() // 2,
                              custom_btn.y + custom_btn.height // 2 - custom_text.get_height() // 2))

    stats_text = font_medium.render("Статистика", True, WHITE)
    stats_btn = pygame.Rect(width // 2 - button_width // 2, 
                            start_y + (len(sizes) + 1) * (button_height + button_margin),
                            button_width, button_height)
    pygame.draw.rect(screen, PURPLE, stats_btn)
    pygame.draw.rect(screen, BLACK, stats_btn, 2)
    screen.blit(stats_text, (stats_btn.x + stats_btn.width // 2 - stats_text.get_width() // 2,
                             stats_btn.y + stats_btn.height // 2 - stats_text.get_height() // 2))

    exit_text = font_medium.render("Выход", True, WHITE)
    exit_btn = pygame.Rect(width - button_width - 20, 20, button_width, button_height)
    pygame.draw.rect(screen, RED, exit_btn)
    pygame.draw.rect(screen, BLACK, exit_btn, 2)
    screen.blit(exit_text, (exit_btn.x + exit_btn.width // 2 - exit_text.get_width() // 2,
                            exit_btn.y + exit_btn.height // 2 - exit_text.get_height() // 2))

    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None, None
            if event.type == pygame.MOUSEBUTTONDOWN:
                for btn, rows, cols in buttons:
                    if btn.collidepoint(event.pos):
                        return rows, cols
                if custom_btn.collidepoint(event.pos):
                    custom_size = get_custom_size(screen, width, height)
                    if custom_size != (None, None):  # Проверяем, что не нажата кнопка "Назад"
                        return custom_size
                    else:
                        return show_menu(screen, width, height, stats)
                if stats_btn.collidepoint(event.pos):
                    if not show_stats_screen(screen, width, height, stats):
                        return None, None
                    return show_menu(screen, width, height, stats)
                if exit_btn.collidepoint(event.pos):
                    pygame.quit()
                    return None, None
            if event.type == pygame.VIDEORESIZE:
                width, height = max(event.size[0], MIN_WIDTH), max(event.size[1], MIN_HEIGHT)
                screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
                return show_menu(screen, width, height, stats)

def calculate_board_offset(width, height, rows, cols):
    board_width = cols * (CARD_WIDTH + MARGIN) + MARGIN
    board_height = rows * (CARD_HEIGHT + MARGIN) + MARGIN
    x_offset = max((width - board_width) // 2, 0)  # Не даем смещению быть отрицательным
    y_offset = max((height - board_height) // 2 + 50, 50)  # Минимальное смещение по Y
    return x_offset, y_offset

def calculate_board_size(width, height, rows, cols):
    max_card_width = (width - MARGIN * (cols + 1)) // cols
    max_card_height = (height - MARGIN * (rows + 1) - 50) // rows
    card_size = min(max_card_width, max_card_height)
    
    board_width = cols * (card_size + MARGIN) + MARGIN
    board_height = rows * (card_size + MARGIN) + MARGIN
    x_offset = (width - board_width) // 2
    y_offset = (height - board_height) // 2 + 50
    
    return x_offset, y_offset, card_size, card_size

def main():
    pygame.display.set_caption("Найди пару")
    screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
    clock = pygame.time.Clock()
    stats = GameStats()

    while True:
        width, height = screen.get_size()
        rows_cols = show_menu(screen, width, height, stats)
        if not rows_cols:
            break
        
        rows, cols = rows_cols
        game = Game(rows, cols)
        running = True
        
        while running:
            width, height = screen.get_size()
            x_offset, y_offset, card_width, card_height = calculate_board_size(width, height, rows, cols)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    # Обновленная проверка позиции кнопки
                    if pygame.Rect(width - 110, 10, 100, 40).collidepoint(pos):
                        running = False
                    else:
                        game.handle_click(pos, x_offset, y_offset, card_width, card_height)
                if event.type == pygame.VIDEORESIZE:
                    width, height = max(event.size[0], MIN_WIDTH), max(event.size[1], MIN_HEIGHT)
                    screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)

            game.update()
            scaled_bg = pygame.transform.scale(game_bg, (width, height))
            screen.blit(scaled_bg, (0, 0))
            game.draw(screen, x_offset, y_offset, card_width, card_height, width, height)
            pygame.display.flip()
            clock.tick(30)

            if game.game_over:
                duration = int(time.time() - game.start_time)
                stats.add_game(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), rows, cols, game.moves, duration)
                result = show_game_over_screen(screen, width, height, game.moves, duration)
                if result == "restart":
                    game = Game(rows, cols)
                elif result == "menu":
                    running = False
                else:
                    pygame.quit()
                    return

    pygame.quit()

if __name__ == "__main__":
    main()