import pygame
from pygame.locals import *
import sys
import random
import math

# Khởi tạo Pygame
pygame.init()

# Thiết lập cửa sổ game
WIDTH, HEIGHT = 1500, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Xe Tăng AZ Replica")

# Thiết lập đồng hồ để quản lý FPS
clock = pygame.time.Clock()

# Màu sắc
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Thiết lập kích thước bản đồ lớn
MAP_WIDTH = 7000  # Gấp đôi chiều rộng màn hình
MAP_HEIGHT = 7000  # Gấp đôi chiều cao màn hình

# Tải hình ảnh
tank_image = pygame.image.load("Picture\\rouge\\rouge.png").convert_alpha()
tank_size = 40
tank_image = pygame.transform.scale(tank_image, (tank_size, tank_size))

background = pygame.image.load("Picture\\Picture2.png").convert_alpha()
background = pygame.transform.scale(background, (MAP_WIDTH, MAP_HEIGHT))  # Scale background theo map

projectile_image = pygame.image.load("Picture\\dagger.png").convert_alpha()
projectile_image = pygame.transform.scale(projectile_image, (30, 30))

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

    def update(self, target):
        x = -target.rect.centerx + WIDTH // 2
        y = -target.rect.centery + HEIGHT // 2
        x = min(0, x)  # Giới hạn trái
        y = min(0, y)  # Giới hạn trên
        x = max(-(self.width - WIDTH), x)  # Giới hạn phải
        y = max(-(self.height - HEIGHT), y)  # Giới hạn dưới
        self.camera = pygame.Rect(x, y, self.width, self.height)

# Lớp xe tăng
class Tank(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.original_image = tank_image  # Giả sử tank_image đã được định nghĩa trước
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.center = (MAP_WIDTH // 2, MAP_HEIGHT // 2)  # MAP_WIDTH và MAP_HEIGHT cần được định nghĩa
        self.hitbox = pygame.Rect(0, 0, 40, 40)
        self.hitbox.center = self.rect.center
        self.speed = 2
        self.flipped = False
        self.shoot_cooldown = 0  # Thời gian cooldown hiện tại
        self.shoot_cooldown_time = 180  # 3 giây * 60 FPS = 180 frames

    def update(self):
        keys = pygame.key.get_pressed()
        move_vector = pygame.math.Vector2(0, 0)

        # Điều khiển di chuyển
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

        # Chuẩn hóa vector di chuyển và áp dụng tốc độ
        if move_vector.length() > 0:
            move_vector = move_vector.normalize() * self.speed

        self.rect.x += move_vector.x
        self.rect.y += move_vector.y

        # Giới hạn xe tăng trong màn hình
        self.rect.clamp_ip(pygame.Rect(0, 0, MAP_WIDTH, MAP_HEIGHT))

        # Cập nhật hình ảnh xe tăng (lật nếu cần)
        self.image = pygame.transform.flip(self.original_image, True, False) if self.flipped else self.original_image
        self.rect = self.image.get_rect(center=self.rect.center)
        self.hitbox.center = self.rect.center

        # Giảm thời gian cooldown mỗi frame
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def shoot(self, enemies):
        # Chỉ cho phép bắn khi cooldown bằng 0
        if self.shoot_cooldown > 0:
            return

        # Tìm kẻ địch gần nhất
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

        # Bắn nếu có kẻ địch trong tầm
        if closest_enemy and min_distance <= 200:
            print(f"Bắn đạn! Khoảng cách: {min_distance:.2f}")
            proj = Projectile(self.rect.centerx, self.rect.centery, closest_enemy)  # Giả sử Projectile đã được định nghĩa
            projectiles.add(proj)  # Giả sử projectiles là một Sprite Group
            all_sprites.add(proj)  # Giả sử all_sprites là một Sprite Group
            self.shoot_cooldown = self.shoot_cooldown_time  # Đặt lại cooldown sau khi bắn

# Lớp đạn
class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, target):
        super().__init__()
        self.image = projectile_image
        self.original_image = self.image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 2
        self.angle = 0
        self.turn_speed = 5
        self.target = target
        self.start_time = pygame.time.get_ticks()  # Lưu thời điểm đạn được bắn

    def update(self):
        self.angle += self.turn_speed
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        
        if self.target and self.target.alive():
            dx = self.target.rect.centerx - self.rect.centerx  # Sửa lỗi tính toán dx
            dy = self.target.rect.centery - self.rect.centery
            distance = math.hypot(dx, dy)
            if distance > 0:
                self.rect.x += self.speed * dx / distance
                self.rect.y += self.speed * dy / distance
        
        # Xóa nếu ra khỏi map
        if not pygame.Rect(0, 0, MAP_WIDTH, MAP_HEIGHT).contains(self.rect):
            self.kill()
        
        # Xóa đạn sau 3 giây
        if pygame.time.get_ticks() - self.start_time > 3000:  # 3000 ms = 3 giây
            self.kill()

# Lớp kẻ thù
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = enemy_image
        self.rect = self.image.get_rect()
        self.speed = 1
        edge = random.choice(['left', 'right', 'top', 'bottom'])
        if edge == 'left':
            self.rect.x = -self.rect.width
            self.rect.y = random.randint(0, MAP_HEIGHT)
        elif edge == 'right':
            self.rect.x = MAP_WIDTH
            self.rect.y = random.randint(0, MAP_HEIGHT)
        elif edge == 'top':
            self.rect.x = random.randint(0, MAP_WIDTH)
            self.rect.y = -self.rect.height
        elif edge == 'bottom':
            self.rect.x = random.randint(0, MAP_WIDTH)
            self.rect.y = MAP_HEIGHT

    def update(self, tank):
        if self.rect.x < tank.rect.x:
            self.rect.x += self.speed
        elif self.rect.x > tank.rect.x:
            self.rect.x -= self.speed
        if self.rect.y < tank.rect.y:
            self.rect.y += self.speed
        elif self.rect.y > tank.rect.y:
            self.rect.y -= self.speed

# Thiết lập các nhóm sprite
all_sprites = pygame.sprite.Group()
projectiles = pygame.sprite.Group()
enemies = pygame.sprite.Group()

# Tạo xe tăng và camera
tank = Tank()
all_sprites.add(tank)
camera = Camera(MAP_WIDTH, MAP_HEIGHT)

# Hàm tải cấp độ
def load_level(level):
    enemies.empty()
    for i in range(level['enemies']):
        enemy = Enemy()
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
load_level(levels[current_level])

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
    for sprite in all_sprites:
        if isinstance(sprite, Enemy):
            sprite.update(tank)
        else:
            sprite.update()
    camera.update(tank)  # Cập nhật camera theo tank

    # Kiểm tra va chạm
    hits = pygame.sprite.groupcollide(projectiles, enemies, True, True)
    for proj, enemies_hit in hits.items():
        for enemy in enemies_hit:
            score += 10

    for enemy in enemies:
        if tank.hitbox.colliderect(enemy.rect):
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

    # Vẽ
    screen.blit(background, camera.camera.topleft)  # Vẽ background với offset camera
    
    for sprite in all_sprites:
        screen.blit(sprite.image, camera.apply(sprite))

    # Vẽ hitbox và debug
    pygame.draw.rect(screen, (0, 255, 0), camera.apply_rect(tank.hitbox), 2)
    for proj in projectiles:
        pygame.draw.circle(screen, (255, 0, 0), camera.apply(proj).center, 5, 1)

    # Vẽ điểm số
    score_text = font.render(f"Điểm: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    pygame.display.update()
    clock.tick(60)