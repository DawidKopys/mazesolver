from tkinter import ttk, filedialog, font
from mazesolver_files import *
from mazesolver_alg import Micromouse

import threading

# defines for print_cell_number()
ALL = 'all'
all = 'all'

# print('mazelayout[{}] = {}, walls_printed = {}'.format(ind-1, self.mazelayout[ind-1], self.walls_printed[ind-1]))

def print_wall_decorate(func):
    def func_wrapper(self, number, colour='blue', w_width=None):
        coords = self.get_cell_coords(number)
        return func(self, coords[0], coords[1], colour, w_width)

    return func_wrapper


class Mazesolver_GUI:
    step_time = 1

    def __init__(self, parent_root):
        self.parent_root = parent_root

        self.size        = 800
        # nr_of_cells = nr_of_cells
        self.edge_list_S = [nr_of_cells*i for i in range(1, nr_of_cells+1)]
        self.edge_list_N = [i-(nr_of_cells-1) for i in self.edge_list_S]
        self.edge_list_W = list(range(1,nr_of_cells+1))
        self.edge_list_E = list(range(nr_of_cells**2+1-nr_of_cells ,nr_of_cells**2+1))
        self.offset      = 20
        self.grid_width  = 1
        self.walls_width = 9
        self.points_list = []
        self.path_lines  = []
        self.mm_env_walls  = []
        self.walls_printed = [zerolistmaker(4) for i in range(nr_of_cells*nr_of_cells)]
        self.maze_edit_enable = False
        self.step = self.size / nr_of_cells
        self.dist_centre_to_wall = (self.size / nr_of_cells) / 2

        self.up    = self.offset
        self.left  = self.offset
        self.down  = self.size + self.offset
        self.right = self.size + self.offset

        self.mm_color = 'red'

        parent_root.wm_title('MazeSolver')
        root_w = self.size*1.27
        root_h = self.size+50
        screen_w = parent_root.winfo_screenwidth()
        screen_h = parent_root.winfo_screenheight()
        # calculate x and y coordinates for the Tk root window
        x = (screen_w/2) - (root_w/2)
        y = (screen_h/2) - (root_h/2)
        # set the dimensions of the screen
        # and where it is placed
        parent_root.geometry('%dx%d+%d+%d' % (root_w, root_h, x, y))

        # root childs can stretch
        parent_root.columnconfigure(0, weight=3)
        parent_root.columnconfigure(1, weight=1)
        parent_root.rowconfigure(0, weight=1)

        self.mazeframe = ttk.Frame(parent_root, padding="3 3 3 3")
        self.mazeframe.grid(column=0, row=0, sticky=N+S+E+W, rowspan=6)
        # self.mazeframe.configure(borderwidth=2, relief='sunken')
        # self.mazeframe.columnconfigure(0, weight=2)
        # self.mazeframe.rowconfigure(0, weight=2)

        self.menuframe = ttk.Frame(parent_root, padding="3 3 3 3")
        self.menuframe.grid(column=1, row=0, sticky=N+S+E+W, rowspan=6)
        # self.menuframe.configure(borderwidth=2, relief='sunken')
        # self.menuframe.columnconfigure(0, weight=2)
        # self.menuframe.rowconfigure(0, weight=2)

        self.spaceframe1 = ttk.Frame(self.menuframe, padding="3 3 3 3", height=self.size/4)
        self.spaceframe1.grid(column=0, row=6, sticky=E+W)
        self.spaceframe2 = ttk.Frame(self.menuframe, padding="3 3 3 3", height=self.size/4)
        self.spaceframe2.grid(column=0, row=11, sticky=S+E+W)

        self.canvas = Canvas(self.mazeframe, width=self.size + 2*self.offset, height=self.size + 2*self.offset)
        self.canvas.configure(background='#d9dde2')
        self.canvas.grid(row=0, column=1)

        self.mm = Micromouse(start_pos=0, start_orientation=E)
        self.mm_polygon = None

        self.b_draw_maze      = ttk.Button(self.menuframe, text='Draw Maze', state=DISABLED, command=self.print_maze)
        self.b_open_maze_file = ttk.Button(self.menuframe, text='Load Maze Layout', command=self.load_maze_layout)
        self.b_clear_maze     = ttk.Button(self.menuframe, text='Clear Maze Layout', command=self.clear_maze_layout)
        self.b_save_maze      = ttk.Button(self.menuframe, text='Save Maze Layout', command=self.save_maze_layout)
        self.b_edit_maze      = ttk.Button(self.menuframe, text='Edit Maze', command=self.toggle_maze_edit)
        self.b_mm_solve_maze  = ttk.Button(self.menuframe, text='Solve The Maze', state=DISABLED, command=self.solve_maze)
        self.b_place_mm       = ttk.Button(self.menuframe, text='Place Micromouse', state=DISABLED, command=self.place_mm)
        self.b_pauze_mm       = ttk.Button(self.menuframe, text='Pauze', state=DISABLED, command=self.pauze_the_alg)
        self.b_bf_step        = ttk.Button(self.menuframe, text='Bellman-Ford', command=self.mm_step_bf)

        self.b_open_maze_file.grid(column=0, row=0, sticky=N+E+W, pady=2)
        self.b_save_maze.grid(column=0, row=1, sticky=E+W, pady=2)
        self.b_draw_maze.grid(column=0, row=2, sticky=E+W, pady=2)
        self.b_place_mm.grid(column=0, row=3, sticky=E+W, pady=2)
        self.b_clear_maze.grid(column=0, row=7, sticky=E+W, pady=2)
        self.b_edit_maze.grid(column=0, row=8, sticky=E+W, pady=2)
        self.b_mm_solve_maze.grid(column=0, row=9, sticky=E+W, pady=2)
        self.b_pauze_mm.grid(column=0, row=10, sticky=E+W, pady=2)
        self.b_bf_step.grid(column=0, row=11, sticky=E+W, pady=2)

        self.algorithm_val = StringVar()
        label_algorithm = ttk.Label(self.menuframe, text='Choose algorithm:')
        self.cb_algorithm = ttk.Combobox(self.menuframe, textvariable=self.algorithm_val, state='readonly')
        self.cb_algorithm['values'] = ['Left-hand Rule', 'Right-hand Rule', 'Bellman-Ford']
        self.cb_algorithm.current(2)

        label_algorithm.grid(row=4, pady=2)
        self.cb_algorithm.grid(row=5, pady=4, padx=10)

        self.cb_algorithm.bind('<<ComboboxSelected>>', self.change_alg)

        self.print_outline()
        self.create_cells_points()
        self.print_cell_number(numbers=all)

        self.b_open_maze_file.focus()
        self.parent_root.bind('<Return>', self.load_maze_layout)
        self.parent_root.bind('<Control-c>', self.clear_maze_layout)

        self.print_wall_NSEW = [self.print_wall_N, self.print_wall_E, self.print_wall_S, self.print_wall_W]

        self.bf_font = font.Font(size=20, weight='bold')


    def change_alg(self, *args):
        choice = self.algorithm_val.get()
        self.cb_algorithm.select_clear()
        if choice == 'Left-hand Rule':
            Micromouse.alg = 'L'
        elif choice == 'Right-hand Rule':
            Micromouse.alg = 'R'
        elif choice == 'Bellman-Ford':
            Micromouse.alg = 'B'

    def place_mm(self, *args):
        self.print_mm()
        self.mm.read_environment(self.mazelayout)
        self.b_mm_solve_maze.state(['!disabled'])
        self.b_mm_solve_maze.focus()
        self.parent_root.bind('<Return>', self.solve_maze)

    def solve_maze(self, *args):
        self.mm_step()
        self.b_pauze_mm.state(['!disabled'])
        self.disable_w_except(parent=self.menuframe, widget_exception=self.b_pauze_mm)
        self.b_pauze_mm.configure(text='Pauze', command=self.pauze_the_alg)

    def pauze_the_alg(self):
        self.mm_step_timer.cancel()
        self.b_pauze_mm.configure(text='Resume', command=self.resume_the_alg)
        self.b_mm_solve_maze.configure(text='Restart the Micromouse', command=self.mm_reset)
        self.b_mm_solve_maze.state(['!disabled'])

    def resume_the_alg(self):
        self.mm_step_timer = threading.Timer(0.5, self.mm_step)
        self.mm_step_timer.start()
        self.b_pauze_mm.configure(text='Pauze', command=self.pauze_the_alg)
        self.b_mm_solve_maze.configure(text='Solve The Maze', command=self.solve_maze)
        self.b_mm_solve_maze.state(['disabled'])

    def mm_reset(self):
        self.mm.reset()
        self.clear_maze_layout()
        self.print_maze()
        self.print_mm()
        self.b_mm_solve_maze.configure(text='Solve The Maze', command=self.solve_maze)
        self.enable_w_except(parent=self.menuframe, widget_exception=self.b_pauze_mm)
        self.b_pauze_mm.state(['disabled'])

    def disable_w_except(self, parent, widget_exception=None):
        children = all_children(parent)
        for child in children:
            if child != widget_exception:
                child.state(['disabled'])

    def enable_w_except(self, parent, widget_exception=None):
        children = all_children(parent)
        for child in children:
            if child != widget_exception:
                child.state(['!disabled'])

    def mm_step_bf(self):

        self.mm.step_bf()
        # print(self.mm.bellman_ford_distance)
        for i in range(len(self.mm.bellman_ford_distance)):
            if self.mm.bellman_ford_distance[i] != 0:
                coords = self.get_cell_coords(i)
                number = self.mm.bellman_ford_distance[i]
                self.canvas.create_text(coords[0], coords[1], text=str(number), fill='red', font=self.bf_font)

    def mm_step(self):
        if self.mm.goal_reached == False:
            self.mm_step_timer = threading.Timer(Mazesolver_GUI.step_time, self.mm_step)
            self.mm_step_timer.start()
            self.mm.step()
            self.print_mm()
            for side in orientation_dict.values():
                if self.mm.mazelayout_mm[self.mm.current_position][side] == 1:
                    self.mm_env_walls.append(self.print_wall_NSEW[side](self.mm.current_position,
                                    colour='red', w_width=self.walls_width/2))
        else:
            self.draw_path()
            self.b_mm_solve_maze.configure(text='Restart the Micromouse', command=self.mm_reset)
            self.b_mm_solve_maze.state(['!disabled'])
            self.b_pauze_mm.state(['disabled'])

    def get_cell_coords(self, number):
        cell_x = self.cells_centres_flat[number][0]
        cell_y = self.cells_centres_flat[number][1]
        return [cell_x, cell_y]

    def draw_path(self):
        path_coords = [self.get_cell_coords(cell) for cell in self.mm.visited_cells]
        for i in range(len(path_coords)-1):
            self.path_lines.append(self.canvas.create_line(path_coords[i][0], path_coords[i][1],
                                path_coords[i+1][0], path_coords[i+1][1], fill='green', width=self.walls_width/2))

    def toggle_maze_edit(self):
        if self.maze_edit_enable == False:
            # enable maze editing
            self.maze_edit_enable = True
            self.b_edit_maze.configure(text='Exit Edit')
            self.canvas.bind('<Double-Button-1>', self.find_closest_cell)
            self.b_edit_maze.state(['pressed'])
            self.canvas.configure(background='white')
            self.disable_w_except(parent=self.menuframe, widget_exception=self.b_edit_maze)
        elif self.maze_edit_enable == True:
            # disable maze editing
            self.maze_edit_enable = False
            self.b_edit_maze.configure(text='Edit Maze')
            self.canvas.unbind('<Double-Button-1>')
            self.b_edit_maze.state(['!pressed'])
            self.canvas.configure(background='#d9dde2')
            #update Micromouse maze environment
            self.mazelayout = prepare_maze_layout_list(self.walls_printed)
            self.mm.read_environment(self.mazelayout)
            self.enable_w_except(parent=self.menuframe)

    # funkcja znajduje komórkę na którą klikamy i rysuje/usuwa odpowiednie ściany
    def find_closest_cell(self, event):
        # jak to działa
        cell_x = min(self.cells_centres_x, key=lambda x:abs(x-event.x))
        cell_y = min(self.cells_centres_y, key=lambda x:abs(x-event.y))

        cell_ind = self.cells_centres_flat.index([cell_x, cell_y]) + 1

        x_diff = event.x - cell_x
        y_diff = event.y - cell_y
        if abs(x_diff) > abs(y_diff):
            if x_diff > 0:
                wall_side = E
            else:
                wall_side = W
        else:
            if y_diff > 0:
                wall_side = S
            else:
                wall_side = N

        if self.is_wall_present(cell_ind, side=wall_side) == True:
            self.destroy_wall(cell_ind, side=wall_side)
            pass
        else:
            self.print_wall(cell_ind, side=wall_side, caller='double_press')

    def print_border(self):
        #canvas.create_line(x0, y0, x1, y1)
        self.canvas.create_line(self.left, self.up, self.right, self.up, width=self.grid_width) #gora pozioma
        self.canvas.create_line(self.left, self.up, self.left, self.down, width=self.grid_width) #lewa pion
        self.canvas.create_line(self.right, self.up, self.right, self.down, width=self.grid_width) #prawa pion
        self.canvas.create_line(self.left, self.down, self.right, self.down, width=self.grid_width) #dol poziom

    def print_walls_border(self):
        #canvas.create_line(x0, y0, x1, y1)
        self.canvas.create_line(self.left, self.up, self.right, self.up, fill='blue', width=self.walls_width) #gora pozioma
        self.canvas.create_line(self.left, self.up, self.left, self.down, fill='blue', width=self.walls_width) #lewa pion
        self.canvas.create_line(self.right, self.up, self.right, self.down, fill='blue', width=self.walls_width) #prawa pion
        self.canvas.create_line(self.left, self.down, self.right, self.down, fill='blue', width=self.walls_width) #dol poziom

    def print_grid(self):
        if self.step % 1 != 0:   #sprawdzamy czy liczba jest calkowita (czy size jest podzielne przez nr_of_cells)
            print('error, step nie jest liczba calkowita (size jest niepodzielne przez nr_of_cells)')
        else:
            pass
            x_pion = self.left
            y_poziom = self.up
            for line in range(nr_of_cells):
                x_pion = x_pion + self.step
                self.canvas.create_line(x_pion, self.up, x_pion, self.down, width=self.grid_width)
                y_poziom = y_poziom + self.step
                self.canvas.create_line(self.left, y_poziom, self.right, y_poziom, width=self.grid_width)

    def print_outline(self):
        self.print_border()
        self.print_grid()

    # funkcja tworząca listę koordynat
    # param:
    #   @nr_of_cells - ilość komórek w labiryncie
    #   @self.size        - rozmiar labiryntu (dlugosc boku w pixelach)
    #   @self.offset      - odleglosc ramki od krawędzi okna
    # return:
    #   #self.cells_centres - lista zawierająca koordynaty punktów
    #       crds to lista zawierająca środki cel, lista jest o formacie:
    #       [[[x0, y0], [x1, y0], [x2, y0], ...]
    #        [[x0, y1], [x1, y1], [x2, y1], ...]
    #        [[],[],[], ...                    ]...]
    def create_cells_points(self):
        self.cells_centres = []
        for x in range(nr_of_cells):
            self.cells_centres.append([])
            for y in range(nr_of_cells):
                self.cells_centres[x].append([int(x * self.step + self.offset + self.step / 2), int(y * self.step + self.offset + self.step/2)])
        self.cells_centres_flat = [col for row in self.cells_centres for col in row]
        self.cells_centres_x = [cell[0] for cell in self.cells_centres_flat]
        self.cells_centres_y = [cell[1] for cell in self.cells_centres_flat]

    # print micromouse and create self.mm object
    def print_mm(self):
        if self.mm_polygon != None:
            self.canvas.delete(self.mm_polygon)
        # cell_coords = self.cel    ls_centres[0][0]
        cell_coords = self.get_cell_coords(self.mm.current_position)
        cell_x = cell_coords[0]
        cell_y = cell_coords[1]
        size_corrector = self.step/16
        if self.mm.current_orientation == S:
            N_W_x = cell_x - self.step/4 + size_corrector
            N_W_y = cell_y - self.step/4
            N_E_x = cell_x + self.step/4 - size_corrector
            N_E_y = N_W_y
            C_x = cell_x
            C_y = cell_y + self.step/4
        elif self.mm.current_orientation == N:
            N_W_x = cell_x - self.step/4 + size_corrector
            N_W_y = cell_y + self.step/4
            N_E_x = cell_x + self.step/4 - size_corrector
            N_E_y = N_W_y
            C_x = cell_x
            C_y = cell_y - self.step/4
        elif self.mm.current_orientation == E:
            N_W_x = cell_x - self.step/4
            N_W_y = cell_y - self.step/4 + size_corrector
            N_E_x = N_W_x
            N_E_y = cell_y + self.step/4 - size_corrector
            C_x = cell_x + self.step/4
            C_y = cell_y
        elif self.mm.current_orientation == W:
            N_W_x = cell_x + self.step/4
            N_W_y = cell_y - self.step/4 + size_corrector
            N_E_x = N_W_x
            N_E_y = cell_y + self.step/4 - size_corrector
            C_x = cell_x - self.step/4
            C_y = cell_y

        self.mm_polygon = self.canvas.create_polygon(N_W_x, N_W_y,
                            N_E_x, N_E_y, C_x, C_y, fill=self.mm_color)

    # funkcja rysująca numery wszystkich komórek
    # param:
    # return: none
    def print_cells_numbers(self):
        i = 1 #todo: change back to 0
        for row in range(nr_of_cells):
            for col in range(nr_of_cells):
                self.canvas.create_text(self.cells_centres[row][col][0], self.cells_centres[row][col][1], text=str(i))
                i = i + 1

    # funkcja rysuje numer komórki o podanym numerze
    # param:
    #   @numbers - lista (lub jeden number) zawierająca numery komórek, których numery chcemy narysować
    #              jeśli chcemy narysować wszystkie numery to możemy podać argument numbers=ALl (lub numbers=all)
    # return: none
    def print_cell_number(self, numbers):
        if type(numbers) == int:
            numbers = [numbers] #jeśli argument jest pojedyńczą liczbą - utwórz listę, której jedynym elementem jest ta liczba
        elif numbers == 'all':
            numbers = range(1, nr_of_cells**2+1)
        for number in numbers:
            self.canvas.create_text(self.cells_centres_flat[number-1][0], self.cells_centres_flat[number-1][1], text=str(number))

    # funkcja rysuje górną ścianę w komórce o podanym numerze
    # param:
    #   @cell_coord_x - koordynata x komórki
    #   @cell_coord_y - koordynata y komórki
    # return: none
    @print_wall_decorate
    def print_wall_N(self, cell_coord_x, cell_coord_y, colour='blue', w_width=None):
        if w_width == None:
            w_width = self.walls_width
        wall_id = self.canvas.create_line(cell_coord_x - self.dist_centre_to_wall - self.walls_width/2, cell_coord_y - self.dist_centre_to_wall,
                                cell_coord_x + self.dist_centre_to_wall + self.walls_width/2, cell_coord_y - self.dist_centre_to_wall,
                                fill=colour, width=w_width)
        return wall_id

    # funkcja rysuje dolną ścianę w komórce o podanym numerze
    # desc: patrz print_wall_N
    @print_wall_decorate
    def print_wall_S(self, cell_coord_x, cell_coord_y, colour='blue', w_width=None):
        if w_width == None:
            w_width = self.walls_width
        wall_id = self.canvas.create_line(cell_coord_x - self.dist_centre_to_wall - self.walls_width/2, cell_coord_y + self.dist_centre_to_wall,
                                cell_coord_x + self.dist_centre_to_wall + self.walls_width/2, cell_coord_y + self.dist_centre_to_wall,
                                fill=colour, width=w_width)
        return wall_id

    # funkcja rysuje prawą ścianę w komórce o podanym numerze
    # desc: patrz print_wall_N
    @print_wall_decorate
    def print_wall_E(self, cell_coord_x, cell_coord_y, colour='blue', w_width=None):
        if w_width == None:
            w_width = self.walls_width
        wall_id = self.canvas.create_line(cell_coord_x + self.dist_centre_to_wall, cell_coord_y - self.dist_centre_to_wall - self.walls_width/2,
                                cell_coord_x + self.dist_centre_to_wall, cell_coord_y + self.dist_centre_to_wall + self.walls_width/2,
                                fill=colour, width=w_width)
        return wall_id

    # funkcja rysuje lewą ścianę w komórce o podanym numerze
    # desc: patrz print_wall_N
    @print_wall_decorate
    def print_wall_W(self, cell_coord_x, cell_coord_y, colour='blue', w_width=None):
        if w_width == None:
            w_width = self.walls_width
        wall_id = self.canvas.create_line(cell_coord_x - self.dist_centre_to_wall, cell_coord_y - self.dist_centre_to_wall - self.walls_width/2,
                                cell_coord_x - self.dist_centre_to_wall, cell_coord_y + self.dist_centre_to_wall + self.walls_width/2,
                                fill=colour, width=w_width)
        return wall_id

    # funkcja rysująca ściany wskazane przez parametr side w komórce o numerze number
    def print_wall(self, number, **option):
        side_s = option.get('side')
        caller = option.get('caller')

        if N in side_s:
            if caller == 'double_press':
                if not self.is_wall_present(number, side=N):
                    self.walls_printed[number-1][0] = self.print_wall_N(number-1)
                if not self.is_on_edge(number, side=N):
                    # jesli nie na krawedzi, narysuj tez sciane u sąsiada
                    self.walls_printed[number-1-1][2] = self.print_wall_S(number-1-1)
            else:
                self.walls_printed[number-1][0] = self.print_wall_N(number-1)

        if E in side_s:
            if caller == 'double_press':
                if not self.is_wall_present(number, side=E):
                    self.walls_printed[number-1][1] = self.print_wall_E(number-1)
                if not self.is_on_edge(number, side=E):
                    self.walls_printed[number-1+nr_of_cells][3] = self.print_wall_W(number-1+nr_of_cells)
            else:
                self.walls_printed[number-1][1] = self.print_wall_E(number-1)

        if S in side_s:
            if caller == 'double_press':
                if not self.is_wall_present(number, side=S):
                    self.walls_printed[number-1][2] = self.print_wall_S(number-1)
                if not self.is_on_edge(number, side=S):
                    self.walls_printed[number-1+1][0] = self.print_wall_N(number-1+1)
            else:
                self.walls_printed[number-1][2] = self.print_wall_S(number-1)

        if W in side_s:
            if caller == 'double_press':
                if not self.is_wall_present(number, side=W):
                    self.walls_printed[number-1][3] = self.print_wall_W(number-1)
                if not self.is_on_edge(number, side=W):
                    self.walls_printed[number-1-nr_of_cells][1] = self.print_wall_E(number-1-nr_of_cells)
            else:
                self.walls_printed[number-1][3] = self.print_wall_W(number-1)

        # walls_printed n-elementowa lista w formacie [[N, E, S, W], ...], n to ilosc
        # print('print_wall: cell {}: {}\n'.format(number, self.walls_printed[number-1]))

    # funkcja usuwająca ściany wskazane przez parametr side w komórce o numerze number
    def destroy_wall(self, number, **option):
        ind = number-1
        side = option.get('side')

        if N in side:
            self.destroy_wall_single(ind=number-1, side=N)

            # zniszcz sciane w sasiedniej komórce (jesli nie jestesmy na krawedzi)
            if not self.is_on_edge(number, side=N):
                ind_neigh = number-1 - 1
                try:
                    self.destroy_wall_single(ind=ind_neigh, side=S)
                except IndexError:
                    pass
        if E in side:
            self.destroy_wall_single(ind=number-1, side=E)

            if not self.is_on_edge(number, side=E):
                ind_neigh = number-1 + nr_of_cells
                try:
                    self.destroy_wall_single(ind=ind_neigh, side=W)
                except IndexError:
                    pass
        if S in side:
            self.destroy_wall_single(ind=number-1, side=S)

            if not self.is_on_edge(number, side=S):
                ind_neigh = number-1 + 1
                try:
                    self.destroy_wall_single(ind=ind_neigh, side=N)
                except IndexError:
                    pass
        if W in side:
            self.destroy_wall_single(ind=number-1, side=W)

            if not self.is_on_edge(number, side=W):
                ind_neigh = number-1 - nr_of_cells
                try:
                    self.destroy_wall_single(ind=ind_neigh, side=E)
                except IndexError:
                    pass

    # funkcja usuwa JEDNĄ ścianę, UWAGA, tutaj arg to ind, nie number (patrz destroy_wall)
    def destroy_wall_single(self, ind, side):
        if len(side) != 1:
            print('error, destroy_wall_single takes single direction argument (N or S or W or E)')
        else:
            if N == side:
                wall_ind = self.walls_printed[ind][0]
                self.walls_printed[ind][0] = 0
                self.canvas.delete(wall_ind)
            elif E == side:
                wall_ind = self.walls_printed[ind][1]
                self.walls_printed[ind][1] = 0
                self.canvas.delete(wall_ind)
            elif S == side:
                wall_ind = self.walls_printed[ind][2]
                self.walls_printed[ind][2] = 0
                self.canvas.delete(wall_ind)
            elif W == side:
                wall_ind = self.walls_printed[ind][3]
                self.walls_printed[ind][3] = 0
                self.canvas.delete(wall_ind)

    def is_wall_present(self, number, side):
        if len(side) != 1:
            print('error, is_wall_present takes single direction argument (N or S or W or E)')
        if N == side:
            wall_ind = 0
            wall_ind_neigh = 2
            ind_neigh = number-1 - 1
        elif E == side:
            wall_ind = 1
            wall_ind_neigh = 3
            ind_neigh = number-1 + nr_of_cells
        elif S == side:
            wall_ind = 2
            wall_ind_neigh = 0
            ind_neigh = number-1 + 1
        elif W == side:
            wall_ind = 3
            wall_ind_neigh = 1
            ind_neigh = number-1 - nr_of_cells

        curr_cell_wall = self.walls_printed[number-1][wall_ind]

        if self.is_on_edge(number, side=side):
            cond = curr_cell_wall == 0
        else:
            try:
                neigh_cell_wall = self.walls_printed[ind_neigh][wall_ind_neigh]
            except IndexError:
                neigh_cell_wall = 0
            cond = curr_cell_wall == 0 and neigh_cell_wall == 0

        if cond:
            return False
        else:
            return True

    def is_on_edge(self, number, side):
        if number in self.edge_list_N:
            if N == side:
                return True
            else:
                #edge cells that are both in N and E or W list
                if number not in self.edge_list_E and number not in self.edge_list_W:
                    return False
        if number in self.edge_list_S:
            if S == side:
                return True
            else:
                #edge cells that are both in S and E or W list
                if number not in self.edge_list_E and number not in self.edge_list_W:
                    return False
        if number in self.edge_list_E:
            if E == side:
                return True
            else:
                return False
        if number in self.edge_list_W:
            if W == side:
                return True
            else:
                return False

    # event=0 ponieważ, kiedy wywołujemy fcje poprzez ENTER (bind), do fcji zostaje przekazany
    # dodatkowy argument - rodzaj eventu jaki go wywołał
    def print_maze(self, event=0):
        self.clear_maze_layout()

        ind = 1
        side = ''
        for cell in self.mazelayout:
            if cell[0] == 1:
                side += N
            if cell[1] == 1:
                side += E
            if cell[2] == 1:
                side += S
            if cell[3] == 1:
                side += W
            self.print_wall(ind, side=side)
            # print('mazelayout[{}] = {}, walls_printed = {}'.format(ind-1, self.mazelayout[ind-1], self.walls_printed[ind-1]))
            side = ''
            ind = ind + 1

        self.b_place_mm.state(['!disabled'])
        self.b_place_mm.focus()
        self.parent_root.bind('<Return>', self.place_mm)

    def load_maze_layout(self, *args):
        try:
            self.filename = filedialog.askopenfilename(initialdir = ".",title = "Select file",
                                filetypes = (("text files","*.txt"),("all files","*.*")))
            # wczytaj mapę labiryntu z pliku (do listy, patrz nagłówek pliku)
            self.mazelayout = read_maze_layout(self.filename)
            if self.filename != '': #sprawdz czy wybrano plik, wlacz pczycisk Draw Maze tylko jesli wybrano
                self.b_draw_maze.state(['!disabled'])
                self.parent_root.bind('<Return>', self.print_maze)
                self.b_draw_maze.focus()
        except ValueError:
            print('ValueError file')

    def clear_maze_layout(self, *args):
        for cell in self.walls_printed:
            for wall in cell:
                if wall != 0:
                    self.canvas.delete(wall)

        self.walls_printed = [zerolistmaker(4) for i in range(nr_of_cells*nr_of_cells)]

        self.canvas.delete(self.mm_polygon)
        if self.path_lines != []:
            for line in self.path_lines:
                self.canvas.delete(line)

        if self.mm_env_walls != []:
            for wall in self.mm_env_walls:
                self.canvas.delete(wall)

    def save_maze_layout(self):
        self.filename_write = filedialog.askopenfilename(initialdir = ".",title = "Select file",
                                filetypes = (("text files","*.txt"),("all files","*.*")))
        if self.filename_write != '': #sprawdz czy wybrano plik, wlacz pczycisk Draw Maze tylko jesli wybrano
            write_maze_layout(self.filename_write, prepare_maze_layout_list(self.walls_printed))

root = Tk()
mazesolver = Mazesolver_GUI(root)

root.mainloop()
