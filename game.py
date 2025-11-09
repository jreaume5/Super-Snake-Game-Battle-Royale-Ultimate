import time
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

###### JACOB'S CHANGES#######
# --- Speed Boost constants---
# default is 150, currently testing        # Your current update tick in start_game()
BASE_TICK_MS = 110
# default is 90 currently testing        # Faster tick while boost is active
BOOST_TICK_MS = 70
SPEED_BOOST_END = pygame.USEREVENT + 1  # one-shot event to end the boost

### SHRINK CONSTANTS -JACOB-######
# --- Idle Shrink constants ---
SHRINK_START_MS = 8000          # time after last eat before shrinking starts
SHRINK_RATE_MS_BASE = 2500      # base interval between shrinks once active
SHRINK_RATE_MS_MIN = 900        # cap so it never becomes too fast
SHRINK_FLASH_WARNING_MS = 1000  # start flashing this long before a shrink


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
        self.snake = Snake()
        self.food = Food()
        self.food_spawner = FoodSpawner()
        ##### JACOB'S CHANGES#####
        self.speed_boost = SpeedBoost()
        ##### SHRINK CHANGES#####
        # --- Idle Shrink state---
        self.last_eat_ms = pygame.time.get_ticks()  # reset when food eaten
        # when the next shrink happens; None until active
        self.next_shrink_due = None
        self.shrinking_border = ShrinkingBorder(num_cells, cell_size)

    ### SHRINK CHANGES#####

    def _current_shrink_rate_ms(self):
        """Shrink a bit faster as the snake gets longer (simple linear scaling)."""
        extra = max(0, len(self.snake.body) -
                    3)   # don’t penalize the starting length
        rate = SHRINK_RATE_MS_BASE - extra * 150   # 150ms faster per extra segment
        return max(SHRINK_RATE_MS_MIN, rate)

    def _process_idle_shrink(self):
        """Handle idle-time shrinking, dynamic rate, and death at zero length."""
        now = pygame.time.get_ticks()

        # If enough time has passed without eating, start (or continue) shrinking
        idle_ms = now - self.last_eat_ms
        if idle_ms >= SHRINK_START_MS:
            # schedule the first shrink if we haven't yet
            if self.next_shrink_due is None:
                self.next_shrink_due = now + self._current_shrink_rate_ms()

        # perform a shrink if we're past due
            if now >= self.next_shrink_due:
                # remove one tail segment
                self.snake.shrink(1)

                if not self.snake.is_dead:
                    # schedule the next shrink based on *current* length
                    self.next_shrink_due = now + self._current_shrink_rate_ms()
            # if dead, the caller (update) will early-out this frame

    def update(self):
        """TODO: Write documentation"""
        self.snake.move()
        self._process_idle_shrink()     # <-- ADD-ONLY
        if self.snake.is_dead:          # if shrink killed us, skip further checks this frame
            return
        self.shrinking_border.update()
        self.check_collisions()

    def draw_elements(self):
        """TODO: Write documentation"""
        if self.food.is_spawned:
            self.food.draw()
        self.snake.draw()
        ##### JACOB'S CHANGES#####
        # Draw speed boost if spawned (ADD-ONLY)
        if getattr(self.speed_boost, "is_spawned", False):
            self.speed_boost.draw()

        self.shrinking_border.draw(screen)

    def check_collisions(self):
        """TODO: Write documentation"""
        # Check if the head of the snake hits a screen border
        head = self.snake.body[0]
        if not 0 <= head.x < num_cells or not 0 <= head.y < num_cells:
            self.game_over()

        # Check if the snake is in the danger zone
        if self.shrinking_border.is_in_danger_zone(head):
            # Only apply damage if cooldown has passed
            if self.shrinking_border.wave_shrink_amount > 0 and self.shrinking_border.can_apply_damage():
                # Check if this damage would kill the snake (shrink below 1 segment)
                if len(self.snake.body) - self.shrinking_border.wave_shrink_amount < 1:
                    self.game_over()
                else:
                    self.snake.grow(-self.shrinking_border.wave_shrink_amount)

        # Check if the snake ate food and draw new food
        if self.snake.body[0] == self.food.pos:
            self.food.effect(self.snake)
            self.food.set_random_pos(self.snake.body)
            #### SHRINK CHANGES#####
            self.last_eat_ms = pygame.time.get_ticks()
            self.next_shrink_due = None

        # Check if the head of the snake hits itself
        for body_segment in self.snake.body[1:]:
            if head == body_segment:
                self.game_over()

        ##### JACOB'S CHANGES#####
        # Check if the snake picked up a speed boost (ADD-ONLY)
        if getattr(self.speed_boost, "is_spawned", False) and self.snake.body[0] == self.speed_boost.pos:
            self.speed_boost.effect(self.snake)

        # Occasionally spawn a speed boost if none is active on the field (ADD-ONLY)
        if not self.speed_boost.is_spawned and random.random() < 0.005:
            # Ensure it doesn't spawn inside the snake or on top of food
            while True:
                self.speed_boost.set_random_pos(self.snake.body)
                if (not self.food.is_spawned) or (self.speed_boost.pos != self.food.pos):
                    break
            self.speed_boost.is_spawned = True

    def game_over(self):
        """TODO: Write documentation"""
        self.snake.is_dead = True


