#Import thư viện
import pygame
import random
import math

#Khởi tạo pygame
pygame.init()

#Giao diện màn hình
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tank Battle AZ")
clock = pygame.time.Clock()

#Load hình ảnh, nhớ chỉnh sửa đường dẫn tới hình ảnh của bạn
tank_img = pygame.image.load("Picture\Tank_tries.png")
enemy_img = pygame.image.load("Picture\enemy_tries.png")
bullet_img = pygame.image.load("Picture\Bullet.jpg")
background_img = pygame.image.load(r"Picture\background.jpg")

# Lớp xe tăng
class Tank:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.speed = 3
        self.bullets = []
    
    def move(self, keys):
        if keys[pygame.K_w]:
            tank_img = pygame.transform.rotate(original_tank, 0)    # Hướng lên
        if keys[pygame.K_s]:
            y += speed
            tank_img = pygame.transform.rotate(original_tank, 180)  # Hướng xuống
        if keys[pygame.K_a]:
            self.angle += 5
        if keys[pygame.K_d]:
            self.angle -= 5
    
    def shoot(self):
        bullet = Bullet(self.x, self.y, self.angle)
        self.bullets.append(bullet)
    
    def draw(self, screen):
        rotated_tank = pygame.transform.rotate(tank_img, self.angle)
        rect = rotated_tank.get_rect(center=(self.x, self.y))
        screen.blit(rotated_tank, rect.topleft)
        for bullet in self.bullets:
            bullet.draw(screen)

# Lớp đạn
class Bullet:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 7
    
    def move(self):
        self.x += self.speed * math.cos(math.radians(self.angle))
        self.y -= self.speed * math.sin(math.radians(self.angle))
    
    def draw(self, screen):
        screen.blit(bullet_img, (self.x, self.y))

# Lớp xe tăng địch
class EnemyTank:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def draw(self, screen):
        screen.blit(enemy_img, (self.x, self.y))

# Khởi tạo xe tăng
player_tank = Tank(WIDTH // 2, HEIGHT // 2)
enemies = [EnemyTank(random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50)) for _ in range(5)]

# Vòng lặp game
running = True
while running:
    screen.fill((50, 50, 50))
    keys = pygame.key.get_pressed()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player_tank.shoot()
    
    player_tank.move(keys)
    for bullet in player_tank.bullets:
        bullet.move()
    
    player_tank.draw(screen)
    for enemy in enemies:
        enemy.draw(screen)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
