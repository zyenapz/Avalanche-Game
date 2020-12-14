import pygame, random
from data.scripts.constants import *

# Draw radius
#temp_rect = self.image.get_rect()
#pygame.draw.circle(self.image, (255,0,0), temp_rect.center, self.radius)

class Player(pygame.sprite.Sprite):
    def __init__(self, images):
        super().__init__()
        self.image = images
        self.image_orig = images
        self.rect = self.image.get_rect()
        self.rect.centerx = WIN_RES["W"] / 2
        self.rect.bottom = WIN_RES["H"] * 0.9
        self.direction = "forward"
        self.has_collided = False
        # For speed
        self.spdx = 0
        self.movspd = 6
        # For collision
        self.radius = 16

    def update(self):

        if not self.has_collided:
            self.spdx = 0
            self.image = self.image_orig

            # Get pressed key
            pressed = pygame.key.get_pressed()
            if pressed[pygame.K_a]:
                self.spdx = -self.movspd
                self.rotate_img(45)
            elif pressed[pygame.K_d]:
                self.spdx = self.movspd
                self.rotate_img(-45)

            # Draw radius
            #temp_rect = self.image.get_rect()
            #pygame.draw.circle(self.image, (255,0,0), temp_rect.center, self.radius)

            # Move sprite on the x-axis
            self.rect.x += self.spdx
            
            self.check_oob()
        else:
            self.rect.y += 8

    def check_oob(self):
        # Check if sprite is out of bounds
        if self.rect.left < 0:
            self.rect.left = 0
            self.spdx = 0
        elif self.rect.right > WIN_RES["W"]:
            self.rect.right = WIN_RES["W"]
            self.spdx = 0

    def rotate_img(self, angle):
        orig_rect = self.image.get_rect()
        rot_image = pygame.transform.rotate(self.image, angle)
        rot_rect = orig_rect.copy()
        rot_rect.center = rot_image.get_rect().center
        rot_image = rot_image.subsurface(rot_rect).copy()
        self.image = rot_image

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, images):
        super().__init__()
        self.image = self.roll_img(images)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(0, WIN_RES["W"]-64)
        self.rect.y = random.randrange(-256, -128)
        self.movspd = SPRITE_MOVESPEED
        self.spdy = self.movspd
        # For collision
        self.radius = 32
    
    def update(self):
        
        # Draw radius
        #temp_rect = self.image.get_rect()
        #pygame.draw.circle(self.image, (255,0,0), temp_rect.center, self.radius)

        self.rect.y += self.spdy

        if self.rect.top > WIN_RES["H"]:
            self.kill()

    def roll_img(self, images):
        img_list = images
        choices = random.choices(img_list, [8,8,8,1,1,1,1,1], k=10)
        return random.choice(choices)

class Fracture(pygame.sprite.Sprite):
    def __init__(self, images):
        super().__init__()
        self.images = images
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(-32, WIN_RES["W"]-64)
        self.rect.y = random.randrange(-256, -128)
        self.movspd = SPRITE_MOVESPEED
        self.spdy = self.movspd
        self.fracture_timer = pygame.time.get_ticks()
        self.fracture_delay = random.randrange(500,1000)
        self.fractured = False
        # For animation
        self.frame = 0
        self.frame_timer = pygame.time.get_ticks()
        self.frame_delay = 200
        # For collision
        self.radius = 48

    def update(self):

        # Draw radius
        #temp_rect = self.image.get_rect()
        #pygame.draw.circle(self.image, (255,0,0), temp_rect.center, self.radius)

        self.rect.y += self.spdy

        now = pygame.time.get_ticks()
        if now - self.fracture_timer > self.fracture_delay:
            self.animate()

        if self.rect.top > WIN_RES["H"]:
            self.kill()

    def animate(self):
        now = pygame.time.get_ticks()
        if now - self.frame_timer > self.frame_delay and self.frame != len(self.images) - 1:
            old_rectx = self.rect.x
            old_recty = self.rect.y
            self.frame_timer = now
            self.frame += 1
            self.image = self.images[self.frame]
            self.rect = self.image.get_rect()
            self.rect.x = old_rectx
            self.rect.y = old_recty
            if self.frame == 4:
                self.fractured = True