class ShrinkingBorder():
    """Handles the shrinking border battle royale element with multiple
    waves that cause more shrinking damage to the snake over time."""

    def __init__(self, num_cells, cell_size):
        """Initializes the shrinking border.

        Args:
            num_cells(int): Number of cells in the grid
            cell_size (int): Size of each cell in pixels
        """
        self.num_cells = num_cells
        self.cell_size = cell_size
        # Current border thickness (in cells from edge)
        self.current_border = 0
        self.target_border = 0  # Target border thickness for current wave
        self.is_shrinking = False
        self.shrink_start_time = 0
        self.wave_shrink_amount = 0
        self.game_start_time = time.time()
        self.last_damage_time = 0  # Track when damage was last applied
        self.damage_cooldown = 0.5  # Damage every 0.5 seconds

        # Wave configuration: (delay_seconds, target_border_cells,
        # shrink_duration_seconds, wave_shrink_amount)
        self.waves = [
            (30, 1, 10, 1),  # Wave 1: After 30s, shrink to 1 cell from edge over 10s
            (60, 2, 10, 1),  # Wave 2: After 60s, shrink to 2 cells from edge over 10s
            (75, 3, 10, 1),  # Wave 3: After 75s, shrink to 3 cells from edge over 10s
            (90, 4, 7.5, 2),  # Wave 4: After 90s, shrink to 4 cells from edge over 7.5s
            # Wave 5: After 115s, shrink to 10 cells from edge over 5s (final shrink)
            (115, 10, 5, 3),
        ]

        self.current_wave_index = 0
        self.shrink_duration = 0

        # Visual properties
        self.warning_color = (255, 165, 0, 100)
        self.danger_color = (255, 0, 0, 150)
        self.safe_color = (0, 255, 0, 50)

    def reset(self):
        """Resets the border for a new game."""
        self.current_border = 0
        self.target_border = 0
        self.is_shrinking = False
        self.current_wave_index = 0
        self.wave_shrink_amount = 0
        self.game_start_time = time.time()
        self.last_damage_time = 0

    def update(self):
        """Updates the border state based on elapsed time."""
        elapsed_time = time.time() - self.game_start_time

        # Check if a new wave needs to start
        if self.current_wave_index < len(self.waves):
            wave_delay, target_border, duration, shrink_amount = self.waves[
                self.current_wave_index]

            if elapsed_time >= wave_delay and not self.is_shrinking:
                # Start shrinking for this wave
                self.is_shrinking = True
                self.target_border = target_border
                self.shrink_start_time = time.time()
                self.shrink_duration = duration
                self.wave_shrink_amount = shrink_amount
                self.current_wave_index += 1

        # Update border position if shrinking
        if self.is_shrinking:
            shrink_elapsed = time.time() - self.shrink_start_time
            progress = min(shrink_elapsed / self.shrink_duration, 1.0)

            # Calculate current border with smooth interpolation
            start_border = self.waves[self.current_wave_index -
                                      1][1] if self.current_wave_index > 1 else 0
            if self.current_wave_index > 0:
                prev_target = self.waves[self.current_wave_index -
                                         2][1] if self.current_wave_index > 1 else 0
                start_border = prev_target

            self.current_border = start_border + \
                (self.target_border - start_border) * progress

            # Stop shrinking when complete
            if progress >= 1.0:
                self.is_shrinking = False
                self.current_border = self.target_border

    def draw(self, screen):
        """Draws the shrinking border to the game environment.

        Args:
            screen (pygame.Surface): The game screen surface
        """
        if self.current_border <= 0:
            return

        border_thickness_pixels = int(self.current_border * self.cell_size)
        screen_width = self.num_cells * self.cell_size
        screen_height = self.num_cells * self.cell_size

        # Determine color based on state
        if self.is_shrinking:
            color = self.warning_color
        else:
            color = self.danger_color

        # Create a transparent surface for the border
        border_surface = pygame.Surface(
            (screen_width, screen_height), pygame.SRCALPHA)

        # Draw the four border rectangles
        # Top border
        pygame.draw.rect(border_surface, color,
                         (0, 0, screen_width, border_thickness_pixels))

        # Bottom border
        pygame.draw.rect(border_surface, color, (0, screen_height -
                         border_thickness_pixels, screen_width, border_thickness_pixels))

        # Left border
        pygame.draw.rect(border_surface, color,
                         (0, 0, border_thickness_pixels, screen_height))

        # Right border
        pygame.draw.rect(border_surface, color, (screen_width -
                         border_thickness_pixels, 0, border_thickness_pixels, screen_height))

        # Blit the border to the screen
        screen.blit(border_surface, (0, 0))

        # Draw warning lines at the inner edge
        line_color = (255, 0, 0) if not self.is_shrinking else (255, 165, 0)
        line_width = 3

        # Top line
        pygame.draw.line(screen, line_color,
                         (border_thickness_pixels, border_thickness_pixels),
                         (screen_width - border_thickness_pixels,
                          border_thickness_pixels),
                         line_width)

        # Bottom line
        pygame.draw.line(screen, line_color,
                         (border_thickness_pixels,
                          screen_height - border_thickness_pixels),
                         (screen_width - border_thickness_pixels,
                          screen_height - border_thickness_pixels),
                         line_width)

        # Left line
        pygame.draw.line(screen, line_color,
                         (border_thickness_pixels, border_thickness_pixels),
                         (border_thickness_pixels,
                          screen_height - border_thickness_pixels),
                         line_width)

        # Right line
        pygame.draw.line(screen, line_color,
                         (screen_width - border_thickness_pixels,
                          border_thickness_pixels),
                         (screen_width - border_thickness_pixels,
                          screen_height - border_thickness_pixels),
                         line_width)

    def is_in_danger_zone(self, pos):
        """Check if a position is in the danger zone (border area).

        Args:
            pos (Vector2): Position to check (in grid coordinates)

        Returns:
            bool: True if position is in danger zone, False otherwise
        """
        border_cells = int(self.current_border)

        if pos.x < border_cells or pos.x >= self.num_cells - border_cells:
            return True
        if pos.y < border_cells or pos.y >= self.num_cells - border_cells:
            return True

        return False

    def can_apply_damage(self):
        """Check if enough time has passed to apply damage again.

        Returns:
            bool: True if damage can be applied, False otherwise
        """
        current_time = time.time()
        if current_time - self.last_damage_time >= self.damage_cooldown:
            self.last_damage_time = current_time
            return True
        return False

    def get_safe_bounds(self):
        """Get the current safe playing area bounds.

        Returns:
            tuple: (min_x, min_y, max_x, max_y) in grid coordinates
        """
        border_cells = int(self.current_border)
        return (
            border_cells,
            border_cells,
            self.num_cells - border_cells - 1,
            self.num_cells - border_cells - 1
        )

    def get_time_to_next_wave(self):
        """Get time remaining until the next shrinking wave.

        Returns:
            float: Seconds until next wave, or -1 if no more waves
        """
        if self.current_wave_index >= len(self.waves):
            return -1

        elapsed_time = time.time() - self.game_start_time
        next_wave_time = self.waves[self.current_wave_index][0]

        return max(0, next_wave_time - elapsed_time)


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

