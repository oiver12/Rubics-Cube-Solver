import random
from rectangle import rectangle
from square import square
from button import button
import pygame
import motor

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

class rubics_cube:
    def __init__(self, surface):
        self.graphics_cube = []
        self.surface = surface
        self.side(blue, 125, 200, 50)
        self.side(red, 300, 200, 50)
        self.side(green, 475, 200, 50)
        self.side(orange, 650, 200, 50)
        self.side(white, 300, 375, 50)
        self.side(yellow, 300, 25, 50)
        self.temp_left = []
        self.temp_front = []
        self.temp_right = []
        self.temp_back = []
        self.temp_up = []
        self.temp_down = []
        self.char_cube = [[['b','b','b'],['b','b','b'],['b','b','b']], 
                    [['r','r','r'],['r','r','r'],['r','r','r']], 
                    [['g','g','g'],['g','g','g'],['g','g','g']], 
                    [['o','o','o'],['o','o','o'],['o','o','o']],
                    [['w','w','w'],['w','w','w'],['w','w','w']],
                    [['y','y','y'],['y','y','y'],['y','y','y']]]
        self.cube_solved = self.is_cube_solved()

    # generating 9 squares for 1 side. x and y is position of TOP LEFT corner
    def side(self, color, x, y, width):
        # 3x3 2D array - inserting 9 squares into the sides
        square_tile = []
        for i in range(0,3):
            temp = []
            for j in range(0,3):
                temp.append(square(self.surface, color, (x+(width*j)), (y+(width*i)), width))
            square_tile.append(temp)
    
        self.graphics_cube.append(square_tile)

    def is_cube_solved(self):
        for s in range(0,6):
            for i in range(0,3):
                for j in range(0,3):
                    if not(self.char_cube[s][i][j] == self.char_cube[s][1][1]):
                        print('cube not solved')
                        return False
        print('cube solved!')
        return True
    
    def check_cube_press(self, mouse):
            for s in range(0,6):
                for i in range(0,3):
                    for j in range(0,3):
                        if mouse.intersects(self.graphics_cube[s][i][j]):
                            self.graphics_cube[s][i][j].color_increment()
                            break
    

    def __draw_cube(self):
        # side squares
        for s in range(0,6):
            for i in range(0,3):
                for j in range(0,3):
                    self.graphics_cube[s][i][j].draw()
        
            # grid line using top left square coordinates
            x = self.graphics_cube[s][0][0].x
            y = self.graphics_cube[s][0][0].y
            width = self.graphics_cube[s][0][0].width
            for line in range(0,4):
                pygame.draw.rect(self.surface, black, (x-2, ((y-2)+(line*width)), (3*width + 2), 2))
                pygame.draw.rect(self.surface, black, (((x-2)+(line*width)), y-2, 2, (3*width + 2)))

    def update_cube(self):
        self.__draw_cube()
        # update the char cube
        for s in range(0,6):
            for i in range(0,3):
                for j in range(0,3):
                    self.char_cube[s][i][j] = self.color_to_char(self.graphics_cube[s][i][j].color)


    def scramble(self):
        print('scrambling')
        shuffles = random.randint(25,30)
        for i in range(0, shuffles):
            turn = random.randint(2,11)
            if turn == 2:
                self.down()
            elif turn == 3:
                self.down_prime()
            elif turn == 4:
                self.left()
            elif turn == 5:
                self.left_prime()
            elif turn == 6:
                self.front()
            elif turn == 7:
                self.front_prime()
            elif turn == 8:
                self.right()
            elif turn == 9:
                self.right_prime()
            elif turn == 10:
                self.back()
            else:
                self.back_prime()

    def render_cube(self):
        self.cube_to_graphics()
        self.__draw_cube()
        pygame.display.update()

    def cube_to_graphics(self):
        for s in range(0,6):
            for i in range(0,3):
                for j in range(0,3):
                    self.graphics_cube[s][i][j].color = self.char_to_color(self.char_cube[s][i][j])

    
    # testing prints
    def print_side(self, side):
        for i in range(0,3):
                print(side[i])

    def print_cube(self):
        for i in range(0,6):
                self.print_side(self.cube[i])
                print()

    def char_to_color(self, char):
        if char == 'b':
            return blue
        elif char == 'r':
            return red
        elif char == 'g':
            return green
        elif char == 'o':
            return orange
        elif char == 'y':
            return yellow
        elif char == 'w':
            return white
        else:
            return black  

    def color_to_char(self, color):
        if color == blue:
            return 'b'
        elif color == red:
            return 'r'
        elif color == green:
            return 'g'
        elif color == orange:
            return 'o'
        elif color == yellow:
            return 'y'
        elif color == white:
            return 'w'
        else:
            return ' '  
     
    def copy_to_temp(self):
        self.temp_left = []
        for i in range(0,3):
            self.temp_left.append(self.char_cube[0][i][:])
        self.temp_front = []
        for i in range(0,3):
            self.temp_front.append(self.char_cube[1][i][:])
        self.temp_right = []
        for i in range(0,3):
            self.temp_right.append(self.char_cube[2][i][:])
        self.temp_back = []
        for i in range(0,3):
            self.temp_back.append(self.char_cube[3][i][:])
        self.temp_down = []
        for i in range(0,3):
            self.temp_down.append(self.char_cube[4][i][:])
        self.temp_up = []
        for i in range(0,3):
            self.temp_up.append(self.char_cube[5][i][:])
        

    # cube movements
    def up(self):
        print('U')
        self.copy_to_temp()
        # rotate up
        for i in range(0,3):
            for j in range(0,3):
                self.char_cube[5][i][j] = self.temp_up[2-j][i]
    
        # left side replace
        for i in range(0,3):
            self.char_cube[0][0][i] = self.temp_front[0][i]
        # front side replace
        for i in range(0,3):
            self.char_cube[1][0][i] = self.temp_right[0][i]
        # right side replace
        for i in range(0,3):
            self.char_cube[2][0][i] = self.temp_back[0][i]
        # back side replace
        for i in range(0,3):
            self.char_cube[3][0][i] = self.temp_left[0][i]

        self.render_cube()
        motor.up()

    def up_prime(self):
        print('U\'')

        self.copy_to_temp()

        # rotate up
        for i in range(0,3):
            for j in range(0,3):
                self.char_cube[5][i][j] = self.temp_up[j][2-i]
    
        # left side replace
        for i in range(0,3):
            self.char_cube[0][0][i] = self.temp_back[0][i]
        # front side replace
        for i in range(0,3):
            self.char_cube[1][0][i] = self.temp_left[0][i]
        # right side replace
        for i in range(0,3):
            self.char_cube[2][0][i] = self.temp_front[0][i]
        # back side replace
        for i in range(0,3):
            self.char_cube[3][0][i] = self.temp_right[0][i]
        self.render_cube()
        motor.up_prime()

    def down(self):
        print('D')

        self.copy_to_temp()

        # rotate down
        for i in range(0,3):
            for j in range(0,3):
                self.char_cube[4][i][j] = self.temp_down[2-j][i]
    
        # left side replace
        for i in range(0,3):
            self.char_cube[0][2][i] = self.temp_back[2][i]
        # front side replace
        for i in range(0,3):
            self.char_cube[1][2][i] = self.temp_left[2][i]
        # right side replace
        for i in range(0,3):
            self.char_cube[2][2][i] = self.temp_front[2][i]
        # back side replace
        for i in range(0,3):
            self.char_cube[3][2][i] = self.temp_right[2][i]
        self.render_cube()
        motor.down()

    def down_prime(self):
        print('D\'')

        self.copy_to_temp()

        # rotate down
        for i in range(0,3):
            for j in range(0,3):
                self.char_cube[4][i][j] = self.temp_down[j][2-i]
    
        # left side replace
        for i in range(0,3):
            self.char_cube[0][2][i] = self.temp_front[2][i]
        # front side replace
        for i in range(0,3):
            self.char_cube[1][2][i] = self.temp_right[2][i]
        # right side replace
        for i in range(0,3):
            self.char_cube[2][2][i] = self.temp_back[2][i]
        # back side replace
        for i in range(0,3):
            self.char_cube[3][2][i] = self.temp_left[2][i]
        self.render_cube()
        motor.down_prime()

    def left(self):
        print('L')

        self.copy_to_temp()

        # rotate left
        for i in range(0,3):
            for j in range(0,3):
                self.char_cube[0][i][j] = self.temp_left[2-j][i]
    
        # back side replace
        for i in range(0,3):
            self.char_cube[3][i][2] = self.temp_down[2-i][0]
        # up side replace
        for i in range(0,3):
            self.char_cube[5][i][0] = self.temp_back[2-i][2]
        # front side replace
        for i in range(0,3):
            self.char_cube[1][i][0] = self.temp_up[i][0]
        # bottom side replace
        for i in range(0,3):
            self.char_cube[4][i][0] = self.temp_front[i][0]
        self.render_cube()
        motor.left()

    def left_prime(self):
        print('L\'')

        self.copy_to_temp()

        # rotate left
        for i in range(0,3):
            for j in range(0,3):
                self.char_cube[0][i][j] = self.temp_left[j][2-i]
    
        # back side replace
        for i in range(0,3):
            self.char_cube[3][i][2] = self.temp_up[2-i][0]
        # up side replace
        for i in range(0,3):
            self.char_cube[5][i][0] = self.temp_front[i][0]
        # front side replace
        for i in range(0,3):
            self.char_cube[1][i][0] = self.temp_down[i][0]
        # bottom side replace
        for i in range(0,3):
            self.char_cube[4][i][0] = self.temp_back[2-i][2]
        self.render_cube()
        motor.left_prime()

    def right(self):
        print('R')

        self.copy_to_temp()

        # rotate left
        for i in range(0,3):
            for j in range(0,3):
                self.char_cube[2][i][j] = self.temp_right[2-j][i]
    
        # back side replace
        for i in range(0,3):
            self.char_cube[3][i][0] = self.temp_up[2-i][2]
        # up side replace
        for i in range(0,3):
            self.char_cube[5][i][2] = self.temp_front[i][2]
        # front side replace
        for i in range(0,3):
            self.char_cube[1][i][2] = self.temp_down[i][2]
        # bottom side replace
        for i in range(0,3):
            self.char_cube[4][i][2] = self.temp_back[2-i][0]
        self.render_cube()
        motor.right()

    def right_prime(self):
        print('R\'')

        self.copy_to_temp()

        # rotate right
        for i in range(0,3):
            for j in range(0,3):
                self.char_cube[2][i][j] = self.temp_right[j][2-i]
    
        # back side replace
        for i in range(0,3):
            self.char_cube[3][i][0] = self.temp_down[2-i][2]
        # up side replace
        for i in range(0,3):
            self.char_cube[5][i][2] = self.temp_back[2-i][0]
        # front side replace
        for i in range(0,3):
            self.char_cube[1][i][2] = self.temp_up[i][2]
        # bottom side replace
        for i in range(0,3):
            self.char_cube[4][i][2] = self.temp_front[i][2]
        self.render_cube()
        motor.right_prime()

    def front(self):
        print('F')

        self.copy_to_temp()

        # rotate front
        for i in range(0,3):
            for j in range(0,3):
                self.char_cube[1][i][j] = self.temp_front[2-j][i]
    
        # left side replace
        for i in range(0,3):
            self.char_cube[0][i][2] = self.temp_down[0][i]
        # up side replace
        for i in range(0,3):
            self.char_cube[5][2][i] = self.temp_left[2-i][2]
        # right side replace
        for i in range(0,3):
            self.char_cube[2][i][0] = self.temp_up[2][i]
        # bottom side replace
        for i in range(0,3):
            self.char_cube[4][0][i] = self.temp_right[2-i][0]
        self.render_cube()
        motor.front()

    def front_prime(self):
        print('F\'')

        self.copy_to_temp()

        # rotate front
        for i in range(0,3):
            for j in range(0,3):
                self.char_cube[1][i][j] = self.temp_front[j][2-i]
    
        # left side replace
        for i in range(0,3):
            self.char_cube[0][i][2] = self.temp_up[2][2-i]
        # up side replace
        for i in range(0,3):
            self.char_cube[5][2][i] = self.temp_right[i][0]
        # right side replace
        for i in range(0,3):
            self.char_cube[2][i][0] = self.temp_down[0][2-i]
        # bottom side replace
        for i in range(0,3):
            self.char_cube[4][0][i] = self.temp_left[i][2]
        self.render_cube()
        motor.front_prime()

    def back(self):
        print('B')

        self.copy_to_temp()

        # rotate back
        for i in range(0,3):
            for j in range(0,3):
                self.char_cube[3][i][j] = self.temp_back[2-j][i]
    
        # up side replace
        for i in range(0,3):
            self.char_cube[0][i][0] = self.temp_up[0][2-i]
        # right side replace
        for i in range(0,3):
            self.char_cube[5][0][i] = self.temp_right[i][2]
        # down side replace
        for i in range(0,3):
            self.char_cube[2][i][2] = self.temp_down[2][2-i]
        # left side replace
        for i in range(0,3):
            self.char_cube[4][2][i] = self.temp_left[i][0]
        self.render_cube()
        motor.back()

    def back_prime(self):
        print('B\'')

        self.copy_to_temp()

        # rotate back
        for i in range(0,3):
            for j in range(0,3):
                self.char_cube[3][i][j] = self.temp_back[j][2-i]
    
        # down side replace
        for i in range(0,3):
            self.char_cube[0][i][0] = self.temp_down[2][i]
        # left side replace
        for i in range(0,3):
            self.char_cube[5][0][i] = self.temp_left[2-i][0]
        # up side replace
        for i in range(0,3):
            self.char_cube[2][i][2] = self.temp_up[0][i]
        # right side replace
        for i in range(0,3):
            self.char_cube[4][2][i] = self.temp_right[2-i][2]  
        self.render_cube()
        motor.back_prime()
    