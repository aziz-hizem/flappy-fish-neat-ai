"""
Train an AI to play Flappy Fish with NEAT (NeuroEvolution of Augmenting Topologies).

Each generation, 50 fish each controlled by their own neural network play at the same time.
The fish that survive longest and pass the most pipes are selected and mutated into the next
generation, until one reaches the fitness threshold set in config-feedforward.txt.

Press E or close the window to stop.
"""
import os
import sys

import neat
import pygame

from game import BASE_DIR, FLOOR_Y, FPS, HEIGHT, PIPE_SPAWN_X, WIDTH, Base, Fish, Pipe, draw_window

MAX_GENERATIONS = 50
# A perfect network would otherwise play forever and the generation would never end
MAX_SCORE_PER_ROUND = 50
generation = 0


def eval_genomes(genomes, config):
    """Play one round with every genome of the generation and score their fitness."""
    global generation
    generation += 1

    # One fish, network and genome per individual, kept at matching indexes
    nets, ge, fishes = [], [], []
    for _, genome in genomes:
        genome.fitness = 0
        nets.append(neat.nn.FeedForwardNetwork.create(genome, config))
        fishes.append(Fish(230, 350))
        ge.append(genome)

    clock = pygame.time.Clock()
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    score = 0
    base = Base(FLOOR_Y)
    pipes = [Pipe(PIPE_SPAWN_X)]

    def remove(index):
        nets.pop(index)
        ge.pop(index)
        fishes.pop(index)

    while fishes and score < MAX_SCORE_PER_ROUND:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_e):
                pygame.quit()
                sys.exit()

        # Look at the next pipe once the fish has passed the first one
        pipe_ind = 0
        if len(pipes) > 1 and fishes[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
            pipe_ind = 1

        for i, fish in enumerate(fishes):
            ge[i].fitness += 0.1  # small reward for staying alive
            fish.move()

            # Inputs: fish height, distance to the top pipe's opening, distance to the bottom pipe
            output = nets[i].activate((
                fish.y,
                abs(fish.y - pipes[pipe_ind].height),
                abs(fish.y - pipes[pipe_ind].bottom),
            ))
            if output[0] > 0.5:
                fish.jump()

        add_pipe = False
        for pipe in pipes:
            pipe.move()

            # Iterate backwards so removing a fish doesn't skip the next one
            for i in reversed(range(len(fishes))):
                if pipe.collide(fishes[i]):
                    ge[i].fitness -= 1  # penalty for hitting a pipe
                    remove(i)

            if fishes and not pipe.passed and pipe.x < fishes[0].x:
                pipe.passed = True
                add_pipe = True

        if add_pipe:
            score += 1
            for genome in ge:
                genome.fitness += 5  # big reward for passing a pipe
            pipes.append(Pipe(PIPE_SPAWN_X))
        pipes = [pipe for pipe in pipes if not pipe.is_off_screen()]

        for i in reversed(range(len(fishes))):
            if fishes[i].hit_floor_or_ceiling():
                remove(i)

        base.move()
        draw_window(win, fishes, pipes, base, score, generation, len(fishes))


def run(config_path, generations=MAX_GENERATIONS):
    config = neat.config.Config(
        neat.DefaultGenome, neat.DefaultReproduction,
        neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path,
    )

    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    population.add_reporter(neat.StatisticsReporter())

    winner = population.run(eval_genomes, generations)
    print(f"\nBest genome:\n{winner}")
    return winner


if __name__ == "__main__":
    run(os.path.join(BASE_DIR, "config-feedforward.txt"))
