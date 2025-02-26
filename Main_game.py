import pygame
import math

# Khởi tạo pygame
pygame.init()

# Cài đặt màn hình
WIDTH, HEIGHT = 600, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Xe tăng di chuyển theo hướng")

# Màu sắc
WHITE = (255, 255, 255)

# Tải hình ảnh xe tăng (thay đổi đường dẫn tới file ảnh của bạn)
tank_image = pygame.image.load("AZ_tank_by_gamer\Picture\Tank_tries.png").convert_alpha()
tank_size = 50
tank_image = pygame.transform.scale(tank_image, (tank_size, tank_size))  # Thay đổi kích thước nếu cần

# Xe tăng
tank_x, tank_y = WIDTH // 2, HEIGHT // 2
angle = 0  # Góc quay của xe (tính theo độ)
speed = 5
turn_speed = 5  # Tốc độ xoay

# Vòng lặp game
running = True
while running:
    pygame.time.delay(30)
    
    # Xử lý sự kiện
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Lấy phím bấm
    keys = pygame.key.get_pressed()

    # Xoay trái/phải
    if keys[pygame.K_a]:
        angle += turn_speed  # Xoay ngược chiều kim đồng hồ
    if keys[pygame.K_d]:
        angle -= turn_speed  # Xoay theo chiều kim đồng hồ

    # Tính toán hướng di chuyển
    radian_angle = math.radians(angle)  # Chuyển đổi độ thành radian
    if keys[pygame.K_w]:  # Tiến lên
        tank_x += speed * math.cos(radian_angle)
        tank_y -= speed * math.sin(radian_angle)
    if keys[pygame.K_s]:  # Lùi lại
        tank_x -= speed * math.cos(radian_angle)
        tank_y += speed * math.sin(radian_angle)

    # Giới hạn xe tăng trong màn hình 
    tank_x = max(tank_size // 2, min(WIDTH - tank_size // 2, tank_x))
    tank_y = max(tank_size // 2, min(HEIGHT - tank_size // 2, tank_y))

    # Vẽ lại màn hình
    screen.fill(WHITE)

    # Xoay và vẽ xe tăng
    rotated_tank = pygame.transform.rotate(tank_image, angle)
    rect = rotated_tank.get_rect(center=(tank_x, tank_y))

    # Hiển thị xe tăng
    screen.blit(rotated_tank, rect.topleft)
    
    pygame.display.update()

pygame.quit()