from mazesolver_files import *


INSPECTION = 'INSPECTION'
inspection = 'INSPECTION'
RACE = 'RACE'
race = 'RACE'

class Micromouse:
    right_turn_dict  = {N:E, E:S, S:W, W:N}
    left_turn_dict   = {N:W, E:N, S:E, W:S}
    go_forward_dict  = {N:N, E:E, S:S, W:W}
    go_back_dict     = {N:S, E:W, S:N, W:E}
    distance_dict    = {N:-1, E:nr_of_cells, S:1, W:-nr_of_cells}
    a = ((nr_of_cells**2)/2)-1
    goal_cells_list = [int(a-(nr_of_cells/2)), int(a-(nr_of_cells/2)+1), int(a+(nr_of_cells/2)), int(a+(nr_of_cells/2)+1)]
    # goal_cells_list = [28, 29, 36, 37]
    alg = 'B'

    def __init__(self, start_pos=0, start_orientation=S):
        # mapa otoczenia
        self.environment = [zerolistmaker(4) for i in range(nr_of_cells*nr_of_cells)]
        # mapa wew. Micromouse, jest postaci [[N, E, S, W, visited]]
        self.mazelayout_mm = [[0, 0, 0, 0, 'Not visited'] for i in range(nr_of_cells*nr_of_cells)]
        # variable that stores mm current position, current cell, 0 - 255
        self.current_position = start_pos
        # variable that stores mm current orientation
        self.current_orientation  = start_orientation
        # etap rozwiazywania labiryntu - przeszukiwanie (INSPECTION) lub wyscig (RACE)
        self.state = INSPECTION

        self.visited_cells = []
        self.goal_reached = False

        self.start_pos = start_pos
        self.start_orientation = start_orientation

        self.bellman_ford_dist_counter = 0
        self.bellman_ford_distance = [0]*(nr_of_cells**2)
        self.bf_initialized = False
        self.bf_ends = [0]

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
        try:
            if self.visited_cells[len(self.visited_cells)-1] != self.current_position:
                self.visited_cells.append(self.current_position)
        except IndexError:
            self.visited_cells.append(self.current_position)
        if self.mazelayout_mm[self.current_position][4] == 'Not visited':
            self.update_cell()
        else:
            # move/turn
            # todo: function maker with this alg on __init__
            self.is_goal_reached()
            if Micromouse.alg == 'L': #left-hand rule
                if self.can_go_left() == True:
                    self.turn_left()
                    self.go_forward()
                elif self.can_go_forward() == True:
                    self.go_forward()
                elif self.can_go_right() == True:
                    self.turn_right()
                    self.go_forward()
                elif self.can_go_back() == True:
                    self.turn_back()
            elif Micromouse.alg == 'R': #right-hand rule
                if self.can_go_right() == True:
                    self.turn_right()
                    self.go_forward()
                elif self.can_go_forward() == True:
                    self.go_forward()
                elif self.can_go_left() == True:
                    self.turn_left()
                    self.go_forward()
                elif self.can_go_back() == True:
                    self.turn_back()


    def step_bf(self):
        # self.bellman_ford_distance - lista 256-u elementow, kazda z nich to pojedyncza cela, zapisujemy w niej "odl do srodka"
        if self.bf_initialized == False:
            self.bf_initialized = True
            self.bellman_ford_ends = [0]
            for cell, cell2 in zip(self.mazelayout_mm, self.environment):
                cell[0:4] = cell2[0:4]

        self.bellman_ford_dist_counter += 1

        new_bf_ends = []
        for end in self.bf_ends:
            neighbours = self.find_neighbours_bf(end)
            print('neighbours of {}: {}'.format(end, neighbours))
            for neigh in neighbours:
                self.bellman_ford_distance[neigh] = self.bellman_ford_dist_counter
                new_bf_ends.append(neigh)

        self.bf_ends = new_bf_ends
        print('self.bf_ends = {}'.format(self.bf_ends))



    def find_neighbours_bf(self, cell):
        neighbours = []
        print('self.mazelayout_mm[cell] = self.mazelayout_mm[{}] = {}'.format(cell, self.mazelayout_mm[cell]))

        if self.can_go_NSEW_bf(N, cell):
            # neigh_nr = cell + Micromouse.distance_dict[N]
            if self.is_valid_cell_nr(cell + Micromouse.distance_dict[N]):
                print('{} can go N'.format(cell))
                neighbours.append(cell + Micromouse.distance_dict[N])
        if self.can_go_NSEW_bf(S, cell):
            if self.is_valid_cell_nr(cell + Micromouse.distance_dict[S]):
                print('{} can go S'.format(cell))
                neighbours.append(cell + Micromouse.distance_dict[S])
        if self.can_go_NSEW_bf(E, cell):
            if self.is_valid_cell_nr(cell + Micromouse.distance_dict[E]):
                print('{} can go E'.format(cell))
                neighbours.append(cell + Micromouse.distance_dict[E])
        if self.can_go_NSEW_bf(W, cell):
            if self.is_valid_cell_nr(cell + Micromouse.distance_dict[W]):
                print('{} can go W'.format(cell))
                neighbours.append(cell + Micromouse.distance_dict[W])

        return neighbours

    def can_go_NSEW_bf(self, side, cell=None):
        if cell == None:
            cell = self.current_position
        if side not in orientation_dict.keys():
            print('error kurwa')
        else:
            if self.mazelayout_mm[cell][orientation_dict[side]] == 1:
                return False
            else:
                return True

    def is_valid_cell_nr(self, cell_nr):
        if cell_nr >= 0 and cell_nr <= 256:
            print('cell_nr {} is valid cell nr'.format(cell_nr))
            return True
        else:
            print('cell_nr {} is not valid cell nr'.format(cell_nr))
            return False

    def can_go_x(self, turn_dict):
        side = orientation_dict[turn_dict[self.current_orientation]]
        if self.mazelayout_mm[self.current_position][side] == 1:
            return False
        else:
            return True

    def can_go_right(self):
        return self.can_go_x(Micromouse.right_turn_dict)

    def can_go_left(self):
        return self.can_go_x(Micromouse.left_turn_dict)

    def can_go_forward(self):
        return self.can_go_x(Micromouse.go_forward_dict)

    def can_go_back(self):
        return self.can_go_x(Micromouse.go_back_dict)

    def is_goal_reached(self):
        if self.current_position in Micromouse.goal_cells_list:
            print('!!!YOU WON!!!')
            self.goal_reached = True
            self.run_in_progress = False

    def turn_right(self):
        self.current_orientation = Micromouse.right_turn_dict[self.current_orientation]

    def turn_left(self):
        self.current_orientation = Micromouse.left_turn_dict[self.current_orientation]

    def turn_back(self):
        self.current_orientation = Micromouse.go_back_dict[self.current_orientation]

    def go_forward(self):
        self.current_position = self.current_position + Micromouse.distance_dict[self.current_orientation]

    # pass Mazesolver.mazelayout as an argument
    def read_environment(self, mazelayout):
        self.environment = [[cell[0], cell[1], cell[2], cell[3]] for cell in mazelayout]

    def reset(self):
        self.mazelayout_mm = [[0, 0, 0, 0, 'Not visited'] for i in range(nr_of_cells*nr_of_cells)]
        self.current_position = self.start_pos
        self.current_orientation = self.start_orientation
        self.visited_cells = []
        self.goal_reached = False

        # for row_Micromouse, row_Mazesolver in zip(self.mazelayout_mm, mazelayout):
        #     print(row_Micromouse, row_Mazesolver)
