from tkinter import *
from socket import *

root = Tk()
titleFrame = Frame(root)
titleFrame.pack()

bFrame = Frame(root)
bFrame.pack(side=BOTTOM, fill=X)

bLFrame = Frame(bFrame)
bLFrame.pack(side=LEFT, fill=X)
bRFrame = Frame(bFrame)
bRFrame.pack(side=RIGHT, fill=X)

addFriend = Button(bLFrame, text="Add Friend", bg="blue", fg="white", fill=X)
addGroup = Button(bRFrame, text="Add Group", bg="red", fg="white", fill=X)
addFriend.pack()
addGroup.pack()

root.mainloop()