import sys, pygame
from pygame import *
import random

WINDOW_WIDTH = 1024 
WINDOW_HEIGHT = 768
ADJUSTED_WINDOW_HEIGHT = WINDOW_HEIGHT + 200
BLOCK_SIZE = 64 
SCREEN_BLOCK_WIDTH = WINDOW_WIDTH/BLOCK_SIZE
SCREEN_BLOCK_HEIGHT = WINDOW_HEIGHT/BLOCK_SIZE
WINDOW_SIZE = WINDOW_WIDTH, WINDOW_HEIGHT 
HALF_WIDTH = int(WINDOW_WIDTH/2)
HALF_HEIGHT= int(WINDOW_HEIGHT/2)

initialPositionX = 128
initialPositionY = 512 

speed = [5,3]
black = 0, 0, 0

def generateRandomColor():
    colorChars = list('ABCDEF0123456789')
    colorString = '#'
    for i in range(6):
        colorString += random.choice(colorChars)

    return colorString


class Entity(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

class Player(Entity):

    def __init__(self, x, y):
        Entity.__init__(self)
        self.alive = True
        self.dx = 0
        self.dy = 0
        self.grounded = False
        self.image = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))
        self.image.convert()
        self.image.fill(Color(generateRandomColor()))
        self.rect = Rect(x,y,BLOCK_SIZE, BLOCK_SIZE)
        self.position = 0
        self.framesAlive = 0
        self.ctlr = {  'Left':False,
                             'Right':False,
                             'Space':False }
    
    def update(self, platforms, hillaries, controller):
        self.ctlr = controller
        self.position = self.rect.x -initialPositionX
        if ((self.ctlr['Left'] and self.ctlr['Right']) or (not self.ctlr['Left'] and not self.ctlr['Right'])):
            if self.dx < 0.01 and self.dx > -0.01:
                self.dx = 0 

            if self.dx > 0:
                self.dx -= 0.1
            
            elif self.dx < 0:
                self.dx += 0.1
        
        elif self.ctlr['Left']:
            if self.dx > -2:
                self.dx += -0.1

        elif self.ctlr['Right']:
            if self.dx < 2:
                self.dx += 0.1

        if self.ctlr['Space']:
            if self.grounded:
                self.dy = -7
        
        if not self.grounded:
            self.dy += 0.3
        
        self.rect.left += self.dx * speed[0]
        self.collide(self.dx, 0, platforms, hillaries)
        self.rect.top += self.dy * speed[1]
        self.grounded = False
        self.collide(0, self.dy, platforms, hillaries)

    def collide(self, dx, dy, platforms, enemies):
        for enemy in enemies:
            if pygame.sprite.collide_rect(self,enemy):
                self.alive = False

        for p in platforms:
            if pygame.sprite.collide_rect(self,p):
                if isinstance(p, EndPlatform):
                    self.position += 1000
                    self.alive = False 
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
    

class Enemy(Entity):
    def __init__(self,x,y):
        Entity.__init__(self)

        self.image = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))
        self.image.convert()
        self.image.fill(Color("#00ff00"))
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

class EndPlatform(Platform):
    def __init__(self,x,y):
        Platform.__init__(self, x, y)
        self.image = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))
        self.image.convert()
        self.image.fill(Color("#ff00ff"))

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

