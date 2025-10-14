from pygame.locals import *
from pygame.math import Vector2
from abc import ABC, abstractmethod
import pygame
import sys
import random

# Public variables
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


class Main:
    """TODO: Write documentation"""

    def __init__(self):
        self.snake = Snake()
        self.food = Food()
        self.food.set_random_pos(self.snake.body)
        self.food_spawner = FoodSpawner()

    def update(self):
        """TODO: Write documentation"""
        self.snake.move()
        self.check_collisions()

    def draw_elements(self):
        """TODO: Write documentation"""
        self.food.draw()
        self.snake.draw()

    def check_collisions(self):
        """TODO: Write documentation"""
        # Check if the head of the snake hits a screen border
        head = self.snake.body[0]
        if not 0 <= head.x < num_cells or not 0 <= head.y < num_cells:
            self.game_over()

        # Check if the snake ate food and draw new food
        if self.snake.body[0] == self.food.pos:
            self.food.effect(self.snake)
            self.food.set_random_pos(self.snake.body)

        # Check if the head of the snake hits itself
        for body_segment in self.snake.body[1:]:
            if head == body_segment:
                self.game_over()

    def game_over(self):
        """TODO: Write documentation"""
        pygame.quit()
        sys.exit()


class PowerUp(ABC):
    """Abstract base class to provide structure and behavior of
    CollectibleItems."""
    power: str = "Default"  # Default PowerUp name
    duration_s: float = 0.0  # Default duration of PowerUp in seconds
    rarity: float = 0.0  # Default PowerUp rarity
    growth: int = 1  # Default PowerUp growth
    active: bool = False  # PowerUp effect(s) is/are not active by default
    color: tuple = (227, 255, 69)  # Default PowerUp color
    pos: Vector2 = (0, 0)  # Default PowerUp coordinates

    def __init__(self):
        None

    @abstractmethod
    def draw(self):
        """TODO: Write documentation"""
        pass

    @abstractmethod
    def set_random_pos(self):
        """TODO: Write documentation"""
        pass

    @abstractmethod
    def effect(self, snake):
        """TODO: Write Documentation"""
        pass


class CollectibleItem(PowerUp):
    """TODO: Write documentation"""

    def __init__(self):
        None

    def draw(self):
        """TODO: Write documentation"""
        None

    def set_random_pos(self):
        None


class Food(CollectibleItem):
    """TODO: Write documentation"""

    def draw(self):
        """TODO: Write documentation"""
        food_rect = pygame.Rect(int(self.pos.x * cell_size),
                                int(self.pos.y * cell_size), cell_size, cell_size)
        pygame.draw.rect(screen, self.color, food_rect)

    def set_random_pos(self, snake_body):
        """TODO: Write documentation"""
        while True:
            self.x = random.randint(0, num_cells - 1)
            self.y = random.randint(0, num_cells - 1)
            self.pos = pygame.math.Vector2(self.x, self.y)

            # Check to make sure the food doesn't spawn inside the snake body
            if self.pos not in snake_body:
                return

    def effect(self, snake):
        """TODO: Write documentation"""
        Snake.grow(snake)


class FoodSpawner():
    """TODO: CURRENTLY UNIMPLEMENTED (needs documentation)
        This class will be used to handle the spawning and management of
        Food/PowerUps.
    """

    def __init__(self):
        """TODO: Write documentation"""
        self.powerups = []  # list of active PowerUp instances


