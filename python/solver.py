from ortools.linear_solver import pywraplp
from ortools.init import pywrapinit
from security_camera import *
import numpy as np
import time
NUM_DIRECTIONS = 8

def solve(bitmap, fov):
    start0 = time.process_time()
    # transpose bitmap to match (x,y)
    bitmap_arr = np.array(bitmap).T
    height = bitmap_arr.shape[0]
    width = bitmap_arr.shape[1]
    neighbors = [(-1, 0), (1, 0), (0, 1), (0, -1)]
    cameras = []
    solver = pywraplp.Solver.CreateSolver("SCIP")
    solver.EnableOutput()

    # initialize camera variables (row,col,dir) with BoolVar
    # where one means a camera exists and zero means no camera
    # (cameras only allowed adjacent to a wall)
    for row in range(height):
        r = []
        for col in range(width):
            # if not a wall
            if bitmap_arr[row][col] == False:
                d = []
                for (dx, dy) in neighbors:
                    # if neighbor in range of bitmap
                    if 0 <= col+dx < width and 0 <= row+dy < height:
                        # if neighbor is a wall (adjacent to wall)
                        if bitmap_arr[row+dy][col+dx] == True:
                            for k in range(NUM_DIRECTIONS):
                                dir = k*(360/NUM_DIRECTIONS)
                                d.append(solver.BoolVar('x[%i][%i][%i]' % (row, col, dir)))
                            r.append(d)
                            break
                if not d:
                    r.append(0)
            else:
                r.append(0)
        cameras.append(r)

    # constraint: any given (x,y) coordination can only contain a single camera
    all_cameras = 0
    for r in range(height):
        for c in range(width):
            # initialize summation of cameras at single location
            if cameras[r][c]!=0:
                # sum over all cameras
                for d in range(0,NUM_DIRECTIONS):
                    all_cameras = all_cameras+cameras[r][c][d]
                # ensure max of 1 camera at a single spot
                single_loc = cameras[r][c][0]
                # sum up rest at single location
                for d in range(1,NUM_DIRECTIONS):
                    single_loc = single_loc+cameras[r][c][d]
                solver.Add(single_loc<=1)

    # initialize white_pixels
    white_pixels = []
    for row in range(height):
        # if not all(bitmap_arr[row]):
            r = []
            for col in range(width):
                # print('row: ',row,'col: ',col)
                if bitmap_arr[row][col] == False:
                    r.append([False])
                else:
                    r.append([True])
            white_pixels.append(r)

    # for each white pixel, find out which cameras can see it
    # append each white pixel with the BoolVar that represents the camera
    for r in range(height):
        for c in range(width):
            if cameras[r][c]!=0:
                for d in range(0,NUM_DIRECTIONS):
                    dir = d*(360/NUM_DIRECTIONS)
                    cam = SecurityCamera(c,r,fov,dir,bitmap)
                    viewable = SecurityCamera.computeViewable(cam)
                    viewable = np.array(viewable).T
                    for row in range(height):
                        for col in range(width):
                            if(white_pixels[row][col][0]==False and viewable[row][col]==True):
                                white_pixels[row][col].append(cameras[r][c][d])

    # constraints: for every white pixel, at least one camera can see that pixel
    # prints out spot if no cameras can see a certain white pixel
    for row in range(height):
        for col in range(width):
            if len(white_pixels[row][col])>1:
                in_view = white_pixels[row][col][1]
                for camera in range(2,len(white_pixels[row][col])):
                    in_view = in_view + white_pixels[row][col][camera]
                solver.Add(in_view>=1)
            elif white_pixels[row][col][0]==False:
                print("no cameras can see this spot: row ",row," col ",col)

    # minimze number of cameras needed to cover facility
    start1 = time.process_time()
    solver.Minimize(all_cameras)
    print(f'Solving with {solver.SolverVersion()}')
    status = solver.Solve()
    if status == pywraplp.Solver.OPTIMAL:
        print('Solution:')
        print('Objective value =', solver.Objective().Value())
    else:
        print('The problem does not have an optimal solution.')
    print('Linear Optimization:',time.process_time() - start1)
    print('Entire Process: ',time.process_time() - start0)

    # populate return with list of cameras necessary to cover bitmap
    ret = []
    for r in range(len(cameras)):
        for c in range(len(cameras[r])):
            for d in range(0,NUM_DIRECTIONS):
                if cameras[r][c]!=0:
                    if cameras[r][c][d].solution_value() != 0:
                        print(cameras[r][c][d].name(), '=',cameras[r][c][d].solution_value())
                        dir = d*(360/NUM_DIRECTIONS)
                        sc = SecurityCamera(c,r,fov,dir,bitmap)
                        ret.append(sc)
    return ret