class Level():
    def __init__(self, levelname, n=1):
        self.players = []
        self.platforms = []
        self.entities = pygame.sprite.Group() 
        self.enemies = []
        self.n = n

        self.levelArray = self.readLevelArray(levelname)
        self.blockWidth = len(self.levelArray[0])
        self.blockHeight = len(self.levelArray) 

    def readLevelArray(self, filename):
        with open(filename, 'r') as lvlFile:
            lvlFile = open(filename, 'r')
            x = y = 0
            level = []
            for line in lvlFile:
                levelRow = []
                for char in line:
                    levelRow.append(char)
                level.append(levelRow)
            
            return level

    #rename to resetLevel?
    def createLevel(self, n):
        self.players = []
        self.entities.empty()
        self.platforms = []
        self.enemies = []

        x = y = 0
        for row in self.levelArray:
            for char in row:
                if char == 'W':
                    platform = Platform(x,y)
                    self.platforms.append(platform)
                    self.entities.add(platform)
                elif char == 'P':
                    platform = EndPlatform(x,y)
                    self.platforms.append(platform)
                    self.entities.add(platform)
                elif char == 'H':
                    enemy = Enemy(x,y)
                    self.enemies.append(enemy)
                    self.entities.add(enemy)
                elif char == 'T':
                    for i in range(n):
                        player = Player(x,y)
                        self.players.append(player)
                        self.entities.add(player) 

                x += BLOCK_SIZE
            y += BLOCK_SIZE
            x = 0 
    
    def allPlayersDead(self):
        for player in self.players:
            if player.alive:
                return False
        
        return True