class Snake:
    """TODO: Write documentation"""

    def __init__(self):
        self.body = [pygame.Vector2(6, 10), Vector2(5, 10), Vector2(4, 10)]
        self.length = len(self.body)
        self.direction = Vector2(1, 0)  # Snake moves to the right by default
        self.pending_growth = 0  # Number of queued growths remaining

    def draw(self):
        """TODO: Write documentation"""
        for body_segment in self.body:
            x = int(body_segment.x * cell_size)
            y = int(body_segment.y * cell_size)

            # Draw snake body with outside border
            body_rect = pygame.Rect(x, y, cell_size, cell_size)
            body_color = (3, 252, 86)
            pygame.draw.rect(screen, body_color, body_rect)

            left = pygame.Vector2(body_segment.x-1, body_segment.y)
            right = pygame.Vector2(body_segment.x+1, body_segment.y)
            up = pygame.Vector2(body_segment.x, body_segment.y-1)
            down = pygame.Vector2(body_segment.x, body_segment.y+1)
            border_color = (0, 0, 0)

            # Draw black border around the snake body, different edges
            # for each block. Check the neighbor of each body segment to
            # decide which sides need borders
            if left not in self.body:
                pygame.draw.line(screen, border_color,
                                 body_rect.topleft, body_rect.bottomleft, 2)
            if right not in self.body:
                pygame.draw.line(screen, border_color,
                                 body_rect.topright, body_rect.bottomright, 2)
            if up not in self.body:
                pygame.draw.line(screen, border_color,
                                 body_rect.topleft, body_rect.topright, 2)
            if down not in self.body:
                pygame.draw.line(screen, border_color,
                                 body_rect.bottomleft, body_rect.bottomright, 2)

    def move(self):
        """TODO: Write documentation"""
        new_head = self.body[0] + \
            self.direction  # Calculate the cooridnates of the new head
        self.body.insert(0, new_head)  # Move the head forward

        # If the snake doesn't have any extra growth queued, update the
        # tail, otherwise
        if self.pending_growth > 0:
            self.pending_growth -= 1
        else:
            self.body.pop()

        # # Copy all body segments except for the last
        # body_copy = self.body[:-1]
        # # Move the head forward
        # body_copy.insert(0, body_copy[0] + self.direction)
        # # Update the coordinates of the actual snake
        # self.body = body_copy[:]

    def grow(self, num_growths=1):
        """TODO: Write documentation"""
        self.pending_growth += num_growths
        self.length += num_growths


def play_music(music):
    """TODO: Write documentation"""
    pygame.mixer.music.stop()
    match music:
        case "main_menu":
            pygame.mixer.music.load('./music/main_menu_music.wav')
        case "game":
            pygame.mixer.music.load('./music/game_music.wav')
        case "sim":
            pygame.mixer.music.load('./music/sim_music.wav')
        case _:
            return  # Unknown music type, do nothing
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
    play_music("main_menu")
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
    main_game = Main()  # Create the snake and food
    # Trigger screen update event every 150ms
    UPDATE_SCREEN = pygame.USEREVENT
    pygame.time.set_timer(UPDATE_SCREEN, 150)
    play_music("game")
    running = True  # Game state
    # Whether or not the snake has already moved this tick
    is_snake_movable = True

    while running:
        # Clear screen with white at beginning of the frame
        screen.fill((250, 250, 250))
        draw_text('welcome to the game', font, (5, 15, 10),
                  screen, SCREEN_WIDTH//2, 100)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    # Switch back to main menu music
                    play_music("main_menu")
                    running = False
                # Ensure that the snake can only move one direction a frame
                elif is_snake_movable == True:
                    if event.key == K_UP and main_game.snake.direction != Vector2(0, 1):
                        main_game.snake.direction = Vector2(0, -1)
                        is_snake_movable = False
                    elif event.key == K_DOWN and main_game.snake.direction != Vector2(0, -1):
                        main_game.snake.direction = Vector2(0, 1)
                        is_snake_movable = False
                    elif event.key == K_LEFT and main_game.snake.direction != Vector2(1, 0):
                        main_game.snake.direction = Vector2(-1, 0)
                        is_snake_movable = False
                    elif event.key == K_RIGHT and main_game.snake.direction != Vector2(-1, 0):
                        main_game.snake.direction = Vector2(1, 0)
                        is_snake_movable = False
            elif event.type == UPDATE_SCREEN:
                main_game.update()
                is_snake_movable = True  # After the screen is updated, the snake can move again

        main_game.draw_elements()
        pygame.display.update()
        main_clock.tick(60)


def start_sim():
    """The simulation game loop. Handles all simulation logic."""
    play_music("sim")
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
                    play_music("main_menu")
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
