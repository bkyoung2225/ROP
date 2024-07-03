import numpy as np 
import matplotlib.pyplot as plt  
import matplotlib.animation as animation
import random
from scipy import mean
from scipy.stats import sem, t
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from matplotlib import cm
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
from matplotlib import colors

def newGrid(N):
    #Defines a new square NxN grid with values of 1 (1 is alive, 0 is dead)
    return np.ones((N,N), dtype=int)

def newGridZeroes(N):
    #Defines a new square NxN grid with values of 1 (1 is alive, 0 is dead)
    return np.zeros((N,N), dtype=int)

cmap1 = ListedColormap(["white", "lightgray", "darkgray"])


def newGridLayered(N):
    PerfGrid = newGrid(N)
    VEGFGrid = newGridZeroes(N)
    NVGrid = newGridZeroes(N)
    return [PerfGrid,VEGFGrid,NVGrid]

def KillBorder(Grid, X):
    #Input = 2d Grid where 1 is alive and 0 is dead. X is thickness of death border
    #Output = Grid with edges are made null (-1) with thickness of X
    for A in range(len(Grid)):
        for B in range(len(Grid[A])):
            if A < X:
                Grid [A][B] = -1
            elif B < X:
                Grid [A][B] = -1
            elif A > len(Grid)-X-1:
                Grid [A][B] = -1
            elif B > len(Grid)-X-1:
                Grid [A][B] = -1
            else:
                continue
            continue    
    return Grid

def KillCircleBorder(Grid, r):
    #Input = 2d Grid where 1 is alive and 0 is dead. r is radius beyond which cells will be dead
    #Output = 2d Grid with r radius beyond which all points are null (-1)
    center = [len(Grid)/2,len(Grid)/2]
    for A in range(len(Grid)):
        for B in range(len(Grid[A])):
            if np.sqrt((A - center[0])**2 + (B - center[1])**2) > r:
                Grid [A][B] = -1
    return Grid


def PerfusionStep(GridLayered,NP,CS):
    #CS = collapse size max
    #NP = nonperf chance
    Grid = GridLayered[0]
    for A in range(len(Grid)):
        for B in range(len(Grid[A])):
            if Grid[A, B] == -1:
                continue
            elif Grid[A, B] == 0:
                continue
            else:
                center = len(Grid)/2
                rad = np.sqrt(((A - center)**2 + (B - center)**2)/(center**2))
                if random.random()  < NP* perfBF(rad):
                    Grid[A][B] = 0
                    # collapseSize = random.randint(1,CS)
                    # for C in range(len(Grid)):
                    #     for D in range(len(Grid[C])):
                    #         if np.sqrt((A - C)**2 + (B - D)**2) <= collapseSize:
                    #             if Grid[A][B] == -1:
                    #                 continue
                    #             else:
                    #                 Grid[A][B] = 0
    GridLayered[0] = Grid                
    return GridLayered

def perfBF(rad):
    if rad < .2:
        return 0
    elif rad >= 0.2 and rad <= 0.7:
        return (rad - 0.2) * (3.1/4)/(0.5)
    elif rad >0.7 and rad <=1:
        return ((rad - 0.2) * ((3.8-3.1)/4)/(0.3)) + (3.1/4)
    else:
        return 0

        

def VEGFStep(GridLayered,VF,VFC,diff):
    #VF is determines chance to increase [VEGF]
    #VFC = chance of VEGF spontaneously clearing
    #Diff = diffusion coefficient
    PerfGrid = GridLayered[0]
    VEGFGrid = GridLayered[1]
    NVGrid = GridLayered[2]
    for A in range(len(VEGFGrid)):
        for B in range(len(VEGFGrid[A])):
            ischemicFactor = 0
            if PerfGrid[A][B] != -1 and PerfGrid[A][B] != 0:
                for C in range(len(PerfGrid)):
                    for D in range(len(PerfGrid[C])):
                        if PerfGrid[C,D] == 0:
                            ischemicFactor = ischemicFactor + (diff/(1+np.sqrt((A - C)**2 + (B - D)**2)))
                        else:
                            continue
                adjNV = 0
                if PerfGrid[A][B] != -1:
                    for dx, dy in [(-1, -1), (-1, 0), (-1, 1),
                                   (0, -1),          ( 0, 1),
                                   ( 1, -1), ( 1, 0), ( 1, 1)]:
                        try:
                            if NVGrid[A+dx][B+dy] == 1:
                                adjNV = adjNV + 1
                        except IndexError:
                            pass
                    if random.random() < VF*ischemicFactor:
                        VEGFGrid[A][B] = VEGFGrid[A][B] + 1 
                    if random.random() < VFC and VEGFGrid[A][B] > 0:
                        VEGFGrid[A][B] = VEGFGrid[A][B] - 1 
                    if VEGFGrid[A][B] > 6 - adjNV:
                        NVGrid[A][B] = 1 
                        VEGFGrid[A][B] = 0
                        GridLayered[1] = VEGFGrid
                        GridLayered[2] = NVGrid 
                        spillover(GridLayered, A, B)
                    
                                            
           
    return GridLayered


