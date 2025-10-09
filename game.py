from pygame.locals import *
from pygame.math import Vector2
import pygame
import sys
import random


class Main:
    def __init__(self):
        self.snake = Snake()
        self.food = Food()
        self.food.set_random_pos(self.snake.body)

    def update(self):
        self.snake.move()
        self.check_collisions()

    def draw_elements(self):
        self.food.draw()
        self.snake.draw()

    def check_collisions(self):
        # Check if the head of the snake hits a screen border
        head = self.snake.body[0]
        if not 0 <= head.x < num_cells or not 0 <= head.y < num_cells:
            self.game_over()

        # Check if the snake ate food and draw new food
        if self.snake.body[0] == self.food.pos:
            self.snake.grow()
            self.food.set_random_pos(self.snake.body)

        # Check if the head of the snake hits itself
        for body_segment in self.snake.body[1:]:
            if head == body_segment:
                self.game_over()

    def game_over(self):
        pygame.quit()
        sys.exit()


class Food:
    def draw(self):
        food_rect = pygame.Rect(int(self.pos.x * cell_size),
                                int(self.pos.y * cell_size), cell_size, cell_size)
        pygame.draw.rect(screen, (227, 255, 69), food_rect)

    def set_random_pos(self, snake_body):
        respawn = True
        while True:
            self.x = random.randint(0, num_cells - 1)
            self.y = random.randint(0, num_cells - 1)
            self.pos = pygame.math.Vector2(self.x, self.y)

            # Check to make sure the food doesn't spawn inside the snake body
            if self.pos not in snake_body:
                return


class Snake:
    def __init__(self):
        self.body = [pygame.Vector2(6, 10), Vector2(5, 10), Vector2(4, 10)]
        self.length = len(self.body)
        self.direction = Vector2(1, 0)  # Snake moves to the right by default

    def draw(self):
        for body_segment in self.body:
            x = int(body_segment.x * cell_size)
            y = int(body_segment.y * cell_size)

            # Draw snake body with outside border
            body_rect = pygame.Rect(x, y, cell_size, cell_size)
            pygame.draw.rect(screen, (3, 252, 86), body_rect)

            # Check the neighbor of each body segment to decide which
            # sides need borders
            left = pygame.Vector2(body_segment.x-1, body_segment.y)
            right = pygame.Vector2(body_segment.x+1, body_segment.y)
            up = pygame.Vector2(body_segment.x, body_segment.y-1)
            down = pygame.Vector2(body_segment.x, body_segment.y+1)

            # Draw black border around the snake body
            if left not in self.body:
                pygame.draw.line(screen, (0, 0, 0),
                                 body_rect.topleft, body_rect.bottomleft, 2)
            if right not in self.body:
                pygame.draw.line(screen, (0, 0, 0),
                                 body_rect.topright, body_rect.bottomright, 2)
            if up not in self.body:
                pygame.draw.line(screen, (0, 0, 0),
                                 body_rect.topleft, body_rect.topright, 2)
            if down not in self.body:
                pygame.draw.line(screen, (0, 0, 0),
                                 body_rect.bottomleft, body_rect.bottomright, 2)

    def move(self):
        # Copy all body segments except for the last
        body_copy = self.body[:-1]
        # Move the head forward
        body_copy.insert(0, body_copy[0] + self.direction)
        self.body = body_copy[:]  # Update the coordinates of the actual snake

    def grow(self):
        self.body.append(self.body[-1])
        self.length += 1


main_clock = pygame.time.Clock()
pygame.init()
pygame.display.set_caption('Super Snake Battle Royale Ultimate')
# Credit for music goes to Newgrounds user ZaneLittle: https://www.newgrounds.com/audio/listen/1475739
cell_size = 40
num_cells = 20
screen = pygame.display.set_mode(
    (num_cells * cell_size, num_cells * cell_size))

# screen = pygame.display.set_mode((0, 0))
SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_width(), screen.get_height()

font = pygame.font.SysFont(None, 100)
click = False  # Boolean flag for click events


