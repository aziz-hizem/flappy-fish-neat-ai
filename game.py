"""
Shared Flappy Fish game objects, used by both play.py (human player) and train_ai.py (NEAT).
"""
import os
import random

import pygame

pygame.init()
pygame.font.init()
pygame.display.set_caption("Flappy Fish")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

WIDTH = 500
HEIGHT = 780
FPS = 30
FLOOR_Y = 700
PIPE_SPAWN_X = 600


def load_image(name):
    return pygame.transform.scale2x(pygame.image.load(os.path.join(ASSETS_DIR, name)))


FISH_IMGS = [load_image(f"fish{x}.png") for x in range(1, 4)]
PIPE_IMG = load_image("pipe.png")
BASE_IMG = load_image("base.png")
BG_IMG = load_image("bg.png")

STAT_FONT = pygame.font.SysFont("comicsans", 25)


class Fish:
    IMGS = FISH_IMGS
    MAX_ROTATION = 25
    ROT_VEL = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        self.vel = -4.5
        self.tick_count = 0  # frames since the last jump
        self.height = self.y

    def move(self):
        self.tick_count += 1

        # displacement for downward acceleration
        d = self.vel * self.tick_count + 0.5 * self.tick_count ** 2

        # terminal velocity
        if d >= 16:
            d = 16
        if d < 0:
            d -= 2  # tweak for a higher/lower jump

        self.y += d

        if d < 0 or self.y < self.height + 50:  # tilt up
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:  # tilt down
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    def draw(self, win):
        self.img_count += 1

        # cycle through the three swim frames
        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME * 2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME * 3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME * 4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME * 4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        # no flapping while diving
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME * 2

        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)

    def hit_floor_or_ceiling(self):
        return self.y + self.img.get_height() - 10 >= FLOOR_Y or self.y < -50


class Pipe:
    GAP = 200
    VEL = 5

    def __init__(self, x):
        self.x = x
        self.height = 0
        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BOTTOM = PIPE_IMG
        self.passed = False
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= self.VEL

    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, fish):
        """Pixel-perfect collision using masks."""
        fish_mask = fish.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - fish.x, self.top - round(fish.y))
        bottom_offset = (self.x - fish.x, self.bottom - round(fish.y))

        return bool(fish_mask.overlap(bottom_mask, bottom_offset) or fish_mask.overlap(top_mask, top_offset))

    def is_off_screen(self):
        return self.x + self.PIPE_TOP.get_width() < 0


class Base:
    VEL = Pipe.VEL  # scrolls at the same speed as the pipes
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        # two copies leapfrog each other for endless scrolling
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


def draw_window(win, fishes, pipes, base, score, gen=None, alive=None):
    win.blit(BG_IMG, (0, 0))
    for pipe in pipes:
        pipe.draw(win)

    text = STAT_FONT.render(f"Score : {score}", 1, "White")
    win.blit(text, (WIDTH - 10 - text.get_width(), 10))

    if gen is not None:
        win.blit(STAT_FONT.render(f"Gen : {gen}", 1, "White"), (10, 10))
    if alive is not None:
        win.blit(STAT_FONT.render(f"Alive : {alive}", 1, "White"), (10, 40))

    base.draw(win)
    for fish in fishes:
        fish.draw(win)
    pygame.display.update()
