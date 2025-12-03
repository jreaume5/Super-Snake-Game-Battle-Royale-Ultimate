from pygame.locals import *
from pygame.math import Vector2
from abc import ABC, abstractmethod
import pygame
import sys
import random
import numpy as np
from collections import deque

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

######JACOB'S CHANGES#######
# --- Speed Boost constants---
BASE_TICK_MS = 110  # default is 150, currently testing
BOOST_TICK_MS = 70  # default is 90 currently testing
SPEED_BOOST_END = pygame.USEREVENT + 1  # one-shot event to end the boost

###SHRINK CONSTANTS -JACOB-######
# --- Idle Shrink constants ---
SHRINK_START_MS = 8000          # time after last eat before shrinking starts
SHRINK_RATE_MS_BASE = 2500      # base interval between shrinks once active
SHRINK_RATE_MS_MIN = 900        # cap so it never becomes too fast
SHRINK_FLASH_WARNING_MS = 1000  # start flashing this long before a shrink


def set_mode(mode):
    """Set the display mode (windowed, borderless, fullscreen)."""
    global screen, current_display_mode
    flags = 0

    if mode == WINDOWED_MODE:
        flags = pygame.RESIZABLE | pygame.SCALED
    elif mode == BORDERLESS_MODE:
        flags = pygame.NOFRAME | pygame.SCALED
    elif mode == FULLSCREEN_MODE:
        flags = pygame.FULLSCREEN

    screen = pygame.display.set_mode(GRID_SIZE, flags)
    current_display_mode = mode
    return screen


screen = set_mode(WINDOWED_MODE)
SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_width(), screen.get_height()

font = pygame.font.SysFont(None, 100)
font2 = pygame.font.SysFont(None, 50)


class Main:
    """Single-player game wrapper (your original snake)."""

    def __init__(self):
        self.snake = Snake()
        self.food = Food()
        self.food_spawner = FoodSpawner()
        #####JACOB'S CHANGES#####
        self.speed_boost = SpeedBoost()
        #####SHRINK CHANGES#####
        # --- Idle Shrink state---
        self.last_eat_ms = pygame.time.get_ticks()  # reset when food eaten
        self.next_shrink_due = None                 # when the next shrink happens; None until active

    ###SHRINK CHANGES#####
    def _current_shrink_rate_ms(self):
        """Shrink a bit faster as the snake gets longer (simple linear scaling)."""
        extra = max(0, len(self.snake.body) - 3)   # don’t penalize the starting length
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
        """Step the snake + collisions for the human-played game."""
        self.snake.move()
        self._process_idle_shrink()
        if self.snake.is_dead:
            return
        self.check_collisions()

    def draw_elements(self):
        """Draw food, snake, and powerups."""
        if self.food.is_spawned:
            self.food.draw()
        self.snake.draw()
        #####JACOB'S CHANGES#####
        # Draw speed boost if spawned
        if getattr(self.speed_boost, "is_spawned", False):
            self.speed_boost.draw()

    def check_collisions(self):
        """Handle food, self-hit, walls, and speed-boost collisions."""
        # Check if the head of the snake hits a screen border
        head = self.snake.body[0]
        if not 0 <= head.x < num_cells or not 0 <= head.y < num_cells:
            self.game_over()

        # Check if the snake ate food and draw new food
        if self.snake.body[0] == self.food.pos:
            self.food.effect(self.snake)
            self.food.set_random_pos(self.snake.body)
            ####SHRINK CHANGES#####
            self.last_eat_ms = pygame.time.get_ticks()
            self.next_shrink_due = None

        # Check if the head of the snake hits itself
        for body_segment in self.snake.body[1:]:
            if head == body_segment:
                self.game_over()

        #####JACOB'S CHANGES#####
        # Check if the snake picked up a speed boost
        if getattr(self.speed_boost, "is_spawned", False) and self.snake.body[0] == self.speed_boost.pos:
            self.speed_boost.effect(self.snake)

        # Occasionally spawn a speed boost if none is active
        if not self.speed_boost.is_spawned and random.random() < 0.005:
            # Ensure it doesn't spawn inside the snake or on top of food
            while True:
                self.speed_boost.set_random_pos(self.snake.body)
                if (not self.food.is_spawned) or (self.speed_boost.pos != self.food.pos):
                    break
            self.speed_boost.is_spawned = True

    def game_over(self):
        """Mark snake dead for human mode."""
        self.snake.is_dead = True


