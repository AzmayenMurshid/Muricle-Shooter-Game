import pygame
from pygame import mixer
import os
import random
from win32api import GetSystemMetrics
import csv
import button
import sys


sys.path.insert(0, 'D:/PythonProjects/Games/ShooterGame/libmpg123')
mixer.init()
pygame.init()

SCREEN_WIDTH = GetSystemMetrics(0)
SCREEN_HEIGHT = GetSystemMetrics(1)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Shooter Game") # Set the title of the window --> Change the name of the game whenever.

# set framerate
clock = pygame.time.Clock()
FPS = 60

# define game variables
GRAVITY = 0.75
SCROLL_THRESH = 200
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
FLOOR_Y = SCREEN_HEIGHT - (TILE_SIZE * 5)
TILE_TYPES =  21
MAX_LEVEL = 3

screen_scroll = 0
bg_scroll = 0
level = 1
start_game = False
start_intro = False


# define player action variables
moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_thrown = False

#load music and sounds

'''
pygame.mixer.music.load('D:/PythonProjects/Games/ShooterGame/audio/music2.mp3')
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1, 0.0, 5000)
'''

jump_fx = pygame.mixer.Sound('D:/PythonProjects/Games/ShooterGame/audio/jump.wav')
jump_fx.set_volume(0.5)

shot_fx = pygame.mixer.Sound('D:/PythonProjects/Games/ShooterGame/audio/shot.wav')
shot_fx.set_volume(0.5)

grenade_fx = pygame.mixer.Sound('D:/PythonProjects/Games/ShooterGame/audio/grenade.wav')
grenade_fx.set_volume(0.5)


# store tiles in a list
img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f'D:/PythonProjects/Games/ShooterGame/img/tile/{x}.png')
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)

# load images
    # Loading buttons
start_img = pygame.image.load(f'D:/PythonProjects/Games/ShooterGame/img/start_btn.png').convert_alpha()
exit_img = pygame.image.load(f'D:/PythonProjects/Games/ShooterGame/img/exit_btn.png').convert_alpha()
restart_img = pygame.image.load(f'D:/PythonProjects/Games/ShooterGame/img/restart_btn.png').convert_alpha()

# loading background images
pine1_image = pygame.image.load('D:/PythonProjects/Games/ShooterGame/img/background/pine1.png').convert_alpha()
pine2_image = pygame.image.load('D:/PythonProjects/Games/ShooterGame/img/background/pine2.png').convert_alpha()
mountain_img = pygame.image.load('D:/PythonProjects/Games/ShooterGame/img/background/mountain2.jpg').convert_alpha()
sky_img = pygame.image.load('D:/PythonProjects/Games/ShooterGame/img/background/sky_cloud2.jpg').convert_alpha()
background = pygame.image.load('D:/PythonProjects/Games/ShooterGame/img/background/background.jpg').convert_alpha()
forest_img = pygame.image.load('D:/PythonProjects/Games/ShooterGame/img/background/city_bg.jpg').convert_alpha()

# loading interactive images
bullet_img = pygame.image.load('D:/PythonProjects/Games/ShooterGame/img/icons/bullet.png').convert_alpha()
grenade_img = pygame.image.load('D:/PythonProjects/Games/ShooterGame/img/icons/grenade.png').convert_alpha()
health_box_img = pygame.image.load('D:/PythonProjects/Games/ShooterGame/img/icons/health_box.png').convert_alpha()
ammo_box = pygame.image.load('D:/PythonProjects/Games/ShooterGame/img/icons/ammo_box.png').convert_alpha()
grenade_box = pygame.image.load('D:/PythonProjects/Games/ShooterGame/img/icons/grenade_box.png').convert_alpha()

# creating dictionary for all the images
item_boxes = { # dictionary for all the item boxes
    'Health': health_box_img,
    'Ammo': ammo_box,
    'Grenade': grenade_box
}

# define colors
BG = (144, 201, 120)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
PINK = (235, 65, 54)

