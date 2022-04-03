'''
gridWidLab = Label(root, text="Determines how many pixels a grid square is")
gridWidSlid = Scale(root, orient=HORIZONTAL, length=150, from_=0, to=50, command=process)
gridColLab = Label(root, text="Determines the color of the grid lines")
color = StringVar(root)
color.set("Gray")  # default color for grid lines
gridColDrop = OptionMenu(root, color, "Black", "White", "Gray", "Blue", "Red",
                         "Yellow", "Orange", "Purple", "Green", command=process)
'''