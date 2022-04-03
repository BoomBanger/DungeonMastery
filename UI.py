import tkinter.filedialog

import Processing
import numpy as np
import cv2
from tkinter import *
from PIL import ImageTk, Image

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

    refineMap.grid(row=0, column=xBut.get()+1)
    # these removes the startup screen buttons, allowing for map to take their place
    xLabel.grid_forget()
    yLabel.grid_forget()
    xBut.grid_forget()
    yBut.grid_forget()
    enter.grid_forget()
    enterPic.grid_forget()


enter = Button(root, text="Generate Blank Dungeon Map", command=getXY)
enter.grid(row=2, column=0, columnspan=2)



# this section is the photo processing section
def runPhotoProcess():
    global wallArray
    imgPath = imgLabel.cget('text')
    imgPath = imgPath[24:]
    print(imgPath)
    wallArray = Processing.fromImage(imgPath)
    goToProcess(2)

# brings user to the image upload/selection screen
def picScreen():
    # removes unneeded widgets
    xLabel.grid_forget()
    yLabel.grid_forget()
    xBut.grid_forget()
    yBut.grid_forget()
    enter.grid_forget()
    enterPic.grid_forget()

    instructions.grid(row=0, column=0)
    selectBut.grid(row=1, column=0)
    imgLabel.grid(row=2, column=0)


# runs all the update screen information once a user selects a photo
def getImage():
    picId = tkinter.filedialog.askopenfilename()
    imgLabel.config(text='Your image location is: ' + picId)
    img = Image.open(picId)

    tkimage = ImageTk.PhotoImage(img)
    aspectRatio = tkimage.height()/tkimage.width()

    resized_image = img.resize((300, int(300 * aspectRatio)), Image.Resampling.LANCZOS)
    new_image = ImageTk.PhotoImage(resized_image)
    picLabel.image = new_image
    picLabel.config(image=new_image)
    picLabel.grid(row=3, column=0)
    contin.grid(row=4, column=0)


# all of these widgets are used/related to the picture dungeon creation tool
instructions = Label(root, text='Please select an image using the button below that you would like to convert into '
                                'a dungeon.\nMake sure the image has clear lines and is drawn on a white background '
                                'with either a pencil or other dark colored utensil.')
enterPic = Button(root, text="Generate Dungeon Using Picture", command=picScreen)
enterPic.grid(row=3, column=0, columnspan=2)
selectBut = Button(root, text="Select Image", command=getImage)
imgLabel = Label(root, text="Your image location is: ")
picLabel = Label(root)
contin = Button(root, text="Submit Photo", command=runPhotoProcess)


# updates the image to match specifications user makes with widgets
def process(x):
    scale = scaleSlid.get()
    smooth = smoothSlid.get()
    rough = roughSlid.get()
    gridWid = gridWidSlid.get()
    gridColor = color.get()  # add to processing later, QoL
    Processing.process(wallArray, scale, smooth, rough, gridWid)

    map = Image.open("img.png")
    tkmap = ImageTk.PhotoImage(map)
    aspectRatio = tkmap.height() / tkmap.width()
    resized_map = map.resize((300, int(300 * aspectRatio)), Image.Resampling.LANCZOS)
    new_map = ImageTk.PhotoImage(resized_map)
    mapLab.image = new_map
    mapLab.config(image=new_map)
    mapLab.grid(row=0, rowspan=7, column=3)

# creation of all the image editing widgets
scaleLab = Label(root, text="Scale (width of picture in pixels)")
scaleSlid = Scale(root, orient=HORIZONTAL, length=150, resolution=10, from_=500, to=1500, command=process)
smoothLab = Label(root, text="Smoothness (Higher means more rounded)")
smoothSlid = Scale(root, orient=HORIZONTAL, length=150, from_=0, to=50, command=process)
roughLab = Label(root, text="Bumpiness (Higher means more bumps")
roughSlid = Scale(root, orient=HORIZONTAL, length=150, from_=0, to=20, command=process)
gridWidLab = Label(root, text="Determines how many pixels a grid square is")
gridWidSlid = Scale(root, orient=HORIZONTAL, length=150, from_=0, to=50, command=process)
gridColLab = Label(root, text="Determines the color of the grid lines")
color = StringVar(root)
color.set("Gray")  # default color for grid lines
gridColDrop = OptionMenu(root, color, "Black", "White", "Gray", "Blue", "Red",
                         "Yellow", "Orange", "Purple", "Green", command=process)
mapLab = Label(root)

# runs the image generation on the user created dungeon layout:   1 is non-photo, 2 is photo
def goToProcess(preset):
    print(wallArray)
    if preset == 1:
        # hiding widgets in square draw path
        refineMap.grid_forget()
        for ro in buttonArray:
            for but in ro:
                but.grid_forget()
    elif preset == 2:
        instructions.grid_forget()
        selectBut.grid_forget()
        imgLabel.grid_forget()
        picLabel.grid_forget()
        contin.grid_forget()

    # scaling(from comp 10-1000, from pic ), smoothing(0-tbd), roughness(0-tbd), gridwidth(0-tbd), gridcolor(tbd)
    scaleLab.grid(row=0, column=0)
    scaleSlid.grid(row=0, column=1)
    smoothLab.grid(row=1, column=0)
    smoothSlid.grid(row=1, column=1)
    roughLab.grid(row=2, column=0)
    roughSlid.grid(row=2, column=1)
    gridWidLab.grid(row=3, column=0)
    gridWidSlid.grid(row=3, column=1)
    gridColLab.grid(row=4, column=0)
    gridColDrop.grid(row=4, column=1)


refineMap = Button(root, text="Process User-Drawn Map", height=2, width=20, command=lambda: goToProcess(1))


# creates dungeon and gives 2d array of buttons and their color values
def createMap(x, y):
    # initializes the two arrays, button array and color/wall array
    array = []
    wArray = np.zeros((y,x))
    # if statement scales size of buttons to how many buttons there are
    h = 4
    w = 10
    if x > 15 or y > 15:
        h = 2
        w = 5
    elif x > 10 or y > 10:
        h = 3
        w = 7
    else:
        h = h
        w = w
    # generates the amount of buttons in each row and column for the button array
    for row in range(y):
        # yArray is each row, and once each row is done it gets appended to the final list
        yArray = []
        for col in range(x):
            sampleBut = Button(root, bg='black', height=h, width=w, command=lambda row=row, col=col: makeWalls(row, col))
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
# roadmap of program looks like
