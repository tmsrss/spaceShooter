import pygame
import random
from os import path

# sets the img folder in the same directory of this python file as the img_dir variable
img_dir = path.join(path.dirname(__file__), "img")
snd_dir = path.join(path.dirname(__file__), "snd")

# constants
WIDTH = 480
HEIGHT = 600
FPS = 60
POWERUP_TIME = 5000

# colours       https://www.rapidtables.com/web/color/RGB_Color.html
black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
yellow = (255, 255, 0)


# Initialise and create pygame window
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")
clock = pygame.time.Clock()

# setting the font for the display score
font_name = pygame.font.match_font("arial")


class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_img, (50, 38))
        self.image.set_colorkey(black)
        self.rect = self.image.get_rect()
        self.radius = 20
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 0
        self.health = 100
        self.shoot_delay = 250  # time in milliseconds
        self.last_shot = pygame.time.get_ticks()
        self.lives = 3
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        self.gun_power = 1
        self.time_gun_powerup = pygame.time.get_ticks()

    def update(self):
        # gun powerup timeout
        if self.gun_power > 1 and pygame.time.get_ticks() - self.time_gun_powerup > POWERUP_TIME:
            self.gun_power -= 1
            self.gun_power_time = pygame.time.get_ticks()
        # un-hide if hidden
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 2000:  # 2000ms means 2 seconds of hiding
            self.hidden = False
            all_sprites.add(self)
            removed.remove(self)
            player.rect.centerx = WIDTH / 2
            player.rect.bottom = HEIGHT - 10
            player.health = 100
        self.speedx = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_a]:
            self.speedx = -8
        if keystate[pygame.K_d]:
            self.speedx = 8
        if keystate[pygame.K_SPACE] and player not in removed:
            self.shoot()
        self.rect.x += self.speedx
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            if self.gun_power == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
                laser_snd.play()
            elif self.gun_power > 1:
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)
                laser_snd.play()

    def gun_powerup(self):
        self.gun_power += 1
        self.time_gun_powerup = pygame.time.get_ticks()

    def hide(self):
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT + 200
        removed.add(self)
        all_sprites.remove(self)


class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_og = random.choice(meteor_images)
        self.image_og.set_colorkey(black)
        self.image = self.image_og.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * 0.85 / 2)
        self.rect.x = random.randrange(0, WIDTH - self.rect.width)
        self.rect.y = random.randrange(-150, -100)
        self.speedy = random.randrange(1, 8)
        self.speedx = random.randrange(-3, 3)
        self.rotation = 0
        self.rotation_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()

    def rotate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.rotation = (self.rotation + self.rotation_speed) % 360
            new_image = pygame.transform.rotate(self.image_og, self.rotation)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center

    def update(self):
        self.rotate()
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if self.rect.top > HEIGHT + 10 or self.rect.left < -10 or self.rect.right > WIDTH + 10:
            self.rect.x = random.randrange(0, WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 8)
            self.speedx = random.randrange(-3, 3)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.image.set_colorkey(black)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -12

    def update(self):
        self.rect.y += self.speedy
        # deletes the bullet when it leaves the top of the screen.
        if self.rect.bottom < 0:
            self.kill()


