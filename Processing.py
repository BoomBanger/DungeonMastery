from random import random
import numpy as np
import cv2

def getBorder(array):
    border = []
    border += list(array[0, :-1])
    border +=list(array[:-1, -1])
    border +=list(array[-1, :0:-1])
    border +=list(array[::-1, 0])
    return np.array(border)
    

def blobWithMaxArea(mask, noblobswithlotsofedges=False):
    numLabelsOut, labelsOut, statsOut, _ = cv2.connectedComponentsWithStats(mask, 8)
    sizes = statsOut[:, -1]
    min_size = 0
    label = np.zeros(labelsOut.shape, dtype="uint8")

    for i in range(numLabelsOut):
        img = np.zeros((labelsOut.shape))
        img[labelsOut == i] = 255
        val = sizes[i] / np.mean(getBorder(img)) if noblobswithlotsofedges else sizes[i]
        if val > min_size:
            label = img
            min_size = val

    return np.uint8(label)

def removeSmallBlobs(arr, area):
    numLabelsOut, labelsOut, statsOut, _ = cv2.connectedComponentsWithStats(arr, 8)
    sizes = statsOut[:, -1]
    min_size = area
    img = np.zeros(labelsOut.shape, dtype="uint8")
    
    for i in range(1,numLabelsOut):
        if(sizes[i] > min_size):
            img[labelsOut == i] = 255

    return img

def removeSmallBlobs(arr, area):
    numLabelsOut, labelsOut, statsOut, _ = cv2.connectedComponentsWithStats(arr, 8)
    sizes = statsOut[:, -1]
    min_size = area
    img = np.zeros(labelsOut.shape, dtype="uint8")
    
    for i in range(1,numLabelsOut):
        if(sizes[i] > min_size):
            img[labelsOut == i] = 255

    return img

def binary(arr):
    return cv2.inRange(arr, 128, 255)

def scale(arr, upscale):
    w = int(arr.shape[1]*upscale)
    h = int(arr.shape[0]*upscale)
    return cv2.resize(arr, (w, h), interpolation=cv2.INTER_NEAREST)

def smooth(arr, smoothingSize:int):
    kernel = np.ones((smoothingSize, smoothingSize)) / (smoothingSize * smoothingSize)
    arr = cv2.filter2D(arr, -1, kernel)
    return arr

def expand(array, size:int):
    arr = array[:,:]
    expanded = cv2.bitwise_not(array)
    expanded = cv2.dilate(expanded, np.ones((size, size)))
    expanded = binary(expanded)
    vals = np.random.rand(arr.shape[0], arr.shape[1])
    valExpand = vals * expanded / 255
    arr[valExpand > .99] = 0
    arr = cv2.bitwise_not(arr)
    arr = cv2.dilate(arr, np.ones((size,size)))
    arr = cv2.bitwise_not(arr)
    return arr

def contract(array, size:int):
    arr = array[:,:]
    contracted = array
    contracted = cv2.dilate(contracted, np.ones((size, size)))
    contracted = binary(contracted)
    vals = np.random.rand(arr.shape[0], arr.shape[1])
    valContract = vals * contracted / 255
    arr[valContract > .99] = 255
    arr = cv2.dilate(arr, np.ones((size,size)))
    return arr

def randomize(arr, size:int):
    arr = contract(arr, size)
    arr = expand(arr, size)
    return arr

def waves(arr, wavyness:int, smoothing:int):
    for w in range(wavyness, 1, -1):
        val = 2*w + 1
        arr = randomize(arr, val)
        arr = smooth(arr, int(smoothing / (2 * w)) * 2 + 1)
        arr = binary(arr)
        print(w)
    return arr

def process(array, upscale, smoothing, wavyness):
    array = np.float32(array) * 255
    array = scale(array, upscale)
    array = binary(array)
    array = waves(array, wavyness, smoothing)
    cv2.imwrite("img.png", array)

def cropBlob(blob):
    x, y, w, h = cv2.boundingRect(cv2.bitwise_not(blob))
    return blob[y:y+h, x:x+w]

def fromImage(file, upscale, smoothing, wavyness):
    img = cv2.imread(file)
    grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    lines = cv2.Canny(grey, 100, 200)
    lines = cv2.dilate(lines, np.ones((5,5)), iterations=6)
    lines = cropBlob(lines)
    dungeon = cv2.bitwise_not(lines)
    oldDungeon = np.array([])
    i = 0
    while oldDungeon.shape != dungeon.shape and i < 100:
        oldDungeon = dungeon
        dungeon = blobWithMaxArea(dungeon, True)
        dungeon = cropBlob(dungeon)
        i += 1
    process(dungeon / 255, upscale, smoothing, wavyness)
    
    
    
    
if __name__ == "__main__":
    """arr =   [[0, 1, 0, 0, 0, 0, 1, 1, 0, 0],
            [0, 1, 1, 1, 0, 0, 1, 1, 0, 0],
            [0, 1, 1, 1, 1, 1, 1, 0, 0, 0],
            [0, 1, 1, 1, 0, 0, 1, 0, 0, 0],
            [0, 0, 1, 0, 0, 1, 1, 1, 0, 0],
            [0, 0, 1, 1, 1, 1, 0, 1, 1, 1],
            [0, 0, 1, 0, 0, 1, 1, 1, 0, 0],
            [1, 1, 1, 0, 0, 0, 1, 0, 0, 0],
            [1, 1, 1, 0, 0, 1, 1, 1, 1, 1],
            [1, 1, 1, 0, 0, 1, 1, 1, 1, 1]]
    cv2.imshow("img", process(arr, 100, 10, 15))"""
    cv2.imshow("img.jpg", fromImage("Dungeon7.jpg"))
    cv2.waitKey(0)