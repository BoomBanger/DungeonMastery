from random import random
import numpy as np
import cv2
from uritemplate import expand

def removeSmallBlobs(arr, area):
    numLabelsOut, labelsOut, statsOut, _ = cv2.connectedComponentsWithStats(arr, 8)
    sizes = statsOut[:, -1]
    min_size = area
    img = np.zeros(labelsOut.shape, dtype="uint8")
    
    for i in range(1,numLabelsOut):
        if(sizes[i] > min_size):
            img[labelsOut == i] = 255

    return img


def scale(arr, upscale):
    w = int(arr.shape[1]*upscale)
    h = int(arr.shape[0]*upscale)
    return cv2.resize(arr, (w, h), interpolation=cv2.INTER_NEAREST)

def smooth(arr, smoothingSize:int):
    kernel = np.ones((smoothingSize, smoothingSize)) / (smoothingSize * smoothingSize)
    arr = cv2.filter2D(arr, -1, kernel)
    return arr

def randomize(array, size:int):
    arr = array[:,:]
    expanded = cv2.bitwise_not(array)
    expanded = cv2.dilate(expanded, np.ones((size, size)))
    expanded = binary(expanded)
    vals = np.random.rand(arr.shape[0], arr.shape[1])
    vals *= expanded / 255
    arr[vals > .99] = 0
    arr = cv2.bitwise_not(arr)
    arr = cv2.dilate(arr, np.ones((size,size)))
    arr = removeSmallBlobs(arr, size*size*10)
    arr = cv2.bitwise_not(arr)
    return arr

def binary(arr):
    return cv2.inRange(arr, 128, 255)

def waves(arr, wavyness:int, smoothing:int):
    for w in range(wavyness, 1, -1):
        val = 2*w + 1
        arr = randomize(arr, val)
        arr = smooth(arr, int(smoothing / (2 * w)) * 2 + 1)
        arr = binary(arr)
    return arr

def process(array, upscale, smoothing, wavyness):
    array = np.float32(array) * 255
    array = scale(array, upscale)
    array = binary(array)
    array = waves(array, wavyness, smoothing)
    return array
    
    
    
if __name__ == "__main__":
    arr =   [[0, 1, 0, 0, 0, 0, 1, 1, 0, 0],
            [0, 1, 1, 1, 0, 0, 1, 1, 0, 0],
            [0, 1, 1, 1, 1, 1, 1, 0, 0, 0],
            [0, 1, 1, 1, 0, 0, 1, 0, 0, 0],
            [0, 0, 1, 0, 0, 1, 1, 1, 0, 0],
            [0, 0, 1, 1, 1, 1, 0, 1, 1, 1],
            [0, 0, 1, 0, 0, 1, 1, 1, 0, 0],
            [1, 1, 1, 0, 0, 0, 1, 0, 0, 0],
            [1, 1, 1, 0, 0, 1, 1, 1, 1, 1],
            [1, 1, 1, 0, 0, 1, 1, 1, 1, 1]]
    cv2.imshow("img", process(arr, 100, 50, 5))
    cv2.waitKey(0)