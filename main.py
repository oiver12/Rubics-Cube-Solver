# 
# Author: Kenneth Hung
# This program will solve the cube using an optimized F2L algorithm ONLY GRAPHICALLY, no arduino!
# This is the file that runs the solver, and displays the cube graphically using PyGame
# Run this file for graphical solve w/o arduino
#




# Import and initialize the pygame library
import pygame
import sys
from rectangle import rectangle
from square import square
from button import button
import rubics_cube as rc
import kociemba
import time

# colors
white = ((255,255,255))
blue = ((0,0,255))
green = ((0,255,0))
red = ((255,0,0))
orange = ((255,150,0))
yellow = ((255,255,0))

black = ((0,0,0))
gray = ((192,192,192))
background_color = ((170,225,240))


pygame.init()
surface = pygame.display.set_mode([1000, 600])
pygame.display.set_caption('Rubik\'s Cube Solver') 
surface.fill(background_color)



def display_text(surface, color, x, y, size, str):

    font = pygame.font.SysFont('Calibri', size) 
    
    # create a text suface object, 
    # on which text is drawn on it. 
    text = font.render(str, True, color) 
    textRect = text.get_rect()  
    
    # set the center of the rectangular object. 
    textRect.center = (x, y) 
    surface.blit(text, textRect) 

def getSideColor(char):
    if char == 'y':
        return 'U'
    elif char == 'g':
        return 'R'
    elif char == 'r':
        return 'F'
    elif char == 'w':
        return 'D'
    elif char == 'b':
        return 'L'
    elif char == 'o':
        return 'B'

def solve(cube: rc.rubics_cube):
    cube_string = ""
    cube_def = []
    yellowSide = cube.char_cube[5]
    whiteSide = cube.char_cube[4]
    blueSide = cube.char_cube[0]
    redSide = cube.char_cube[1]
    greenSide = cube.char_cube[2]
    orangeSide = cube.char_cube[3]
    for row in yellowSide:
        for color in row:
            cube_def.append(getSideColor(color))
    for row in greenSide:
        for color in row:
            cube_def.append(getSideColor(color))
    for row in redSide:
        for color in row:
            cube_def.append(getSideColor(color))
    for row in whiteSide:
        for color in row:
            cube_def.append(getSideColor(color))
    for row in blueSide:
        for color in row:
            cube_def.append(getSideColor(color))
    for row in orangeSide:
        for color in row:
            cube_def.append(getSideColor(color))
    
    cube_string = ''.join(cube_def)
    print(cube_string)
    if not(cube.is_cube_solved()):
        solve_steps = kociemba.solve(cube_string)
    else: 
        solve_steps = []
    
    totalSteps = 0
    totalSteps = execute_steps(cube, solve_steps)
    print(solve_steps)
    return totalSteps

def execute_steps(cube: rc.rubics_cube, solve_steps):
    total_steps = 0
    i = 0
    while i < len(solve_steps):
        time.sleep(0.1)
        turn: str = solve_steps[i]
        if turn == ' ':
            i += 1
            continue
        assert(turn.isalpha())
        if len(solve_steps) > i+1 and solve_steps[i+1] == '2':
            turn += '2'
            i += 1
        if len(solve_steps) > i+1 and solve_steps[i+1] == '\'':
            turn += '\''
            i += 1
        i += 1
        if turn == 'U':
            cube.up()
            total_steps+=1
        elif turn == 'U2':
            cube.up()
            cube.up()
            total_steps+=2
        elif turn == 'U\'':
            cube.up_prime()
            total_steps+=1
        elif turn == 'D':
            cube.down()
            total_steps+=1
        elif turn == 'D2':
            cube.down()
            cube.down()
            total_steps+=2
        elif turn == 'D\'':
            cube.down_prime()
            total_steps+=1
        elif turn == 'L':
            cube.left()
            total_steps+=1
        elif turn == 'L2':
            cube.left()
            cube.left()
            total_steps+=2
        elif turn == 'L\'':
            cube.left_prime()
            total_steps+=1
        elif turn == 'R':
            cube.right()
            total_steps+=1
        elif turn == 'R2':
            cube.right()
            cube.right()
            total_steps+=2
        elif turn == 'R\'':
            cube.right_prime()
            total_steps+=1
        elif turn == 'F':
            cube.front()
            total_steps+=1
        elif turn == 'F2':
            cube.front()
            cube.front()
            total_steps+=2
        elif turn == 'F\'':
            cube.front_prime()
            total_steps+=1
        elif turn == 'B':
            cube.back()
            total_steps+=1
        elif turn == 'B2':
            cube.back()
            cube.back()
            total_steps+=2
        elif turn == 'B\'':
            cube.back_prime()
            total_steps+=1
    print(f'Totale Steps: {total_steps}')
    return total_steps


