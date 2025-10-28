from pygame.locals import *
from pygame.math import Vector2
from abc import ABC, abstractmethod
import pygame
import sys
import random

game_clock = pygame.time.Clock()
pygame.init()
pygame.display.set_caption('Super Snake Battle Royale Ultimate')
cell_size = 40
num_cells = 20
GRID_SIZE = (num_cells * cell_size, num_cells * cell_size)

WINDOWED_MODE = "windowed"
BORDERLESS_MODE = "borderless"
FULLSCREEN_MODE = "fullscreen"
current_display_mode = WINDOWED_MODE
UPDATE_SCREEN = pygame.USEREVENT  # Global screen update event


def set_mode(mode):
    """TODO: Write documentation"""
    global screen, current_display_mode
    # The flags argument controls which type of display the window
    # should use. Multiple types can be combined using the bitwise or
    # operator (pipe "|" character).
    # https://www.pygame.org/docs/ref/display.html#pygame.display.set_mode
    flags = 0

    size = GRID_SIZE

    # Set the flags for each display mode
    if mode == WINDOWED_MODE:
        flags = pygame.RESIZABLE | pygame.SCALED
    elif mode == BORDERLESS_MODE:
        flags = pygame.NOFRAME | pygame.SCALED
    elif mode == FULLSCREEN_MODE:
        flags = pygame.FULLSCREEN

    screen = pygame.display.set_mode(GRID_SIZE, flags)
    curren_display_mode = mode
    return screen


screen = set_mode(WINDOWED_MODE)
SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_width(), screen.get_height()

font = pygame.font.SysFont(None, 100)
font2 = pygame.font.SysFont(None, 50)


class Main:
    """TODO: Write documentation"""

    def __init__(self):
        self.snakes = [
            Snake(start_pos=Vector2(5,5), direction=Vector2(1, 0), color=(0, 200, 0), snake_id=0),
            Snake(start_pos=Vector2(14, 14), direction=Vector2(-1, 0), color=(0, 0, 200), snake_id=1),
            Snake(start_pos=Vector2(5, 14), direction=Vector2(0, -1), color=(200, 0, 0), snake_id=2),
            Snake(start_pos=Vector2(14, 5), direction=Vector2(0, 1), color=(200, 0, 200), snake_id=3),
        ]
        #self.food = Food()
        #self.food_spawner = FoodSpawner() #ignoring this for now cause we don't need food for now

    def update(self):
        """TODO: Write documentation"""
        # move all alive snakes
        for snake in self.snakes:
            if not snake.is_dead:
                snake.move()
        # after everyone moves, resolve collisions
        self.check_collisions()

    def draw_elements(self):
        """TODO: Write documentation"""
        for snake in self.snakes:
            if not snake.is_dead:
                snake.draw()

    def check_collisions(self):
        """TODO: Write documentation"""
        # Border and self collision 
        for snake in self.snakes:
            if snake.is_dead:
                continue

            head = snake.body[0]
            
            # out of bounds 
            if not (0 <= head.x < num_cells and 0 <= head.y < num_cells):
                snake.is_dead = True
                continue

            # bite their own body
            if head in snake.body[1:]:
                snake.is_dead = True
                continue

        # Now snake vs snake collision
        # we gonna check each pair (attacker, victim)
        for attacker in self.snakes:
            if attacker.is_dead:
                continue
            attacker_head = attacker.body[0]

            for victim in self.snakes:
                if victim.is_dead:
                    continue
                if victim.id == attacker.id:
                    continue #we just want to check if its not comparing with it self

                #if attacker head hit any part fo victim 
                if attacker_head in victim.body:
                    #attacker eat victim
                    victim.is_dead = True
                    #rewad the attacke to grow by 3 squares
                    attacker.grow(num_growths=3)
        # # Check if the head of the snake hits a screen border
        # head = self.snake.body[0]
        # if not 0 <= head.x < num_cells or not 0 <= head.y < num_cells:
        #     self.game_over()

        # # Check if the snake ate food and draw new food
        # if self.snake.body[0] == self.food.pos:
        #     self.food.effect(self.snake)
        #     self.food.set_random_pos(self.snake.body)

        # # Check if the head of the snake hits itself
        # for body_segment in self.snake.body[1:]:
        #     if head == body_segment:
        #         self.game_over()

    def game_over(self):
        """TODO: Write documentation"""
        self.snake.is_dead = True


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
    is_spawned: bool = False  # PowerUps are not spawned by default

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
        collectible_rect = pygame.Rect(int(self.pos.x * cell_size),
                                       int(self.pos.y * cell_size), cell_size, cell_size)
        pygame.draw.rect(screen, self.color, collectible_rect)

    def set_random_pos(self, snake_body):
        """TODO: Write documentation"""
        while True:
            self.x = random.randint(0, num_cells - 1)
            self.y = random.randint(0, num_cells - 1)
            self.pos = pygame.math.Vector2(self.x, self.y)

            # Check to make sure the food doesn't spawn inside the snake body
            if self.pos not in snake_body:
                return