####### JACOB'S CHANGES#######


class SpeedBoost(CollectibleItem):
    """A pickup that temporarily speeds up the game tick (snake moves faster)."""
    color = (255, 165, 0)   # orange block
    duration_ms = 5000      # 5 seconds
    is_spawned = False

    def __init__(self):
        super().__init__()
        # Ensure it's a Vector2 from the start
        self.pos = pygame.math.Vector2(-1, -1)

    def set_random_pos(self, snake_body):
        """Ensure we always choose a free cell; prefer parent logic but keep it explicit."""
        while True:
            x = random.randint(0, num_cells - 1)
            y = random.randint(0, num_cells - 1)
            candidate = pygame.math.Vector2(x, y)
            # Avoid spawning on the snake or on top of food (if you pass food pos)
            if candidate not in snake_body:
                self.pos = candidate
                return

    def effect(self, snake):
        # Apply boost
        pygame.time.set_timer(UPDATE_SCREEN, BOOST_TICK_MS)
        # Schedule end (Pygame 2 supports one-shot via third arg True)
        pygame.time.set_timer(SPEED_BOOST_END, self.duration_ms, True)
        # Despawn immediately so it's not drawn again
        self.is_spawned = False
        # Move it off-board defensively (in case any stale draw gets called)
        self.pos = pygame.math.Vector2(-1, -1)


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
        self.is_dead = False

    def draw(self):
        """Draw the snake body and add eyes to the head."""
        for body_segment in self.body:
            x = int(body_segment.x * cell_size)
            y = int(body_segment.y * cell_size)

            # Draw snake body with outside border
            body_rect = pygame.Rect(x, y, cell_size, cell_size)
            body_color = (3, 252, 86)
            pygame.draw.rect(screen, body_color, body_rect)

            left = pygame.Vector2(body_segment.x - 1, body_segment.y)
            right = pygame.Vector2(body_segment.x + 1, body_segment.y)
            up = pygame.Vector2(body_segment.x, body_segment.y - 1)
            down = pygame.Vector2(body_segment.x, body_segment.y + 1)
            border_color = (0, 0, 0)

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

        # --- ADD ONLY EYES TO HEAD ---
        if not self.body:
            return

        head = self.body[0]
        hx, hy = int(head.x * cell_size), int(head.y * cell_size)
        head_rect = pygame.Rect(hx, hy, cell_size, cell_size)

        eye_r = 4
        off = 8
        if self.direction == Vector2(1, 0):        # right
            eyes = [(head_rect.right - off, head_rect.top + off),
                    (head_rect.right - off, head_rect.bottom - off)]
        elif self.direction == Vector2(-1, 0):     # left
            eyes = [(head_rect.left + off, head_rect.top + off),
                    (head_rect.left + off, head_rect.bottom - off)]
        elif self.direction == Vector2(0, -1):     # up
            eyes = [(head_rect.left + off, head_rect.top + off),
                    (head_rect.right - off, head_rect.top + off)]
        else:                                      # down
            eyes = [(head_rect.left + off, head_rect.bottom - off),
                    (head_rect.right - off, head_rect.bottom - off)]

        for e in eyes:
            pygame.draw.circle(screen, (255, 255, 255), e, eye_r)  # white eye
            pygame.draw.circle(screen, (0, 0, 0), e, 2)

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
        """Grows or shrinks the snake.

        Args:
            num_growths (int): Number of segments to grow (positive) or
            shrink (negative)
        """
        # Handle negative growth (shrinking)
        if num_growths < 0:
            # Remove segments from the tail immediately
            segments_to_remove = abs(num_growths)
            for _ in range(segments_to_remove):
                if len(self.body) > 1:  # Keep at least the head
                    self.body.pop()
            self.length = len(self.body)
            # Don't change pending_growth for negative values
        else:
            # Positive growth - add to pending
            self.pending_growth += num_growths
            self.length += num_growths

    def shrink(self, n=1):
        """Remove n tail segments. If length hits 0, mark snake dead."""
        for _ in range(n):
            if len(self.body) > 0:
                self.body.pop()
                self.length = len(self.body)
            if len(self.body) == 0:
                self.is_dead = True
                break


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
        game_clock.tick(120)  # default value is 60 currently testing