def spillover(GridLayered, A, B):
    VEGFGrid = GridLayered[1]
    NVGrid = GridLayered[2]
    PerfGrid = GridLayered[0]
    adjNV = 0
    for ddx, ddy in [(-1, -1), (-1, 0), (-1, 1),
                   (0, -1),          ( 0, 1),
                   ( 1, -1), ( 1, 0), ( 1, 1)]:
        try:
             if NVGrid[A+ddx][B+ddy] == 1:
                 adjNV = adjNV + 1
        except IndexError:
             pass
         
            

    for dx, dy in [(-1, -1), (-1, 0), (-1, 1),
                    ( 0, -1),          ( 0, 1),
                    ( 1, -1), ( 1, 0), ( 1, 1)]:
        
        try:
            if VEGFGrid[A+dx][B+dy] > 7 - adjNV:
                NVGrid[A+dx][B+dy] = 1 
                #PerfGrid[A+dx][B+dy] = 1
                VEGFGrid[A+dx][B+dy] = 0
                GridLayered[1] = VEGFGrid
                GridLayered[2] = NVGrid
                GridLayered[0] = PerfGrid
                spillover(GridLayered, A+dx, B+dy)
        except IndexError or GridLayered[0][A+dx][B+dy] == -1:
            pass
    

def graphPerfusion(GridLayered,NP,CS):
    plt.axis('off')
    plt.imshow(PerfusionStep(GridLayered,NP,CS)[0],interpolation='nearest', cmap = cmap1, animated=True)
 
def graphVEGF(GridLayered,VF,VFC,diff):
    plt.axis('off')
    plt.imshow(VEGFStep(GridLayered,VF, VFC, diff)[1],interpolation='nearest',cmap = cmap1, animated=True)
    
def graphNV(GridLayered,VF, VFC, diff):
    plt.axis('off')
    img=plt.imshow(VEGFStep(GridLayered,VF, VFC, diff)[2],interpolation='nearest',cmap = cmap1, animated=True)
    img.set_cmap('Reds')
    
def graphNVPerf(GridLayered,VF, VFC, diff):
    plt.axis('off')
    Grid = VEGFStep(GridLayered,VF, VFC, diff)
    im1 = plt.imshow(Grid[1],interpolation='nearest',cmap = cmap1, animated=True)
    plt.clim(0,7)
    im2 = plt.imshow(Grid[2],interpolation='nearest',cmap = cmap1, alpha = 0.7, animated=True)
    im2.set_cmap('Reds')
    plt.show()

def plotPerf(N,NP,CS,time):
    #Input = Size of NxN grid, factor is death factor, number of time steps to iterate,radius of living cells
    #Output = Plot of surviving cells
    
    #Border area is represented as -1
    
    Grid = newGridLayered(N)
    y_axis = []
    TotalArea = N*N
    i = 0
    while i < time: 
        y_axis.append((sum(map(sum,PerfusionStep(Grid,NP,CS)[0])))/(N*N))
        i +=1
        print(i)
        
    x_axis = np.arange(0,len(y_axis),1)
    plt.plot(x_axis,y_axis)
    plt.xlabel("Time Steps")
    plt.ylabel("Total Perfusion")
    plt.title('Size=' + str(N) + 'Non-Perf Factor' + str(NP) + 'Collapse Size Max' + str(CS))
    
def plotLogPerf(N,NP,CS,time):
    #Input = Size of NxN grid, factor is death factor, number of time steps to iterate,radius of living cells
    #Output = Plot of surviving cells
    
    #Border area is represented as -1
    
    Grid = newGridLayered(N)
    y_axis = []
    TotalArea = N*N
    i = 0
    while i < time: 
        y_axis.append((sum(map(sum,PerfusionStep(Grid,NP,CS)[0])))/(N*N))
        i +=1
        print(i)
    y_axis = np.log(y_axis)
        
    x_axis = np.arange(0,len(y_axis),1)
    plt.plot(x_axis,y_axis)
    plt.xlabel("Time Steps")
    plt.ylabel("Log Total Perfusion")
    plt.title('Size=' + str(N) + 'Non-Perf Factor' + str(NP) + 'Collapse Size Max' + str(CS))
  
