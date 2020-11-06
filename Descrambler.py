from PIL import Image
import numpy as np
import random
import math
import matplotlib.pyplot as plt
from multiprocessing import Pool
import sys
import os
import copy
from Timer import Timer


def function(x):
    return 50 / x

def addArray(a0, a1):
    i = 0
    while i < len(a0):
        a0[i] = a0[i] + a1[i]
        i += 1
    return a0

def tupleSubtract(t0, t1):
    r = []
    i = 0
    while i < len(t0):
        r.append(t0[i] - t1[i])
        i += 1
    return tuple(r)

def genMoveArray(start, end, maxLength = math.inf):
    """
    Creates a array that maps a move from start to end
    :param start: Start pos
    :param end: End pos
    :return: Array of positions the car enters during the move
    """

    def numSplit(num, parts):
        div = num // parts
        return_array = [div] * parts
        rem = num % parts
        for i in range(rem):
            return_array[i] += 1
        return return_array

    move = tupleSubtract(end, start)

    length = abs(move[0]) + abs(move[1])
    if length > maxLength:
        move = tuple((round(pos*(maxLength / length)) for pos in move))
        start = (end[0] - move[0], end[1] - move[1])

    currPos = list(start)
    if abs(move[0]) > abs(move[1]):
        p = (0, 1)
    else:
        p = (1, 0)

    arr = numSplit(abs(move[p[0]]), abs(move[p[1]]) + 1)
    retArr = [start]

    i = 0
    while True:
        # Do
        for increment in range(arr[i]):
            currPos[p[0]] += move[p[0]] / abs(move[p[0]])
            retArr.append((int(currPos[0]), int(currPos[1])))
        # While
        if i > (len(arr) - 2):
            break
        currPos[p[1]] += move[p[1]] / abs(move[p[1]])
        retArr.append((int(currPos[0]), int(currPos[1])))
        i += 1
    return retArr

def addPixel(scrambledArray, path, color):
    i = 0
    while i < len(path):
        pathPosition = path[len(path) - 1 - i]
        scrambledArray[pathPosition[0]][pathPosition[1]].append((color, function(i + 1)))
        i += 1

def calculateColorRow(pathArrayRow):
    return [calculateColor(pathArray) for pathArray in pathArrayRow]

def calculateColor(pathArray):
    if len(pathArray) == 0:
        return [255,255,255]

    finalSum = 0
    finalColor = [0,0,0]
    for path in pathArray:
        scaledColor = [val*path[1] for val in path[0]]
        finalColor = addArray(finalColor, scaledColor)
        finalSum += path[1]

    return tuple(round(x/finalSum) for x in finalColor)

def createPointLocationArray(dimTuple):
    a = []
    for r in range(dimTuple[0]):
        for c in range(dimTuple[1]):
            a.append((r,c))
    return a

def layoutPixelPaths(moveArray, moveArrayArgs, imageArray):
    pathArray = [[[] for x in range(len(imageArray[0]))] for x in range(len(imageArray))]
    while len(moveArray):
        move = moveArray.pop()
        match = moveArrayArgs.pop()
        color = imageArray[match[1][0]][match[1][1]]
        addPixel(pathArray, move, color)

    return pathArray

def moveArrayArguments(imageShape, cutoff, pathSize):
    pixelLocations = createPointLocationArray(imageShape)
    pixelLocationsRandom = random.sample([x for x in pixelLocations], imageShape[0] * imageShape[1])

    moveArrayArgs = []
    for i in range(len(pixelLocations)):
        color = imageArray[pixelLocations[i][0]][pixelLocations[i][1]]
        valid = [abs(val - 128) < cutoff for val in color]
        if sum(valid) == 3:
            moveArrayArgs.append((pixelLocationsRandom[i], pixelLocations[i], pathSize))

    return moveArrayArgs

if __name__ == '__main__':
    # Start Timer
    timer = Timer()
    timer.start()

    # Open photo
    photoFileName = 'wallCropped_AdjustedFinal.jpg'
    imageArray = np.array(Image.open(photoFileName))
    imageShape = imageArray.shape
    timer.step("Load Photo: ")

    moveArrayArgs = moveArrayArguments(imageShape, 50, 200)
    print("Number of Pixels to be moved: " + str(len(moveArrayArgs)))
    timer.step("Args creation: ")

    with Pool() as pool:
        moveArray = pool.starmap(genMoveArray, moveArrayArgs)
    timer.step("Move array created: ")

    pathArray = layoutPixelPaths(moveArray, moveArrayArgs, imageArray)
    timer.step("Laid out pixel paths: ")

    with Pool() as pool:
        finalImage = pool.map(calculateColorRow, pathArray)
    timer.step("Calculate colors in final Image: ")




    im = Image.fromarray(np.array(finalImage).astype('uint8'), 'RGB')
    im.show()
    im.save('momAndPop.png')
