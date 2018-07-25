from tkinter import *

orientation_dict = {N:0, E:1, S:2, W:3}
nr_of_cells = 16

# function reading maze layout to file, save the information in Mazesolver.mazelayout
def read_maze_layout(filename):
    try:
        with open(filename, 'r') as maze_layout_f:
            maze_layout_cont = maze_layout_f.readlines()
        maze_layout = [[int(line[0]), int(line[2]), int(line[4]), int(line[6]),] for line in maze_layout_cont]
        return maze_layout
    except FileNotFoundError:
        pass

def zerolistmaker(n):
    listofzeros = [0] * n
    return listofzeros

def all_children (wid) :
    _list = wid.winfo_children()

    for item in _list :
        if item.winfo_children() :
            _list.extend(item.winfo_children())

    return _list

# function to convert Mazesolver.walls_printed to Mazesolver.mazelayout
def prepare_maze_layout_list(maze_layout):
    maze_layout_out = []
    ind = 0
    for cell in maze_layout:
        maze_layout_out.append([])
        for wall in cell:
            if wall == 0:
                maze_layout_out[ind].append(0)
            else:
                maze_layout_out[ind].append(1)
        ind = ind + 1
    return maze_layout_out

def write_maze_layout(filename, prepared_maze_layout):
    try:
        with open(filename, 'w') as file_out:
            for cell in prepared_maze_layout:
                n_of_spaces = 0
                for wall in cell:
                    file_out.write(str(wall))
                    if n_of_spaces < 3:
                        file_out.write(' ')
                    n_of_spaces = n_of_spaces + 1
                n_of_spaces = 0
                file_out.write('\n')

    except FileNotFoundError:
        print('write_maze_layout: FileNotFoundError')
