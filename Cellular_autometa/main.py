# -*- coding: utf-8 -*-
import pygame, sys, time
import numpy as np
from pygame.locals import *

# Matrix width and matrix height
WIDTH = 80
HEIGHT = 40

# A global variable that records mouse button conditions
pygame.button_down = False

# A matrix that records the game world
# pygame.world=np.zeros((HEIGHT,WIDTH))
pygame.world=np.random.randint(0,2, (HEIGHT, WIDTH))
print(pygame.world)
# Create a Cell class to facilitate Cell drawing
class Cell(pygame.sprite.Sprite):

    size = 10

    def __init__(self, position):

        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.Surface([self.size, self.size])

        # Fill in the white
        self.image.fill((255,255,255))

        # Creates a rectangle with the upper-left corner as the anchor point
        self.rect = self.image.get_rect()
        self.rect.topleft = position

# Drawing function
def draw():
    screen.fill((0,0,0))
    for sp_col in range(pygame.world.shape[1]):
        for sp_row in range(pygame.world.shape[0]):
            if pygame.world[sp_row][sp_col]:
                new_cell = Cell((sp_col * Cell.size,sp_row * Cell.size))
                print("draw right")
                screen.blit(new_cell.image,new_cell.rect)

# Update the map according to cell update rules
def next_generation():
    nbrs_count = sum(np.roll(np.roll(pygame.world, i, 0), j, 1)
                 for i in (-1, 0, 1) for j in (-1, 0, 1)
                 if (i != 0 or j != 0))

    pygame.world = (nbrs_count == 3) | ((pygame.world == 1) & (nbrs_count == 2)).astype('int')

# init Map
def init():
    # pygame.world.fill(0)
    pygame.world=np.random.randint(0,2, (HEIGHT, WIDTH))

    draw()
    return 'Stop'

# Stop operation
def stop():
    for event in pygame.event.get():
        # if len(event) > 0:
        print(event)
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        if event.type == KEYDOWN and event.key == K_RETURN:
            return 'Move'

        if event.type == KEYDOWN and event.key == K_r:
            return 'Reset'

        if event.type == MOUSEBUTTONDOWN:
            pygame.button_down = True
            pygame.button_type = event.button

        if event.type == MOUSEBUTTONUP:
            pygame.button_down = False

        if pygame.button_down:
            mouse_x, mouse_y = pygame.mouse.get_pos()

            sp_col = int(mouse_x / Cell.size);
            sp_row = int(mouse_y / Cell.size);

            if pygame.button_type == 1: # The left mouse button
                pygame.world[sp_row][sp_col] = 1
            elif pygame.button_type == 3: # The right mouse button
                pygame.world[sp_row][sp_col] = 0
            draw()

    return 'Stop'

# Timer, control frame rate
pygame.clock_start = 0


# Evolution operations
def move():
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN and event.key == K_SPACE:
            return 'Stop'
        if event.type == KEYDOWN and event.key == K_r:
            return 'Reset'
        if event.type == MOUSEBUTTONDOWN:
            pygame.button_down = True
            pygame.button_type = event.button

        if event.type == MOUSEBUTTONUP:
            pygame.button_down = False

        if pygame.button_down:
            mouse_x, mouse_y = pygame.mouse.get_pos()

            sp_col = mouse_x // Cell.size;
            sp_row = mouse_y // Cell.size;
 
            print(sp_col)
            print(sp_row)
            print("before:", pygame.world[sp_row][sp_col])

            if pygame.button_type == 1:
                pygame.world[sp_row][sp_col] = 1
            elif pygame.button_type == 3:
                pygame.world[sp_row][sp_col] = 0
            print("after:", pygame.world[sp_row][sp_col])
            draw()


    if time.clock() - pygame.clock_start > 0.02:
        next_generation()
        draw()
        pygame.clock_start = time.clock()

    return 'Move'



if __name__ == '__main__':

    # init, stop, move
    state_actions = {
            'Reset': init,
            'Stop': stop,
            'Move': move
        }
    state = 'Reset'

    pygame.init()
    pygame.display.set_caption('Conway\'s Game of Life')

    screen = pygame.display.set_mode((WIDTH * Cell.size, HEIGHT * Cell.size))

    while True:

        state = state_actions[state]()
        pygame.display.update()