def draw_bg():
    screen.fill(BLACK) # --> Background Color
    width = background.get_width()
    for x in range(5):
        screen.blit(forest_img,((x * width) - bg_scroll * 0.5, 0))

        '''
        screen.blit(sky_img,((x * width) - bg_scroll * 0.5, 0))
        screen.blit(mountain_img, ((x * width) - bg_scroll * 0.6, 0))
        screen.blit(pine1_image, ((x * width) - bg_scroll * 0.7, SCREEN_HEIGHT - pine1_image.get_height() - 170))
        screen.blit(pine2_image, ((x * width) - bg_scroll * 0.8, SCREEN_HEIGHT - pine2_image.get_height()))
        '''


# define font
font = pygame.font.SysFont('Futura', 30)
intro_font = pygame.font.SysFont('Georgia', 150)
death_font = pygame.font.SysFont('Georgia', 100)
end_font = pygame.font.SysFont('Georgia', 150)

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


#function to reset level
def reset_level():
    enemy_group.empty()
    bullet_group.empty()
    grenade_group.empty()
    explosion_group.empty()
    item_box_group.empty()
    decoration_group.empty()
    water_group.empty()
    exit_group.empty()

    # create empty tile list
    data = []
    for row in range(ROWS):
        r = [-1] * COLS
        data.append(r)

    return data

class Soldier(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo, grenades):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.ammo = ammo
        self.start_ammo = ammo
        self.shoot_cooldown = 0
        self.grenades = grenades
        self.health = 100
        self.max_health = self.health
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        # ai specific variables
        self.move_counter = 0
        self.vision = pygame.Rect(0,0, 150, 20) # --> 150 is how far the ai can look.
        self.idling = False
        self.idling_counter = 0

        #load all images for the players
        animation_types = ["Idle", "Run", "Jump", "Death"]
        for animation in animation_types:
            #reset temporary list of images
            temp_list = []  # --> temporary list to store images
            #count number of files in the folder
            num_of_frames = len(os.listdir(
                f'D:/PythonProjects/Games/ShooterGame/img/{self.char_type}/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(
                    f'D:/PythonProjects/Games/ShooterGame/img/{self.char_type}/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        self.update_animation()
        self.check_alive()
        # update cooldown animation
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self, moving_left, moving_right):
        # reset movement variables
        screen_scroll = 0
        dx = 0
        dy = 0

        # assign movement variables if moving left or right
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        elif moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        #Jump
        if self.jump == True and self.in_air == False:
            self.vel_y = -13 # -13 is the vertical velocity that will allow the player to jump. Negative means the player is moving up.
            self.jump = False
            self.in_air = True

        #apply gravity
        self.vel_y += GRAVITY # adding means decreasing the y velocity
        if self.vel_y > 10:
            self.vel_y

        dy += self.vel_y

        # check for collision
        for tile in world.obstacle_list:
            # check collision in x direction
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
                #if the ai has hit the wall, turn around
                if self.char_type == 'enemy':
                    self.direction *= -1
                    self.move_counter = 0
            # check collision in y direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                #check if below the ground, i.e jumping
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top

                # check if above the ground, i.e falling
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom

        # check for collision with water
        if pygame.sprite.spritecollide(self, water_group, False):
            self.health = 0

        # check for collision with exit
        level_complete = False
        if pygame.sprite.spritecollide(self, exit_group, False):
            level_complete = True


        # check if fallen off the map
        if self.rect.bottom > SCREEN_HEIGHT:
            self.health = 0

        # check  if  going off the edges of the screen
        if self.char_type == 'player':
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                dx = 0

        #update rectangle position
        self.rect.x += dx
        self.rect.y += dy

        # update scroll based on player position
        if self.char_type == 'player':
            if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and bg_scroll < (world.level_length * TILE_SIZE) - SCREEN_WIDTH)\
                or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
                self.rect.x -= dx
                screen_scroll = -dx

        return screen_scroll, level_complete

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20 # --> `20` is the cooldown time between each bullet. Lower the number, the fast you can shoot.
            bullet = Bullet(self.rect.centerx + (0.65 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
            bullet_group.add(bullet)
            # reduce amnmo by 1
            self.ammo -= 1
            shot_fx.play()


    def ai(self):
        if  self.alive and player.alive:
            if self.idling == False and random.randint(1, 200) == 1:
                self.update_action(0)# --> `0` is the index of the idle animation in the animation list
                self.idling = True
                self.idling_counter = 50
            # check if ai is near the player
            if self.vision.colliderect(player.rect):
                #stop running and face the player
                self.update_action(0) # 0 is the index of the idle animation in the animation list
                self.shoot() # shot the player
            else:
                if self.idling == False:
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1) # --> `1` is the index of the run animation in the animation list
                    self.move_counter +=1
                    #update vision as the enemy moves
                    self.vision.center = (self.rect.centerx + (self.rect.size[0] * self.direction), self.rect.centery)

                    if self.move_counter > TILE_SIZE:
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False

        #scroll
        self.rect.x += screen_scroll

    def update_animation(self):
        # update animation
        ANIMATION_COOLDOWN = 100
        #Update Image depending on current frame
        self.image = self.animation_list[self.action][self.frame_index]
        #check if enough time has passed since last animation update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        #if animation is at the end of the list, reset to first frame
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) -1
            else:
                self.frame_index = 0


    def update_action(self, new_action):
        #check if new action is different from the previous action
        if new_action != self.action:
            self.action = new_action
            #update the animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
            if self.health <= 0:
                self.health = 0
                self.speed = 0
                self.alive = False
                self.update_action(3)

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)