class Game():
    def __init__(self, filename, n=1):
        pygame.init()
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        self.myfont = pygame.font.SysFont("Courier New", 30)
        self.n = n

        self.level = Level(filename, n)
        self.clock=pygame.time.Clock()
        
        self.pixel_lvl_width = len(self.level.levelArray[0]) * BLOCK_SIZE
        self.pixel_lvl_height = len(self.level.levelArray) * BLOCK_SIZE
        self.camera = Camera(simple_camera, self.pixel_lvl_width, self.pixel_lvl_height)

        #UI information
        self.generation = 0
        self.numSpecies = 0
        self.maxFitness = 0
        self.population = 0
        
        self.neuronPositions = {}

    def playGame(self):
        while(1):
            self.level.createLevel(1)
            while self.level.players[0].alive:
                self.update()
            
    def update(self):
        controller = {'Right':False, 'Left':False, 'Space':False}

        keys = pygame.key.get_pressed()
            
        controller['Left'] = keys[pygame.K_LEFT] 
        controller['Right'] = keys[pygame.K_RIGHT] 
        controller['Space'] = keys[pygame.K_SPACE] 

        self.advance_frame(ctlrs=[controller])
    
    def advance_frame(self, ctlrs=[], ui=True, network=None):
        self.clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                sys.exit()
            else:
                None

        self.camera.update(self.getBestAlivePlayer()[1])
        for i, player in enumerate(self.level.players):
            if player.alive:
                player.update(self.level.platforms, self.level.enemies, ctlrs[i])
                player.framesAlive += 1

        self.screen.fill(black)

        for enemy in self.level.enemies:
            enemy.update(self.level.platforms)
            
        for e in self.level.entities:
            self.screen.blit(e.image, self.camera.apply(e))
        
        #labels
        if ui:
            player = self.getBestAlivePlayer()[1]
            positionLabel = self.myfont.render('Position: ' + str(player.position), 1, (255,255,255))
            self.screen.blit(positionLabel, (600, 100))
            maxFitnessLabel = self.myfont.render('Max Fitness ' + str(self.maxFitness), 1, (255,255,255))
            self.screen.blit(maxFitnessLabel, (600, 130))
            generationLabel = self.myfont.render('Generation ' + str(self.generation), 1, (255,255,255))
            self.screen.blit(generationLabel, (600, 160))
            numSpeciesLabel = self.myfont.render('# Species ' + str(self.numSpecies), 1, (255,255,255))
            self.screen.blit(numSpeciesLabel, (600, 190))
            populationLabel = self.myfont.render('Population: ' + str(self.population), 1, (255,255,255))
            self.screen.blit(populationLabel, (600,220))

            inputs = self.getInputs(self.getPlayerBlockPosition(0))
            self.drawInputGrid(inputs, network)

        pygame.display.flip()
                
    def getPlayerBlockPosition(self, i):
        player = self.level.players[i]
        x = int(player.rect.x/self.pixel_lvl_width * self.level.blockWidth)
        y = int(player.rect.y/self.pixel_lvl_height * self.level.blockHeight)

        return x,y

    def getBestAlivePlayer(self):
        bestPlayerIndex = 0 
        for i, player in enumerate(self.level.players):
            if player.position > self.level.players[bestPlayerIndex].position and player.alive:
                bestPlayerIndex = i
        
        return bestPlayerIndex, self.level.players[bestPlayerIndex] 

    def getInputs(self, playerBlockPosition):
        inputs = []
        playerBlockPositionX = playerBlockPosition[0]
        playerBlockPositionY = playerBlockPosition[1]
        
        leftBlockPosition = playerBlockPositionX - 5 
        topBlockPosition = playerBlockPositionY - 5 
        realpadding = 0 - topBlockPosition 
        padding = 0
        for row in range(topBlockPosition, topBlockPosition + 12):
            if row < 0:
                inputs.extend([0] * 12)
                padding += 1
            elif row > self.level.blockHeight - 1:
                inputs.extend([0] * 12)
            
            else:

                for i in range(leftBlockPosition, leftBlockPosition + 12): 
                    if i >= self.level.blockWidth - 1 or i < 0:
                        inputs.append(0)
                        continue
                    
                    if (self.level.levelArray[row][i] == 'W'):
                        inputs.append(1) 
                    else:
                        inputs.append(0)

        #get enemy positions
        for enemy in self.level.enemies:
            enemyBlockX = int(enemy.rect.x/self.pixel_lvl_width * self.level.blockWidth) 
            enemyBlockY = int(enemy.rect.y/self.pixel_lvl_height * self.level.blockHeight) + realpadding
            if enemyBlockX >= leftBlockPosition and enemyBlockX < leftBlockPosition + 12 and enemyBlockY >= topBlockPosition and enemyBlockY < topBlockPosition + 12: 
                #There is an enemy...
                inputs[enemyBlockY*12+enemyBlockX-leftBlockPosition] = -1
        
        return inputs

    def drawInputGrid(self,inputs, network=None):
        y = 100 
        x = 130 
        for i in range(len(inputs)):
            space = inputs[i]
            square = pygame.Surface((8,8))
            if space == 1: 
                square.fill(Color('#ffffff'))
                self.screen.blit(square, (x, y))
            elif space == -1:
                square.fill(Color('#00ff00'))
                self.screen.blit(square, (x, y))

            self.neuronPositions[i] = (x, y)
            x += 9 
        
            if i % 12 == 11:
                y += 9 
                x = 130
        '''
        if network != None:
            for num, neuron in network['neurons'].items():
                square = pygame.Surface((8,8))
                if num > len(inputs) and num < 1000000:
                    #non output
                    square.fill(Color('#eeeeee'))
                    x = random.randint(140, 240)
                    y = random.randint(100, 200)
                    self.neuronPositions[num] = (x,y)
                    self.screen.blit(square, (x,y))
                    
                elif num >= 1000000: #output 
                    square.fill(Color('#cccccc'))
                    x = 260
                    y = num - 1000000 + 100
                    self.neuronPositions[num] = (x,y)
                    self.screen.blit(square,(x,y))
            
            for num, neuron in network['neurons'].items():
                for incoming in neuron.incoming:
                    prevPos = self.neuronPositions[incoming]
                    incPos = self.neuronPositions[num]
                    pygame.draw.line(self.screen, Color('#888888'), prevPos, incPos)
        '''

    def updateUI(self, generation, numSpecies, maxFitness, population):
        self.generation = generation
        self.numSpecies = numSpecies
        self.maxFitness = maxFitness
        self.population = population

if __name__ == '__main__':
    if len(sys.argv) == 2:
        game = Game(sys.argv[1])

    else:
        game = Game('level.txt')

    game.playGame()