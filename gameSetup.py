import pygame, sys, random  #it is the module for system

pygame.init() #to start the pygame

#<a href="https://www.flaticon.com/free-icons/snake" title="snake icons">Snake icons created by Ivan Abirawa - Flaticon</a>
#<a href="https://www.flaticon.com/free-icons/snake" title="snake icons">Snake icons created by apien - Flaticon</a>
snake_icon = pygame.image.load("game.png")
pygame.display.set_icon(snake_icon) # for some reason this is not working on the mac os... I tried everything like checked on google and all 


width = 400
height = 500
screen = pygame.display.set_mode((width,height)) # this just set the display to 400 x 500 pixels
pygame.display.set_caption("Snake Game") # set the title of the display

game_running = True # set it to true 

# Food 
food_color = (255, 0, 0)
food_size = 20

# we want to put the food at random location so we gonna use random lib
foodX = random.randint(0, width - food_size)
foodY = random.randint(0, height - food_size)

# draw food on the display
food = pygame.Rect(foodX, foodY, food_size, food_size)


snake_color = (0, 255, 0) # using RGB value for the snake color 
snake_size = 20 
snakeX = width // 2
snakeY = height // 2
snake_speed = 8


snake = pygame.Rect(snakeX, snakeY, snake_size, snake_size) # left, top, width, height  ||| creating snake rectange as snake body

snake_body = []

#run until the condition is false
while game_running:
    for event in pygame.event.get(): 
        if event.type == pygame.QUIT: 
            game_running = False 

    screen.fill((0,0,0)) #fill the screen with color black (RGB)

    pygame.draw.rect(screen, snake_color, snake) # draw the snake
    pygame.draw.rect(screen, food_color, food)


    pygame.display.update() #update display
    
    # Snake movement
    snake_mx = 0
    snake_my = 0

    # window boundries 
    if snake.x < 0 or snake.x + snake_size > width or snake.y < 0 or snake.y + snake_size > height:
        game_running = False

    # snake controls
    snake_speed_multi = 1

    #update snake position 
    snake.x += snake_mx * snake_speed * snake_speed_multi
    snake.y += snake_my * snake_speed * snake_speed_multi

    if snake.collidedict(food):
        snake_size += 1
        score += 1

        food.x = random.randint(0, width - food_size)
        food.y = random.randint(0, height - food_size)

    snake_body.append(pygame.Rect(snake.x, snake.y, snake_size, snake_size))
    if len(snake_body) > snake_size:
        del snake_body[0]

    #check collison between two snake head and body
    if len(snake_body) > 1 and snake.colliderect(snake_body[i] for i in range(1, len(snake_body))):
        game_running = False


#we want to display the game message and the final score after we do with the game
game_over_font = pygame.font.Font(None, 48) #it takes (name, size)
game_over_text = game_over_font.render("Game Over", True, (255, 255, 255)) #text with white color

#we need font for the score
score_font = pygame.font.Font(None, 35)
score_text = score_font.render("Final Score: " + str(score), True, (255, 255,255) ) #we have text "Final Score: " wiht the score 

#game_window.blit(game_over_text, (width // 2 - game_over_text.get_width() // 2, height // 2 - 48))
#I will continue working on this - Deep

pygame.quit()
sys.exit()
