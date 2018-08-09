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
        self.bellman_ford_distance = [-1]*(nr_of_cells**2)
        self.bf_initialized = False
        # self.bf_ends = [0]
        self.bf_ends = Micromouse.goal_cells_list
        self.bf_maze_filled = False
        self.bf_path = []
        self.bf_paths = [0, 0]
        self.bf_state_machines = [[], []]
        self.bf_state_machine_index = 0
        for destination_cell in Micromouse.goal_cells_list:
            self.bellman_ford_distance[destination_cell] = 0

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

    def reset_bf(self):
        self.bellman_ford_dist_counter = 0
        self.bellman_ford_distance = [-1]*(nr_of_cells**2)
        self.bf_initialized = False
        self.bf_ends = [0]
        self.bf_maze_filled = False
        self.bf_path = []
        self.bf_paths = [0, 0]
        self.bf_state_machines = [[], []]
        self.bf_state_machine_index = 0
        # self.bellman_ford_distance[0] = 0


    def step_bf(self):
        # self.bellman_ford_distance - lista 256-u elementow, kazda z nich to pojedyncza cela, zapisujemy w niej "odl do srodka"
        self.is_maze_filled()
        if self.bf_maze_filled == False:
            self.bellman_ford_dist_counter += 1
            new_bf_ends = []
            for end in self.bf_ends:
                neighbours = self.find_neighbours_bf(end)
                for neigh in neighbours:
                    self.bellman_ford_distance[neigh] = self.bellman_ford_dist_counter
                    new_bf_ends.append(neigh)

            self.bf_ends = new_bf_ends
        elif self.bf_maze_filled == True:
            if self.bf_paths[0] == 0:
                self.bf_find_path()
                # temp:
                self.create_bf_state_machines()
                self.choose_path()
            else:
                if self.is_goal_reached() == False:
                    self.bf_state_machines[self.path_chosen][self.bf_state_machine_index]()
                    self.bf_state_machine_index = self.bf_state_machine_index + 1
                else:
                    pass


    def bf_get_direction(self, cell, l_current_position=None):
        if l_current_position == None:
            l_current_position = self.current_position

        if cell == l_current_position + Micromouse.distance_dict[N]:
            return N
        elif cell == l_current_position + Micromouse.distance_dict[S]:
            return S
        elif cell == l_current_position + Micromouse.distance_dict[W]:
            return W
        elif cell == l_current_position + Micromouse.distance_dict[E]:
            return E

    def bf_find_path(self):
        goal_cell_nr = self.find_entrance_to_finish()
        self.bf_path.append([goal_cell_nr])

        last_cell = self.bf_path[len(self.bf_path)-1]

        while [0] not in self.bf_path:
            way = []
            for cell, i in zip(last_cell, range(len(last_cell))):
                cell = self.bf_path[len(self.bf_path)-1][i]
                cell_dist = self.bellman_ford_distance[cell]
                cell_neighs = self.find_neighbours_bf(cell,
                                        ignore_cells_with_distance=False)

                ways_to_go = []
                for neigh in cell_neighs:
                    if self.bellman_ford_distance[neigh] == cell_dist - 1:
                        ways_to_go.append(neigh)

                if len(ways_to_go) == 1:
                    way.append(ways_to_go[0])
                elif len(ways_to_go) == 2:
                    way.append(ways_to_go[0])
                    way.append(ways_to_go[1])

            if len(way) == 2:
                if way[0] == way[1]:
                    way = [way[0]]

            self.bf_path.append(way)
            last_cell = self.bf_path[len(self.bf_path)-1]

        self.bf_paths[0] = [cell[0] for cell in self.bf_path]
        if self.are_there_two_paths() == True:
            self.bf_paths[1] = self.bf_get_second_path()

    def create_bf_state_machines(self):

        for path, state_machine in zip(self.bf_paths, self.bf_state_machines):
            if path != 0:
                local_path = path[::-1]

                curr_orient = self.current_orientation
                current_pos = self.current_position

                i = 1
                while current_pos not in Micromouse.goal_cells_list:

                    next_cell_dir = self.bf_get_direction(local_path[i], l_current_position=current_pos)
                    if next_cell_dir == curr_orient:
                        state_machine.append(self.go_forward)
                        current_pos = local_path[i]
                        i = i + 1
                    elif next_cell_dir != curr_orient:
                        if Micromouse.right_turn_dict[curr_orient] == next_cell_dir:
                            state_machine.append(self.turn_right)
                        elif Micromouse.left_turn_dict[curr_orient] == next_cell_dir:
                            state_machine.append(self.turn_left)
                        curr_orient = next_cell_dir

    def choose_path(self):
        if self.are_there_two_paths == True:
            path_one_turns, path_two_turns = 0, 0
            for function in self.bf_state_machines[0]:
                if function == self.turn_right or function == self.turn_left:
                    path_one_turns = path_one_turns + 1
            for function in self.bf_state_machines[1]:
                if function == self.turn_right or function == self.turn_left:
                    path_two_turns = path_two_turns + 1

            if path_one_turns <= path_two_turns:
                self.path_chosen = 0
            else:
                self.path_chosen = 1
        else:
            self.path_chosen = 0


    def are_there_two_paths(self):
        for cell in self.bf_path:
            if len(cell) > 1:
                return True
        return False

    def bf_get_second_path(self):
        list_to_draw = []
        for cell in self.bf_path:
            if len(cell) == 2:
                list_to_draw.append(cell[1])
            elif len(cell) == 1:
                list_to_draw.append(cell[0])
        return list_to_draw

    def bf_read_whole_maze(self):
        for cell, cell2 in zip(self.mazelayout_mm, self.environment):
            cell[0:4] = cell2[0:4]

    def find_entrance_to_finish(self):
        cell = Micromouse.goal_cells_list[0]
        for side in [N, W]:
            if self.can_go_NSEW_bf(side, cell):
                return cell

        cell = Micromouse.goal_cells_list[1]
        for side in [S, W]:
            if self.can_go_NSEW_bf(side, cell):
                return cell

        cell = Micromouse.goal_cells_list[2]
        for side in [N, E]:
            if self.can_go_NSEW_bf(side, cell):
                return cell

        cell = Micromouse.goal_cells_list[3]
        for side in [S, E]:
            if self.can_go_NSEW_bf(side, cell):
                return cell

        # if we cant reach goal
        return 0

    def is_maze_filled(self):
        if -1 not in self.bellman_ford_distance:
            self.bf_maze_filled = True #dla gui

    def find_neighbours_bf(self, cell, ignore_cells_with_distance=True):
        neighbours = []

        if self.can_go_NSEW_bf(N, cell):
            neigh_nr = cell + Micromouse.distance_dict[N]
            if self.is_valid_cell_nr(neigh_nr):
                if ignore_cells_with_distance == True:
                    if self.bellman_ford_distance[neigh_nr] == -1:
                        neighbours.append(neigh_nr)
                else:
                    neighbours.append(neigh_nr)
        if self.can_go_NSEW_bf(S, cell):
            neigh_nr = cell + Micromouse.distance_dict[S]
            if self.is_valid_cell_nr(neigh_nr):
                if ignore_cells_with_distance == True:
                    if self.bellman_ford_distance[neigh_nr] == -1:
                        neighbours.append(neigh_nr)
                else:
                    neighbours.append(neigh_nr)
        if self.can_go_NSEW_bf(E, cell):
            neigh_nr = cell + Micromouse.distance_dict[E]
            if self.is_valid_cell_nr(neigh_nr):
                if ignore_cells_with_distance == True:
                    if self.bellman_ford_distance[neigh_nr] == -1:
                        neighbours.append(neigh_nr)
                else:
                    neighbours.append(neigh_nr)
        if self.can_go_NSEW_bf(W, cell):
            neigh_nr = cell + Micromouse.distance_dict[W]
            if self.is_valid_cell_nr(neigh_nr):
                if ignore_cells_with_distance == True:
                    if self.bellman_ford_distance[neigh_nr] == -1:
                        neighbours.append(neigh_nr)
                else:
                    neighbours.append(neigh_nr)

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
            return True
        else:
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
            return True
        else:
            return False

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
        self.reset_bf()
