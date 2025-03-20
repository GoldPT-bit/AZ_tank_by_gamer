import pygame
from pygame.locals import *
import sys
import random
import math

# Khởi tạo Pygame
pygame.init()

# Thiết lập cửa sổ game
WIDTH, HEIGHT = 1300, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Xe Tăng AZ Replica")

# Thiết lập đồng hồ để quản lý FPS
clock = pygame.time.Clock()

# Màu sắc
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Thiết lập kích thước bản đồ lớn
MAP_WIDTH = 7000
MAP_HEIGHT = 7000

# Thiết lập kích thước tank
tank_size = 40

# Tải hình ảnh cho Tank (nhân vật thứ nhất)
tank_image = pygame.image.load("Picture\\rouge\\rouge.png").convert_alpha()
tank_image = pygame.transform.scale(tank_image, (tank_size, tank_size))

# Tải các frame animation cho Tank (rouge)
tank_run_frames = []
for i in range(1, 13):  # Từ 1 đến 6
    if i%2==1: 
        frame = pygame.image.load(f"Picture\\rouge\\run\\rouge_run{int(i/2)+1}.png").convert_alpha()
    else: frame = pygame.image.load(f"Picture\\rouge\\run\\rouge_run{int(i/2)}.png").convert_alpha()
    frame = pygame.transform.scale(frame, (tank_size, tank_size))
    tank_run_frames.append(frame)

# Tải hình ảnh cho Tank2 (nhân vật thứ hai)
tank2_image = pygame.image.load("Picture\\vikin\\vikin.png").convert_alpha()
tank2_image = pygame.transform.scale(tank2_image, (50, 50))

# Tải các frame animation cho Tank2 (vikin)
tank2_run_frames = []
for i in range(1, 13):  # Từ 1 đến 6
    if i%2==1:
        frame = pygame.image.load(f"Picture\\vikin\\run\\vikin_run{int(i/2)+1}.png").convert_alpha()
    else: pygame.image.load(f"Picture\\vikin\\run\\vikin_run{int(i/2)}.png").convert_alpha()
    frame = pygame.transform.scale(frame, (50, 50))
    tank2_run_frames.append(frame)

# Tải hình nền
background = pygame.image.load("Picture\\Picture2.png").convert_alpha()
background = pygame.transform.scale(background, (MAP_WIDTH, MAP_HEIGHT))

# Tải hình ảnh cho vũ khí của Tank (nhân vật thứ nhất)
projectile_image = pygame.image.load("Picture\\dagger.png").convert_alpha()
projectile_image = pygame.transform.scale(projectile_image, (30, 30))

# Tải hình ảnh cho vũ khí của Tank2 (nhân vật thứ hai)
projectile2_image = pygame.image.load("Picture\\axe.png").convert_alpha()
projectile2_image = pygame.transform.scale(projectile2_image, (30, 30))

# Tải các frame animation cho kẻ thù (aimon)
enemy_run_frames = []
for i in range(1, 3):  # Từ 1 đến 2
    frame = pygame.image.load(f"Picture\\mob\\aimon{i}.png").convert_alpha()
    frame = pygame.transform.scale(frame, (30, 30))
    enemy_run_frames.append(frame)

enemy_image = pygame.image.load("Picture\\mob\\aimon1.png").convert_alpha()
enemy_image = pygame.transform.scale(enemy_image, (30, 30))

# Lớp Camera
class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def apply_rect(self, rect):
        return rect.move(self.camera.topleft)

    def update(self, target1, target2):
        mid_x = (target1.rect.centerx + target2.rect.centerx) / 2
        mid_y = (target1.rect.centery + target2.rect.centery) / 2
        x = -mid_x + WIDTH // 2
        y = -mid_y + HEIGHT // 2
        x = min(0, x)
        y = min(0, y)
        x = max(-(self.width - WIDTH), x)
        y = max(-(self.height - HEIGHT), y)
        self.camera = pygame.Rect(x, y, self.width, self.height)

# Lớp Tank (nhân vật thứ nhất)
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

# Lớp Tank2 (nhân vật thứ hai)
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

# Lớp Projectile (vũ khí)
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

# Lớp Enemy (kẻ thù) - Đã sửa
class Enemy(pygame.sprite.Sprite):
    def __init__(self, camera):  # Nhận camera làm tham số
        super().__init__()
        self.original_image = enemy_image
        self.run_frames = enemy_run_frames
        self.image = self.run_frames[0]
        self.rect = self.image.get_rect()
        self.speed = 1
        
        # Spawn ở các cạnh của camera, cách góc 50-100px
        offset = random.randint(50, 100)  # Khoảng cách ngẫu nhiên từ 50-100px
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
        
        # Đảm bảo enemy không spawn bên ngoài bản đồ
        self.rect.clamp_ip(pygame.Rect(0, 0, MAP_WIDTH, MAP_HEIGHT))
        
        self.frame_index = 0
        self.animation_speed = 15
        self.animation_counter = 0

    def update(self, tank, tank2):  # Nhận cả tank và tank2
        # Tính khoảng cách đến tank và tank2
        dist_to_tank = math.hypot(self.rect.x - tank.rect.x, self.rect.y - tank.rect.y)
        dist_to_tank2 = math.hypot(self.rect.x - tank2.rect.x, self.rect.y - tank2.rect.y)
        
        # Chọn nhân vật gần hơn làm mục tiêu
        if dist_to_tank < dist_to_tank2:
            target = tank
        else:
            target = tank2
        
        # Di chuyển về phía mục tiêu
        if self.rect.x < target.rect.x:
            self.rect.x += self.speed
        elif self.rect.x > target.rect.x:
            self.rect.x -= self.speed
        if self.rect.y < target.rect.y:
            self.rect.y += self.speed
        elif self.rect.y > target.rect.y:
            self.rect.y -= self.speed

        self.animation_counter += 1
        if self.animation_counter >= self.animation_speed:
            self.animation_counter = 0
            self.frame_index = (self.frame_index + 1) % len(self.run_frames)
            self.image = self.run_frames[self.frame_index]