def play_main_menu_music():
    """Plays the main menu music"""
    pygame.mixer.music.stop()
    pygame.mixer.music.load('./music/main_menu_music.wav')
    pygame.mixer.music.play(-1)


def play_game_music():
    """Plays the game music"""
    pygame.mixer.music.stop()
    pygame.mixer.music.load('./music/game_music.wav')
    pygame.mixer.music.play(-1)


def play_sim_music():
    """Plays the simulation music"""
    pygame.mixer.music.stop()
    pygame.mixer.music.load('./music/sim_music.wav')
    pygame.mixer.music.play(-1)


def play_main_menu_music():
    pygame.mixer.music.stop()
    pygame.mixer.music.load('./music/main_menu_music.wav')
    pygame.mixer.music.play(-1)


def play_game_music():
    pygame.mixer.music.stop()
    pygame.mixer.music.load('./music/game_music.wav')
    pygame.mixer.music.play(-1)


def play_sim_music():
    pygame.mixer.music.stop()
    pygame.mixer.music.load('./music/sim_music.wav')
    pygame.mixer.music.play(-1)


def draw_button(surface, button, text, font, bg_color, text_color):
    """Draws a rectangular button with centered text to a surface.

    Args:
        surface (pygame.Surface): The surface to draw onto.
        button (pygame.Rect): The button rectangle.
        text (str): The label displayed on the button.
        font (pygame.font.Font): The pygame font used to render the text.
        bg_color (tuple[int, int, int]): RGB color for the button
            background.
        text_color (tuple[int, int, int]): RGB color for the button text.

    Returns:
        None
    """

    # Draw button background
    pygame.draw.rect(surface, bg_color, button)

    # Render the text
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=button.center)

    # BLIT text centered in the button
    surface.blit(text_surface, text_rect)


def draw_text(text, font, color, surface, x, y, center=True):
    """Draws text to a surface.

    Args:
        text (str): The text to render.
        font (pygame.font.Font): The pygame font object.
        color (tuple[int, int, int]): The RGB color of the text.
        x (int): X coordiante.
        y (int): Y coordinate.
        center (bool, optional): If True, the text is centered at (x, y).
            If false, the text's top-left corner is positioned at (x, y).
            Defaults to True.

    Returns:
        None
    """
    text_obj = font.render(text, 1, color)  # create surface with rendered text
    text_rect = text_obj.get_rect()  # get a reference to the text_obj rect
    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)

    surface.blit(text_obj, text_rect)  # BLIT text to the surface


