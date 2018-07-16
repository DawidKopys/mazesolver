from tkinter import *
from tkinter import ttk, filedialog
from mazesolver_files import read_maze_layout, zerolistmaker

import time

ALL = 'all'
all = 'all'

# print('mazelayout[{}] = {}, walls_printed = {}'.format(ind-1, self.mazelayout[ind-1], self.walls_printed[ind-1]))

class Mazesolver_GUI:

    def __init__(self, parent_root):
        self.size        = 800
        self.nr_of_cells = 16
        self.offset      = 20
        self.grid_width  = 1
        self.walls_width = 9
        self.points_list = []
        self.walls_printed = []

        self.parent_root = parent_root

        self.step = self.size / self.nr_of_cells
        self.dist_centre_to_wall = (self.size / self.nr_of_cells) / 2

        self.up    = self.offset
        self.left  = self.offset
        self.down  = self.size + self.offset
        self.right = self.size + self.offset

        parent_root.wm_title('MazeSolver')

        # root childs can stretch
        parent_root.columnconfigure(0, weight=3)
        parent_root.columnconfigure(1, weight=1)
        parent_root.rowconfigure(0, weight=1)

        self.mazeframe = ttk.Frame(parent_root, padding="3 3 3 3")
        self.mazeframe.grid(column=0, row=0, sticky=N+S+E+W)
        self.mazeframe.configure(borderwidth=2, relief='sunken')
        self.mazeframe.columnconfigure(0, weight=2)
        self.mazeframe.rowconfigure(0, weight=2)

        self.menuframe = ttk.Frame(parent_root, padding="3 3 3 3")
        self.menuframe.grid(column=1, row=0, sticky=N+S+E+W)
        self.menuframe.configure(borderwidth=2, relief='sunken')
        self.menuframe.columnconfigure(0, weight=2)
        self.menuframe.rowconfigure(0, weight=2)

        self.canvas = Canvas(self.mazeframe, width=self.size + 2*self.offset, height=self.size + 2*self.offset)
        self.canvas.configure(background='white')
        self.canvas.grid(row=0, column=0, sticky=N+S+E+W)

        self.b_draw_maze      = ttk.Button(self.menuframe, text='Draw Maze', state=DISABLED, command=self.print_maze)
        self.b_open_maze_file = ttk.Button(self.menuframe, text='Load Maze Layout', command=self.load_maze_layout)
        self.b_clear_maze     = ttk.Button(self.menuframe, text='Clear Maze Layout', command=self.clear_maze_layout)
        self.b_draw_maze.grid()
        self.b_clear_maze.grid()
        self.b_open_maze_file.grid()

        self.print_outline()
        self.create_cells_points()
        self.print_cell_number(numbers=all)

        self.b_draw_maze.focus()
        self.parent_root.bind('<Control-c>', self.clear_maze_layout)
        self.parent_root.bind('<Double-Button-1>', self.find_closest_cell)

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

        self.print_wall(cell_ind, side=wall_side)

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
            for line in range(self.nr_of_cells):
                x_pion = x_pion + self.step
                self.canvas.create_line(x_pion, self.up, x_pion, self.down, width=self.grid_width)
                y_poziom = y_poziom + self.step
                self.canvas.create_line(self.left, y_poziom, self.right, y_poziom, width=self.grid_width)

    def print_outline(self):
        self.print_border()
        self.print_grid()

    # funkcja tworząca listę koordynat
    # param:
    #   @self.nr_of_cells - ilość komórek w labiryncie
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
        for x in range(self.nr_of_cells):
            self.cells_centres.append([])
            for y in range(self.nr_of_cells):
                self.cells_centres[x].append([int(x * self.step + self.offset + self.step / 2), int(y * self.step + self.offset + self.step/2)])
        self.cells_centres_flat = [col for row in self.cells_centres for col in row]
        self.cells_centres_x = [cell[0] for cell in self.cells_centres_flat]
        self.cells_centres_y = [cell[1] for cell in self.cells_centres_flat]

    # funkcja rysująca numery wszystkich komórek
    # param:
    # return: none
    def print_cells_numbers(self):
        i = 1 #todo: change back to 0
        for row in range(self.nr_of_cells):
            for col in range(self.nr_of_cells):
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
            numbers = range(1, self.nr_of_cells**2+1)
        for number in numbers:
            self.canvas.create_text(self.cells_centres_flat[number-1][0], self.cells_centres_flat[number-1][1], text=str(number))

    # funkcja rysuje górną ścianę w komórce o podanym numerze
    # param:
    #   @cell_coord_x - koordynata x komórki
    #   @cell_coord_y - koordynata y komórki
    # return: none
    def print_wall_N(self, cell_coord_x, cell_coord_y):
        wall_id = self.canvas.create_line(cell_coord_x - self.dist_centre_to_wall - self.walls_width/2, cell_coord_y - self.dist_centre_to_wall,
                                cell_coord_x + self.dist_centre_to_wall + self.walls_width/2, cell_coord_y - self.dist_centre_to_wall,
                                fill='blue', width=self.walls_width)
        return wall_id

    # funkcja rysuje dolną ścianę w komórce o podanym numerze
    # desc: patrz print_wall_N
    def print_wall_S(self, cell_coord_x, cell_coord_y):
        wall_id = self.canvas.create_line(cell_coord_x - self.dist_centre_to_wall - self.walls_width/2, cell_coord_y + self.dist_centre_to_wall,
                                cell_coord_x + self.dist_centre_to_wall + self.walls_width/2, cell_coord_y + self.dist_centre_to_wall,
                                fill='blue', width=self.walls_width)
        return wall_id

    # funkcja rysuje prawą ścianę w komórce o podanym numerze
    # desc: patrz print_wall_N
    def print_wall_E(self, cell_coord_x, cell_coord_y):
        wall_id = self.canvas.create_line(cell_coord_x + self.dist_centre_to_wall, cell_coord_y - self.dist_centre_to_wall - self.walls_width/2,
                                cell_coord_x + self.dist_centre_to_wall, cell_coord_y + self.dist_centre_to_wall + self.walls_width/2,
                                fill='blue', width=self.walls_width)
        return wall_id

    # funkcja rysuje lewą ścianę w komórce o podanym numerze
    # desc: patrz print_wall_N
    def print_wall_W(self, cell_coord_x, cell_coord_y):
        wall_id = self.canvas.create_line(cell_coord_x - self.dist_centre_to_wall, cell_coord_y - self.dist_centre_to_wall - self.walls_width/2,
                                cell_coord_x - self.dist_centre_to_wall, cell_coord_y + self.dist_centre_to_wall + self.walls_width/2,
                                fill='blue', width=self.walls_width)
        return wall_id

    # funkcja rysująca ściany wskazane przez parametr side w komórce o numerze number
    def print_wall(self, number, **option):
        cell_x = self.cells_centres_flat[number-1][0]
        cell_y = self.cells_centres_flat[number-1][1]
        walls_ids = []

        if N in option.get('side'):
            walls_ids.append(self.print_wall_N(cell_x, cell_y))
        else:
            walls_ids.append(0)
        if E in option.get('side'):
            walls_ids.append(self.print_wall_E(cell_x, cell_y))
        else:
            walls_ids.append(0)
        if S in option.get('side'):
            walls_ids.append(self.print_wall_S(cell_x, cell_y))
        else:
            walls_ids.append(0)
        if W in option.get('side'):
            walls_ids.append(self.print_wall_W(cell_x, cell_y,))
        else:
            walls_ids.append(0)

        walls_ids.append(number)

        # walls_printed - lista list w formacie [[N, E, S, W, cell_number]]
        self.walls_printed.append(walls_ids)

    # event=0 ponieważ, kiedy wywołujemy fcje poprzez ENTER (bind), do fcji zostaje przekazany
    # dodatkowy argument - rodzaj eventu jaki go wywołał
    def print_maze(self, event=0):
        self.print_walls_border()
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


    def load_maze_layout(self):
        try:
            self.filename = filedialog.askopenfilename(initialdir = ".",title = "Select file",
                                                    filetypes = (("text files","*.txt"),("all files","*.*")))
            # wczytaj mapę labiryntu z pliku (do listy, patrz nagłówek pliku)
            self.mazelayout = read_maze_layout(self.filename)
            self.b_draw_maze.state(['!disabled'])
            self.parent_root.bind('<Return>', self.print_maze)
        except ValueError:
            print('ValueError file')

    def clear_maze_layout(self):
        for cell in self.walls_printed:
            print(cell)
            for wall in cell:
                self.canvas.delete(wall)

        self.walls_printed = []



i = 0
root = Tk()
mazesolver = Mazesolver_GUI(root)
# print(mazesolver.cells_centres_flat)
# mazesolver.print_wall(2, side=E)
# mazesolver.print_wall(119, side=E+W)
# mazesolver.print_wall(26, side=E+W+N+S)
# print('mazesolver.walls_printed', mazesolver.walls_printed)


# time = 1000
# print('kakao')
# for cell in mazesolver.walls_printed:
#     print(cell[0])
#     for line_id in cell[0]:
#         print(line_id)
#         time = time + 1000
#         mazesolver.canvas.after(time, mazesolver.canvas.delete, line_id)
# mazesolver.canvas.after(1000, mazesolver.canvas.delete, mazesolver.wall)
i = i + 1
root.mainloop()