COIN_WIDTH, COIN_HEIGHT = 40, 40

# Lớp đồng xu (giữ nguyên)
class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.coin_frames = [pygame.image.load(f"Picture\\coin\\coin{i}.png") for i in range(1, 8)]
        self.coin_frames = [pygame.transform.scale(frame, (COIN_WIDTH, COIN_HEIGHT)) for frame in self.coin_frames]
        self.frame_index = 0
        self.image = self.coin_frames[self.frame_index]  # animation coin
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.hitbox = pygame.Rect(x - 20, y - 20, 40, 40)
        self.animation_speed = 100  # Đổi frame sau mỗi 100ms
        self.last_update = pygame.time.get_ticks()

    def update(self):
        # Cập nhật animation theo thời gian
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update > self.animation_speed:
            self.frame_index = (self.frame_index + 1) % len(self.coin_frames)  # Chuyển frame
            self.image = self.coin_frames[self.frame_index]  # Cập nhật hình ảnh
            self.last_update = current_time  # Reset thời gian

# Thiết lập các nhóm sprite
all_sprites = pygame.sprite.Group()
projectiles = pygame.sprite.Group()
enemies = pygame.sprite.Group()
coins = pygame.sprite.Group()

# Tạo tank và camera
tank = Tank()
all_sprites.add(tank)
tank2 = Tank2()
all_sprites.add(tank2)
camera = Camera(MAP_WIDTH, MAP_HEIGHT)

# Hàm tải cấp độ - Đã sửa
def load_level(level, camera):  # Thêm tham số camera
    enemies.empty()
    for i in range(level['enemies']):
        enemy = Enemy(camera)  # Truyền camera vào khi tạo enemy
        enemies.add(enemy)
        all_sprites.add(enemy)

# Định nghĩa các cấp độ
levels = [
    {'enemies': 100},
    {'enemies': 150},
    {'enemies': 200},
    {'enemies': 30},
]
current_level = 0
load_level(levels[current_level], camera)  # Truyền camera vào lần đầu

# Thiết lập điểm số
score = 0
font = pygame.font.Font(None, 36)

# Vòng lặp game chính
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    # Cập nhật
    tank.update()
    tank.shoot(enemies)
    tank2.update()
    tank2.shoot(enemies)
    for sprite in all_sprites:
        if isinstance(sprite, Enemy):
            sprite.update(tank, tank2)  # Truyền cả tank và tank2
        else:
            sprite.update()
    camera.update(tank, tank2)

    # Cập nhật đồng xu 
    coins.update()

    for coin in coins:
        if tank.hitbox.colliderect(coin.hitbox) or tank2.hitbox.colliderect(coin.hitbox):
            coin.kill()
            score += 10  # Cộng điểm khi nhặt coin

    # Kiểm tra va chạm
    hits = pygame.sprite.groupcollide(projectiles, enemies, True, True)
    for proj, enemies_hit in hits.items():
        for enemy in enemies_hit:
            coin = Coin(enemy.rect.centerx, enemy.rect.centery)
            all_sprites.add(coin)
            coins.add(coin)

    for enemy in enemies:
        if tank.hitbox.colliderect(enemy.rect) or tank2.hitbox.colliderect(enemy.rect):
            print("Trò chơi kết thúc")
            pygame.quit()
            sys.exit()

    if not enemies:
        current_level += 1
        if current_level < len(levels):
            load_level(levels[current_level], camera)  # Truyền camera khi tải cấp mới
        else:
            print("Bạn đã thắng!")
            pygame.quit()
            sys.exit()

    # Vẽ
    screen.blit(background, camera.camera.topleft)
    
    for sprite in all_sprites:
        screen.blit(sprite.image, camera.apply(sprite))

    # Đã xóa hai dòng vẽ hitbox màu xanh lá cây
    # pygame.draw.rect(screen, (0, 255, 0), camera.apply_rect(tank.hitbox), 2)
    # pygame.draw.rect(screen, (0, 255, 0), camera.apply_rect(tank2.hitbox), 2)
    
    for proj in projectiles:
        pygame.draw.circle(screen, (255, 0, 0), camera.apply(proj).center, 5, 1)

    score_text = font.render(f"Điểm: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    pygame.display.update()
    clock.tick(60)