from mazesolver_files import *

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
        self.bf_ends = Micromouse.goal_cells_list
        self.bf_maze_filled = False
        self.bf_paths = [[]]
        self.bf_state_machines = [[]]
        self.bf_state_machine_index = 0
        for destination_cell in Micromouse.goal_cells_list:
            self.bellman_ford_distance[destination_cell] = 0

        self.step_part = 1

    def add_wall(self, cell_number, side):
        side_nr = orientation_dict[side]
        self.mazelayout_mm[cell_number][side_nr] = 1

    def update_cell(self):
        for side in orientation_dict.values():
            if self.environment[self.current_position][side] == 1:
                self.mazelayout_mm[self.current_position][side] = 1
                self.update_cell_neighbour(side)

        self.mazelayout_mm[self.current_position][4] = 'visited'

    def update_cell_neighbour(self, side):
        neigh_id = self.current_position + Micromouse.distance_dict[orientation_dict_rev[side]]
        try:
            self.mazelayout_mm[neigh_id][orientation_dict[Micromouse.go_back_dict[orientation_dict_rev[side]]]] = 1
        except IndexError:
            pass

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
        self.bf_maze_filled = False
        self.bf_paths = [0, 0]
        self.bf_state_machines = [[], []]
        self.bf_state_machine_index = 0

    def step_bf(self):
        if self.step_part == 1:
            # wykryj ściany
            self.update_cell()

            # zalanie wodą
            self.flood_fill()
        elif self.step_part == 2:
            # temp:
            # wybor drogi
            self.bf_find_path()
            self.create_bf_state_machines()
            self.choose_path()

            # ruch
            self.bf_move()

    def bf_move(self):
        self.bf_state_machines[self.path_chosen][0]()


    def flood_fill(self):
        old = self.bellman_ford_distance[:]
        self.bellman_ford_distance = [-1]*(nr_of_cells**2)

        # if self.is_maze_filled() == False:
        # self.bellman_ford_distance = [-1]*(nr_of_cells**2)
        self.bellman_ford_dist_counter = 0
        self.bf_ends = Micromouse.goal_cells_list
        for destination_cell in Micromouse.goal_cells_list:
            self.bellman_ford_distance[destination_cell] = 0

        while self.is_maze_filled() == False:
            self.bellman_ford_dist_counter += 1

            new_bf_ends = []
            for end in self.bf_ends:
                neighbours = self.find_neighbours_bf(end)
                for neigh in neighbours:
                    self.bellman_ford_distance[neigh] = self.bellman_ford_dist_counter
                    new_bf_ends.append(neigh)

            self.bf_ends = new_bf_ends

    def fill_edges(self):
        for cell in edge_list_E:
            self.mazelayout_mm[cell-1][orientation_dict[E]] = 1
        for cell in edge_list_W:
            self.mazelayout_mm[cell-1][orientation_dict[W]] = 1
        for cell in edge_list_S:
            self.mazelayout_mm[cell-1][orientation_dict[S]] = 1
        for cell in edge_list_N:
            self.mazelayout_mm[cell-1][orientation_dict[N]] = 1

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
        old = self.bf_paths[:]
        self.bf_paths = [[]]

        goal_cell_nrs = self.find_entrance_to_finish()

        self.bf_paths[0].append(self.current_position)

        while self.is_goal_in_paths(goal_cell_nrs) == False:
            for path in self.bf_paths:
                cell = path[len(path)-1]
                cell_dist = self.bellman_ford_distance[cell]
                cell_neighs = self.find_neighbours_bf(cell, ignore_cells_with_distance=False)

                ways_to_go = []
                for neigh in cell_neighs:
                    neigh_dist = self.bellman_ford_distance[neigh]
                    if  neigh_dist == cell_dist - 1:
                        ways_to_go.append(neigh)

                nr_of_paths = len(ways_to_go)
                if nr_of_paths > 1 and len(self.bf_paths) < 50:
                    for i in range(1, nr_of_paths): #dla kazdej sciezki tworzymy nowa liste
                        new_path = path[:]
                        new_path.append(ways_to_go[i])
                        self.bf_paths.append(new_path)

                if nr_of_paths != 0:
                    path.append(ways_to_go[0])

        # for i in range(0, len(self.bf_paths)):
        #     print('self.bf_paths[{}] = {}'.format(i, self.bf_paths[i]))

    def is_goal_in_paths(self, goal_list):
        cond1 = [i for i in goal_list if i in self.bf_paths[len(self.bf_paths)-1]]
        cond2 = [i for i in goal_list if i in self.bf_paths[0]]
        if cond1 == [] or cond2 == []:
            return False
        else:
            return True

    def create_bf_state_machines(self):
        self.bf_state_machines = [[]]

        nr_of_paths = len(self.bf_paths)
        # utworz listę maszyn stanow - tyle pustych list ile sciezek
        self.bf_state_machines = [[] for _ in range(nr_of_paths)]

        for path, state_machine in zip(self.bf_paths, self.bf_state_machines):
            curr_orient = self.current_orientation
            current_pos = self.current_position

            i = 1
            while current_pos not in Micromouse.goal_cells_list:

                next_cell_dir = self.bf_get_direction(path[i], l_current_position=current_pos)
                if next_cell_dir == curr_orient:
                    state_machine.append(self.go_forward)
                    current_pos = path[i]
                    i = i + 1
                elif next_cell_dir != curr_orient:
                    if Micromouse.right_turn_dict[curr_orient] == next_cell_dir:
                        state_machine.append(self.turn_right)
                    elif Micromouse.left_turn_dict[curr_orient] == next_cell_dir:
                        state_machine.append(self.turn_left)
                    elif Micromouse.go_back_dict[curr_orient] == next_cell_dir:
                        state_machine.append(self.turn_back)
                    curr_orient = next_cell_dir

    def choose_path(self):
        turns_counts = [0]*len(self.bf_state_machines)
        self.path_chosen = 0

        for state_machine, i in zip(self.bf_state_machines, range(len(turns_counts))):
            for function in state_machine:
                if function == self.turn_right or function == self.turn_left:
                    turns_counts[i] = turns_counts[i] + 1

            if turns_counts[i] < turns_counts[self.path_chosen]:
                self.path_chosen = i

    def bf_read_whole_maze(self):
        for cell, cell2 in zip(self.mazelayout_mm, self.environment):
            cell[0:4] = cell2[0:4]

    def find_entrance_to_finish(self):
        list_of_goal_cells = []

        cell = Micromouse.goal_cells_list[0]
        for side in [N, W]:
            if self.can_go_NSEW_bf(side, cell):
                # return cell
                list_of_goal_cells.append(cell)

        cell = Micromouse.goal_cells_list[1]
        for side in [S, W]:
            if self.can_go_NSEW_bf(side, cell):
                # return cell
                list_of_goal_cells.append(cell)

        cell = Micromouse.goal_cells_list[2]
        for side in [N, E]:
            if self.can_go_NSEW_bf(side, cell):
                # return cell
                list_of_goal_cells.append(cell)

        cell = Micromouse.goal_cells_list[3]
        for side in [S, E]:
            if self.can_go_NSEW_bf(side, cell):
                # return cell
                list_of_goal_cells.append(cell)

        # if we cant reach goal
        return list(set(list_of_goal_cells))

    def is_maze_filled(self):
        if -1 not in self.bellman_ford_distance:
            self.bf_maze_filled = True #dla gui
            return True
        else:
            self.bf_maze_filled = False
            return False

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
            print('error can_go_NSEW_bf')
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
