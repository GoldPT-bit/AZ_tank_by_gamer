
set
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = enemy_image
        self.rect = self.image.get_rect()
        self.speed = 1
        edge = random.choice(['left', 'right', 'top', 'bottom'])
        if edge == 'left':
            self.rect.x = -self.rect.width
            self.rect.y = random.randint(0, HEIGHT)
        elif edge == 'right':
            self.rect.x = WIDTH
            self.rect.y = random.randint(0, HEIGHT)
        elif edge == 'top':
            self.rect.x = random.randint(0, WIDTH)
            self.rect.y = -self.rect.height
        elif edge == 'bottom':
            self.rect.x = random.randint(0, WIDTH)
            self.rect.y = HEIGHT

    def update(self, tank):
        if self.rect.x < tank.rect.x:
            self.rect.x += self.speed
        elif self.rect.x > tank.rect.x:
            self.rect.x -= self.speed
        if self.rect.y < tank.rect.y:
            self.rect.y += self.speed
        elif self.rect.y > tank.rect.y:
            self.rect.y -= self.speed
