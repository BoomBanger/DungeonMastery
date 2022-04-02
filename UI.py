import Processing
import copy
from tkinter import *
root = Tk()


sizeOfMapX = int(input("Enter X buttons: "))
sizeOfMapY = int(input("Enter Y buttons: "))
buttonArray = []


def createMap(x, y):
    array = []
    for row in range(y):
        yArray = []
        for col in range(x):
            sampleBut = Button(root, bg='white', command=lambda row=row, col=col: makeWalls(row, col))
            sampleBut.grid(row=row, column=col)
            yArray.append(sampleBut)
        array.append(yArray)
    return array


def makeWalls(x, y):
    print(x, y)


buttonArray = createMap(sizeOfMapX, sizeOfMapY)
print("HI")
root.mainloop()