class World():
    def __init__(self):
        self.obstacle_list = []

    def process_data(self, data):
        self.level_length = len(data[0])
        # iterate through each value in the level data file
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >=0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    if tile >= 0 and tile <= 8:
                        self.obstacle_list.append(tile_data)
                    elif  tile >= 9 and tile <= 10:
                        water = Water(img, int(x * TILE_SIZE), (y * TILE_SIZE))
                        water_group.add(water)
                    elif tile >= 11 and tile <= 14:
                        decoration = Decoration(img, int(x * TILE_SIZE), (y * TILE_SIZE))
                        decoration_group.add(decoration)
                    elif tile == 15: # create a player
                        player = Soldier('player', x * TILE_SIZE, y * TILE_SIZE, 1.75, 5, 20, 5) # -- > (x, y, scale, speed, ammo), 20 is the ammo amount, 5 is the number of grenades
                        health_bar = HealthBar(10, 10, player.health, player.health)
                    elif tile == 16: # create enemy
                        enemy = Soldier('enemy', (x* TILE_SIZE), (y * TILE_SIZE), 1.75, 2.5, 50, 0)
                        enemy_group.add(enemy)
                    elif tile == 17: # create ammo box
                        item_box = ItemBox('Ammo', int(x * TILE_SIZE), (y * TILE_SIZE), 0.85)
                        item_box_group.add(item_box)
                    elif tile == 18: # creating grenade box
                        item_box = ItemBox('Grenade', int(x * TILE_SIZE), (y * TILE_SIZE), 0.85)
                        item_box_group.add(item_box)
                    elif tile == 19: # creating health box
                        item_box = ItemBox('Health', int(x * TILE_SIZE), (y * TILE_SIZE), 0.85)
                        item_box_group.add(item_box)
                    elif tile == 20: # create exit
                       exit = Exit(img, int(x * TILE_SIZE), (y * TILE_SIZE))
                       exit_group.add(exit)

        return player, health_bar

    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])

class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll

class Water(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll

class Exit(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll

class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE//2, y + (TILE_SIZE - self.image.get_height()))
        self.image = pygame.transform.scale(self.image, (int(self.image.get_width() * scale), int(self.image.get_height() * scale)))

    def update(self):
        #scroll
        self.rect.x += screen_scroll
        # check if the player has picked up the box
        if pygame.sprite.collide_rect(self, player):
            # check what type of box
            if self.item_type == 'Health':
                player.health += 25
                if player.health > player.max_health:
                    player.health = player.max_health
            elif self.item_type == 'Ammo':
                player.ammo += 15
            elif self.item_type == 'Grenade':
                player.grenades += 3

            # delete the item box
            self.kill()


class HealthBar():
    def __init__(self, x, y, health, max_health):
        [self.x, self.y] = [x, y]
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        # draw health bar with updated health
        self.health = health

        pygame.draw.rect(screen, BLACK, (self.x -2, self.y-2, 304, 24))
        pygame.draw.rect(screen, RED, (self.x, self.y, 300, 20)) # draw the health bar RED
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 300 * (self.health/self.max_health), 20)) # draw the health bar GREEN


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self) # parent class inheriting from pygame.sprite.Sprite
        self.speed = 10
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        # move bullet
        self.rect.x += (self.direction * self.speed) + screen_scroll
        # check if bullet has gone off screen
        if self.rect.left > SCREEN_WIDTH or self.rect.right < 0:
            self.kill()

        #check for collision with level
        for  tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()

        # check collision with characters
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -=5
                self.kill()
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive:
                    enemy.health -=25
                    self.kill()

