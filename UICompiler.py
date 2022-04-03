import tkinter.filedialog
import tkinter.font

import Processing
import numpy as np
from tkinter import *
from PIL import ImageTk, Image
import platform
if platform.system() == "Darwin":
    from tkmacosx import Button

root = Tk()
root.title("Dungeon Mastery")
buttonArray = []
wallArray = []
sampleArray = []
listOfDoorDrags = []
listOfNumDrags = []
mapOldNewWidthRatio = 0
activeDraggable = None
finalPic = ["LOL PICTURE GOES HERE"]

# beginning page widgets
dunLab = Label(root, text='Dungeon Mastery', font=('Parchment', 30), fg='green')
dunLab.grid(row=0, column=0, columnspan=2)
xLabel = Label(root, text="Layout Width (5ft per block)")
xLabel.grid(row=1, column=0)
yLabel = Label(root, text="Layout Height (5ft per block)")
yLabel.grid(row=2, column=0)
xBut = Scale(root, orient='horizontal', from_=5, to=20)
xBut.grid(row=1, column=1)
yBut = Scale(root, orient='horizontal', from_=5, to=20)
yBut.grid(row=2, column=1)


class Draggable:
    def __init__(self, canvas, x, y, r, ):
        self.x = x
        self.y = y
        self.description = None
        self.canvas = canvas
        self.mouseX = None
        self.mouseY = None
        self.marker = canvas.create_oval(x-r, y-r, x+r, y+r, fill='gray')
        canvas.tag_bind(self.marker, "<ButtonPress-1>", self.startDrag)
        canvas.tag_bind(self.marker, "<ButtonRelease-1>", self.stopDrag)
        canvas.tag_bind(self.marker, "<B1-Motion>", self.drag)

    def getTuple(self):
        if self.description is not None:
            return self.x, self.y, self.description
        return self.x, self.y

    def changePos(self, dx, dy):
        self.x += dx
        self.y += dy
        self.canvas.move(self.marker, dx, dy)

    def startDrag(self, event):
        global activeDraggable
        self.mouseX = event.x
        self.mouseY = event.y
        activeDraggable = self
        canProcess(0)
        onClick()

    def stopDrag(self, event):
        self.mouseX = None
        self.mouseY = None
        self.isTrash()
        canProcess(0)

    def drag(self, event):
        if self.mouseX is not None and self.mouseY is not None:
            dx = event.x - self.mouseX
            dy = event.y - self.mouseY
            self.changePos(dx, dy)
            self.mouseX = event.x
            self.mouseY = event.y
            canProcess(0)

    def isTrash(self):
        if self.x > 400 and self.y > 300:
            self.canvas.delete(self.marker)
            if self in listOfNumDrags:
                listOfNumDrags.remove(self)
            elif self in listOfDoorDrags:
                listOfDoorDrags.remove(self)


# gets dimensions of dungeon and creates it
def getXY():
    global buttonArray
    global wallArray

    buttonArray, wallArray = createMap(xBut.get(), yBut.get())

    refineMap.grid(row=0, column=xBut.get()+1)
    backCompStart.grid(row=yBut.get()-1, column=xBut.get()+1)
    # these removes the startup screen buttons, allowing for map to take their place
    dunLab.grid_forget()
    xLabel.grid_forget()
    yLabel.grid_forget()
    xBut.grid_forget()
    yBut.grid_forget()
    enter.grid_forget()
    enterPic.grid_forget()


enter = Button(root, text="Generate Blank Layout Map", command=getXY)
enter.grid(row=3, column=0, columnspan=2)


def startWidgets():
    dunLab.grid(row=0, column=0, columnspan=2)
    xLabel.grid(row=1, column=0)
    yLabel.grid(row=2, column=0)
    xBut.grid(row=1, column=1)
    yBut.grid(row=2, column=1)
    enter.grid(row=3, column=0, columnspan=2)
    enterPic.grid(row=4, column=0, columnspan=2)