def plotNV(N,VF, VFC, diff, time):
    #Input = Size of NxN grid, factor is death factor, number of time steps to iterate,radius of living cells
    #Output = Plot of surviving cells
    
    #Border area is represented as -1
    
    Grid = newGridLayered(N)
    Grid = PerfusionStep(Grid,0.1,10)
    Grid = PerfusionStep(Grid,0.1,10)
    y_axis = [0]
    i = 0
    while i < time: 
        y_axis.append((sum(map(sum,VEGFStep(Grid,VF, VFC, diff)[2]))) - y_axis[i-1])
        print(i)
        i +=1
        
    #x_axis = np.arange(0,len(y_axis),1)
    #plt.plot(x_axis,y_axis)
    plt.hist(y_axis, bins='auto' )
    plt.xlabel("Size of NV event")
    plt.ylabel("Frequency")
    plt.title('Size=' + str(N))
    
    
def plotPerfPop(N,NP, CS, time, iterations):
    #Input = Size of NxN grid, factor is death factor, number of time steps to iterate,radius of living cells
    #Output = Plot of surviving cells
    
    #Border area is represented as -1
    PopArray = []
    TimeArray = []
    i = 0
    while i < iterations:
        Grid = newGridLayered(N)
        j = 0
        randTime = np.random.normal(time/2,time/6)
        round(randTime)
        while j < randTime:
            PerfusionStep(Grid,NP,CS)[0]
            j = j+1
        PopArray.append(((N*N)-(sum(sum(Grid[0]))))/(N*N))
        print(i)
        print(randTime)
        i = i+1
        
    plt.hist(PopArray, bins='auto' )
    plt.xlabel("Perfusion area")
    plt.ylabel("Frequency")
    plt.title('Size=' + str(N) + 'Non-Perf Factor' + str(NP) + 'Collapse Size Max' + str(CS))
    plt.show()

def plotNVPop(N,NP,CS,VF,VFC,diff, time, iterations):
    #Input = Size of NxN grid, factor is death factor, number of time steps to iterate,radius of living cells
    #Output = Plot of surviving cells
    
    #Border area is represented as -1
    PopArray = []
    i = 0
    a = 0
    gridPerf = newGridLayered(N)
    while i < iterations:
        Grid = newGridLayered(N)
        PerfusionStep(Grid,NP,CS)
        j = 0
        randTime = np.random.normal(time/2,time/6)
        round(randTime)
        while j <= randTime: 
            #PerfusionStep(Grid,NP,CS)
            VEGFStep(Grid,VF, VFC, diff)
            j = j+1
        print(j)
        print(i)
        area = sum(sum(Grid[2]))
        if area != 0:
            PopArray.append(area)
        i = i+1
        
        
    plt.hist(PopArray, bins='auto' )
    plt.xlabel("NV area")
    plt.ylabel("Frequency")
    plt.title('Size=' + str(N) + 'Non-Perf Factor' + str(NP) + 'Collapse Size Max' + str(CS))
    plt.show()
    return PopArray

def plotNVPoploglog(N,NP,CS,VF,VFC,diff, time, iterations):
    #Input = Size of NxN grid, factor is death factor, number of time steps to iterate,radius of living cells
    #Output = Plot of surviving cells
    
    #Border area is represented as -1
    PopArray = []
    i = 0
    a = 0
    gridPerf = newGridLayered(N)
    while i < iterations:
        Grid = newGridLayered(N)
        PerfusionStep(Grid,NP,CS)
        j = 0
        randTime = np.random.normal(time/2,time/10)
        round(randTime)
        while j <= randTime: 
            #PerfusionStep(Grid,NP,CS)
            VEGFStep(Grid,VF, VFC, diff)
            j = j+1
        print(j)
        print(i)
        area = sum(sum(Grid[2]))
        if area != 0:
            PopArray.append(area)
        i = i+1
        
        
    #plt.hist(np.log(PopArray), bins='auto' )
    a,b = np.histogram(PopArray, bins = 'auto')
    index = [1]
    b = np.delete(b, index)
    try:
        plt.scatter(np.log(b),np.log(a))
    except ValueError:
        print('oops')
    # z = np.polyfit(np.log(b), np.log(a),1)
    # predict = np.poly1d(z)
    # r2_score = (a, predict)
    # print(r2_score)
    # x_lin_reg = range(0,5)
    # y_lin_reg = predict(x_lin_reg)
    # plt.plot(x_lin_reg, y_lin_reg, c='r')
        
    plt.yscale('log')
    plt.xlabel("Log NV area")
    plt.ylabel("Log Frequency")
    plt.title('Size=' + str(N) + 'Non-Perf Factor' + str(NP) + 'Collapse Size Max' + str(CS))
    plt.show()
    return a,b
    