class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self) # parent class inheriting from pygame.sprite.Sprite
        self.timer = 100
        self.vel_y = -11
        self.speed = 7
        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.direction = direction


    def update(self):
        self.vel_y += GRAVITY
        [dx, dy] = [self.direction * self.speed, self.vel_y]

        # check for collsion will level
        for  tile in world.obstacle_list:
            # check collision with obstacles
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
               self.direction *= -1
               dx = self.direction * self.speed
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                self.speed = 0 # stop moving, wait for timer to expire. Speed is 0 so it doesn't move
                # check iif the velow the ground, i.e thrown up
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                # check if above the ground. i.e falling
                elif self.vel_y >=0:
                    self.vel_y = 0
                    dy = tile[1].top - self.rect.bottom


        # check collision with walls
        if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
            self.direction *= -1
            dx = self.direction * self.speed

        # update grenade position
        self.rect.x += dx + screen_scroll
        self.rect.y += dy

        # countdown timer
        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            grenade_fx.play()
            explosion = Explosion(self.rect.x, self.rect.y, 2)
            explosion_group.add(explosion)

            # do damage to anyone nearby
            if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 1 and\
                abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 1:
                    player.health -= 50

            elif abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2 and\
                abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 2:
                    player.health -= 25
            else:
                pass

            for enemy in enemy_group:

                if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 1 and\
                    abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 1:
                        enemy.health -= 100

                elif abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2 and\
                    abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 2:
                        enemy.health -= 50
                
                else:
                    pass

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self) # parent class inheriting from pygame.sprite.Sprite
        self.images = []
        for num in range(1, 6):
            img = pygame.image.load(f'D:/PythonProjects/Games/ShooterGame/img/explosion/exp{num}.png').convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.images.append(img)
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0

    def update(self):
        # scroll
        self.rect.x += screen_scroll
        EXPLOSION_SPEED = 14
        # update explosion animation
        self.counter += 1

        if self.counter >= EXPLOSION_SPEED:
            self.counter = 0
            self.frame_index += 1
            # if animation is complete then delete the explosion
            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index]


