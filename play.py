"""
Play Flappy Fish yourself.

Controls: SPACE / UP to swim up, E to quit.
"""
import glob
import os

import pygame

from game import BASE_DIR, FLOOR_Y, FPS, HEIGHT, PIPE_SPAWN_X, WIDTH, Base, Fish, Pipe, draw_window


def start_music():
    """Loop the first mp3 found in music/, if any (the folder is not part of the repository)."""
    tracks = sorted(glob.glob(os.path.join(BASE_DIR, "music", "*.mp3")))
    if tracks:
        pygame.mixer.music.load(tracks[0])
        pygame.mixer.music.play(-1)


def play_round(win, clock):
    """Play until the fish crashes. Returns False if the player quit."""
    score = 0
    fish = Fish(230, 350)
    base = Base(FLOOR_Y)
    pipes = [Pipe(PIPE_SPAWN_X)]

    while True:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    return False
                if event.key in (pygame.K_SPACE, pygame.K_UP):
                    fish.jump()

        fish.move()

        add_pipe = False
        for pipe in pipes:
            if pipe.collide(fish):
                return True
            if not pipe.passed and pipe.x < fish.x:
                pipe.passed = True
                add_pipe = True
            pipe.move()

        if add_pipe:
            score += 1
            pipes.append(Pipe(PIPE_SPAWN_X))
        pipes = [pipe for pipe in pipes if not pipe.is_off_screen()]

        if fish.hit_floor_or_ceiling():
            return True

        base.move()
        draw_window(win, [fish], pipes, base, score)


def main():
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    game_over_font = pygame.font.SysFont("pixellarri", 90)
    game_over_text = game_over_font.render("GAME OVER !", 1, "White")
    start_music()

    while play_round(win, clock):
        win.blit(game_over_text, (WIDTH / 2 - game_over_text.get_width() / 2, HEIGHT / 2 - game_over_text.get_height() / 2))
        pygame.display.update()
        pygame.time.delay(2000)

    pygame.quit()


if __name__ == "__main__":
    main()
