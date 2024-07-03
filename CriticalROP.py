import random
import numpy
import matplotlib.pyplot as plt
import os
from matplotlib import colors 



def randomAtRadius(radius, seedX, seedY):
    theta = 2*numpy.pi*random.random() #generate random theta
    x=int(radius*numpy.cos(theta))+seedX #use trig to transfer into X
    y=int(radius*numpy.sin(theta))+seedY #find Y coordinate
    location=[x, y] #save locaction
    return location

def nonRandomAtRadius(radius, theta, seedX, seedY):
    #theta = 2*numpy.pi*random.random() #generate random theta
    x=int(radius*numpy.cos(theta))+seedX #use trig to transfer into X
    y=int(radius*numpy.sin(theta))+seedY #find Y coordinate
    location=[x, y] #save locaction
    return location

def checkAround(location,deflector, squareSize,matrix):
    foundFriend = False #found another particle
    exitCircle = False #reached the required radius
    nearEdge=False #near the edge of the field
    
    
    # Check if a walker is near the edge
    if (location[1] + 1) > squareSize - 1 or (location[1] - 1) < 1 or (location[0] + 1) > squareSize - 1 or (location[0] - 1) < 1:
        nearEdge = True

    # If not near the edge, check if the walker is near a neighbor or reached the required radius
    # location[1]=row, location[2]=column
    if not nearEdge:
        neighborDown = matrix[location[1]+1,location[0]]
        if neighborDown == 1:
            foundFriend = True
        if neighborDown == 2:
            exitCircle = True

        neighborUp=matrix[location[1]-1,location[0]]
        if neighborUp==1:
            foundFriend=True
        if neighborUp==2:
            exitCircle=True

        neighborRight=matrix[location[1],location[0]+1]
        if neighborRight==1:
            foundFriend=True
        if neighborRight==2:
            exitCircle=True

        neighborLeft=matrix[location[1],location[0]-1]
        if neighborLeft==1:
            foundFriend=True
        if neighborLeft==2:
            exitCircle=True

    # After checking locations, if locations are good, start the random walk
    if not foundFriend and not nearEdge:
        DeflectX = deflector[0] - location[0]
        DeflectY = deflector[1] - location[1]
        #DistanceDeflect = 0
        DistanceDeflect = (DeflectX**2 + DeflectY**2)**0.5
        # if DistanceDeflect == 0:
        #     DeflectXChance = 0
        #     DeflectYChance = 0
        # else:
        #     DeflectXFrac = DeflectX/(DistanceDeflect)
        #     DeflectYFrac = DeflectY/(DistanceDeflect)
        #     DeflectXChance = DeflectXFrac/(DistanceDeflect)
        #     DeflectYChance = DeflectYFrac/(DistanceDeflect)
        # direction = ['N','S','E','W']
        # directionWeights = [1 + DeflectYChance,1-DeflectYChance,1-DeflectXChance,1+DeflectXChance]
        # decide = random.choices(direction, weights = directionWeights)


        direction = []
        #Hardcode area of 10 for now because you're bad at coding
        #If the walker is within 10 of the deflector, tell it to go away
        #rand = 
        if DistanceDeflect !=0:
            if DistanceDeflect < 20:
                if random.random() > 1/DistanceDeflect:
                    if DeflectX >= 0:
                        direction.append('E')
                    elif DeflectX < 0:
                        direction.append('W')
                    if DeflectY >= 0:
                        direction.append('N')
                    elif DeflectY < 0 :
                        direction.append('S')
                else:
                    direction = ['N','S','E','W']
            else:
                direction = ['N','S','E','W']
        else:
            direction = ['N','S','E','W']
        decide = random.choices(direction)
        if decide == ['W']:
            location = [location[0] + 1,location[1]]
        elif decide == ['E']:
            location = [location[0] - 1,location[1]]
        elif decide == ['N']:
            location = [location[0],location[1] - 1]
        elif decide == ['S']:
            location = [location[0],location[1] + 1]
        else:
            print(decide)

    return (location, foundFriend, nearEdge, exitCircle)

