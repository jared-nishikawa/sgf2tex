#!/usr/bin/python

#SIZE = 9
SIZE = 19

class GoBoard():
    def __init__(self):
        # The board and the moves
        self.BOARD = make_board()
        self.MOVES = []
        self.CURFILL = 1
    
    # MISC 
    ###############
    def place_stone(self, coords, alternate=True):
        x,y = coords

        # Place the stone
        self.BOARD[x][y] = self.cur_color()

        # Remove stones
        self.remove_stones()

        # Increment color
        if alternate:
            self.CURFILL += 1


    def remove_stones(self):
        # Remove stones of the opposite color with 0 libs (black = 1, white = 2)
        OPP = self.opp_color()
    
        # Gather group reps
        reps = get_all_reps(self.BOARD)
    
        # For each rep, check the color
        for rep in reps:
            if self.BOARD[rep[0]][rep[1]] == OPP:
                # If it's the right color, check the libs
                grp, libs = get_group(self.BOARD, rep[0], rep[1])
    
                # If it has 0 libs, then delete them all!
                if len(libs) == 0:
                    for node in grp:
                        # Delete it off the logical board
                        self.BOARD[node[0]][node[1]] = 0
    
    # Maps CURFILL to either 1 (black) or 2 (white)
    def cur_color(self):
        return 2 - (self.CURFILL % 2)
    
    # Maps CURFILL to opposite of cur_color
    def opp_color(self):
        return 2 - ((self.CURFILL + 1) % 2)
    
    # So, if a stone is capturing a group, then it's not a suicide move
    # If it captures even a SINGLE stone, then it's not a suicide move
    def suicide(self, i,j):
        temp = copy_board(self.BOARD)
        cur = self.cur_color()
        opp = self.opp_color()
    
        temp[i][j] = cur
        grp,libs = get_group(temp, i, j)
    
        # If we get 0 libs, it's a POTENTIAL suicide move
        if len(libs) == 0:
            # Let's check the neighbors for capturing first...
            nbd = get_neighbors(i,j)
            for nbr in nbd:
                if temp[nbr[0]][nbr[1]] == opp:
                    opp_grp, opp_libs = get_group(temp, nbr[0], nbr[1])
                    if len(opp_libs) == 0:
                        print("Capturing move!")
                        return False
            print("Suicide move!")
            return True
        return False

    def disp(self):
        for row in self.BOARD:
            print row

def clean(moves, handi=[]):
    B = GoBoard()
    for move in handi:
        B.place_stone(move,alternate=False)
    if handi:
        B.CURFILL += 1
    for move in moves:
        B.place_stone(move)
    bmvs = []
    wmvs = []
    size = len(B.BOARD)
    for i in range(size):
        for j in range(size):
            if B.BOARD[i][j] == 1:
                bmvs.append((i,j))
            elif B.BOARD[i][j] == 2:
                wmvs.append((i,j))
    #B.disp()
    return bmvs, wmvs

def sgf2num(move):
    alph = 'abcdefghjklmnopqrst'
    let = move[0]
    num = move[1:]
    return alph.index(let), int(num) - 1

def num2sgf(move):
    alph = 'abcdefghjklmnopqrst'
    x,y = move
    return ''.join([alph[x], str(y+1)])

def copy_list(L):
    M = []
    for item in L:
        M.append(item)
    return M

def copy_board(board):
    newbrd = []
    for row in board:
        newbrd.append(copy_list(row))
    return newbrd

def make_board():
    board = []
    for i in range(SIZE):
        row = [0]*SIZE
        board.append(row)
    return board

def get_neighbors(i,j):
    assert i>=0 and i<SIZE and j>=0 and j<SIZE
    neighbors = [pair for pair in \
            [(i-1,j), (i+1,j), (i,j-1), (i,j+1)] \
            if pair[0] >= 0 and pair[0] < SIZE and \
            pair[1] >= 0 and pair[1] < SIZE]
    return neighbors

def get_group(board_master, i,j):
    # Make a copy... (because I'm going to be messing with it)
    board = copy_board(board_master)

    if board[i][j] == 0:
        return [], []
    color = board[i][j]
    grp = []

    # Liberties
    libs = []

    # Start with a single point
    neighbors = [(i,j)]

    # DEPTH FIRST SEARCH!!!!
    # Assume that everything that makes it into neighbors is the right color
    while neighbors:
        # Pop off the last element
        a,b = neighbors.pop()

        # Put it into grp
        grp.append((a,b))

        # Mark it on the board
        board[a][b] = 0

        # Find the neighbors
        nbd = get_neighbors(a,b)

        # Loop through the neighbors and find the ones of the right color
        for nbr in nbd:
            # The following line would let us find ALL visible adjacencies
            #grp.append(nbr)
            
            # Let's also find the liberties... (neighbors that are 0)
            # Note: Should check board_master rather than board
            #   b/c board gets changed
            if not board_master[nbr[0]][nbr[1]]:
                libs.append(nbr)

            # This will let us continue finding the group
            elif board[nbr[0]][nbr[1]] == color:
                neighbors.append(nbr)

    # Eliminate duplicates from libs
    libs = set(libs)

    return grp, libs

# Define a unique way to produce a group representative
# Steps:
#   Take the top row (lowest y value)
#   Take the leftmost cell in the top row (lowest x value)
def group_rep(grp):
    ymin = 100
    for cell in grp:
        if cell[1] < ymin:
            ymin = cell[1]
    xmin = 100
    for cell in grp:
        if cell[0] < xmin and cell[1] == ymin:
            xmin = cell[0]
    return xmin, ymin

# Gather all the group representatives
def get_all_reps(board_master):
    board = copy_board(board_master)

    reps = []
    for i in range(SIZE):
        for j in range(SIZE):
            if board[i][j]:
                grp,libs = get_group(board, i,j)
                for node in grp:
                    board[node[0]][node[1]] = 0
                rep = group_rep(grp)
                reps.append(rep)
    return reps

def test():
    B = make_board()
    B[3][4] = 1
    B[4][4] = 1
    B[5][4] = 1

    print get_group(B, 3, 4)

if __name__ == '__main__':
    #test()
    moves = [(10,10),(10,11), (3,3), (10,9),(3,4),(9,10), (3,5), (11,10)]
    b,w = clean(moves)
    print b
    print w