class PowerUp(ABC):
    """Abstract base class to provide structure and behavior of CollectibleItems."""
    power: str = "Default"
    duration_s: float = 0.0
    rarity: float = 0.0
    growth: int = 1
    active: bool = False
    color: tuple = (227, 255, 69)
    pos: Vector2 = (0, 0)
    is_spawned: bool = False

    def __init__(self):
        None

    @abstractmethod
    def draw(self):
        pass

    @abstractmethod
    def set_random_pos(self):
        pass

    @abstractmethod
    def effect(self, snake):
        pass


class CollectibleItem(PowerUp):
    """Base class for Food / SpeedBoost items."""

    def __init__(self):
        None

    def draw(self):
        collectible_rect = pygame.Rect(int(self.pos.x * cell_size),
                                       int(self.pos.y * cell_size), cell_size, cell_size)
        pygame.draw.rect(screen, self.color, collectible_rect)

    def set_random_pos(self, snake_body):
        """Place this collectible on a random free cell."""
        while True:
            self.x = random.randint(0, num_cells - 1)
            self.y = random.randint(0, num_cells - 1)
            self.pos = pygame.math.Vector2(self.x, self.y)

            # Check to make sure the food doesn't spawn inside the snake body
            if self.pos not in snake_body:
                return


class Food(CollectibleItem):
    """Basic food for growing the snake(s)."""

    def effect(self, snake):
        Snake.grow(snake)


#######JACOB'S CHANGES#######
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
        """Ensure we always choose a free cell."""
        while True:
            x = random.randint(0, num_cells - 1)
            y = random.randint(0, num_cells - 1)
            candidate = pygame.math.Vector2(x, y)
            if candidate not in snake_body:
                self.pos = candidate
                return

    def effect(self, snake):
        # Apply boost
        pygame.time.set_timer(UPDATE_SCREEN, BOOST_TICK_MS)
        # Schedule end
        pygame.time.set_timer(SPEED_BOOST_END, self.duration_ms, True)
        # Despawn immediately so it's not drawn again
        self.is_spawned = False
        self.pos = pygame.math.Vector2(-1, -1)


class FoodSpawner():
    """Placeholder for future powerup management."""

    def __init__(self):
        self.powerups = []  # list of active PowerUp instances


class Snake:
    """Snake used both for human game and RL environment."""

    def __init__(
        self,
        start_body=None,
        direction=Vector2(1, 0),
        color=(3, 252, 86),
    ):
        # Default to your original starting body if none given
        if start_body is None:
            start_body = [pygame.Vector2(6, 10), Vector2(5, 10), Vector2(4, 10)]

        # Make a copy to avoid aliasing
        self.body = [Vector2(seg.x, seg.y) for seg in start_body]
        self.length = len(self.body)
        self.direction = direction
        self.pending_growth = 0
        self.is_dead = False
        self.color = color

    def draw(self):
        """Draw the snake and eyes."""
        for body_segment in self.body:
            x = int(body_segment.x * cell_size)
            y = int(body_segment.y * cell_size)

            body_rect = pygame.Rect(x, y, cell_size, cell_size)
            body_color = self.color
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

        # Eyes
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
            pygame.draw.circle(screen, (255, 255, 255), e, eye_r)
            pygame.draw.circle(screen, (0, 0, 0), e, 2)

    def move(self):
        """Move the snake one step in its current direction."""
        new_head = self.body[0] + self.direction
        self.body.insert(0, new_head)

        if self.pending_growth > 0:
            self.pending_growth -= 1
        else:
            self.body.pop()

    def grow(self, num_growths=1):
        """Queue growth for the snake."""
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
    """Credit for music goes to Newgrounds user ZaneLittle."""
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
            return
    pygame.mixer.music.play(-1)