def excelPerfPop(N,NP, CS,  time, iterations):
    #Input = Size of NxN grid, factor is death factor, number of time steps to iterate,radius of living cells
    #Output = Plot of surviving cells
    
    #Border area is represented as -1
    PopArray = []
    i = 0
    while i < iterations:
        Grid = newGridLayered(N)
        j = 0
        #randTime = np.random.randint(1,time)
        while j < i:
            PerfusionStep(Grid,NP,CS)[0]
            j = j+1
        PopArray.append((sum(sum(Grid[0]))/(N*N)))
        print(i)
        i = i+1
        
    df= pd.DataFrame(PopArray).T
    df.to_excel("PerfPop.xlsx")
    
def excelNVPop(N,NP, CS, VF, VFC, diff, time, iterations):
    #Input = Size of NxN grid, factor is death factor, number of time steps to iterate,radius of living cells
    #Output = Plot of surviving cells
    #factor = 0-1, modifies chance of nonperfusion
    #factor2 = size of non-perf events
    #factor3 = 0-1 diffusion
    #factor4 = max time pt might have diabetes
    
    #Border area is represented as -1
    PopArray = []
    i = 0
    a = 0
    gridPerf = newGridLayered(N)
    while i < iterations:
        Grid = newGridLayered(N)
        PerfusionStep(Grid,NP,CS)
        j = 0
        randTime = np.random.normal(time/2,time/10)
        round(randTime)
        while j <= randTime: 
            #PerfusionStep(Grid,NP,CS)
            VEGFStep(Grid,VF, VFC, diff)
            j = j+1
        print(j)
        print(i)
        area = sum(sum(Grid[2]))
        if area != 0:
            PopArray.append(area)
        i = i+1
        
     
    df= pd.DataFrame(PopArray).T
    df.to_excel("NVPop.xlsx")
    

def newGridScalloped(N):
    grid = newGrid(N)
    center = [N/2, N/2]
    NScal = [N/2, N]
    EScal = [N, N/2]
    WScal = [0, N/2]
    SScal = [N/2, 0]
    r = N/16
    
    for A in range(len(grid)):
        for B in range(len(grid[A])):
            if np.sqrt((A - NScal[0])**2 + (B - NScal[1])**2) < r:
                grid[A][B] = 0
            elif np.sqrt((A - EScal[0])**2 + (B - EScal[1])**2) < r:
                grid[A][B] = 0
            elif np.sqrt((A - WScal[0])**2 + (B - WScal[1])**2) < r:
                grid [A][B] = 0
            elif np.sqrt((A - SScal[0])**2 + (B - SScal[1])**2) < r:
                grid [A][B] = 0
                
    grid = KillCircleBorder(grid,N/2)
    
    return grid

def runSim(factor1):
    grid = newGrid(150)
    grid = KillCircleBorder(grid,75)
    #grid = newGridScalloped(150)
    i = 0
    while i <=70:
        if i == 0 or i == 10 or i ==40 or i == 70:
            plt.imshow(grid, cmap = cmap1)
            plt.axis('off')
            plt.show()
            PerfusionStep(grid,factor1)
            i = i+1            
        else:
            PerfusionStep(grid,factor1)
            i = i+1
            continue 
    
             
            

# fig = plt.figure()
# grid = newGridLayered(50)
# PerfusionStep(grid,0.1,1)
# ax = fig.add_subplot(111)
# ax.set_axis_off()
# bounds = [0,1,2,3]
# norm = colors.BoundaryNorm(bounds, cmap.N)

# im = plt.imshow(grid[1], cmap = cmap1, animated=True)


# def updatefig(i):
#     plt.imshow(grid[1], cmap = cmap1)
#     im.set_array(VEGFStep(grid,0.1, 0.1, 0.1)[2])
#     #print("step")
#     return im,


# ani = animation.FuncAnimation(fig, updatefig, frames = 20, interval=50, blit = True)
# plt.axis('off')
# plt.show()
# ani.save('sim.gif')

# # The animation function: called to produce a frame for each generation.
# def animate(i):
#     im.set_data(animate.grid)
#     animate.grid = VEGFStep(animate.grid,0.075, 0.075, 0.1)
# # Bind our grid to the identifier X in the animate function's namespace.
# animate.grid = grid

# # Interval between frames (ms).
# interval = 100
# anim = animation.FuncAnimation(fig, animate, interval=interval, frames=200)
# plt.show()

# # grid = KillCircleBorder(grid,75)

# # im = plt.imshow(grid, cmap = cmap1, animated=True)



# # def updatefig(i):
# #     plt.imshow(grid, cmap = cmap1)
# #     im.set_array(PerfusionStep(grid,0.2,10))
# #     return im,


# # ani = animation.FuncAnimation(fig, updatefig, frames = 70, save_count = 5, interval=100, blit=True)
# # plt.axis('off')
# # plt.show()
# # ani.save('sim.gif')
    
    
if __name__ == "__main__":
    # execute only if run as a script
    excelNVPop(5, 1, 0, 1, 1, 1, 1, 1)
