
from tkinter import *
from mazesolver_files import zerolistmaker

INSPECTION = 'INSPECTION'
inspection = 'INSPECTION'
RACE = 'RACE'
race = 'RACE'
orientation_dict = {N:0, E:1, S:2, W:3}
right_turn_dict  = {N:E, E:S, S:W, W:N}
left_turn_dict   = {N:W, E:N, S:E, W:S}
go_forward_dict  = {N:N, E:E, S:S, W:W}
go_back_dict     = {N:S, E:W, S:N, W:E}

class Micromouse:

    def __init__(self, start_pos=0, start_orientation=S):
        self.nr_of_cells = 16
        # mapa otoczenia
        self.environment = [zerolistmaker(4) for i in range(self.nr_of_cells*self.nr_of_cells)]
        # mapa wew. Micromouse, jest postaci [[N, E, S, W, visited]]
        self.mazelayout_mm = [[0, 0, 0, 0, 'Not visited'] for i in range(self.nr_of_cells*self.nr_of_cells)]
        # variable that stores mm current position, current cell, 0 - 255
        self.current_position = start_pos
        # variable that stores mm current orientation
        self.current_orientation  = start_orientation
        # etap rozwiazywania labiryntu - przeszukiwanie (INSPECTION) lub wyscig (RACE)
        self.state = INSPECTION

    def add_wall(self, cell_number, side):
        side_nr = orientation_dict[side]
        self.mazelayout_mm[cell_number][side_nr] = 1

    # def perform_alg_step(self):
    def update_cell(self):
        for side in orientation_dict.values():
            if self.environment[self.current_position][side] == 1:
                self.mazelayout_mm[self.current_position][side] = 1

        self.mazelayout_mm[self.current_position][4] = 'visited'

    def step(self):
        print(self.mazelayout_mm[self.current_position])
        self.update_cell()
        print(self.mazelayout_mm[self.current_position])
        if self.can_go_right() == True:
            print('Can turn right')
        else:
            print('Can\'t turn right')
        if self.can_go_left() == True:
            print('Can turn left')
        else:
            print('Can\'t turn left')
        if self.can_go_forward() == True:
            print('Can go forward')
        else:
            print('Can\'t go forward')
        if self.can_go_back() == True:
            print('Can go back')
        else:
            print('Can\'t go back')

    def can_go_x(self, turn_dict):
        side = orientation_dict[turn_dict[self.current_orientation]]
        if self.mazelayout_mm[self.current_position][side] == 1:
            return False
        else:
            return True

    def can_go_right(self):
        return self.can_go_x(right_turn_dict)

    def can_go_left(self):
        return self.can_go_x(left_turn_dict)

    def can_go_forward(self):
        return self.can_go_x(go_forward_dict)

    def can_go_back(self):
        return self.can_go_x(go_back_dict)

    # pass Mazesolver.mazelayout as an argument
    def read_environment(self, mazelayout):

        self.environment = [[cell[0], cell[1], cell[2], cell[3]] for cell in mazelayout]

        # for row_Micromouse, row_Mazesolver in zip(self.mazelayout_mm, mazelayout):
        #     print(row_Micromouse, row_Mazesolver)