def draw_button(surface, button, text, font, bg_color, text_color):
    """Draws a rectangular button with centered text to a surface."""
    transparent_surface = pygame.Surface(
        (button.width, button.height), pygame.SRCALPHA)

    pygame.draw.rect(transparent_surface, bg_color,
                     transparent_surface.get_rect())

    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(
        center=(button.width//2, button.height//2))
    transparent_surface.blit(text_surface, text_rect)

    surface.blit(transparent_surface, button.topleft)


def draw_text(text, font, color, surface, x, y, center=True):
    """Draws text to a surface."""
    text_obj = font.render(text, 1, color)
    text_rect = text_obj.get_rect()
    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)

    surface.blit(text_obj, text_rect)


def main_menu():
    """Main menu loop."""
    play_music("main_menu")
    click = False

    while True:
        screen.fill((250, 250, 250))
        draw_text('main menu', font,
                  (5, 15, 10), screen, SCREEN_WIDTH//2, 100)

        mouse_x, mouse_y = pygame.mouse.get_pos()

        button_labels = ["Start Game", "Simulation", "Settings", "Quit"]
        button_colors = [
            (255, 0, 0),
            (0, 255, 0),
            (0, 0, 255),
            (205, 220, 190)
        ]

        menu_buttons = []
        num_buttons = len(button_labels)
        menu_button_width, menu_button_height = 400, 75
        menu_button_padding = 20

        total_button_height = (menu_button_height * num_buttons) + \
            (menu_button_padding * (num_buttons - 1))

        button_start_y = (SCREEN_HEIGHT - total_button_height) // 2

        for i, label in enumerate(button_labels):
            menu_button = pygame.Rect(
                0, 0, menu_button_width, menu_button_height)
            menu_button.center = (
                SCREEN_WIDTH // 2, button_start_y + i * (menu_button_height + menu_button_padding))
            menu_buttons.append((menu_button, label, button_colors[i]))

        for button, label, button_color in menu_buttons:
            draw_button(screen, button, label, font,
                        button_color, (0, 0, 0))
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

        click = False
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True
        pygame.display.update()
        game_clock.tick(120)


def reset_speed_boost_state(game):
    """Reset timers and despawn any existing speed boost."""
    pygame.time.set_timer(SPEED_BOOST_END, 0)
    pygame.time.set_timer(UPDATE_SCREEN, BASE_TICK_MS)
    if hasattr(game, "speed_boost"):
        game.speed_boost.is_spawned = False
        game.speed_boost.pos = pygame.math.Vector2(-1, -1)


def start_game():
    """Human-controlled classic snake mode."""
    game = Main()

    reset_speed_boost_state(game)

    food = game.food
    snake = game.snake
    pygame.time.set_timer(UPDATE_SCREEN, BASE_TICK_MS)

    pygame.mixer.music.stop()

    is_snake_movable = True
    game_not_started = True
    ignore_next_keydown = False

    while True:
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
                if ignore_next_keydown:
                    ignore_next_keydown = False
                    continue

                if game_not_started:
                    if not food.is_spawned:
                        food.set_random_pos(snake.body)
                        food.is_spawned = True
                    game_not_started = False
                    play_music("game")
                    continue

                if event.key == K_ESCAPE:
                    pygame.time.set_timer(UPDATE_SCREEN, 0)
                    pause_menu(game)
                    pygame.event.clear(pygame.KEYDOWN)
                    ignore_next_keydown = True
                    pygame.time.set_timer(UPDATE_SCREEN, BASE_TICK_MS)
                    continue

                elif is_snake_movable:
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
                    is_snake_movable = True

            elif event.type == SPEED_BOOST_END:
                pygame.time.set_timer(UPDATE_SCREEN, BASE_TICK_MS)

        game.draw_elements()
        pygame.display.update()
        game_clock.tick(60)

        if snake.is_dead:
            continue_playing = game_over()
            if continue_playing:
                game = Main()
                reset_speed_boost_state(game)
                food = game.food
                snake = game.snake
                game_not_started = True
                is_snake_movable = True
                pygame.event.clear(pygame.KEYDOWN)
                continue
            return "Main Menu"


def game_over():
    """Basic game-over screen for human mode."""
    play_music("game_over")
    screen.fill((255, 255, 255))
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


# ================= MULTI-SNAKE RL ENVIRONMENT & AGENT (NumPy) ==================

ACTION_UP = 0
ACTION_DOWN = 1
ACTION_LEFT = 2
ACTION_RIGHT = 3
NUM_ACTIONS = 4


def action_to_direction(current_dir, action):
    """Map an action (0–3) to a new direction, disallowing instant reverse."""
    if action == ACTION_UP:
        new_dir = Vector2(0, -1)
    elif action == ACTION_DOWN:
        new_dir = Vector2(0, 1)
    elif action == ACTION_LEFT:
        new_dir = Vector2(-1, 0)
    else:
        new_dir = Vector2(1, 0)

    # Disallow 180° turns
    if new_dir + current_dir == Vector2(0, 0):
        return current_dir
    return new_dir


class BattleEnv4Snakes:
    """
    RL environment with 4 snakes:
    - Shared board
    - One Food object
    - Same rules for all snakes
    """

    def __init__(self, num_snakes=4, max_steps=500):
        self.num_snakes = num_snakes
        self.max_steps = max_steps
        self.step_count = 0
        self.snakes = []
        self.food = Food()
        self.alive = [True] * num_snakes

    def _all_snake_cells(self):
        cells = []
        for s in self.snakes:
            cells.extend(s.body)
        return cells

    def _encode_state(self, i):
        """Simple feature vector for snake i.

        For dead snakes (or snakes with empty bodies), we return a zero vector.
        This keeps the state shape consistent and avoids index errors.
        """
        snake = self.snakes[i]

        # If this snake is dead or has no body left, just return zeros
        # (10 features: hx, hy, fx, fy, dx, dy, danger_left, danger_right,
        #  danger_forward, alive_flag)
        if (not self.alive[i]) or len(snake.body) == 0:
            return np.zeros(10, dtype=np.float32)

        head = snake.body[0]
        food_pos = self.food.pos

        # normalized positions
        hx = head.x / num_cells
        hy = head.y / num_cells
        fx = food_pos.x / num_cells
        fy = food_pos.y / num_cells
        dx = snake.direction.x
        dy = snake.direction.y

        def is_danger(pos):
            if pos.x < 0 or pos.x >= num_cells or pos.y < 0 or pos.y >= num_cells:
                return 1.0
            for s in self.snakes:
                for seg in s.body:
                    if seg.x == pos.x and seg.y == pos.y:
                        return 1.0
            return 0.0

        # directions relative to current heading
        left_dir = Vector2(-snake.direction.y, snake.direction.x)
        right_dir = Vector2(snake.direction.y, -snake.direction.x)
        forward_dir = snake.direction

        danger_left = is_danger(head + left_dir)
        danger_right = is_danger(head + right_dir)
        danger_forward = is_danger(head + forward_dir)

        alive_flag = 1.0 if self.alive[i] else 0.0

        return np.array([
            hx, hy, fx, fy, dx, dy,
            danger_left, danger_right, danger_forward,
            alive_flag
        ], dtype=np.float32)

    def _get_all_states(self):
        states = [self._encode_state(i) for i in range(self.num_snakes)]
        return np.stack(states, axis=0)

    def reset(self):
        """Reset env and return state for all 4 snakes."""
        self.step_count = 0

        # 4 starting snakes in each quadrant, facing inward
        starts = [
            [Vector2(3, 3), Vector2(2, 3), Vector2(1, 3)],                                     # top-left
            [Vector2(num_cells - 4, 3), Vector2(num_cells - 5, 3), Vector2(num_cells - 6, 3)],  # top-right
            [Vector2(3, num_cells - 4), Vector2(2, num_cells - 4), Vector2(1, num_cells - 4)],  # bottom-left
            [Vector2(num_cells - 4, num_cells - 4),
             Vector2(num_cells - 5, num_cells - 4),
             Vector2(num_cells - 6, num_cells - 4)],
        ]

        dirs = [
            Vector2(1, 0),
            Vector2(-1, 0),
            Vector2(1, 0),
            Vector2(-1, 0),
        ]

        colors = [
            (0, 200, 0),
            (200, 0, 0),
            (0, 0, 200),
            (200, 200, 0),
        ]

        self.snakes = []
        for i in range(self.num_snakes):
            s = Snake(start_body=starts[i], direction=dirs[i], color=colors[i])
            self.snakes.append(s)

        # Food not on any snake
        self.food.set_random_pos(self._all_snake_cells())
        self.food.is_spawned = True

        self.alive = [True] * self.num_snakes

        return self._get_all_states()

    def step(self, actions):
        """
        actions: list[int] of length num_snakes
        Returns:
            next_states: np.array (num_snakes, state_dim)
            rewards: list[float]
            dones: list[bool]
            info: dict
        """
        self.step_count += 1
        rewards = [0.0] * self.num_snakes
        dones = [False] * self.num_snakes

        # Track distance to food BEFORE moving (for reward shaping)
        dists_before = [0.0] * self.num_snakes
        for i, s in enumerate(self.snakes):
            if not self.alive[i] or len(s.body) == 0:
                continue
            head = s.body[0]
            dists_before[i] = abs(head.x - self.food.pos.x) + abs(head.y - self.food.pos.y)

        # Set directions
        for i, s in enumerate(self.snakes):
            if not self.alive[i]:
                continue
            s.direction = action_to_direction(s.direction, actions[i])

        # Move snakes
        for i, s in enumerate(self.snakes):
            if not self.alive[i]:
                continue
            s.move()

        # Check collisions & food
        food_eaten_by = None
        for i, s in enumerate(self.snakes):
            if not self.alive[i] or len(s.body) == 0:
                continue
            head = s.body[0]

            # Wall collision
            if head.x < 0 or head.x >= num_cells or head.y < 0 or head.y >= num_cells:
                s.is_dead = True

            # Body collision (self or others)
            if not s.is_dead:
                for j, other in enumerate(self.snakes):
                    for idx, seg in enumerate(other.body):
                        if j == i and idx == 0:
                            continue
                        if head == seg:
                            s.is_dead = True
                            break
                    if s.is_dead:
                        break

            # Food
            if not s.is_dead and head == self.food.pos and food_eaten_by is None:
                s.grow(1)
                rewards[i] += 4.0 #FOOD EATEN REWARD
                food_eaten_by = i

                # Update alive flags, death rewards, distance-based shaping, and tail-chasing penalty
        for i, s in enumerate(self.snakes):
            if self.alive[i] and s.is_dead:
                self.alive[i] = False
                rewards[i] -= 2.0 #DEATH PUNISHMENT
                # Clear body so dead snakes vanish if drawn
                s.body = []

            if self.alive[i] and len(s.body) > 0:
                # Distance to food AFTER moving
                head = s.body[0]
                dist_after = abs(head.x - self.food.pos.x) + abs(head.y - self.food.pos.y)
                dist_before = dists_before[i]

                # If we moved closer to the food, small bonus; otherwise small penalty
                if dist_after < dist_before:
                    rewards[i] += 0.02
                elif dist_after > dist_before:
                    rewards[i] -= 0.02
                    
                # tiny step penalty so it doesn't stall
                rewards[i] -= 0.005


        # Respawn food if eaten
        if food_eaten_by is not None:
            self.food.set_random_pos(self._all_snake_cells())

        # Done flags
        env_done = (self.step_count >= self.max_steps) or (sum(self.alive) == 0)
        for i in range(self.num_snakes):
            dones[i] = (not self.alive[i]) or env_done

        next_states = self._get_all_states()
        info = {"alive_count": sum(self.alive)}
        return next_states, rewards, dones, info


class ReplayBuffer:
    def __init__(self, capacity=50_000):
        self.buffer = deque(maxlen=capacity)

    def push(self, state, action, reward, next_state, done):
        self.buffer.append((
            np.array(state, dtype=np.float32),
            int(action),
            float(reward),
            np.array(next_state, dtype=np.float32),
            bool(done)
        ))

    def sample(self, batch_size):
        batch = random.sample(self.buffer, batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)

        states = np.stack(states, axis=0)
        next_states = np.stack(next_states, axis=0)
        actions = np.array(actions, dtype=np.int64)
        rewards = np.array(rewards, dtype=np.float32)
        dones = np.array(dones, dtype=np.float32)

        return states, actions, rewards, next_states, dones

    def __len__(self):
        return len(self.buffer)


class DQNNumPy:
    """Simple 2-layer MLP Q-network implemented in NumPy."""

    def __init__(self, state_dim, action_dim, hidden1=128, hidden2=128):
        self.state_dim = state_dim
        self.action_dim = action_dim

        self.W1 = np.random.randn(state_dim, hidden1).astype(np.float32) / np.sqrt(state_dim)
        self.b1 = np.zeros(hidden1, dtype=np.float32)

        self.W2 = np.random.randn(hidden1, hidden2).astype(np.float32) / np.sqrt(hidden1)
        self.b2 = np.zeros(hidden2, dtype=np.float32)

        self.W3 = np.random.randn(hidden2, action_dim).astype(np.float32) / np.sqrt(hidden2)
        self.b3 = np.zeros(action_dim, dtype=np.float32)

    def _relu(self, x):
        return np.maximum(0.0, x)

    def _relu_deriv(self, x):
        return (x > 0).astype(np.float32)

    def forward(self, X):
        Z1 = X @ self.W1 + self.b1
        H1 = self._relu(Z1)
        Z2 = H1 @ self.W2 + self.b2
        H2 = self._relu(Z2)
        Z3 = H2 @ self.W3 + self.b3
        Q = Z3
        cache = (X, Z1, H1, Z2, H2)
        return Q, cache

    def predict_batch(self, X):
        Q, _ = self.forward(X)
        return Q

    def predict_single(self, state_vec):
        X = np.array(state_vec, dtype=np.float32).reshape(1, -1)
        Q, _ = self.forward(X)
        return Q[0]

    def train_batch(self, states, actions, targets, lr):
        B = states.shape[0]
        Q, (X, Z1, H1, Z2, H2) = self.forward(states)

        Y = Q.copy()
        idx = np.arange(B)
        Y[idx, actions] = targets

        dQ = (2.0 / B) * (Q - Y)

        dZ3 = dQ
        dW3 = H2.T @ dZ3
        db3 = dZ3.sum(axis=0)

        dH2 = dZ3 @ self.W3.T
        dZ2 = dH2 * self._relu_deriv(Z2)
        dW2 = H1.T @ dZ2
        db2 = dZ2.sum(axis=0)

        dH1 = dZ2 @ self.W2.T
        dZ1 = dH1 * self._relu_deriv(Z1)
        dW1 = X.T @ dZ1
        db1 = dZ1.sum(axis=0)

        self.W3 -= lr * dW3
        self.b3 -= lr * db3
        self.W2 -= lr * dW2
        self.b2 -= lr * db2
        self.W1 -= lr * dW1
        self.b1 -= lr * db1


class MultiSnakeAgent:
    """Shared DQN agent controlling all 4 snakes."""

    def __init__(
        self,
        state_dim,
        action_dim,
        lr=1e-3,
        gamma=0.99,
        batch_size=64,
        eps_start=1.0,
        eps_end=0.05,
        eps_decay=20_000,   # faster decay so you see learning sooner
        target_update_freq=1000,
    ):
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.gamma = gamma
        self.batch_size = batch_size
        self.lr = lr

        self.policy_net = DQNNumPy(state_dim, action_dim)
        self.target_net = DQNNumPy(state_dim, action_dim)
        self._sync_target()

        self.replay = ReplayBuffer()

        self.eps_start = eps_start
        self.eps_end = eps_end
        self.eps_decay = eps_decay
        self.total_steps = 0
        self.target_update_freq = target_update_freq

    def _sync_target(self):
        self.target_net.W1 = self.policy_net.W1.copy()
        self.target_net.b1 = self.policy_net.b1.copy()
        self.target_net.W2 = self.policy_net.W2.copy()
        self.target_net.b2 = self.policy_net.b2.copy()
        self.target_net.W3 = self.policy_net.W3.copy()
        self.target_net.b3 = self.policy_net.b3.copy()

    def epsilon(self):
        frac = max(0.0, 1.0 - self.total_steps / self.eps_decay)
        return self.eps_end + (self.eps_start - self.eps_end) * frac

    def select_action(self, state):
        """
        Epsilon-greedy: used during training.
        """
        self.total_steps += 1
        eps = self.epsilon()

        if random.random() < eps:
            return random.randrange(self.action_dim)

        q_vals = self.policy_net.predict_single(state)
        return int(np.argmax(q_vals))

    def select_action_greedy(self, state):
        """
        Pure greedy: used for visual episodes so you see *learned* behavior.
        """
        q_vals = self.policy_net.predict_single(state)
        return int(np.argmax(q_vals))

    def remember(self, state, action, reward, next_state, done):
        self.replay.push(state, action, reward, next_state, done)

    def train_step(self):
        if len(self.replay) < self.batch_size:
            return

        states, actions, rewards, next_states, dones = self.replay.sample(self.batch_size)

        q_next = self.target_net.predict_batch(next_states)
        max_next = np.max(q_next, axis=1)

        targets = rewards + self.gamma * max_next * (1.0 - dones)

        self.policy_net.train_batch(states, actions, targets, self.lr)

        if self.total_steps % self.target_update_freq == 0:
            self._sync_target()


def train_multi_snake(env, agent, num_episodes=10, max_steps_per_episode=None):
    """Train the DQN for multiple episodes (headless)."""
    if max_steps_per_episode is None:
        max_steps_per_episode = env.max_steps

    for episode in range(num_episodes):
        states = env.reset()
        episode_rewards = np.zeros(env.num_snakes, dtype=np.float32)

        for t in range(max_steps_per_episode):
            actions = []
            for i in range(env.num_snakes):
                state_i = states[i]
                if env.alive[i]:
                    a = agent.select_action(state_i)
                else:
                    a = 0
                actions.append(a)

            next_states, rewards, dones, info = env.step(actions)

            for i in range(env.num_snakes):
                agent.remember(states[i], actions[i], rewards[i], next_states[i], dones[i])
                episode_rewards[i] += rewards[i]

            agent.train_step()
            states = next_states

            if all(dones):
                break

        print(f"Episode {episode + 1}/{num_episodes}, rewards per snake: {episode_rewards}")


def run_visual_episode(env, agent, max_steps=200, fps=10):
    """
    Run a single episode visually using the current agent:
    - Draws the 4 snakes and food on the main screen.
    - Uses a greedy policy (no randomness) so learning is visible.
    """
    states = env.reset()
    step = 0
    running_vis = True

    while running_vis and step < max_steps:
        step += 1

        # Handle quit / escape events
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                running_vis = False

        # Choose actions for each snake (pure greedy for visualization)
        actions = []
        for i in range(env.num_snakes):
            if env.alive[i]:
                a = agent.select_action_greedy(states[i])
            else:
                a = 0
            actions.append(a)

        # Step environment
        next_states, rewards, dones, info = env.step(actions)
        states = next_states

        # Draw current state
        screen.fill((250, 250, 250))
        if env.food.is_spawned:
            env.food.draw()

        # Only draw alive snakes
        for i, s in enumerate(env.snakes):
            if env.alive[i]:
                s.draw()

        draw_text('RL Episode (ESC to exit)', font2, (5, 15, 10),
                  screen, SCREEN_WIDTH//2, 30)

        pygame.display.update()
        game_clock.tick(fps)

        if all(dones):
            running_vis = False


# ================== SIMULATION / RL MENU ======================

def start_sim():
    """Simulation / RL mode menu + control."""
    play_music("sim")

    # Create env + agent once, reuse between runs
    env = BattleEnv4Snakes(num_snakes=4, max_steps=200)
    states = env.reset()
    state_dim = states.shape[1]
    agent = MultiSnakeAgent(state_dim=state_dim, action_dim=NUM_ACTIONS)

    running = True
    training_done = False

    while running:
        screen.fill((250, 250, 250))
        draw_text('Simulation / RL mode', font,
                  (5, 15, 10), screen, SCREEN_WIDTH//2, 100)
        draw_text('R - Run one visual RL episode (4 snakes)', font2,
                  (5, 15, 10), screen, SCREEN_WIDTH//2, 200)
        draw_text('T - Train headless for 500 episodes (console output)', font2,
                  (5, 15, 10), screen, SCREEN_WIDTH//2, 250)
        draw_text('ESC - Return to main menu', font2,
                  (5, 15, 10), screen, SCREEN_WIDTH//2, 300)

        if training_done:
            draw_text('Training finished (agent improved)', font2,
                      (0, 120, 0), screen, SCREEN_WIDTH//2, 350)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    play_music("main_menu")
                    running = False
                elif event.key == K_r:
                    # Visualize current policy (greedy)
                    run_visual_episode(env, agent, max_steps=200, fps=10)
                elif event.key == K_t:
                    # Train in console only
                    train_multi_snake(env, agent, num_episodes=1000)
                    training_done = True

        pygame.display.update()
        game_clock.tick(60)


def pause_menu(game):
    """Pause menu for the human game."""
    prev_volume = pygame.mixer.music.get_volume()
    pygame.time.set_timer(UPDATE_SCREEN, 0)
    pygame.mixer.music.set_volume(0.3)

    pause_labels = ["back", "settings", "quit"]
    num_buttons = len(pause_labels)
    pause_buttons = []
    pause_button_color = (205, 220, 190, 20)
    pause_button_width, pause_button_height = 400, 75
    pause_button_padding = 20

    total_button_height = (pause_button_height * num_buttons) + \
        pause_button_padding * (num_buttons - 1)

    button_start_y = (SCREEN_HEIGHT - total_button_height) // 2

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
                    pygame.mixer.music.set_volume(prev_volume)
                    pygame.mixer.music.unpause()
                    pygame.event.clear(KEYDOWN)
                    pygame.event.pump
                    pygame.time.set_timer(UPDATE_SCREEN, BASE_TICK_MS)
                    return "resume game"
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True

        screen.fill((250, 250, 250))
        game.draw_elements()

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

            if button.collidepoint((mouse_x, mouse_y)) and click:
                if label == "back":
                    pygame.mixer.music.set_volume(prev_volume)
                    pygame.mixer.music.unpause()
                    pygame.event.clear(KEYDOWN)
                    pygame.event.post(pygame.event.Event(UPDATE_SCREEN))
                    pygame.time.set_timer(UPDATE_SCREEN, BASE_TICK_MS)
                    return "resume game"
                elif label == "settings":
                    print("SETTINGS IN PAUSE MENU UNIMPLEMENTED")
                elif label == "quit":
                    pygame.mixer.music.set_volume(prev_volume)
                    main_menu()

        pygame.display.update()
        game_clock.tick(60)


def settings():
    """Settings menu for volume."""
    running = True
    dragging = False

    slider_rect = pygame.Rect(
        SCREEN_WIDTH//1.75, 250, 200, 10)  # Volume slider track
    handle_x = SCREEN_WIDTH//1.75 + slider_rect.width
    handle_rect = pygame.Rect(handle_x, 245, 10, 20)  # Volume slider handle

    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
            if event.type == pygame.MOUSEMOTION and dragging:
                handle_rect.x = max(slider_rect.left, min(
                    event.pos[0], slider_rect.right - handle_rect.width))
            if event.type == pygame.MOUSEBUTTONDOWN:
                if handle_rect.collidepoint(event.pos):
                    dragging = True
                if slider_rect.collidepoint(event.pos):
                    handle_rect.x = max(slider_rect.left, min(
                        event.pos[0], slider_rect.right - handle_rect.width))
                if back_button.collidepoint(event.pos):
                    running = False
            elif event.type == pygame.MOUSEBUTTONUP:
                dragging = False

            volume = (handle_rect.centerx - slider_rect.left) / \
                slider_rect.width

            if volume >= 0.975:
                volume = 1
            elif volume <= 0.025:
                volume = 0

            pygame.mixer.music.set_volume(volume)

        screen.fill((250, 250, 250))

        draw_text('Settings', font, (5, 15, 10), screen, SCREEN_WIDTH//2, 100)

        back_button = pygame.Rect(10, 57.5, 200, 75)

        setting_label = pygame.font.SysFont(None, 75)

        draw_button(screen, back_button, "Back", setting_label,
                    (205, 220, 190), (0, 0, 0))
        draw_text('Volume', setting_label, (5, 15, 10),
                  screen, SCREEN_WIDTH//2.5, 250)

        pygame.draw.rect(screen, (100, 100, 100), slider_rect)
        pygame.draw.rect(screen, (200, 200, 200), handle_rect)

        pygame.display.update()
        game_clock.tick(60)


main_menu()
