#!/usr/local/bin/python3
# solve_luddy.py : Sliding tile puzzle solver
#
#
# Code by: [PLEASE PUT Divyanshu Jhawar-djhawar, Manuja Bandal-msbandal & Sathyan-satvenk ]
#
# Based on skeleton code by D. Crandall, September 2019
#
import Queue
import Queue as Q

from Queue import PriorityQueue

import sys
import time

MOVES = { "R": (0, -1), "L": (0, 1), "D": (-1, 0), "U": (1,0) }

MOVES_LUDDY = { "A":(2,1),"B": (2,-1),"C":(-2,1),"D": (-2, -1),"E":(1,2),"F":(1,-2),"G": (-1,2),"H": (-1, -2) }

def rowcol2ind(row, col):
    return row*4 + col

# Heuristic1
def manhattan(state):

    dis = 0

    for i in range(15):
        r = i/4
        c = i%4
        if state[i] != i+1:
            dis += abs(state[i] - (i+1))*((4-r))

    return dis

# Heuristic2
# Find the number of misplaced tiles on the board
def misplaced_tiles(state):
    count =0
    #print(state)
    for i in range(15):
        if state[i] != (i+1):
            count+=1
    if state[15] != 0:
        count+= 1
    #print("Count is ", count)
    return count

# Heuristic3
def permutation_inversion(state):
    inversions = 0

    pos = 0

    for i in range(len(state)):

        if state[i] == 0:
            pos = i

        for j in range(i,len(state)):
            #print((state[i] > state[j]))
            if (state[i] > state[j]) and state[i] != 0 and state[j] != 0:
                inversions += 1

    inversions += 15 - pos

    return inversions


# Checks the board is solvable or not
def solvability(state):

    inversions = 0

    for i in range(len(state)):
        for j in range(i,len(state)):
            #print((state[i] > state[j]))
            if (state[i] > state[j]) and state[i] != 0 and state[j] != 0:
                inversions += 1
    (empty_row, empty_col) = ind2rowcol(state.index(0))

    if empty_row %2 == 0 and inversions %2 == 1:
        return True
    if empty_row %2 == 1 and inversions %2 == 0:
        return True

    return False

def ind2rowcol(ind):
    return (int(ind/4), ind % 4)

def valid_index(row, col):
    return 0 <= row <= 3 and 0 <= col <= 3

def swap_ind(list, ind1, ind2):
    return list[0:ind1] + (list[ind2],) + list[ind1+1:ind2] + (list[ind1],) + list[ind2+1:]

def swap_tiles(state, row1, col1, row2, col2):
    return swap_ind(state, *(sorted((rowcol2ind(row1,col1), rowcol2ind(row2,col2)))))

def printable_board(row):
    return [ '%3d %3d %3d %3d'  % (row[j:(j+4)]) for j in range(0, 16, 4) ]

# return a list of possible successor states
def successors(state):
    # Finding the coordinates of '0'
    (empty_row, empty_col) = ind2rowcol(state.index(0))
    if (sys.argv[2] == 'original'):
        return [ (swap_tiles(state, empty_row, empty_col, empty_row+i, empty_col+j), c) \
             for (c, (i, j)) in MOVES.items() if valid_index(empty_row+i, empty_col+j) ]
    elif (sys.argv[2] == 'luddy'):
        return [ (swap_tiles(state, empty_row, empty_col, empty_row+i, empty_col+j), c) \
             for (c, (i, j)) in MOVES_LUDDY.items() if valid_index(empty_row+i, empty_col+j) ]
    else:
        return [(swap_tiles(state, empty_row, empty_col, (empty_row + i) % 4, (empty_col + j) % 4), c) for (c, (i, j))
                in MOVES.items()]

# check if we've reached the goal
def is_goal(state):
    return sorted(state[:-1]) == list(state[:-1]) and state[-1]==0