# buttons
start_button = button(surface, gray, 800, 100, 150, 75, 'start', white, 30)

up_button = button(surface, gray, 650, 400, 30, 30, 'U', white, 20)
up_prime_button = button(surface, gray, 700, 400, 30, 30, 'U\'', white, 20)
front_button = button(surface, gray, 650, 450, 30, 30, 'F', white, 20)
front_prime_button = button(surface, gray, 700, 450, 30, 30, 'F\'', white, 20)
down_button = button(surface, gray, 650, 500, 30, 30, 'D', white, 20)
down_prime_button = button(surface, gray, 700, 500, 30, 30, 'D\'', white, 20)

left_button = button(surface, gray, 550, 450, 30, 30, 'L', white, 20)
left_prime_button = button(surface, gray, 600, 450, 30, 30, 'L\'', white, 20)
right_button = button(surface, gray, 750, 450, 30, 30, 'R', white, 20)
right_prime_button = button(surface, gray, 800, 450, 30, 30, 'R\'', white, 20)
back_button = button(surface, gray, 850, 450, 30, 30, 'B', white, 20)
back_prime_button = button(surface, gray, 900, 450, 30, 30, 'B\'', white, 20)

scramble_button = button(surface, gray, 825, 350, 100, 30, 'Scramble', white, 20)


cube = rc.rubics_cube(surface=surface)
solving = False

# event loop
while True:
    # events in for loop
    for event in pygame.event.get():

        # check if user has quit the game
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        # check if mouse is clicked
        if event.type == pygame.MOUSEBUTTONDOWN:
            (mouse_x, mouse_y) = pygame.mouse.get_pos()
            mouse = rectangle(surface, black, mouse_x, mouse_y, 1, 1)

            # checks for buttons
            if mouse.intersects(start_button):
                solving = True
            if not(solving):
                if mouse.intersects(scramble_button):
                    cube.scramble()
                elif mouse.intersects(up_button):
                    cube.up()
                elif mouse.intersects(up_prime_button):
                    cube.up_prime()

                elif mouse.intersects(front_button):
                    cube.front()
                elif mouse.intersects(front_prime_button):
                    cube.front_prime()

                elif mouse.intersects(down_button):
                    cube.down()

                elif mouse.intersects(down_prime_button):
                    cube.down_prime()

                elif mouse.intersects(left_button):
                    cube.left()

                elif mouse.intersects(left_prime_button):
                    cube.left_prime()

                elif mouse.intersects(right_button):
                    cube.right()

                elif mouse.intersects(right_prime_button):
                    cube.right_prime()   

                elif mouse.intersects(back_button):
                    cube.back()

                elif mouse.intersects(back_prime_button):
                    cube.back_prime()

                cube.check_cube_press(mouse=mouse)

    # buttons
    if not(solving):
        start_button.draw()
        scramble_button.draw()
        up_button.draw()
        up_prime_button.draw()
        front_button.draw()
        front_prime_button.draw()
        down_button.draw()
        down_prime_button.draw()
        left_button.draw()
        left_prime_button.draw()
        right_button.draw()
        right_prime_button.draw()
        back_button.draw()
        back_prime_button.draw()
    if solving:
        solve(cube=cube)
        solving = False

    display_text(surface, black, 150, 100, 30, 'Rubik\'s Cube Solver')
    cube.update_cube()
    pygame.display.update()
    # update content