def reset_speed_boost_state(game):
    """Reset timers and despawn any existing speed boost."""
    pygame.time.set_timer(
        SPEED_BOOST_END, 0)              # stop the one-shot end timer
    # restore normal speed
    pygame.time.set_timer(UPDATE_SCREEN, BASE_TICK_MS)
    if hasattr(game, "speed_boost"):
        game.speed_boost.is_spawned = False
        game.speed_boost.pos = pygame.math.Vector2(-1, -1)


def start_game():
    """The actual game loop. Handles all snake game logic."""
    game = Main()  # Create the snake and food

    reset_speed_boost_state(game)  # ensure no leftover boost/timers

    food = game.food
    snake = game.snake
    game.shrinking_border.reset()
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

            ##### JACOB'S CHANGES#####
            elif event.type == SPEED_BOOST_END:
                # Restore normal tick rate when boost expires (ADD-ONLY)
                pygame.time.set_timer(UPDATE_SCREEN, BASE_TICK_MS)

        game.draw_elements()
        pygame.display.update()
        game_clock.tick(60)

        # Check if the game is over (snake collided/died)
        if snake.is_dead:
            continue_playing = game_over()
            if continue_playing:
                game = Main()

                # ensure no leftover boost/timers
                reset_speed_boost_state(game)

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


if __name__ == "__main__":
    pygame.init()
    pygame.display.set_caption('Super Snake Battle Royale Ultimate')
    # recreate screen in case module-level initialization was removed/moved:
    screen = set_mode(WINDOWED_MODE)
    SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_width(), screen.get_height()
    main_menu()
