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
HALF_WIDTH = int(WINDOW_WIDTH/2)
HALF_HEIGHT= int(WINDOW_HEIGHT/2)

initialPositionX = 64
initialPositionY = 512

#initialize font
myfont = pygame.font.SysFont("Courier New", 45)

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
        self.fitness = 0
    
    def update(self, left, right, space, platforms):
        if ((left and right) or (not left and not right)):
            if self.dx > 0:
                self.dx -= 0.1
            
            elif self.dx < 0:
                self.dx += 0.1
        
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
                    self.fitness += 100
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

class Hillary(Entity):
    def __init__(self,x,y):
        Entity.__init__(self)
        self.image = pygame.image.load('sprites/hillary.png').convert_alpha()
        self.rect = Rect(x,y,BLOCK_SIZE, BLOCK_SIZE)
        self.dx = -1
        self.dy = 3

    def update(self, platforms):
        self.rect.left += self.dx * speed[0]
        self.collide(self.dx, 0, platforms)
        self.rect.top += self.dy * speed[1]
        self.collide(0, self.dy, platforms)
                
    def collide(self, dx, dy, platforms):
        for p in platforms:
            if pygame.sprite.collide_rect(self, p):
                if dx > 0:
                    self.rect.right = p.rect.left
                    self.dx = -dx
                elif dx < 0:
                    self.rect.left = p.rect.right
                    self.dx = -dx

                if dy > 0:
                    self.rect.bottom = p.rect.top
                    self.dy = 0

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
        self.image = pygame.image.load('sprites/putin.png').convert_alpha()

class Camera(object):
    def __init__(self, camera_func, level_width, level_height):
        self.camera_func = camera_func
        self.state = Rect(0,0,level_width, level_height)
    
    def apply(self, target):
        return target.rect.move(self.state.topleft)

    def update(self, target):
        self.state = self.camera_func(self.state, target.rect)


def complex_camera(camera, target_rect):
    l, t, _, _ = target_rect
    _, _, w, h = camera
    l, t, _, _ = -l+CAMERA_OFFSET_WIDTH, -t+CAMERA_OFFSET_HEIGHT, w, h # center player

    l = min(0, l)                           # stop scrolling at the left edge
    l = max(-(camera.width-WINDOW_WIDTH), l)   # stop scrolling at the right edge
    t = max(-(camera.height-WINDOW_HEIGHT), t) # stop scrolling at the bottom
    t = min(0, t)                           # stop scrolling at the top

    return Rect(l, t, w, h)

def simple_camera(camera, target_rect):
    l, t, _, _ = target_rect # l = left,  t = top
    _, _, w, h = camera      # w = width, h = height
    return Rect(-l+HALF_WIDTH, -t+HALF_HEIGHT, w, h)

speed = [5,3]
black = 0, 0, 0

platforms = []
hillaries = []
entities = pygame.sprite.Group()
trump = Player(initialPositionX, initialPositionY)
entities.add(trump)

clock=pygame.time.Clock()

#initialize lvl
lvlFile = open('level.txt', 'r')
x = y = 0
level = []
for line in lvlFile:
    levelRow = []
    for char in line:
        if char == 'W':
            platform = Platform(x,y)
            platforms.append(platform)
            entities.add(platform)
        elif char == 'P':
            platform = EndPlatform(x,y)
            platforms.append(platform)
            entities.add(platform)
        elif char == 'H':
            hillary = Hillary(x,y)
            hillaries.append(hillary)
            entities.add(hillary)
        levelRow.append(char) 
    
        x += BLOCK_SIZE
    level.append(levelRow)

    y += BLOCK_SIZE
    x = 0

lvlFile.close()

pixel_lvl_width = len(level[0] * BLOCK_SIZE)
pixel_lvl_height = len(level * BLOCK_SIZE)
camera = Camera(simple_camera, pixel_lvl_width, pixel_lvl_height)

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
    
    camera.update(trump)
    trump.update(left, right, space, platforms)
    screen.fill(black)

    for hillary in hillaries:
        hillary.update(platforms)
        
    for e in entities:
        screen.blit(e.image, camera.apply(e))
    
    label = myfont.render('Fitness: ' + str(trump.fitness), 1, (255,255,255))
    screen.blit(label, (100, 100))
    pygame.display.flip()