class Food(CollectibleItem):
    """TODO: Write documentation"""

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

    def __init__(self, start_pos, direction, color, snake_id):
        # self.body = [pygame.Vector2(6, 10), Vector2(5, 10), Vector2(4, 10)]
        self.direction = direction  # Snake moves to the right by default
        self.color = color # r,g,b
        self.id = snake_id # id for each agent snake (int or string)

        # initial 3 blocks of body in a row
        self.body = [
            pygame.Vector2(start_pos.x, start_pos.y),
            pygame.Vector2(start_pos.x - direction.x, start_pos.y - direction.y),
            pygame.Vector2(start_pos.x - 2*direction.x, start_pos.y - 2*direction.y),
        ]
        self.length = len(self.body)
        self.pending_growth = 0  # Number of queued growths remaining
        self.is_dead = False

    def draw(self):
        """TODO: Write documentation"""
        for body_segment in self.body:
            x = int(body_segment.x * cell_size)
            y = int(body_segment.y * cell_size)

            # Draw snake body with outside border
            body_rect = pygame.Rect(x, y, cell_size, cell_size)
            #body_color = (3, 252, 86)
            pygame.draw.rect(screen, self.color, body_rect)

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
    """Credit for music goes to Newgrounds user ZaneLittle: https://www.newgrounds.com/audio/listen/1475739"""
    pygame.mixer.music.stop()
    match music:
        case "main_menu":
            pygame.mixer.music.load('./music/main_menu_music.wav')
        case "game":
            pygame.mixer.music.load('./music/game_music.wav')
        case "sim":
            pygame.mixer.music.load('./music/sim_music.wav')
        case "game_over":
            pygame.mixer.music.load('./music/game_over_music.wav')
        case "pause_menu":
            pygame.mixer.music.load('./music/pause_menu_music.wav')
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

    transparent_surface = pygame.Surface(
        (button.width, button.height), pygame.SRCALPHA)

    # Draw button background
    pygame.draw.rect(transparent_surface, bg_color,
                     transparent_surface.get_rect())

    # Render the text
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(
        center=(button.width//2, button.height//2))
    transparent_surface.blit(text_surface, text_rect)

    # BLIT text centered in the button
    surface.blit(transparent_surface, button.topleft)


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
    click = False

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
        game_clock.tick(60)


def start_game():
    """The actual game loop. Handles all snake game logic."""
    game = Main()  # Create the snake and food
    food = game.food
    snake = game.snake
    # Trigger screen update event every 150ms
    pygame.time.set_timer(UPDATE_SCREEN, 150)

    pygame.mixer.music.stop()  # Stop playing the menu music

    # Whether or not the snake has already moved this tick
    is_snake_movable = True
    game_not_started = True
    ignore_next_keydown = False

    while True:
        # Clear screen with white at beginning of the frame
        screen.fill((250, 250, 250))

        if game_not_started:
            draw_text('welcome to the game', font, (5, 15, 10),
                      screen, SCREEN_WIDTH//2, 100)
            draw_text('press any key to start', font, (5, 15, 10),
                      screen, SCREEN_WIDTH//2, 175)
            game.draw_elements()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == KEYDOWN:
                # Ignore the first keypress after pause to prevent
                # instant movement
                if ignore_next_keydown:
                    ignore_next_keydown = False
                    continue

                if game_not_started:
                    if not food.is_spawned:
                        food.set_random_pos(snake.body)
                        food.is_spawned = True
                    game_not_started = not game_not_started
                    play_music("game")
                    continue

                if event.key == K_ESCAPE:
                    pygame.time.set_timer(UPDATE_SCREEN, 0)
                    pause_menu(game)
                    pygame.event.clear(pygame.KEYDOWN)
                    ignore_next_keydown = True
                    pygame.time.set_timer(UPDATE_SCREEN, 150)
                    continue

                # Ensure that the snake can only move one direction a frame
                elif is_snake_movable == True:
                    if event.key == K_UP and snake.direction != Vector2(0, 1):
                        game.snake.direction = Vector2(0, -1)
                        is_snake_movable = False
                    elif event.key == K_DOWN and snake.direction != Vector2(0, -1):
                        snake.direction = Vector2(0, 1)
                        is_snake_movable = False
                    elif event.key == K_LEFT and snake.direction != Vector2(1, 0):
                        snake.direction = Vector2(-1, 0)
                        is_snake_movable = False
                    elif event.key == K_RIGHT and snake.direction != Vector2(-1, 0):
                        snake.direction = Vector2(1, 0)
                        is_snake_movable = False

            elif event.type == UPDATE_SCREEN:
                if not game_not_started:
                    game.update()
                    is_snake_movable = True  # After the screen is updated, the snake can move again

        game.draw_elements()
        pygame.display.update()
        game_clock.tick(60)

        # Check if the game is over (snake collided/died)
        if snake.is_dead:
            continue_playing = game_over()
            if continue_playing:
                game = Main()
                food = game.food
                snake = game.snake
                game_not_started = True
                is_snake_movable = True
                pygame.event.clear(pygame.KEYDOWN)
                continue
            return "Main Menu"


def game_over():
    """TODO: Write documentation"""
    play_music("game_over")
    screen.fill((255, 255, 255))  # Clear the screen with white
    draw_text('game over :c', font, (5, 15, 10),
              screen, SCREEN_WIDTH//2, 100)
    draw_text('press space or enter to play again', font2, (5, 15, 10),
              screen, SCREEN_WIDTH//2, 300)
    draw_text('press escape or backspace to quit', font2, (5, 15, 10),
              screen, SCREEN_WIDTH//2, 350)

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key in (K_ESCAPE, K_BACKSPACE):
                    play_music("main_menu")
                    return False
                elif event.key in (K_SPACE, K_RETURN):
                    pygame.mixer.music.stop()
                    return True
            pygame.display.update()
            game_clock.tick(60)


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
        game_clock.tick(60)


def pause_menu(game):
    """TODO: Write documentation"""
    # Freeze all game updates and lower the music volume
    prev_volume = pygame.mixer.music.get_volume()
    pygame.time.set_timer(UPDATE_SCREEN, 0)
    music_volume = pygame.mixer.music.get_volume()
    pygame.mixer.music.set_volume(0.3)

    # Create menu buttons
    pause_labels = ["back", "settings", "quit"]
    num_buttons = len(pause_labels)
    pause_buttons = []
    pause_button_color = (205, 220, 190, 20)
    pause_button_width, pause_button_height = 400, 75
    pause_button_padding = 20  # Spacing between buttons

    # Total height of all buttons including padding (amount of space
    # taken up by the buttons in the window)
    total_button_height = (pause_button_height * num_buttons) + \
        pause_button_padding * (num_buttons - 1)

    # Starting Y position for vertical centering of buttons
    button_start_y = (SCREEN_HEIGHT - total_button_height) // 2

    # Create a transparent overlay with a dim background that matches
    # the screen dimensions
    transparent_overlay = pygame.Surface(
        (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

    for i, label in enumerate(pause_labels):
        pause_button = pygame.Rect(
            0, 0, pause_button_width, pause_button_height)
        pause_button.center = (SCREEN_WIDTH // 2, button_start_y +
                               i * (pause_button_height + pause_button_padding))
        pause_buttons.append((pause_button, label))

    while True:
        click = False
        mouse_x, mouse_y = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key in (K_ESCAPE, K_RETURN, K_p):
                    pygame.mixer.music.set_volume(
                        prev_volume)
                    pygame.mixer.music.unpause()
                    pygame.event.clear(KEYDOWN)
                    pygame.event.pump
                    pygame.time.set_timer(UPDATE_SCREEN, 150)
                    return "resume game"
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True

        # Redraw last frozen game frame
        screen.fill((250, 250, 250))
        game.draw_elements()

        # Dim overlay
        transparent_overlay.fill((0, 0, 0, 150))
        screen.blit(transparent_overlay, (0, 0))

        draw_text('paused', font, (255, 255, 255),
                  screen, SCREEN_WIDTH//2, 100)
        draw_text("press escape, enter, or p to resume", font2, (255, 255, 255),
                  screen, SCREEN_WIDTH//2, 175)

        for button, label in pause_buttons:
            bg = pause_button_color if not button.collidepoint(
                (mouse_x, mouse_y)) else (255, 255, 255, 20)
            draw_button(screen, button, label, font,
                        bg, (255, 255, 255))

            # Check if the user clicks a menu button
            if button.collidepoint((mouse_x, mouse_y)) and click:
                if label == "back":
                    pygame.mixer.music.set_volume(prev_volume)
                    pygame.mixer.music.unpause()
                    # Clear current key press
                    pygame.event.clear(KEYDOWN)
                    # Fire an instant game update
                    pygame.event.post(pygame.event.Event(UPDATE_SCREEN))
                    pygame.time.set_timer(UPDATE_SCREEN, 150)
                    return "resume game"
                elif label == "settings":
                    print("SETTINGS IN PAUSE MENU UNIMPLEMENTED")
                    pass
                elif label == "quit":
                    pygame.mixer.music.set_volume(prev_volume)
                    main_menu()

        pygame.display.update()
        game_clock.tick(60)


def settings():
    """The settings game loop. Handles all settings logic."""
    running = True
    dragging = False

    slider_rect = pygame.Rect(
        SCREEN_WIDTH//1.75, 250, 200, 10)  # Volume slider track
    # Calculate the x coordinate of the volume slider handle (default
    #  set at 100%)
    handle_x = SCREEN_WIDTH//1.75 + slider_rect.width
    handle_rect = pygame.Rect(handle_x, 245, 10, 20)  # Volume slider handle

    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            # Exiting settings menu logic
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
            # Dragging slider handle through slider track
            if event.type == pygame.MOUSEMOTION and dragging:
                # Constrain handle movement within slider_rect
                handle_rect.x = max(slider_rect.left, min(
                    event.pos[0], slider_rect.right - handle_rect.width))
            # Clicking to set volume or drag slider
            if event.type == pygame.MOUSEBUTTONDOWN:
                if handle_rect.collidepoint(event.pos):
                    dragging = True
                if slider_rect.collidepoint(event.pos):
                    handle_rect.x = max(slider_rect.left, min(
                        event.pos[0], slider_rect.right - handle_rect.width))
                if back_button.collidepoint(event.pos):
                    running = False
            # Resetting drag boolean when mouse button released
            elif event.type == pygame.MOUSEBUTTONUP:
                dragging = False

            # Calculate volume from slider track and slider handle positions
            volume = (handle_rect.centerx - slider_rect.left) / \
                slider_rect.width

            # Hacky fix for volume but it works
            if volume >= 0.975:
                volume = 1
            elif volume <= 0.025:
                volume = 0

            # Set the volume
            pygame.mixer.music.set_volume(volume)

        # Clear screen at beginning of the frame with white
        screen.fill((250, 250, 250))

        draw_text('Settings', font, (5, 15, 10), screen, SCREEN_WIDTH//2, 100)

        back_button = pygame.Rect(
            10, 57.5, 200, 75)

        setting_label = pygame.font.SysFont(None, 75)

        draw_button(screen, back_button, "Back", setting_label,
                    (205, 220, 190), (0, 0, 0))
        draw_text('Volume', setting_label, (5, 15, 10),
                  screen, SCREEN_WIDTH//2.5, 250)

        pygame.draw.rect(screen, (100, 100, 100), slider_rect)  # Slider track
        pygame.draw.rect(screen, (200, 200, 200), handle_rect)  # Slider handle

        pygame.display.update()
        game_clock.tick(60)


main_menu()