def DLAcluster(radius, needGif=True):
    
    #check if folder "images" exists, and if not - create it
    if not os.path.isdir("images"):
        os.mkdir("images")
    
    if needGif:
        #Import there libraries if intend to save gif
        import imageio

    
    #initialize variables that are dependent upon the radius
    # note - we add 2 to the parameters to get a thick broder between the edges of the disk and square
    # x coordinate of origin for a seed particle where a random value will be added to it
    seedX = radius
    # y coordinate of a seed
    seedY = radius 
    # size of the grid to account for field of wandering around
    squareSize = radius*2+4
    #Set the fovea at the center
    deflector = [seedX,seedY]

    matrix=numpy.zeros((squareSize, squareSize))
    matrixPerf = numpy.zeros((squareSize,squareSize))

    for row in range (0,squareSize):
        for col in range (0,squareSize):
            #put a seed particle, add 7 to the X to simulate initating location of optic nerve
            if row==seedY and col==seedX - (radius/4): 
                matrix[row][col]=1
            #define field outside of circle
            elif numpy.sqrt((seedX-col)**2+(seedY-row)**2)>radius:
                matrix[row][col]=5
    matrix[deflector[1]][deflector[0]] = 4
    cvals = [0,1,2,3,4]
    #color = ['orange', 'red', 'red', 'black', 'red']
    #norm = plt.Normalize(min(cvals), max(cvals))
    #tuples = list(zip(map(norm,cvals),color))
    #cmap = colors.LinearSegmentedColormap.from_list("",tuples)
    # 0= unperfused retina, 1 = perfused retina, 2= vessel, 3 = border
    cmap = colors.ListedColormap(['linen','pink', 'red','black', 'navy'])
    #cmap = plt.cm.Pastel1
    # Initialize the random walker counter
    randomWalkersCount = 0

    # Set the cluster to NOT be complete
    completeCluster = False

    # Start running random walkers
    addedCount=0 #keep track of number added

    # initialize array for the used interval for graphing
    usedInterval=[]
    theta = 18
    
    while not completeCluster:
        # Release a walker
        randomWalkersCount += 1
        random.seed()

        # Generate a (Xstart, Ystart) for walker, need within radius
        # Only generate a new walker from unperfused retina
        NonPerf = False
        
               
        while not NonPerf:
            #Sequentially release a random walker at every 10 degrees
            rand = random.random()
            randRad = radius * rand
            location=nonRandomAtRadius(randRad, ((theta % 36)/36)*(numpy.pi *2), seedX, seedY)
            theta+=1
            
            #location = nonRandomAtRadius(radius, theta)
            if matrixPerf[location[1]][location[0]] != 1:
                NonPerf = True

        # Initialize variables, like Friend tag and near edge identifier
        foundFriend = False #not near other particle
        nearEdge=False #not near the edge of the field

        #ROP simulation step; after a certain point, reduce chance of adding more VEGF by 60%
        if addedCount > 12000 and random.rand() <0.4:
            nearEdge = True

        # Set an individual walker out, stop if found a 'friend', give up if it reached the edge of the board
        while not foundFriend and not nearEdge:
            # Run the checking/walking function
            locationNew,foundFriend, nearEdge, exitCircle = checkAround(location,deflector,squareSize,matrix)

            # Add to the cluster if near a friend
            if foundFriend:
                # current location, replace with 1 and stop, and perfuse surrounding retina
                matrix[location[1]][location[0]] = 1
                matrixPerf[location[1]][location[0]] = 1
                #perfRadius is how much surrounding tissue is perfused by a vessel. For now just scale by size of retina
                perfRadius = round(radius/10)
                for dx in list(range(-1*perfRadius, perfRadius)):
                    for dy in list(range(-1*perfRadius, perfRadius)):
                        try:
                            matrixPerf[(location[1]+dx),(location[0]+dy)] = 1        
                        except IndexError:
                                pass
                addedCount+=1
                #matrix[deflector[1]][deflector[0]] = 5
                #completePerf = numpy.sum(matrixPerf)/(numpy.pi*(radius**2)) >0.75

            # Otherwise, save the location
            else:
                location = locationNew
        
        #print update 
        intervalSavePic=range(2,30000,100)
        if randomWalkersCount in intervalSavePic:
            print("still working, have added ", randomWalkersCount, " random walkers.", " Added to cluster: ", addedCount)
        if needGif:
            if randomWalkersCount in intervalSavePic:
                print("save picture")
                usedInterval.append(randomWalkersCount) #append to the used count
                label=str(randomWalkersCount)
                plt.title("DLA Cluster", fontsize=20)
                finalMatrix = matrix + matrixPerf
                for row in range (0,squareSize):
                    for col in range (0,squareSize):
                        #repaint outside of circle as neutral color again
                        if numpy.sqrt((seedX-col)**2+(seedY-row)**2)>radius:
                            matrix[row][col]=3
                plt.matshow(finalMatrix, interpolation='nearest',cmap=cmap)#plt.cm.Blues) #ocean, Paired
                #plt.matshow(matrixPerf, interpolation='nearest',cmap=cmap)
                # plt.xlabel("direction, $x$", fontsize=15)
                # plt.ylabel("direction, $y$", fontsize=15)
                plt.axis('off')
                plt.savefig("images/cluster{}.png".format(label), dpi=200)
                plt.close()
       
        if randomWalkersCount==15000:
            print("CAUTION: had to break the cycle, taking too many iterations")
            completeCluster = True

    # Once it finds a friend and leaves the previous loop, we must check if it
    # is also touching a circular wall. If so, we have a complete cluster
    if foundFriend or nearEdge:
        print("Random walkers in the cluster: ",addedCount)
        completeCluster = True
    
    #plt.title("Retinal Vasculogenesis", fontsize=20)
    plt.matshow(finalMatrix, interpolation='nearest',cmap=cmap)#plt.cm.Blues) #ocean, Paired
    #plt.xlabel("direction, $x$", fontsize=15)
    #plt.ylabel("direction, $y$", fontsize=15)
    plt.axis('off')
    plt.savefig("images/cluster.png", dpi=200)
    plt.close()

    print(usedInterval)

    if needGif:
        with imageio.get_writer('images/movie.gif', mode='I') as writer:
            for i in usedInterval:
                filename="images/cluster"+str(i)+".png"
                image = imageio.imread(filename)
                writer.append_data(image)
                os.remove(filename)
            image = imageio.imread("images/cluster.png")
            writer.append_data(image)

    return addedCount, matrix