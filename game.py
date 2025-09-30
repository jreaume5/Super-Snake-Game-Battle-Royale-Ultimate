from pygame.locals import *
import pygame
import sys

main_clock = pygame.time.Clock()
pygame.init()
pygame.display.set_caption('Super Snake Battle Royale Ultimate')
screen = pygame.display.set_mode((0, 0))
SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_width(), screen.get_height()
font = pygame.font.SysFont(None, 100)


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


click = False  # Boolean flag for click events


def main_menu():
    """The menu game loop. Handles all main menu logic."""
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
            draw_button(screen, button, label, font, button_color, (0, 0, 0))

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
    running = True
    while running:
        # Clear screen at beginning of the frame with white
        screen.fill((250, 250, 250))
        draw_text('welcome to the game', font,
                  (5, 15, 10), screen, SCREEN_WIDTH//2, 100)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False

        pygame.display.update()
        main_clock.tick(60)


def start_sim():
    """The simulation game loop. Handles all simulation logic."""
    running = True
    while running:
        # Clear screen at beginning of the frame with white
        screen.fill((250, 250, 250))
        draw_text('this is placeholder text for the simulation', font,
                  (5, 15, 10), screen, SCREEN_WIDTH//2, 100)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False

        pygame.display.update()
        main_clock.tick(60)


def settings():
    """The settings game loop. Handles all settings logic."""
    running = True
    while running:
        # Clear screen at beginning of the frame with white
        screen.fill((250, 250, 250))
        draw_text('haha nothing for you to change here', font,
                  (5, 15, 10), screen, SCREEN_WIDTH//2, 100)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False

        pygame.display.update()
        main_clock.tick(60)


main_menu()