class Debris(pygame.sprite.Sprite):
    def __init__(self, images, window):
        super().__init__()
        self.images = images
        size = random.randrange(200,232)
        self.img_roll = random.randrange(0, len(images))
        self.image = pygame.transform.scale(self.images["normal"][self.img_roll], (size, size))
        self.rect = self.image.get_rect()
        self.rect.centerx = random.randrange(64, WIN_RES["W"]-64)
        self.rect.centery = WIN_RES["H"]*1.2
        self.window = window
        self.impacted = False
        self.img_changed = False
        self.movspd = SPRITE_MOVESPEED
        self.spdx = self.calc_spdx()
        self.shaked = False # Bool if it has shaked the screen. See game loop.
        # The point at which the object will stop moving on the y-axis
        self.max_disty = random.randrange(96, WIN_RES["H"] * 0.2)
        # For shrinking
        self.shrink_timer = pygame.time.get_ticks()
        self.shrink_delay = 120
        self.scaler = 0
        # For collision
        self.radius = 64

    def update(self):

        # Draw radius
        #temp_rect = self.image.get_rect()
        #pygame.draw.circle(self.image, (255,0,0), temp_rect.center, self.radius)

        # Stop on the specified y-axis line
        if self.rect.top < self.max_disty:
            self.impacted = True

        if self.impacted:
            self.rect.y += self.movspd
            if self.img_changed == False:
                self.change_image()
                self.img_changed = True
                self.radius = self.image.get_width() // 3
        else: 
            self.rect.y -= random.randrange(7,9)
            self.rect.x += self.spdx
            self.shrink()

        if self.impacted and self.rect.top > WIN_RES["H"]:
            self.kill()

    def shrink(self):
        now = pygame.time.get_ticks()
        if now - self.shrink_timer > self.shrink_delay:
            old_x = self.rect.centerx
            old_y = self.rect.centery
            self.shrink_timer = now
            x_scale = self.image.get_width() - self.scaler
            y_scale = self.image.get_height() - self.scaler
            self.image = pygame.transform.scale(self.image, (x_scale,y_scale))
            self.rect = self.image.get_rect()
            self.rect.centerx = old_x
            self.rect.centery = old_y
            self.scaler += 1

    def change_image(self):
        old_x = self.rect.centerx
        old_y = self.rect.centery
        x_scale = self.image.get_width() - self.scaler
        y_scale = self.image.get_height() - self.scaler
        self.image = pygame.transform.scale(self.images["impacted"][self.img_roll], (x_scale, y_scale))
        self.rect.centerx = old_x
        self.rect.centery = old_y

    def calc_spdx(self):
        if self.rect.centerx > WIN_RES["W"] / 2:
            return -2
        elif self.rect.centerx < WIN_RES["W"] / 2:
            return 2
        else:
            return random.choice([-2,2])

class Particle():
    def __init__(self, window, WIN_RES, x, y, colors, launch_type):
        self.window = window
        self.WIN_RES = WIN_RES
        self.x = x
        self.y = y
        self.color = random.choice(colors)
        self.launch_type = launch_type
        if self.launch_type == "explosion":
            self.spdx = random.choice([num for num in range(-8,8) if num not in [-2,-1,0,1,2]])
            self.spdy = random.choice([num for num in range(-8,8) if num not in [-2,-1,0,1,2]])
            self.size = random.choice([4,8])
        elif self.launch_type == "trail":
            self.spdx = 0
            self.spdy = SPRITE_MOVESPEED
            self.size = 8
            self.y = self.y -32

    def update(self):
        self.x += self.spdx
        self.y += self.spdy
        if self.launch_type == "explosion":
            pygame.draw.rect(self.window, self.color, (self.x, self.y, self.size, self.size))
        elif self.launch_type == "trail":
            pygame.draw.circle(self.window, self.color, (self.x+2, self.y), self.size)