class ScreenFade():
    def __init__(self, direction, color, speed):
        self.direction = direction
        self.color = color
        self.speed = speed
        self.fade_counter = 0

    def fade(self):
        fade_complete = False
        self.fade_counter += self.speed
        if self.direction ==1: # whole screen fade
            pygame.draw.rect(screen, self.color, (0 - self.fade_counter, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.color, (SCREEN_WIDTH // 2 + self.fade_counter, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.color, (0, 0 - self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
            pygame.draw.rect(screen, self.color, (0, SCREEN_HEIGHT // 2 + self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT))
        if self.direction == 2: # vertical screen down
            pygame.draw.rect(screen, self.color, [0, 0, SCREEN_WIDTH, 0 + self.fade_counter])
        if self.fade_counter >= SCREEN_HEIGHT:
            fade_complete = True
        return fade_complete

# create screen fades
intro_fade = ScreenFade(1, BLACK, 4)
death_fade = ScreenFade(2, BLACK, 8)

# create buttons
start_button  = button.Button(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 + 25, start_img, 1)
exit_button  = button.Button(SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 + 175, exit_img, 1)
restart_button  = button.Button(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 100, restart_img, 3)
quit_button  = button.Button(SCREEN_WIDTH // 2 - 90, SCREEN_HEIGHT // 2 + 100, exit_img, 1)


# create sprite groups
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()


# create  empty tile list
world_data = []
for row in range(ROWS):
    r = [-1] * COLS
    world_data.append(r)

#load in level data and create world
with open(f'D:/PythonProjects/Games/ShooterGame/scripts/level{level}_data.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)


world = World()
player, health_bar = world.process_data(world_data)
player.ammo +=1


run = True
while run:

    clock.tick(FPS)

    if start_game == False:
        #draw menu
        screen.blit(background, (0, 0))
        # add buttons
        draw_text('Muricle', intro_font, BLACK, SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 - 300)
        if start_button.draw(screen):
            start_game = True
            start_intro = True
        if exit_button.draw(screen):
            run = False

    else:
        # update background
        draw_bg()
        # draw world map
        world.draw()

        #show player health
        health_bar.draw(player.health)

        #Show Ammo
        draw_text('AMMO: ', font, WHITE, 10, 35)
        for x in range(player.ammo):
            screen.blit(bullet_img, (100 + (x*10), 40))

        #Show Grenades
        draw_text('Grenades: ', font, WHITE, 10, 60)
        for x in range(player.grenades):
            screen.blit(grenade_img, (135 + (x*15), 60))


        player.update()
        player.draw()

        for enemy in enemy_group:
            enemy.ai()
            enemy.update()
            enemy.draw()


        # update and draw groups
        bullet_group.update()
        bullet_group.draw(screen)

        grenade_group.update()
        grenade_group.draw(screen)

        explosion_group.update()
        explosion_group.draw(screen)

        item_box_group.update()
        item_box_group.draw(screen)

        decoration_group.update()
        decoration_group.draw(screen)

        water_group.update()
        water_group.draw(screen)

        exit_group.update()
        exit_group.draw(screen)

        #show intro
        if start_intro == True:
            if intro_fade.fade():
                start_intro = False
                intro_fade.fade_counter = 0 # setting fade counter to 0

        if player.alive:
            # update player actions
            if shoot:
                player.shoot()
            # throw grenades
            elif grenade and grenade_thrown == False and player.grenades > 0:
                grenade = Grenade(player.rect.centerx + (0.5 * player.rect.size[0] * player.direction),\
                                player.rect.top, player.direction)
                grenade_group.add(grenade)
                # reduce grenades by 1
                player.grenades -= 1
                grenade_thrown = True
            if player.in_air:
                player.update_action(2) #2: jump
            elif moving_left or moving_right:
                player.update_action(1) #1: run
            else:
                player.update_action(0) #0: idle
            screen_scroll, level_complete = player.move(moving_left, moving_right)
            bg_scroll -= screen_scroll
            # check if player has completed the level
            if level_complete:
                start_intro = True
                level += 1
                bg_scroll = 0
                world_data = reset_level()
                if level <= MAX_LEVEL:
                    #load in level data and create world
                    with open(f'D:/PythonProjects/Games/ShooterGame/scripts/level{level}_data.csv', newline='')\
                        as csvfile:

                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)

                    world = World()
                    player, health_bar = world.process_data(world_data)
                    
                else: # end game
                    run = False


        else:
            screen_scroll = 0
            if death_fade.fade():
                draw_text('YOU DIED!', death_font, RED, SCREEN_WIDTH // 2 - 240, SCREEN_HEIGHT // 2 - 300)
                if restart_button.draw(screen):
                    death_fade.fade_counter = 0
                    start_intro = True
                    bg_scroll = 0
                    world_data = reset_level()
                    #load in level data and create world
                    with open(f'D:/PythonProjects/Games/ShooterGame/scripts/level{level}_data.csv', newline='')\
                        as csvfile:

                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)

                    world = World()
                    player, health_bar = world.process_data(world_data)
                
                if quit_button.draw(screen):
                    run = False


    # Event Handling
    for event in pygame.event.get():
        # quit Game
        if event.type == pygame.QUIT:
            run = False


        #Keyboard inputs
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_SPACE and player.alive:
                player.jump = True
                jump_fx.play()
            if event.key == pygame.K_ESCAPE:
                run = False

        #Keyboard button release
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and player.alive:
                shoot = True
            if event.button == 3 and player.alive:
                grenade = True

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                shoot = False
            if event.button == 3:
                grenade = False
                grenade_thrown = False


    pygame.display.update()

pygame.quit()

