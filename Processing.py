import numpy as np
import cv2

def debugShow(img):
    cv2.imshow("img", img)
    cv2.waitKey(0)

#gets the values around the border of an array
def getBorder(array):
    border = []
    border += list(array[0, :-1])
    border +=list(array[:-1, -1])
    border +=list(array[-1, :0:-1])
    border +=list(array[::-1, 0])
    return np.array(border)
    
#gets largest blob in image, if noblobswithlotsofedges is true, prioritizes blobs that don't touch the edge often
def blobWithMaxArea(mask, noblobswithlotsofedges=False):
    numLabelsOut, labelsOut, statsOut, _ = cv2.connectedComponentsWithStats(mask, 8)
    sizes = statsOut[:, -1]
    min_size = 0
    label = np.zeros(labelsOut.shape, dtype="uint8")

    for i in range(numLabelsOut):
        img = np.zeros((labelsOut.shape))
        img[labelsOut == i] = 255
        val = sizes[i] / np.sqrt(np.mean(getBorder(img)) + 1) if noblobswithlotsofedges else sizes[i]
        if val > min_size:
            label = img
            min_size = val

    return np.uint8(label)

#removes blobs in image smaller than {area}
def removeSmallBlobs(arr, area):
    numLabelsOut, labelsOut, statsOut, _ = cv2.connectedComponentsWithStats(arr, 8)
    sizes = statsOut[:, -1]
    min_size = area
    img = np.zeros(labelsOut.shape, dtype="uint8")
    
    for i in range(1,numLabelsOut):
        if(sizes[i] > min_size):
            img[labelsOut == i] = 255

    return img

#if pixels are less than half bright, makes it black, if more than half bright, makes it white
def binary(arr):
    return cv2.inRange(arr, 128, 255)

#scales image to have a width of {width} pixels
def scale(arr, width):
    w = arr.shape[1]
    h = arr.shape[0]
    h, w = int(h * width/w), width
    img = cv2.resize(arr, (w, h), interpolation=cv2.INTER_NEAREST)
    cv2.imwrite("downscale.png", img)
    return img

#smooths walls
def smooth(arr, smoothingSize:int):
    kernel = np.ones((smoothingSize, smoothingSize)) / (smoothingSize * smoothingSize)
    arr = cv2.filter2D(arr, -1, kernel)
    return arr

#does expansion of walls as part of wavyness
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

#does contraction of walls as part of wavyness
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

#does random wavyness roughening
def randomize(arr, size:int):
    arr = contract(arr, size)
    arr = expand(arr, size)
    return arr

#does wavyness stuff on multiple scales with {wavyness} numbe rof operations
def waves(arr, wavyness:int, smoothing:int):
    step = int(wavyness / 7) + 1
    for w in range(wavyness, 1, -step):
        val = 2*w + 1
        arr = randomize(arr, val)
    return arr

#draws grid on {arr} with a spacing of {width} pixels
def drawGrid(arr, width:int, color:str):
    if width:
        col = {"Black": (0, 0, 0),
            "White": (255, 255, 255),
            "Gray": (128, 128, 128),
            "Blue:": (255, 0, 0),
            "Red": (0, 0, 255),
            "Yellow": (0, 255, 255),
            "Orange": (0, 255, 165),
            "Purple": (250, 230, 230),
            "Green": (0, 255, 0)}
        if len(arr.shape) == 2:
            h, w = arr.shape
            arr = cv2.cvtColor(arr, cv2.COLOR_GRAY2BGR)
        else:
            h, w, _ = arr.shape
        for x in range(0, w, width):
            cv2.line(arr, (x, 0), (x, h), col[color])
        for y in range(0, h, width):
            cv2.line(arr, (0, y), (w, y), col[color])

    return arr

#process image and save it in img.png
#upscale: width of the target image
#smoothing: how round you want it to be
#wavyness: how bumpy you want it to be
#gridWidth: pixel width between gridlines. 0 is no grid
def process(array, upscale, smoothing, wavyness):
    smoothing = smoothing * 2 + 1
    wavyness = wavyness * 2 + 1
    array = np.float32(array) * 255
    array = scale(array, upscale)
    array = binary(array)
    array = waves(array, wavyness, smoothing)
    array = smooth(array, smoothing)
    array = binary(array)
    cv2.imwrite("img.png", array)
    return array

#crop all bordering black pixels out of {blob}
def cropBlob(blob):
    x, y, w, h = cv2.boundingRect(cv2.bitwise_not(blob))
    return blob[y:y+h, x:x+w]

#get wall array of 1s and 0s from image located at {file}
def fromImage(file):
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
    return dungeon / 255
    