class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_animation[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 75

    def update(self, *args):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_animation[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_animation[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center


class Powerup(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(["shield", "gun"])
        self.image = powerup_images[self.type]
        self.image.set_colorkey(black)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 4

    def update(self):
        self.rect.y += self.speedy
        # deletes the bullet when it leaves the top of the screen.
        if self.rect.bottom > HEIGHT:
            self.kill()


def newmob():
    m = Mob()
    all_sprites.add(m)
    mobs.add(m)


def draw_health_bar(surf, x, y, pct):
    if pct < 0:
        pct = 0
    bar_length = 100
    bar_height = 10
    fill = (pct/100)*bar_length
    outline_rect = pygame.Rect(x, y, bar_length, bar_height)
    fill_rect = pygame.Rect(x, y, fill, bar_height)
    pygame.draw.rect(surf, green, fill_rect)
    pygame.draw.rect(surf, white, outline_rect, 2)


def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, white)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


def draw_lives(surf, x, y, lives, image):
    for v in range(lives):
        img_rect = image.get_rect()
        img_rect.x = x - 30 * v  # makes starships disappear from left to right
        img_rect.y = y
        surf.blit(image, img_rect)


def show_gameover_screen():
    screen.blit(background, background_rect)
    draw_text(screen, "THE Game!", 64, WIDTH/2, HEIGHT/4)
    draw_text(screen, "a and d keys to move. Space bar to fire.", 22, WIDTH/2, HEIGHT/2)
    draw_text(screen, "Press any key to begin.", 18, WIDTH/2, HEIGHT*3/4)
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP:
                waiting = False


def create_player():  # creates the player (the main starship)
    player = Player()
    all_sprites.add(player)


# loading graphics
background = pygame.image.load(path.join(img_dir, "starfield.png")).convert()
background_rect = background.get_rect()
player_img = pygame.image.load(path.join(img_dir, "playerShip1_red.png")).convert()
bullet_img = pygame.image.load(path.join(img_dir, "laserRed16.png")).convert()
meteor_img = pygame.image.load(path.join(img_dir, "meteorBrown_med1.png")).convert()
mini_starship = pygame.transform.scale(player_img, (25, 19))
mini_starship.set_colorkey(black)
meteor_images = []
meteor_list = ['meteorBrown_big1.png', 'meteorBrown_med1.png', 'meteorBrown_med1.png', 'meteorBrown_med3.png',
               'meteorBrown_small1.png', 'meteorBrown_small2.png', 'meteorBrown_tiny1.png']
for image in meteor_list:
    meteor_images.append(pygame.image.load(path.join(img_dir, image)).convert())
explosion_animation = dict(large=[], small=[], player=[])
for i in range(9):
    # regular explosion
    filename = "regularexplosion0{}.png".format(i)
    img = pygame.image.load(path.join(img_dir, filename)).convert()
    img.set_colorkey(black)
    img_large = pygame.transform.scale(img, (75, 75))
    explosion_animation["large"].append(img_large)
    img_small = pygame.transform.scale(img, (32, 32))
    explosion_animation["small"].append(img_small)
    # death/sonic explosion
    sonicfilename = "sonicExplosion0{}.png".format(i)
    sonicimg = pygame.image.load(path.join(img_dir, sonicfilename)).convert()
    sonicimg.set_colorkey(black)
    explosion_animation["player"].append(sonicimg)
powerup_images = dict(shield=pygame.image.load(path.join(img_dir, "shield_gold.png")).convert(),
                      gun=pygame.image.load(path.join(img_dir, "bolt_gold.png")).convert())


# loading sounds
laser_snd = pygame.mixer.Sound(path.join(snd_dir, "Laser_Shoot.wav"))
explosion_snd = []
for i in ["expl3.wav", "expl6.wav"]:
    explosion_snd.append(pygame.mixer.Sound(path.join(snd_dir, i)))
player_die_snd = pygame.mixer.Sound(path.join(snd_dir, "rumble1.ogg"))
pygame.mixer.music.load(path.join(snd_dir, "tgfcoder-FrozenJam-SeamlessLoop.ogg"))
pygame.mixer.music.set_volume(.4)
shield_snd = pygame.mixer.Sound(path.join(snd_dir, "Powerup4.wav"))
gun_snd = pygame.mixer.Sound(path.join(snd_dir, "Powerup8.wav"))


# GAME LOOP
pygame.mixer.music.play(loops=-1)
running = True
gameover = True
while running:
    if gameover:
        show_gameover_screen()
        gameover = False
        # set starting constants for each new game
        # group all objects
        all_sprites = pygame.sprite.Group()
        mobs = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        powerups = pygame.sprite.Group()
        removed = pygame.sprite.Group()
        # spawn the meteorites
        for i in range(8):
            newmob()
        # creates the player (the main starship)
        player = Player()
        all_sprites.add(player)
        score = 0

    # keep loop running at right speed
    clock.tick(FPS)
    # Process input
    for event in pygame.event.get():
        # check for closing window
        if event.type == pygame.QUIT:
            running = False
        # checks spacebar press
    # Update
    all_sprites.update()
    removed.update()
    # check if player has been hit by a mob, it returns a list
    hits = pygame.sprite.spritecollide(player, mobs, True, pygame.sprite.collide_circle)
    for hit in hits:
        player.health -= hit.radius * 2
        newmob()
        random.choice(explosion_snd).play()
        explosion = Explosion(hit.rect.center, "small")
        all_sprites.add(explosion)
        if player.health <= 0:
            player_die_snd.play()
            death_explosion = Explosion(player.rect.center, "player")
            all_sprites.add(death_explosion)
            player.hide()
            player.lives -= 1
            player.shield = 100
    # check if player has hit a powerup
    grabs = pygame.sprite.spritecollide(player, powerups, True)
    for grab in grabs:
        if grab.type == "shield":
            shield_snd.play()
            player.health += random.randint(20, 30)
            if player.health >= 100:
                player.health = 100
        elif grab.type == "gun":
            gun_snd.play()
            player.gun_powerup()
    # if the player died and the explosion has finished playing
    if player.lives == 0 and not death_explosion.alive():
        gameover = True
    # check if a bullet hit a mob
    shots = pygame.sprite.groupcollide(mobs, bullets, True, True)
    for shot in shots:
        score += 50 - shot.radius
        random.choice(explosion_snd).play()
        explosion = Explosion(shot.rect.center, "large")
        all_sprites.add(explosion)
        if random.random() > 0.95:
            powerup = Powerup(shot.rect.center)
            all_sprites.add(powerup)
            powerups.add(powerup)
        newmob()

    # Render
    screen.fill(black)
    screen.blit(background, background_rect)
    all_sprites.draw(screen)
    draw_text(screen, str(score), 18, WIDTH / 2, 10)
    draw_health_bar(screen, 5, 5, player.health)
    draw_lives(screen, WIDTH - 40, 5, player.lives, mini_starship) # WIDTH - 40 makes starships disappear from left to right
    # last, after drawing everything
    pygame.display.flip()


pygame.quit()
