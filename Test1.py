import pygame
from pygame.locals import *
import sys
import random
import math

# Khởi tạo Pygame
pygame.init()

# Thiết lập cửa sổ game
WIDTH, HEIGHT = 600, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Xe Tăng AZ Replica")

# Thiết lập đồng hồ để quản lý FPS
clock = pygame.time.Clock()

# Màu sắc
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Tải hình ảnh
tank_image = pygame.image.load("Picture\\rouge\\rouge.png").convert_alpha()
tank_size = 60
tank_image = pygame.transform.scale(tank_image, (tank_size, tank_size))

background = pygame.image.load("Picture\\background_grass.png").convert_alpha()

projectile_image = pygame.Surface((10, 10))
projectile_image.fill((255, 0, 0))

enemy_image = pygame.Surface((40, 40))
enemy_image.fill((255, 0, 0))

# Lớp xe tăng (giữ nguyên)
class Tank(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.original_image = tank_image
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.speed = 3
        self.flipped = False  # Trạng thái lật ảnh

    def update(self):
        keys = pygame.key.get_pressed()

        # Xử lý lật ảnh và di chuyển trái khi nhấn 'A'
        if keys[K_a]:
            self.flipped = True  # Lật ảnh
            self.rect.x -= self.speed  # Di chuyển trái

        # Khi không nhấn 'A', không lật ảnh
        else:
            self.flipped = False

        # Di chuyển phải khi nhấn 'D'
        if keys[K_d]:
            self.rect.x += self.speed  # Di chuyển phải

        # Di chuyển lên khi nhấn 'W'
        if keys[K_w]:
            self.rect.y -= self.speed  # Di chuyển lên

        # Di chuyển xuống khi nhấn 'S'
        if keys[K_s]:
            self.rect.y += self.speed  # Di chuyển xuống

        # Giới hạn trong màn hình
        self.rect.clamp_ip(screen.get_rect())

        # Xác định ảnh cơ sở (gốc hay lật)
        self.image = pygame.transform.flip(self.original_image, True, False) if self.flipped else self.original_image
        # Không cần xoay nữa, nên không dùng self.angle
        self.rect = self.image.get_rect(center=self.rect.center)

# Lớp đạn (giữ nguyên)
class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, angle):
        super().__init__()
        self.image = projectile_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 10
        self.angle = angle

    def update(self):
        radian_angle = math.radians(self.angle)
        self.rect.x += self.speed * math.cos(radian_angle)
        self.rect.y -= self.speed * math.sin(radian_angle)
        if not screen.get_rect().contains(self.rect):
            self.kill()

# Lớp kẻ thù (sửa đổi để xuất hiện từ ngoài màn hình)
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = enemy_image
        self.rect = self.image.get_rect()
        self.speed = 1
        
        # Chọn ngẫu nhiên một cạnh màn hình để xuất hiện
        edge = random.choice(['left', 'right', 'top', 'bottom'])
        if edge == 'left':
            self.rect.x = -self.rect.width  # Ngoài bên trái
            self.rect.y = random.randint(0, HEIGHT)
        elif edge == 'right':
            self.rect.x = WIDTH  # Ngoài bên phải
            self.rect.y = random.randint(0, HEIGHT)
        elif edge == 'top':
            self.rect.x = random.randint(0, WIDTH)
            self.rect.y = -self.rect.height  # Ngoài phía trên
        elif edge == 'bottom':
            self.rect.x = random.randint(0, WIDTH)
            self.rect.y = HEIGHT  # Ngoài phía dưới

    def update(self, tank):
        # Di chuyển về phía xe tăng
        if self.rect.x < tank.rect.x:
            self.rect.x += self.speed
        elif self.rect.x > tank.rect.x:
            self.rect.x -= self.speed
        if self.rect.y < tank.rect.y:
            self.rect.y += self.speed
        elif self.rect.y > tank.rect.y:
            self.rect.y -= self.speed

# Thời gian spqwn coin
coin_spawn_time = 0
coin_spawn_interval = 60 * 5

# Hàm random đồng xu    
def spawn_coin():
    coin = Coin()
    all_sprites.add(coin)
    coins.add(coin)

COIN_WIDTH, COIN_HEIGHT = 40, 40

# Lớp đồng xu (giữ nguyên)
class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.coin_frames = [pygame.image.load(f"Picture\\coin\\coin{i}.png") for i in range(1, 8)]
        self.coin_frames = [pygame.transform.scale(frame, (COIN_WIDTH, COIN_HEIGHT)) for frame in self.coin_frames]
        self.frame_index = 0
        self.image = self.coin_frames[self.frame_index] #animation coin
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = random.randint(0, HEIGHT - self.rect.height)
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

# Tạo xe tăng
tank = Tank()
all_sprites.add(tank)

# Hàm tải cấp độ (giữ nguyên)
def load_level(level):
    enemies.empty()
    for i in range(level['enemies']):
        enemy = Enemy()  # Không cần truyền x, y nữa vì đã xử lý trong Enemy
        enemies.add(enemy)
        all_sprites.add(enemy)

# Định nghĩa các cấp độ
levels = [
    {'enemies': 5},
    {'enemies': 10},
    {'enemies': 15}
]
current_level = 0
load_level(levels[current_level])

# Thiết lập điểm số
score = 0
font = pygame.font.Font(None, 36)

# Thời gian chờ bắn lại
shoot_cooldown = 0

# Vòng lặp game chính
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == KEYDOWN:
            if event.key == K_SPACE and shoot_cooldown == 0:
                proj = Projectile(tank.rect.centerx, tank.rect.centery, tank.angle)
                projectiles.add(proj)
                all_sprites.add(proj)
                shoot_cooldown = 30
    if shoot_cooldown > 0:
        shoot_cooldown -= 1

    # Sinh ra đồng xu ngẫu nhiên
    coin_spawn_time += 1
    if coin_spawn_time >= coin_spawn_interval:
        spawn_coin()
        coin_spawn_time = 0

    # Cập nhật tất cả sprite
    tank.update()
    projectiles.update()
    for enemy in enemies:
        enemy.update(tank)

    # Cập nhật đồng xu 
    coins.update()

    # Kiểm tra va chạm giữa xe tăng và đồng xu
    coin_hits = pygame.sprite.spritecollide(tank, coins, True)
    for coin in coin_hits:
        score += 5    

    # Kiểm tra va chạm
    hits = pygame.sprite.groupcollide(projectiles, enemies, True, True)
    for proj, enemies_hit in hits.items():
        for enemy in enemies_hit:
            score += 10

    if pygame.sprite.spritecollide(tank, enemies, False):
        print("Trò chơi kết thúc")
        pygame.quit()
        sys.exit()

    if not enemies:
        current_level += 1
        if current_level < len(levels):
            load_level(levels[current_level])
        else:
            print("Bạn đã thắng!")
            pygame.quit()
            sys.exit()

    # Vẽ mọi thứ lên màn hình
    screen.blit(background, (0, 0))
    all_sprites.draw(screen)

    # Hiển thị điểm số
    score_text = font.render(f"Điểm: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    pygame.display.update()
    clock.tick(60)