# contains all the back button widget info -- 1 is comp back, 2 is converge back, 3 is photo back, 4 is downscale back,
# 5 is canvas to start, # 6 is from final canvas downloads to start
def backButtons(preset):
    # for comp draw back to start screen
    if preset == 1:
        # removing unnecessary widgets
        refineMap.grid_forget()
        for ro in buttonArray:
            for but in ro:
                but.grid_forget()
        backCompStart.grid_forget()
        # placing widgets back on start screen
        startWidgets()
    elif preset == 2:
        # removing unnecessary widgets
        scaleLab.grid_forget()
        scaleSlid.grid_forget()
        smoothLab.grid_forget()
        smoothSlid.grid_forget()
        roughLab.grid_forget()
        roughSlid.grid_forget()
        mapLab.grid_forget()
        generateLab.grid_forget()
        generateBut.grid_forget()
        downloadBut.grid_forget()
        backConvergeStart.grid_forget()
        detailBut.grid_forget()
        # placing widgets back on start screen
        startWidgets()
    elif preset == 3:
        # removing unnecessary widgets
        instructions.grid_forget()
        selectBut.grid_forget()
        imgLabel.grid_forget()
        picLabel.grid_forget()
        contin.grid_forget()
        downSizBut.grid_forget()
        downLab.grid_forget()
        backPicStart.grid_forget()
        # placing widgets back on start screen
        startWidgets()
    elif preset == 4:
        # removing unnecessary widgets
        downScalSlid.grid_forget()
        downScalLab.grid_forget()
        downScalBut.grid_forget()
        backScalePic.grid_forget()
        # placing widgets back of pic select screen
        instructions.grid(row=0, column=0, columnspan=2)
        selectBut.grid(row=1, column=0, columnspan=2)
        imgLabel.grid(row=2, column=0, columnspan=2)
    elif preset == 5:
        global listOfDoorDrags
        global listOfNumDrags
        # removing unnecessary widgets
        gridWidLab.grid_forget()
        gridWidSlid.grid_forget()
        gridColLab.grid_forget()
        gridColDrop.grid_forget()
        picBackground.grid_forget()
        doorLab.grid_forget()
        doorBut.grid_forget()
        markLab.grid_forget()
        markBut.grid_forget()
        descLab.grid_forget()
        descEnt.grid_forget()
        backCanStart.grid_forget()
        compiBut.grid_forget()
        startWidgets()
        listOfDoorDrags = []
        listOfNumDrags = []

# this section is the photo processing section
def runPhotoProcess():
    global wallArray
    imgPath = imgLabel.cget('text')
    imgPath = imgPath[24:]
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
    dunLab.grid_forget()

    instructions.grid(row=0, column=0, columnspan=2)
    selectBut.grid(row=1, column=0, columnspan=2)
    imgLabel.grid(row=2, column=0, columnspan=2)


def downScaleProcess(x):
    global sampleArray
    sampleArray = Processing.scale(wallArray, int(x))


def downscaling():
    global wallArray
    imgPath = imgLabel.cget('text')
    imgPath = imgPath[24:]
    wallArray = Processing.fromImage(imgPath)

    # removing unnecessary widgets
    instructions.grid_forget()
    selectBut.grid_forget()
    imgLabel.grid_forget()
    picLabel.grid_forget()
    contin.grid_forget()
    downSizBut.grid_forget()
    downLab.grid_forget()
    backPicStart.grid_forget()

    downScalSlid.grid(row=0, column=0, columnspan=2)
    downScalLab.grid(row=1, column=0, columnspan=2)
    downScalBut.grid(row=2, column=1)
    backScalePic.grid(row=2, column=0)

    downScaleProcess(30)

downScalSlid = Scale(root, orient=HORIZONTAL, from_=30, to=100, command=downScaleProcess)
downScalLab = Label(root, text="The values on the slider represent the width"
                               "\nof the image in pixels. 30 pixels in width"
                               "\nis the minimum and 100 pixels is the max.")
downScalBut = Button(root, text='Downscale', command=lambda: goToProcess(3))
backScalePic = Button(root, text='Back to Picture Select', command=lambda: backButtons(4))


