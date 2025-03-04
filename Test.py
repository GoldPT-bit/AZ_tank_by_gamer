import pygame
import sys

# Khởi tạo Pygame
pygame.init()

WIDTH, HEIGHT = 600, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Tải hai hình ảnh (thay đường dẫn bằng đường dẫn thực tế trên máy của bạn)
image_A = pygame.image.load("Picture\\rouge.png")  # Đường dẫn đến ảnh A.png
imgge_A_size = 40
image_A = pygame.transform.scale(image_A, (imgge_A_size, imgge_A_size))
image_B = pygame.transform.flip(image_A, True, False)
# Điều chỉnh kích thước hình ảnh (ví dụ: 100x100 pixel)

# Biến lưu hình ảnh hiện tại (mặc định là A.png)
current_image = image_A

# Vòng lặp chính
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # Thoát khi nhấn nút đóng cửa sổ
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:  # Khi nhấn phím
            if event.key == pygame.K_a:  # Nhấn phím 'A'
                current_image = image_A
            elif event.key == pygame.K_d:  # Nhấn phím 'D'
                current_image = image_B

    # Xóa màn hình bằng màu đen
    screen.fill((0, 0, 0))
    # Hiển thị hình ảnh hiện tại ở giữa màn hình
    screen.blit(current_image, (350, 250))
    # Cập nhật màn hình
    pygame.display.flip()

    # Giới hạn tốc độ khung hình (FPS)
    clock.tick(60)