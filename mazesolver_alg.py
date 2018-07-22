
from tkinter import *
from mazesolver_files import zerolistmaker

INSPECTION = 'INSPECTION'
inspection = 'INSPECTION'
RACE = 'RACE'
race = 'RACE'
orientation_dict = {N:0, E:1, S:2, W:3}

class Micromouse:

    def __init__(self, start_pos=0, start_orientation=S):
        self.nr_of_cells = 16
        # mapa labiryntu micromouse'a
        # mapa jest postaci [[N, E, S, W, visited]]
        self.mazelayout_mm = [zerolistmaker(5) for i in range(self.nr_of_cells*self.nr_of_cells)]
        # variable that stores mm current position, current cell, 1 - 256
        self.current_position = start_pos
        # variable that stores mm current orientation
        self.current_orientation  = start_orientation
        # etap rozwiazywania labiryntu - przeszukiwanie (INSPECTION) lub wyscig (RACE)
        self.state = INSPECTION

    def add_wall(self, cell_number, side):
        side_nr = orientation_dict[side]
        self.mazelayout_mm[cell_number][side_nr] = 1

    # def perform_alg_step(self):

    # pass Mazesolver.mazelayout as an argument
    def read_environment(self, mazelayout):
        self.mazelayout_mm = [[cell[0], cell[1], cell[2], cell[3], 'Not visited'] for cell in mazelayout]

        # for row_Micromouse, row_Mazesolver in zip(self.mazelayout_mm, mazelayout):
        #     print(row_Micromouse, row_Mazesolver)
