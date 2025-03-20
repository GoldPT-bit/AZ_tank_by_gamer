# Download pygame, pyinstaller
import pygame
from pygame.locals import *
import sys
import random
import math
import os

# Function to get the correct path for resources
def resource_path(relative_path):
    """Get absolute path to resource, works for dev and PyInstaller"""
    if hasattr(sys, '_MEIPASS'):
        # Running as PyInstaller executable
        return os.path.join(sys._MEIPASS, relative_path)
    else:
        # Running as script
        return os.path.join(os.path.dirname(__file__), relative_path)

# Khởi tạo Pygame
pygame.init()

# Thiết lập cửa sổ game
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game Menu")

# Màu sắc
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# **Lớp Button**
class Button:
    def __init__(self, x, y, image, hover_image, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.hover_image = pygame.transform.scale(hover_image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False

    def draw(self, surface):
        action = False
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            surface.blit(self.hover_image, (self.rect.x, self.rect.y))
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                self.clicked = True
                action = True
        else:
            surface.blit(self.image, (self.rect.x, self.rect.y))
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
        return action

# **Hàm Menu**
def menu(screen):
    try:
        bg_img = pygame.image.load(resource_path("Picture/menubg.png")).convert()
        ip_img = pygame.image.load(resource_path("Picture/button/button1.png")).convert_alpha()
        ip_hover_img = pygame.image.load(resource_path("Picture/button/button2.png")).convert_alpha()
        iip_img = pygame.image.load(resource_path("Picture/button/button3.png")).convert_alpha()
        iip_hover_img = pygame.image.load(resource_path("Picture/button/button4.png")).convert_alpha()
        qt_img = pygame.image.load(resource_path("Picture/button/button5.png")).convert_alpha()
        qt_hover_img = pygame.image.load(resource_path("Picture/button/button6.png")).convert_alpha()
    except pygame.error as e:
        print(f"Error loading images: {e}")
        return "quit"

    ip_but = Button(515, 200, ip_img, ip_hover_img, 0.1)
    iip_but = Button(515, 300, iip_img, iip_hover_img, 0.1)
    qt_but = Button(515, 400, qt_img, qt_hover_img, 0.1)

    font = pygame.font.Font(None, 36)
    clock = pygame.time.Clock()
    run = True
    
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

        screen.blit(bg_img, (0, 0))

        if ip_but.draw(screen):
            return "1p"
        if iip_but.draw(screen):
            return "2p"
        if qt_but.draw(screen):
            return "quit"

        pygame.display.flip()
        clock.tick(60)

    return "quit"

# **Hàm Pause**
def pause(screen):
    red = (227, 172, 75)
    try:
        font = pygame.font.Font(resource_path("Fonts/pxred.ttf"), 36)
    except:
        font = pygame.font.Font(None, 36)

    try:
        bg_img = pygame.image.load(resource_path("Picture/menubg.png")).convert()
        qt_img = pygame.image.load(resource_path("Picture/button/button5.png")).convert_alpha()
        qt_hover_img = pygame.image.load(resource_path("Picture/button/button6.png")).convert_alpha()
        rt_img = pygame.image.load(resource_path("Picture/button/button7.png")).convert_alpha()
        rt_hover_img = pygame.image.load(resource_path("Picture/button/button8.png")).convert_alpha()
    except pygame.error as e:
        print(f"Error loading images: {e}")
        return "quit"

    qt_but = Button(515, 300, qt_img, qt_hover_img, 0.1)
    rt_but = Button(415, 300, rt_img, rt_hover_img, 0.1)

    def drawtxt(txt, fnt, col, x, y):
        img = fnt.render(txt, True, col)
        screen.blit(img, (x, y))

    run = True
    while run:
        screen.blit(bg_img, (0, 0))
        drawtxt("Paused", font, red, 545, 50)

        if rt_but.draw(screen):
            return "resume"
        if qt_but.draw(screen):
            return "quit"

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

        pygame.display.update()

# **Các lớp Game**
class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def apply_rect(self, rect):
        return rect.move(self.camera.topleft)

    def update(self, targets):
        if not targets:
            return
        total_x = sum(target.rect.centerx for target in targets)
        total_y = sum(target.rect.centery for target in targets)
        mid_x = total_x / len(targets)
        mid_y = total_y / len(targets)
        x = -mid_x + WIDTH // 2
        y = -mid_y + HEIGHT // 2
        x = min(0, x)
        y = min(0, y)
        x = max(-(self.width - WIDTH), x)
        y = max(-(self.height - HEIGHT), y)
        self.camera = pygame.Rect(x, y, self.width, self.height)

class Tank(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.original_image = tank_image
        self.run_frames = tank_run_frames
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.center = (MAP_WIDTH // 2, MAP_HEIGHT // 2)
        self.hitbox = pygame.Rect(0, 0, tank_size, tank_size)
        self.hitbox.center = self.rect.center
        self.speed = 2
        self.flipped = False
        self.shoot_cooldown = 0
        self.shoot_cooldown_time = 180
        self.frame_index = 0
        self.animation_speed = 10
        self.animation_counter = 0
        self.is_moving = False

    def update(self):
        keys = pygame.key.get_pressed()
        move_vector = pygame.math.Vector2(0, 0)
        if keys[K_a]:
            self.flipped = True
            move_vector.x -= 1
        if keys[K_d]:
            self.flipped = False
            move_vector.x += 1
        if keys[K_w]:
            move_vector.y -= 1
        if keys[K_s]:
            move_vector.y += 1
        self.is_moving = move_vector.length() > 0
        if self.is_moving:
            move_vector = move_vector.normalize() * self.speed
        self.rect.x += move_vector.x
        self.rect.y += move_vector.y
        self.rect.clamp_ip(pygame.Rect(0, 0, MAP_WIDTH, MAP_HEIGHT))
        if self.is_moving:
            self.animation_counter += 1
            if self.animation_counter >= self.animation_speed:
                self.animation_counter = 0
                self.frame_index = (self.frame_index + 1) % len(self.run_frames)
            current_frame = self.run_frames[self.frame_index]
            self.image = pygame.transform.flip(current_frame, True, False) if self.flipped else current_frame
        else:
            self.image = pygame.transform.flip(self.original_image, True, False) if self.flipped else self.original_image
            self.frame_index = 0
        self.rect = self.image.get_rect(center=self.rect.center)
        self.hitbox.center = self.rect.center
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def shoot(self, enemies):
        if self.shoot_cooldown > 0:
            return
        closest_enemy = None
        min_distance = float('inf')
        for enemy in enemies:
            if enemy.alive():
                dx = enemy.rect.centerx - self.rect.centerx
                dy = enemy.rect.centery - self.rect.centery
                distance = math.hypot(dx, dy)
                if distance < min_distance:
                    min_distance = distance
                    closest_enemy = enemy
        if closest_enemy and min_distance <= 200:
            proj = Projectile(self.rect.centerx, self.rect.centery, closest_enemy, projectile_image)
            projectiles.add(proj)
            all_sprites.add(proj)
            self.shoot_cooldown = self.shoot_cooldown_time

class Tank2(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.original_image = tank2_image
        self.run_frames = tank2_run_frames
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.center = (MAP_WIDTH // 2 + 100, MAP_HEIGHT // 2)
        self.hitbox = pygame.Rect(0, 0, tank_size, tank_size)
        self.hitbox.center = self.rect.center
        self.speed = 2
        self.flipped = False
        self.shoot_cooldown = 0
        self.shoot_cooldown_time = 180
        self.frame_index = 0
        self.animation_speed = 10
        self.animation_counter = 0
        self.is_moving = False

    def update(self):
        keys = pygame.key.get_pressed()
        move_vector = pygame.math.Vector2(0, 0)
        if keys[K_LEFT]:
            self.flipped = True
            move_vector.x -= 1
        if keys[K_RIGHT]:
            self.flipped = False
            move_vector.x += 1
        if keys[K_UP]:
            move_vector.y -= 1
        if keys[K_DOWN]:
            move_vector.y += 1
        self.is_moving = move_vector.length() > 0
        if self.is_moving:
            move_vector = move_vector.normalize() * self.speed
        self.rect.x += move_vector.x
        self.rect.y += move_vector.y
        self.rect.clamp_ip(pygame.Rect(0, 0, MAP_WIDTH, MAP_HEIGHT))
        if self.is_moving:
            self.animation_counter += 1
            if self.animation_counter >= self.animation_speed:
                self.animation_counter = 0
                self.frame_index = (self.frame_index + 1) % len(self.run_frames)
            current_frame = self.run_frames[self.frame_index]
            self.image = pygame.transform.flip(current_frame, True, False) if self.flipped else current_frame
        else:
            self.image = pygame.transform.flip(self.original_image, True, False) if self.flipped else self.original_image
            self.frame_index = 0
        self.rect = self.image.get_rect(center=self.rect.center)
        self.hitbox.center = self.rect.center
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def shoot(self, enemies):
        if self.shoot_cooldown > 0:
            return
        closest_enemy = None
        min_distance = float('inf')
        for enemy in enemies:
            if enemy.alive():
                dx = enemy.rect.centerx - self.rect.centerx
                dy = enemy.rect.centery - self.rect.centery
                distance = math.hypot(dx, dy)
                if distance < min_distance:
                    min_distance = distance
                    closest_enemy = enemy
        if closest_enemy and min_distance <= 200:
            proj = Projectile(self.rect.centerx, self.rect.centery, closest_enemy, projectile2_image)
            projectiles.add(proj)
            all_sprites.add(proj)
            self.shoot_cooldown = self.shoot_cooldown_time

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, target, projectile_image):
        super().__init__()
        self.image = projectile_image
        self.original_image = self.image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 7
        self.angle = 0
        self.turn_speed = 5
        self.target = target
        self.start_time = pygame.time.get_ticks()

    def update(self):
        self.angle += self.turn_speed
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        if self.target and self.target.alive():
            dx = self.target.rect.centerx - self.rect.centerx
            dy = self.target.rect.centery - self.rect.centery
            distance = math.hypot(dx, dy)
            if distance > 0:
                self.rect.x += self.speed * dx / distance
                self.rect.y += self.speed * dy / distance
        if not pygame.Rect(0, 0, MAP_WIDTH, MAP_HEIGHT).contains(self.rect):
            self.kill()
        if pygame.time.get_ticks() - self.start_time > 600:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, camera):
        super().__init__()
        self.original_image = enemy_image
        self.run_frames = enemy_run_frames
        self.image = self.run_frames[0]
        self.rect = self.image.get_rect()
        self.speed = 1
        
        # Spawn ở các cạnh của camera
        offset = 0
        side = random.choice(['left', 'right', 'top', 'bottom'])
        if side == 'left':
            self.rect.x = camera.camera.left - offset
            self.rect.y = random.randint(camera.camera.top, camera.camera.bottom)
        elif side == 'right':
            self.rect.x = camera.camera.right + offset
            self.rect.y = random.randint(camera.camera.top, camera.camera.bottom)
        elif side == 'top':
            self.rect.x = random.randint(camera.camera.left, camera.camera.right)
            self.rect.y = camera.camera.top - offset
        elif side == 'bottom':
            self.rect.x = random.randint(camera.camera.left, camera.camera.right)
            self.rect.y = camera.camera.bottom + offset
        
        self.rect.clamp_ip(pygame.Rect(0, 0, MAP_WIDTH, MAP_HEIGHT))
        
        self.frame_index = 0
        self.animation_speed = 15
        self.animation_counter = 0

    def update(self, player_tanks):
        if not player_tanks:
            return
        closest_tank = min(player_tanks, key=lambda t: math.hypot(self.rect.x - t.rect.x, self.rect.y - t.rect.y))
        if self.rect.x < closest_tank.rect.x:
            self.rect.x += self.speed
        elif self.rect.x > closest_tank.rect.x:
            self.rect.x -= self.speed
        if self.rect.y < closest_tank.rect.y:
            self.rect.y += self.speed
        elif self.rect.y > closest_tank.rect.y:
            self.rect.y -= self.speed
        self.animation_counter += 1
        if self.animation_counter >= self.animation_speed:
            self.animation_counter = 0
            self.frame_index = (self.frame_index + 1) % len(self.run_frames)
            self.image = self.run_frames[self.frame_index]

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.coin_frames = [pygame.image.load(resource_path(f"Picture/coin/coin{i}.png")) for i in range(1, 8)]
        self.coin_frames = [pygame.transform.scale(frame, (40, 40)) for frame in self.coin_frames]
        self.frame_index = 0
        self.image = self.coin_frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.hitbox = pygame.Rect(x - 20, y - 20, 40, 40)
        self.animation_speed = 100
        self.last_update = pygame.time.get_ticks()

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update > self.animation_speed:
            self.frame_index = (self.frame_index + 1) % len(self.coin_frames)
            self.image = self.coin_frames[self.frame_index]
            self.last_update = current_time

# **Logic chính**
choice = menu(screen)
if choice == "quit":
    pygame.quit()
    sys.exit()

# Thiết lập biến game
MAP_WIDTH = 7000
MAP_HEIGHT = 7000
tank_size = 40

# Tải hình ảnh
background = pygame.image.load(resource_path("Picture/Picture2.png")).convert_alpha()
background = pygame.transform.scale(background, (MAP_WIDTH, MAP_HEIGHT))

tank_image = pygame.image.load(resource_path("Picture/rouge/rouge.png")).convert_alpha()
tank_image = pygame.transform.scale(tank_image, (tank_size, tank_size))
tank_run_frames = []
for i in range(1, 7):
    frame = pygame.image.load(resource_path(f"Picture/rouge/run/rouge_run{i}.png")).convert_alpha()
    frame = pygame.transform.scale(frame, (tank_size, tank_size))
    tank_run_frames.append(frame)

tank2_image = pygame.image.load(resource_path("Picture/vikin/vikin.png")).convert_alpha()
tank2_image = pygame.transform.scale(tank2_image, (50, 50))
tank2_run_frames = []
for i in range(1, 7):
    frame = pygame.image.load(resource_path(f"Picture/vikin/run/vikin_run{i}.png")).convert_alpha()
    frame = pygame.transform.scale(frame, (50, 50))
    tank2_run_frames.append(frame)

projectile_image = pygame.image.load(resource_path("Picture/dagger.png")).convert_alpha()
projectile_image = pygame.transform.scale(projectile_image, (30, 30))

projectile2_image = pygame.image.load(resource_path("Picture/axe.png")).convert_alpha()
projectile2_image = pygame.transform.scale(projectile2_image, (30, 30))

enemy_image = pygame.image.load(resource_path("Picture/mob/aimon1.png")).convert_alpha()
enemy_image = pygame.transform.scale(enemy_image, (30, 30))
enemy_run_frames = []
for i in range(1, 6):
    frame = pygame.image.load(resource_path(f"Picture/mob/aimon{i}.png")).convert_alpha()
    frame = pygame.transform.scale(frame, (30, 30))
    enemy_run_frames.append(frame)

# Khởi tạo tank theo lựa chọn
if choice == "1p":
    player_tanks = [Tank()]
elif choice == "2p":
    player_tanks = [Tank(), Tank2()]

all_sprites = pygame.sprite.Group()
for tank in player_tanks:
    all_sprites.add(tank)
projectiles = pygame.sprite.Group()
enemies = pygame.sprite.Group()
coins = pygame.sprite.Group()

camera = Camera(MAP_WIDTH, MAP_HEIGHT)

score = 0
font = pygame.font.Font(None, 36)
clock = pygame.time.Clock()

spawn_timer = 0
spawn_interval = 3 * 60  # 3 giây * 60 FPS
spawn_amount = 30
max_score_to_spawn = 100

# Vòng lặp game
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pause_choice = pause(screen)
                if pause_choice == "quit":
                    pygame.quit()
                    sys.exit()

    # Cập nhật tank và sprite
    for tank in player_tanks:
        tank.update()
        tank.shoot(enemies)
    for sprite in all_sprites:
        if isinstance(sprite, Enemy):
            sprite.update(player_tanks)
        else:
            sprite.update()
    camera.update(player_tanks)
    coins.update()

    # Spawn quái định kỳ
    if score < max_score_to_spawn:
        spawn_timer += 1
        if spawn_timer >= spawn_interval:
            for _ in range(spawn_amount):
                enemy = Enemy(camera)
                enemies.add(enemy)
                all_sprites.add(enemy)
            spawn_timer = 0

    # Kiểm tra nhặt xu
    for coin in coins:
        for player_tank in player_tanks:
            if player_tank.hitbox.colliderect(coin.hitbox):
                coin.kill()
                score += 10
                break

    # Kiểm tra va chạm đạn và kẻ thù
    hits = pygame.sprite.groupcollide(projectiles, enemies, True, True)
    for proj, enemies_hit in hits.items():
        for enemy in enemies_hit:
            coin = Coin(enemy.rect.centerx, enemy.rect.centery)
            all_sprites.add(coin)
            coins.add(coin)

    # Kiểm tra va chạm tank và kẻ thù
    for enemy in enemies:
        for player_tank in player_tanks:
            if player_tank.hitbox.colliderect(enemy.rect):
                print("Trò chơi kết thúc")
                pygame.quit()
                sys.exit()

    # Vẽ lên màn hình
    screen.blit(background, camera.camera.topleft)
    for sprite in all_sprites:
        screen.blit(sprite.image, camera.apply(sprite))
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))
    pygame.display.update()
    clock.tick(60)