def main_menu():
    """The menu game loop. Handles all main menu logic."""
    # Start menu music
    play_main_menu_music()
    while True:
        screen.fill((250, 250, 250))
        draw_text('main menu', font,
                  (5, 15, 10), screen, SCREEN_WIDTH//2, 100)

        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Menu button setup
        button_labels = ["Start Game", "Simulation", "Settings", "Quit"]

        # List of RGB tuples for button background colors
        button_colors = [
            (255, 0, 0),
            (0, 255, 0),
            (0, 0, 255),
            (205, 220, 190)
        ]

        menu_buttons = []  # List of pygame.Rect objects (buttons)

        num_buttons = len(button_labels)
        menu_button_width, menu_button_height = 400, 75
        menu_button_padding = 20  # Spacing between buttons

        # Total height of all buttons including padding (amount of space
        # taken up by the buttons in the window)
        total_button_height = (menu_button_height * num_buttons) + \
            (menu_button_padding * (num_buttons - 1))

        # Starting Y position for vertical centering of buttons
        button_start_y = (SCREEN_HEIGHT - total_button_height) // 2

        # Create menu buttons
        for i, label in enumerate(button_labels):
            menu_button = pygame.Rect(
                0, 0, menu_button_width, menu_button_height)
            menu_button.center = (
                SCREEN_WIDTH // 2, button_start_y + i * (menu_button_height + menu_button_padding))
            menu_buttons.append((menu_button, label, button_colors[i]))

        # Draw the buttons to the main menu screen
        for button, label, button_color in menu_buttons:
            draw_button(screen, button, label, font,
                        button_color, (0, 0, 0))
            # Check if the user clicks a menu button
            if button.collidepoint((mouse_x, mouse_y)) and click:
                if label == "Start Game":
                    start_game()
                elif label == "Simulation":
                    start_sim()
                elif label == "Settings":
                    settings()
                elif label == "Quit":
                    pygame.quit()
                    sys.exit()

        click = False  # Reset the click event flag
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True
        pygame.display.update()
        main_clock.tick(60)


def start_game():
    """The actual game loop. Handles all snake game logic."""
    main_game = Main()
    # Trigger screen update event every 150ms
    UPDATE_SCREEN = pygame.USEREVENT
    pygame.time.set_timer(UPDATE_SCREEN, 150)
    play_game_music()
    running = True
    while running:
        # Clear screen at beginning of the frame with white
        screen.fill((250, 250, 250))
        draw_text('welcome to the game', font, (5, 15, 10),
                  screen, SCREEN_WIDTH//2, 100)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    # Switch back to main menu music
                    play_main_menu_music()
                    running = False
                if event.key == K_UP and main_game.snake.direction != (0, 1):
                    main_game.snake.direction = (0, -1)
                if event.key == K_DOWN and main_game.snake != (0, -1):
                    main_game.snake.direction = (0, 1)
                if event.key == K_LEFT and main_game.snake != (1, 0):
                    main_game.snake.direction = (-1, 0)
                if event.key == K_RIGHT and main_game.snake != (-1, 0):
                    main_game.snake.direction = (1, 0)
            if event.type == UPDATE_SCREEN:
                main_game.update()

            main_game.draw_elements()
            pygame.display.update()
            main_clock.tick(60)


def start_sim():
    """The simulation game loop. Handles all simulation logic."""
    play_sim_music()
    running = True
    while running:
        # Clear screen at beginning of the frame with white
        screen.fill((250, 250, 250))
        draw_text('this is the simulation', font,
                  (5, 15, 10), screen, SCREEN_WIDTH//2, 100)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    # Switch back to main menu music
                    play_main_menu_music()
                    running = False
        pygame.display.update()
        main_clock.tick(60)


def settings():
    """The settings game loop. Handles all settings logic."""
    running = True
    while running:
        # Clear screen at beginning of the frame with white
        screen.fill((250, 250, 250))
        draw_text('Settings', font, (5, 15, 10), screen, SCREEN_WIDTH//2, 100)

        setting_label = pygame.font.SysFont(None, 75)

        draw_text('Volume', setting_label, (5, 15, 10),
                  screen, SCREEN_WIDTH//2.5, 250)
        slider_rect = pygame.Rect(
            SCREEN_WIDTH//1.75, 250, 200, 10)  # Slider track
        # Calculate the x coordinate of the slider handle (default
        # volume set at 100%)
        handle_x = SCREEN_WIDTH//1.75 + slider_rect.width
        handle_rect = pygame.Rect(handle_x, 245, 10, 20)  # Slider handle

        pygame.draw.rect(screen, (100, 100, 100), slider_rect)  # Draw track
        pygame.draw.rect(screen, (200, 200, 200), handle_rect)  # Draw handle

        dragging = False
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if handle_rect.collidepoint(event.pos):
                    dragging = True
            elif event.type == pygame.MOUSEBUTTONUP:
                dragging = False
            elif event.type == pygame.MOUSEMOTION and dragging:
                # Constrain handle movement within slider_rect
                handle_rect.x = max(slider_rect.left, min(
                    event.pos[0], slider_rect.right - handle_rect.width))

        volume = (handle_rect.centerx - slider_rect.left) / \
            slider_rect.width
        pygame.mixer.music.set_volume(volume)

        pygame.display.update()
        main_clock.tick(60)


def game_over():
    None  # Unimplemented


main_menu()
