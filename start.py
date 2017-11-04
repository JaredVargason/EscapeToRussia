import sys, pygame

pygame.init()
WINDOW_WIDTH = 1024 
WINDOW_HEIGHT = 1024 
WINDOW_SIZE = WINDOW_WIDTH, WINDOW_HEIGHT
speed = [3,3]

black = 0, 0, 0
trump = pygame.image.load('sprites/trump.png')
trumprect = trump.get_rect()

clock=pygame.time.Clock()

screen = pygame.display.set_mode(WINDOW_SIZE)

while 1:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            sys.exit()

    trumprect = trumprect.move(speed)

    if trumprect.left < 0 or trumprect.right > WINDOW_WIDTH:
        speed[0] = -speed[0]
    if trumprect.top < 0 or trumprect.bottom > WINDOW_HEIGHT:
        speed[1] = -speed[1]
    screen.fill(black)
    screen.blit(trump, trumprect)
    pygame.display.flip()