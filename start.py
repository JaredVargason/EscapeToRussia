import sys, pygame
from pygame import *

pygame.init()
WINDOW_WIDTH = 1024 
WINDOW_HEIGHT = 768
BLOCK_SIZE = 64 
SCREEN_BLOCK_WIDTH = WINDOW_WIDTH/BLOCK_SIZE
SCREEN_BLOCK_HEIGHT = WINDOW_HEIGHT/BLOCK_SIZE
WINDOW_SIZE = WINDOW_WIDTH, WINDOW_HEIGHT
screen = pygame.display.set_mode(WINDOW_SIZE)

class Entity(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

class Player(Entity):
    def __init__(self, x, y):
        Entity.__init__(self)
        self.dx = 0
        self.dy = 0
        self.grounded = False
        self.image = pygame.image.load('sprites/trump.png').convert_alpha()
        self.rect = Rect(x,y,BLOCK_SIZE, BLOCK_SIZE)
    
    def update(self, left, right, space, platforms):
        if ((left and right) or (not left and not right)):
            self.dx = 0
        
        elif left:
            if self.dx > -2:
                self.dx += -0.1

        elif right:
            if self.dx < 2:
                self.dx += 0.1

        if space:
            if self.grounded:
                self.dy = -7
        
        if not self.grounded:
            self.dy += 0.3
        
        self.rect.left += self.dx * speed[0]
        self.collide(self.dx, 0, platforms)
        self.rect.top += self.dy * speed[1]
        self.grounded = False
        self.collide(0, self.dy, platforms)

    def collide(self, dx, dy, platforms):
        for p in platforms:
            if pygame.sprite.collide_rect(self,p):
                if isinstance(p, EndPlatform):
                    pygame.event.post(pygame.event.Event(QUIT))
                if dx > 0:
                    self.rect.right = p.rect.left
                elif dx < 0:
                    self.rect.left = p.rect.right

                if dy > 0:
                    self.rect.bottom = p.rect.top
                    self.grounded = True
                    self.dy = 0
                elif dy < 0:
                    self.rect.top = p.rect.bottom


class Platform(Entity):
    def __init__(self,x,y):
        Entity.__init__(self)
        self.image = pygame.Surface((BLOCK_SIZE,BLOCK_SIZE))
        self.image.convert()
        self.image.fill(Color('#ff0000'))
        self.rect = Rect(x,y,BLOCK_SIZE,BLOCK_SIZE)
    
    def update():
        pass

class EndPlatform(Platform):
    def __init__(self,x,y):
        Platform.__init__(self, x, y)
        self.image.fill(Color("#0000ff"))


speed = [5,3]
black = 0, 0, 0

platforms = []
entities = pygame.sprite.Group()
trump = Player(100, 600)
entities.add(trump)

clock=pygame.time.Clock()



#initialize lvl
lvlFile = open('level.txt', 'r')
x = y = 0

for line in lvlFile:
    for char in line:
        if char == 'W':
            platform = Platform(x,y)
            platforms.append(platform)
            entities.add(platform)
        elif char == 'E':
            platform = EndPlatform(x,y)
            platforms.append(platform)
            entities.add(platform)

        x += BLOCK_SIZE

    y += BLOCK_SIZE
    x = 0


lvlFile.close()

            
while 1:
    left = right = space = False
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            sys.exit()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_RIGHT] and keys[pygame.K_LEFT]:
        left = right = False
    
    elif keys[pygame.K_RIGHT]:
        right = True

    elif keys[pygame.K_LEFT]:
        left = True

    if keys[pygame.K_SPACE]:
        space = True
    
    trump.update(left, right, space, platforms)
    
    screen.fill(black)
    entities.draw(screen)
    pygame.display.flip()

