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