# final function of program, leads to canvas
def toDetail():
    # removes unnecessary widgets
    scaleLab.grid_forget()
    scaleSlid.grid_forget()
    smoothLab.grid_forget()
    smoothSlid.grid_forget()
    roughLab.grid_forget()
    roughSlid.grid_forget()
    mapLab.grid_forget()
    generateLab.grid_forget()
    generateBut.grid_forget()
    downloadBut.grid_forget()
    backConvergeStart.grid_forget()
    detailBut.grid_forget()
    # starts canvas file
    startCanvas()


# runs all the update screen information once a user selects a photo
def getImage():
    picId = tkinter.filedialog.askopenfilename()
    if picId:
        imgLabel.config(text='Your image location is: ' + picId)
        img = Image.open(picId)

        tkimage = ImageTk.PhotoImage(img)
        aspectRatio = tkimage.height()/tkimage.width()

        resized_image = img.resize((300, int(300 * aspectRatio)))
        new_image = ImageTk.PhotoImage(resized_image)
        picLabel.image = new_image
        picLabel.config(image=new_image)
        picLabel.grid(row=3, column=0, rowspan=4)
        contin.grid(row=3, column=1)
        downSizBut.grid(row=4, column=1)
        downLab.grid(row=5, column=1)
        backPicStart.grid(row=6, column=1)


# all of these widgets are used/related to the picture dungeon creation tool
instructions = Label(root, text='Please select an image using the button below that you would like to convert into '
                                'a layout.\nMake sure the image has clear lines and is drawn on a white background '
                                'with a dark colored utensil. \n The image must be cropped such that the entrances'
                                'and exits touch the edge of the picture')
enterPic = Button(root, text="Generate Layout from Picture", command=picScreen)
enterPic.grid(row=4, column=0, columnspan=2)
selectBut = Button(root, text="Select Image", command=getImage)
imgLabel = Label(root, text="Your image location is: ")
picLabel = Label(root)
contin = Button(root, text="Submit Photo \n(Skip Downscaling)", command=runPhotoProcess)
downSizBut = Button(root, text="Downscale Photo", command=downscaling)
downLab = Label(root, text="Downscaling decreases the photo's resolution for better map imagery "
                           "\n                                                                    "
                           "\n"
                           "\n"
                           "\n"
                           "\n")
backPicStart = Button(root, text='Back to Start', command=lambda: backButtons(3))


def downloadPic():
    file = tkinter.filedialog.asksaveasfilename()
    if file: Processing.downloadImg(finalPic, file)


# updates the image to match specifications user makes with widgets
def process(x):
    global finalPic
    scale = scaleSlid.get()
    smooth = smoothSlid.get()
    rough = roughSlid.get()
    finalPic = Processing.process(wallArray, scale, smooth, rough)

    map = Image.open("img.png")
    tkmap = ImageTk.PhotoImage(map)
    aspectRatio = tkmap.height() / tkmap.width()
    resized_map = map.resize((300, int(300 * aspectRatio)))
    new_map = ImageTk.PhotoImage(resized_map)
    mapLab.image = new_map
    mapLab.config(image=new_map)
    mapLab.grid(row=0, rowspan=7, column=3)


# creation of all the image editing widgets
scaleLab = Label(root, text="Scale (width of picture in pixels)")
scaleSlid = Scale(root, orient=HORIZONTAL, length=150, resolution=10, from_=500, to=1500, command=process)
smoothLab = Label(root, text="Smoothness (Higher means more rounded)")
smoothSlid = Scale(root, orient=HORIZONTAL, length=150, from_=0, to=50, command=process)
roughLab = Label(root, text="Bumpiness (Higher means more bumps)")
roughSlid = Scale(root, orient=HORIZONTAL, length=150, from_=0, to=20, command=process)
mapLab = Label(root)
generateLab = Label(root, text='Rerun generation process with same parameters')
generateBut = Button(root, text='Generate', command=lambda: process(0))
downloadBut = Button(root, text='Download', command=downloadPic)
backConvergeStart = Button(root, text='Back to Start', command=lambda: backButtons(2))
detailBut = Button(root, text='Detail Map', command=toDetail)


