import Processing
import copy
import numpy as np
from tkinter import *

root = Tk()
root.title("BoomBanger Dungeon Generator")

buttonArray = []
wallArray = []

# beginning page widgets
xLabel = Label(root, text="Dungeon Width (5ft per block)")
xLabel.grid(row=0, column=0)
yLabel = Label(root, text="Dungeon Length (5ft per block)")
yLabel.grid(row=1, column=0)
xBut = Scale(root, orient='horizontal', from_=5, to=20)
xBut.grid(row=0, column=1)
yBut = Scale(root, orient='horizontal', from_=5, to=20)
yBut.grid(row=1, column=1)


# gets dimensions of dungeon and creates it
def getXY():
    global buttonArray
    global wallArray

    buttonArray, wallArray = createMap(xBut.get(), yBut.get())
    # these destroy the startup screen buttons, allowing for map to take their place
    xLabel.destroy()
    yLabel.destroy()
    xBut.destroy()
    yBut.destroy()
    enter.destroy()

enter = Button(root, text="Generate Blank Dungeon Map", command=getXY)
enter.grid(row=2, column=0, columnspan=2)


# creates dungeon and gives 2d array of buttons and their color values
def createMap(x, y):
    # initializes the two arrays, button array and color/wall array
    array = []
    wArray = np.zeros((y,x))
    # generates the amount of buttons in each row and column for the button array
    for row in range(y):
        # yArray is each row, and once each row is done it gets appended to the final list
        yArray = []
        for col in range(x):
            sampleBut = Button(root, bg='black', height=4, width=10, command=lambda row=row, col=col: makeWalls(row, col))
            sampleBut.grid(row=row, column=col)
            yArray.append(sampleBut)
        array.append(yArray)

    return array, wArray


# this function runs whenever a button is pressed, it
# 1 in wallArray represents white, 0 represents black
def makeWalls(x, y):
    currentButton = buttonArray[x][y]
    currentColor = currentButton.cget('bg')
    if currentColor == 'white':
        buttonArray[x][y].config(bg='black')
        wallArray[x][y] = 0
    else:
        buttonArray[x][y].config(bg='white')
        wallArray[x][y] = 1


print("HI")
root.mainloop()
