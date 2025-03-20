import pygame
from pygame.locals import *


class Button:
    def __init__(self, x, y, image, hover_image, scale):
        width = image.get_width()
        height = image.get_height()

        self.image = pygame.transform.scale(
            image, (int(width * scale), int(height * scale))
        )
        self.hover_image = pygame.transform.scale(
            hover_image, (int(width * scale), int(height * scale))
        )
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False

    def draw(self, surface):
        action = False
        pos = pygame.mouse.get_pos()

        # Change image on hover
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


def menu(screen):
    wht = (255, 255, 255)
    blk = (0, 0, 0)

    bg_img = pygame.image.load("Picture/menubg.png").convert()

    ip_img = pygame.image.load("Picture\\button\\button1.png").convert_alpha()
    ip_hover_img = pygame.image.load("Picture\\button\\button2.png").convert_alpha()

    iip_img = pygame.image.load("Picture\\button\\button3.png").convert_alpha()
    iip_hover_img = pygame.image.load("Picture\\button\\button4.png").convert_alpha()

    qt_img = pygame.image.load("Picture\\button\\button5.png").convert_alpha()
    qt_hover_img = pygame.image.load("Picture\\button\\button6.png").convert_alpha()

    ip_but = Button(515, 200, ip_img, ip_hover_img, 0.1)
    iip_but = Button(515, 300, iip_img, iip_hover_img, 0.1)
    qt_but = Button(515, 400, qt_img, qt_hover_img, 0.1)

    def drawtxt(txt, fnt, col, x, y):
        img = fnt.render(txt, True, col)
        screen.blit(img, (x, y))

    run = True
    while run:
        screen.blit(bg_img, (0, 0))

        if ip_but.draw(screen):
            return "1p"
        if iip_but.draw(screen):
            return "2p"
        if qt_but.draw(screen):
            exit()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        pygame.display.update()

    pygame.quit()