# runs the image generation on the user created dungeon layout:   1 is non-photo, 2 is photo, 3 is downscale
def goToProcess(preset):
    global wallArray
    if preset == 1:
        # hiding widgets in square draw path
        refineMap.grid_forget()
        for ro in buttonArray:
            for but in ro:
                but.grid_forget()
        backCompStart.grid_forget()
    elif preset == 2:
        instructions.grid_forget()
        selectBut.grid_forget()
        imgLabel.grid_forget()
        picLabel.grid_forget()
        contin.grid_forget()
        downSizBut.grid_forget()
        downLab.grid_forget()
        backPicStart.grid_forget()
    elif preset == 3:
        wallArray = sampleArray
        downScalSlid.grid_forget()
        downScalLab.grid_forget()
        downScalBut.grid_forget()
        backScalePic.grid_forget()

    # scaling(from comp 10-1000, from pic ), smoothing(0-tbd), roughness(0-tbd), gridwidth(0-tbd), gridcolor(tbd)
    scaleLab.grid(row=0, column=0, columnspan=2)
    scaleSlid.grid(row=0, column=2)
    smoothLab.grid(row=1, column=0, columnspan=2)
    smoothSlid.grid(row=1, column=2)
    roughLab.grid(row=2, column=0, columnspan=2)
    roughSlid.grid(row=2, column=2)
    generateLab.grid(row=5, column=0, columnspan=2)
    generateBut.grid(row=5, column=2)
    backConvergeStart.grid(row=6, column=0)
    downloadBut.grid(row=6, column=1)
    detailBut.grid(row=6, column=2)

    # hopefully starts map right next to stuff pls and tlhanmk oyou
    process(0)

h, w = (2, 20) if platform.system() != "Darwin" else (30, 300)
refineMap = Button(root, text="Process User-Drawn Map", height=h, width=w, command=lambda: goToProcess(1))
backCompStart = Button(root, text='Back to Start', height=h, width=w, command=lambda: backButtons(1))


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

    if platform.system() == "Darwin":
        h *= 20
        w = h
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


def addDoor():
    d = Draggable(picBackground, 460, 40, 5)
    listOfDoorDrags.append(d)
    canProcess(0)


def addEventMarker():
    global activeDraggable
    e = Draggable(picBackground, 460, 140, 5)
    e.description = ''
    listOfNumDrags.append(e)
    activeDraggable = e
    canProcess(0)

# hopefully works with descriptions
def onClick():
    global activeDraggable
    # handling the description entry and label
    if activeDraggable and activeDraggable.description is not None:
        num = listOfNumDrags.index(activeDraggable) + 1
        descLab.config(text='Current marker active: #' + str(num) +
                            '                                                 Description:')
        sv.set(activeDraggable.description)


# updates the descriptions of event markers
def update():
    global activeDraggable
    activeDraggable.description = descEnt.get()


# starts all widgets in canvas section
def startCanvas():
    gridWidLab.grid(row=0, column=0)
    gridWidSlid.grid(row=0, column=1)
    gridColLab.grid(row=1, column=0)
    gridColDrop.grid(row=1, column=1)
    picBackground.grid(row=0, column=2, rowspan=7, columnspan=2)
    doorLab.grid(row=2, column=0)
    doorBut.grid(row=2, column=1)
    markLab.grid(row=3, column=0)
    markBut.grid(row=3, column=1)
    descLab.grid(row=7, column=2)
    descEnt.grid(row=7, column=3)
    backCanStart.grid(row=4, column=0)
    compiBut.grid(row=4, column=1)
    picBackground.create_rectangle(400, 300, 500, 500, fill='red')
    canProcess(0)