# ***********************************************************************************************
# The solver! - using A* Search
def solve(initial_board,variant):

    closed = set()

    q = Q.PriorityQueue()
    cost = 0
    q.put((misplaced_tiles(initial_board), initial_board, "", 0))


    while not q.empty():
        (h, state, route_so_far, cost) = q.get()
        cost = cost + 1


        if is_goal(state):
            return (route_so_far)

        for (succ, move) in successors(state):

            if succ not in closed:
                closed.add(succ)
                q.put((misplaced_tiles(succ) + len(move) + cost, succ, route_so_far + move, cost))

            # for k in range(len(fringe)):
            # if succ == fringe[k][0]:
            # if len(move) < len(fringe[k][1]):
            # fringe.remove((succ,fringe[k][1]))
            # break
            # fringe.insert(0, (succ, route_so_far + move))

    return "Inf"






# **********************************************************************************************

# The solver! - using IDA* Search
def solve_idastar(initial_board,variant):
    fringe = [ (initial_board, "") ]
    closed = []

    # depth
    threshold = 3

    while len(fringe) > 0:

        # For priority queue
        #min_val = (distance_from_original(fringe[0][0]) + misplaced_tiles(fringe[0][0]) + len(fringe[0][1]))
        min_val = (permutation_inversion(fringe[0][0]) + len(fringe[0][1]))
        misplaced = misplaced_tiles(fringe[0][0])
        min_idx = 0
    
        for i in range(len(fringe)):
            #temp = (distance_from_original(fringe[i][0]) + misplaced_tiles(fringe[i][0]) + len(fringe[i][1]))
            temp = (permutation_inversion(fringe[i][0])  + len(fringe[i][1]))
            if temp <= min_val and misplaced > misplaced_tiles(fringe[i][0]):
                min_val = temp
                misplaced = misplaced_tiles(fringe[i][0])
                min_idx = i


        (state, route_so_far)=fringe.pop(min_idx)
        print(state)
        if state in closed:
            continue
        closed.append(state)

        if is_goal(state):
            return (route_so_far)
        for (succ,value,move) in dfs_with_limit(state,0,threshold):
            fringe.insert(0, (succ, route_so_far+move))

    return "Inf"

# Function to find the cost upto depth d for IDA*
def dfs_with_limit(state,depth,threshold):

    min_value = 100000

    if depth == threshold:
        
        for (succ,move) in successors(state):
            if min_value > misplaced_tiles(succ):
                min_succ = succ
                min_value = misplaced_tiles(succ)

        return min_value


    best_set_of_succ = []
    min_succ = []

    for (succ,move) in successors(state):
        
        best_value = dfs_with_limit(succ,depth+1,threshold)

        best_set_of_succ.insert(0,(succ,best_value,move))

    if depth == 0:
        for j in range(len(best_set_of_succ)):

            if min_value == best_set_of_succ[j][1]:
                min_succ.append(best_set_of_succ[j])

            if min_value > best_set_of_succ[j][1]:
                min_succ = []
                min_value = best_set_of_succ[j][1]
                min_succ.append(best_set_of_succ[j])

        return min_succ

    else:

        for k in range(len(best_set_of_succ)):
            if min_value > best_set_of_succ[k][1]:
                min_value = best_set_of_succ[k][1]

        return min_value

if __name__ == "__main__":
    if(len(sys.argv) != 3):
        raise(Exception("Error: expected 2 arguments"))

    start_state = []
    with open(sys.argv[1], 'r') as file:
        for line in file:
            start_state += [ int(i) for i in line.split() ]

    if len(start_state) != 16:
        raise(Exception("Error: couldn't parse start state file"))

    start_state = tuple(start_state)

    print("Start state: \n" +"\n".join(printable_board(start_state)))

    print("Solving....")
    if solvability(start_state):
        # ##### A* #######
        route = solve(start_state,sys.argv[2])

        # ##### IDA* #######
        #route = solve_idastar(start_state,sys.argv[2])
        if route == 'Inf':
            print(route)
        else:
            print("Solution found in " + str(len(route)) + " moves:" + "\n" + route)
    else:
        print("Inf")