def downloadImg(array, file):
    cv2.imwrite(file, array)
    

def length(array, m, x, y):
    h, w = array.shape
    line = lambda X: m * (X - x) + y
    roundLine = lambda X: int(np.round(line(X)))
    inBounds = lambda X, Y: 1 <= X and X < w - 1 and 1 <= Y and Y < h - 1
    isDark = lambda X, Y: array[Y, X] <= 128
    edge = lambda X: not inBounds(X, roundLine(X)) or isDark(X, roundLine(X))
    
    xMin, xMax = x, x
    while not edge(xMax): 
        xMax += 1
    while not edge(xMin): 
        xMin -= 1
    xMax -= 1
    xMin += 1
    dx = xMax - xMin
    dy = line(xMax) - line(xMin)
    edges = cv2.Canny(array, 100, 200)
    notEdge = lambda X, Y: edges[Y, X] <= 128
    notByEdge = lambda X, Y: inBounds(X, Y) and (notEdge(X, Y) and notEdge(X+1, Y) and notEdge(X-1, Y) and notEdge(X, Y-1) and notEdge(X, Y + 1))
    yMin = roundLine(xMin)
    yMax = roundLine(xMax)
    direction = -np.sign(yMax - yMin)
    if direction:
        if isDark(xMin, yMin):
            while notByEdge(xMin, yMin):
                yMin -= direction
        else:
            while notByEdge(xMin, yMin): 
                yMin += direction
        if isDark(xMax, yMax):
            while notByEdge(xMax, yMax):
                yMax += direction
        else:
            while notByEdge(xMax, yMax): 
                yMax -= direction
        
    return np.sqrt(dx**2 + dy**2), (xMin, yMin), (xMax, yMax)
    
    
def addDoor(array, color, door):
    x, y = door
    if not array[y,x]:
        print("no door")
        return color
    bestPoints1 = (0,0)
    bestPoints2 = (0,0)
    bestLength = np.inf
    for angle in np.linspace(0, np.pi, num=50):
        m = np.tan(angle)
        l, pt1, pt2 = length(array, m, x, y)
        if l < bestLength:
            bestLength = l
            bestPoints1 = pt1
            bestPoints2 = pt2
    cv2.line(color, bestPoints1, bestPoints2, (42, 42, 165), thickness=5)
    return color
    
def addNumbers(color, numbers, fontSize, fileLocation):
    if not fileLocation:
        for i, (x, y, description) in enumerate(numbers):
            cv2.putText(color, "#" + str(i + 1), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (128, 128, 128), thickness=fontSize)
        return color
    with open(fileLocation, "w") as f:
        for i, (x, y, description) in enumerate(numbers):
            cv2.putText(color, "#" + str(i + 1), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (128, 128, 128), thickness=fontSize)
            f.write("#" + str(i) + "\n\n" + description + "\n\n\n")
    return color

def rescale(scale, point):
    x, y = point[0], point[1]
    x *= scale
    y *= scale
    x, y = int(np.round(x)), int(np.round(y))
    if len(point) > 2:
        des = point[2]
        return x, y, des
    return x, y
    
def rescaleList(scale, points):
    newList = []
    for point in points:
        newList.append(rescale(scale, point))
    return newList

def addPoints(array, scale, doors, numbers, fontSize, fileLocation=None):
    color = cv2.cvtColor(array, cv2.COLOR_GRAY2BGR)
    doors = rescaleList(scale, doors)
    numbers = rescaleList(scale, numbers)
    for door in doors:
        color = addDoor(array, color, door)
    color = addNumbers(color, numbers, fontSize, fileLocation)
    return color
    
if __name__ == "__main__":
    arr =   [[0, 1, 0, 0, 0, 0, 1, 1, 0, 0],
            [0, 1, 1, 1, 0, 0, 1, 1, 0, 0],
            [0, 1, 1, 1, 1, 1, 1, 0, 0, 0],
            [0, 1, 1, 1, 0, 0, 1, 0, 0, 0],
            [0, 0, 1, 0, 0, 1, 1, 1, 0, 0],
            [0, 0, 1, 1, 1, 1, 0, 1, 1, 1],
            [0, 0, 1, 0, 0, 1, 1, 1, 0, 0],
            [1, 1, 1, 0, 0, 0, 1, 0, 0, 0]]
    img =process(arr, 500, 0, 0)
    img = addPoints(img, 50, [(4.5, 2.5), (6.4, 4.5)],[(1, 2, "cool thing here"), (3, 4, "bad thing here")], 1)
    img = drawGrid(img, 50, "Gray")
    cv2.imshow("img.jpg", img)
    cv2.waitKey(0)