# produces additional details on picture
def canProcess(x):
    global finalPic
    global mapOldNewWidthRatio

    # processes doors and number markers into image
    tempArray = Processing.addPoints(finalPic, mapOldNewWidthRatio, [door.getTuple() for door in listOfDoorDrags],
                                     [number.getTuple() for number in listOfNumDrags], 3)

    # this changes the grid attributes, HAS to go after door processing
    tempArray = Processing.drawGrid(tempArray, int(gridWidSlid.get()), color.get())
    Processing.downloadImg(tempArray, "sample.png")
    img = Image.open("sample.png")
    sampleMap = ImageTk.PhotoImage(img)

    mapOldNewWidthRatio = sampleMap.width()/400
    aspectRatio = sampleMap.height() / sampleMap.width()

    resized_sampleMap = img.resize((400, int(400 * aspectRatio)))
    new_sampleMap = ImageTk.PhotoImage(resized_sampleMap)
    picture = picBackground.create_image(0, 0, anchor=NW, image=new_sampleMap)
    picBackground.image = new_sampleMap
    picBackground.tag_lower(picture)


def saveTxt():
    txtFile = tkinter.filedialog.asksaveasfilename()
    if txtFile: Processing.addPoints(finalPic, mapOldNewWidthRatio, [door.getTuple() for door in listOfDoorDrags],
                         [number.getTuple() for number in listOfNumDrags], 3, fileLocation=txtFile)


def saveImg():
    imgFile = tkinter.filedialog.asksaveasfilename()
    if imgFile:
        tempArray = Processing.addPoints(finalPic, mapOldNewWidthRatio, [door.getTuple() for door in listOfDoorDrags],
                                     [number.getTuple() for number in listOfNumDrags], 3)

        # this changes the grid attributes, HAS to go after door processing
        tempArray = Processing.drawGrid(tempArray, int(gridWidSlid.get()), color.get())
        Processing.downloadImg(tempArray, imgFile)


# compiles notes and map into final product
def compiCan():
    # removes unnecessary widgets
    gridWidLab.grid_forget()
    gridWidSlid.grid_forget()
    gridColLab.grid_forget()
    gridColDrop.grid_forget()
    picBackground.grid_forget()
    doorLab.grid_forget()
    doorBut.grid_forget()
    markLab.grid_forget()
    markBut.grid_forget()
    descLab.grid_forget()
    descEnt.grid_forget()
    backCanStart.grid_forget()
    compiBut.grid_forget()

    saveTxtBut.grid(row=0, column=0)
    saveImgBut.grid(row=1, column=0)


saveTxtBut = Button(root, text='Save your notes in a .txt file', command=saveTxt)
saveImgBut = Button(root, text='Save your image in a .jpg/.png file', command=saveImg)

gridWidLab = Label(root, text="Determines pixel length of grid squares")
gridWidSlid = Scale(root, orient=HORIZONTAL, length=150, from_=0, to=50, command=canProcess)
gridColLab = Label(root, text="Determines the color of the grid lines")
color = StringVar(root)
color.set("Gray")  # default color for grid lines
gridColDrop = OptionMenu(root, color, "Black", "White", "Gray", "Blue", "Red",
                         "Yellow", "Orange", "Purple", "Green", command=canProcess)
picBackground = Canvas(root, height=500, width=500)
doorLab = Label(root, text="Button creates a new door. Drag between walls"
                           "\nwhere you would like a door formed. Drag "
                           "\nmarker into the red box to delete it.")
doorBut = Button(root, text='Door Markers', command=addDoor)
markLab = Label(root, text='Button creates a new marker. Marker will have'
                           '\ndescription and number associated with it.'
                           '\nEnter description into the box on the side '
                           '\nwhile clicking on marker. Drag marker into'
                           '\nthe red box to delete it.')
markBut = Button(root, text='Event Markers', command=addEventMarker)
descLab = Label(root, text='Current marker active: __                                                 Description:')
backCanStart = Button(root, text='Back to Start', command=lambda: backButtons(5))
# callback is for the onchange for the entry descriptions
def callback(sv):
    update()
sv = StringVar()
sv.trace("w", lambda name, index, mode, sv=sv: callback(sv))
descEnt = Entry(root, textvariable=sv)
compiBut = Button(root, text='Compile Notes and Image', command=compiCan)
root.mainloop()
