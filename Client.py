import sys
from tkinter import *
from socket import *
import platform
import atexit
import unicodedata


class Room:
    def __init__(self, name, roomId):
        self.name = name
        self.roomId = roomId


class Friend:
    def __init__(self, name, friendId):
        self.name = name
        self.friendId = friendId


class Message:
    def __init__(self, name, messageId):
        self.name = name
        self.messageId = messageId


class Application(Tk):
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        self.Tk = Tk
        self.title("GROUP CHAT")
        self.iconbitmap('groupIcon.ico')
        self.geometry("320x600")
        self.minsize(320, 400)
        self.resizable(0, 1)
        self.autoCrediential = False
        self.rememberCreditials = False
        self.menu = Menu(self)
        self.selectionMenu = Menu(self.menu, tearoff=0)
        self.selectionMenu.add_command(label='Messages', command=self.toMessages)
        self.selectionMenu.add_command(label='Friends', command=self.toFriends)
        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.serverPort = 12019
        self.serverName = "localhost" #I.P Address
        self.serverSocket = socket(AF_INET, SOCK_STREAM)
        # get friends from User by sending a request to the server and recieving the information
        self.friendsArray = []
        self.roomsArray = []
        self.messagesArray = {}
        self.friendsFrame = Listbox(self)
        self.friendsGroupFrame = Listbox(self)

        connected = False
        try:
            self.serverSocket.connect((self.serverName, self.serverPort))
            connected = True
        except Exception as e:
            print("Something went wrong:")
            print(e)
            connected = False
            self.serverSocket.close()

        self.frames = {}
        for F in (MessagesApp, FriendsApp, CreateGroupApp, FailedConnection, LoginApp, RegisterApp):
            page_name = F.__name__
            frame = F(master=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        if(connected):
            self.show_frame("LoginApp")
        else:
            self.show_frame("FailedConnection")


    def refreshClient(self):
        '''refresh messages, groups, and friends'''
        #refresh rooms
        command = "RoomsInfo"
        self.serverSocket.send(command.encode())
        returnedRooms = self.serverSocket.recv(1024).decode('ascii')
        print(returnedRooms)
        returnedRooms = returnedRooms.split('\t')
        returnedRooms = returnedRooms[1].__str__()

        rooms = self.grabObjectsFromString(returnedRooms)

        for r in rooms:
            roomName = (r.split(',')[0].__str__().split(':')[1])
            roomName = roomName[2:-1]
            roomId = int((r.split(',')[1].__str__().split(':')[1].split(' ')[1]))
            newRoom = Room(roomName, roomId)
            print(roomName + " : " + roomId.__str__())
            self.roomsArray.append(newRoom)

        #refresh friends
        command = "FriendsList"
        self.serverSocket.send(command.encode())
        returnedFriends = self.serverSocket.recv(1024).decode('ascii')
        print(returnedFriends)
        returnedFriends = returnedFriends.split('\t')
        returnedFriends = returnedFriends[1].__str__()

        friends = self.grabObjectsFromString(returnedFriends)

        for f in friends:
            friendName = (f.split(',')[0].__str__().split(':')[1])
            friendName = friendName[2:-1]
            friendId = int((f.split(',')[1].__str__().split(':')[1].split(' ')[1]))
            newFriend = Friend(friendName, friendId)
            print(friendName + " : " + friendId.__str__())
            self.friendsArray.append(newFriend)


    def toMessages(self):
        self.show_frame("MessagesApp")

    def toFriends(self):
        self.show_frame("FriendsApp")

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()

    def grabObjectsFromString(self, arrString):
        objects = []
        objectStr = ""
        created = False
        for i in range(len(arrString)):
            if arrString[i] == '{' or arrString[i] == '[':
                created = False
            elif arrString[i] == '}':
                if created == False:
                    objects.append(objectStr)
                    objectStr = ""
                    created = True
            elif created == False:
                objectStr += arrString[i]

        return objects


class MessagesApp(Frame):
    def __init__(self, master, controller):
        Frame.__init__(self, master)
        self.controller = controller

        toolbar = Frame(self, bg="blue")
        self.controller.menu.add_cascade(label="MENU", menu=self.controller.selectionMenu)
        Label(toolbar, text="MESSAGES", bg="blue", fg="white", justify=CENTER).pack(side=TOP, padx=16, pady=2, expand=1)
        toolbar.pack(side=TOP, fill=X)
        roomsFrame = Frame(self)
        roomsFrame.pack(side=TOP)

        #get rooms from User by sending a request to the server and recieving the information


        for room in self.controller.roomsArray:
            #button for each friend
            rButton = Button(roomsFrame, bg='gray', fg='black', text=room, width=320, justify=RIGHT, command=lambda : self.create_room_window(room))
            rButton.pack(side=TOP, pady=2, padx=2)

        addGroupFrame = Frame(self)
        addGroupFrame.pack(side=BOTTOM)
        addButton = Button(addGroupFrame, bg='blue', fg='white', text='Create New Group', width=320, command=self.createGroup)
        addButton.pack(side=BOTTOM, padx=16, pady=8)

    def createGroup(self):
        self.controller.show_frame("CreateGroupApp")

    def create_room_window(self, room):
        large_font = ('Verdana', 30)
        window = Toplevel(self, takefocus=None)
        window.lift(aboveThis=None)
        window.minsize(320, 320)
        window.resizable(0, 1)
        window.iconbitmap('groupIcon.ico')
        toolbar = Frame(window, bg="blue")
        Label(toolbar, text=room, bg="blue", fg="white", justify=CENTER).pack(side=TOP, padx=16, pady=2, expand=1)
        toolbar.pack(side=TOP, fill=X)
        messageFrame = Frame(window, bg='gray')
        messageFrame.pack(side=BOTTOM, fill=X)
        messageSend = Button(messageFrame, text='SEND', bg='blue', fg='white')
        messageSend.pack(side=RIGHT)
        messageInput = Entry(messageFrame)
        messageInput.pack(padx=2, pady=2, fill=X)
        messageInput.focus_set()


class CreateGroupApp(Frame):
    def __init__(self, master, controller):
        Frame.__init__(self, master)
        self.controller = controller

        #refresh friendlist

        toolbar = Frame(self, bg="blue")
        Label(toolbar, text="CREATE NEW GROUP", bg="blue", fg="white", justify=CENTER).pack(side=TOP, padx=16, pady=2, expand=1)
        toolbar.pack(side=TOP, fill=X)

        nameFrame = Frame(self)
        nameFrame.pack(side=TOP)
        Label(nameFrame, text="Group Name:", ).pack(anchor="w", fill=X, padx=8, pady=2)
        self.gNameInput = Entry(nameFrame, bg='white', width=24)
        self.gNameInput.insert(0, "Group X")
        self.gNameInput.focus_set()
        self.gNameInput.pack(side=TOP, fill=X, padx=8, pady=2)

        friendsList = LabelFrame(self, text='Choose Friends To Be In The Group:')
        friendsList.pack(side=TOP, padx=8, pady=8)
        self.yScroll = Scrollbar(friendsList, orient=VERTICAL)
        self.yScroll.pack(side=RIGHT, fill=Y)
        self.controller.friendsFrame = Listbox(friendsList, selectmode=MULTIPLE, width=320, yscrollcommand=self.yScroll.set)
        self.controller.friendsFrame.bind('<<ListboxSelect>>', self.CurSelect)
        self.controller.friendsFrame.pack()
        self.yScroll['command'] = self.controller.friendsFrame.yview

        for friend in self.controller.friendsArray:
            # button for each friend
            self.controller.friendsFrame.insert(END, friend)

        button_frame = Frame(self)
        button_frame.pack(side=BOTTOM)
        self.backButton = Button(button_frame, bg='red', fg='white', text="Back", width=320,
                                  command=self.toMessages)
        self.backButton.pack(side=BOTTOM, padx=8, pady=8)
        self.groupButton = Button(button_frame, bg='blue', fg='white', text="Create Group", width=320,
                                  command=self.createGroup)
        self.groupButton.pack(side=BOTTOM, padx=8)

        groupFrame = Frame(self)
        groupFrame.pack(side=TOP)
        groupLabel = Label(groupFrame, text="Create Group With:", width=320)
        groupLabel.pack(side=TOP)

        self.groupLabel = Text(groupFrame)
        self.groupLabel.insert(INSERT, "Please select group members", "a")
        self.groupLabel.pack()

        self.groupNames = ""
        self.selectedMemebers = {}

    def CurSelect(self, evt):
        self.groupNames = ""
        self.selectedMemebers = self.controller.friendsFrame.curselection()
        for index in self.selectedMemebers:
            self.groupNames += self.controller.friendsFrame.get(index)
            self.groupNames += "\n"
        self.groupNames = self.groupNames[:-1]
        self.groupLabel.delete('1.0', END)
        self.groupLabel.insert(INSERT, self.groupNames, "a")

    def createGroup(self):
        print("Create Group: ")

    def toMessages(self):
        self.controller.show_frame("MessagesApp")


class FriendsApp(Frame):
    def __init__(self, master, controller):
        Frame.__init__(self, master)
        self.controller = controller

        #refresh friendlist

        self.selectedFriend = -1

        toolbar = Frame(self, bg="blue")
        Label(toolbar, text="FRIENDS", bg="blue", fg="white", justify=CENTER).pack(side=TOP, padx=16, pady=2, expand=1)
        toolbar.pack(side=TOP, fill=X)

        friendsList = Frame(self)
        friendsList.pack(side=TOP)
        self.yScroll = Scrollbar(friendsList, orient=VERTICAL)
        self.yScroll.pack(side=RIGHT, fill=Y)
        self.controller.friendsGroupFrame = Listbox(friendsList, selectmode=SINGLE, width=320, yscrollcommand=self.yScroll.set)
        self.controller.friendsGroupFrame.bind('<<ListboxSelect>>', self.CurSelet)
        self.controller.friendsGroupFrame.pack(side=TOP)
        self.yScroll['command'] = self.controller.friendsGroupFrame.yview

        self.controller.friendsGroupFrame.delete(0, END)
        for friend in self.controller.friendsArray:
            #button for each friend
            self.controller.friendsGroupFrame.insert(END, friend)

        removeButton = Button(self, bg='red', fg='white', text='Remove Friend', width=320, command=self.removeFriend)
        removeButton.pack(side=TOP)

        addFriendFrame = LabelFrame(self, text="Input an email to add friends:", width=320)
        addFriendFrame.pack(side=BOTTOM)
        addButton = Button(addFriendFrame, bg='blue', fg='white', text='Add Friend', width=320)
        addButton.pack(side=BOTTOM, padx=16, pady=4)
        self.fInput = Entry(addFriendFrame, bg='white', width=320)
        self.fInput.pack(side=BOTTOM, padx=16, pady=4)


    def CurSelet(self, evt):
        if len(self.controller.friendsGroupFrame.curselection()) > 0:
            self.selectedFriend = self.controller.friendsGroupFrame.curselection()[0]

    def addFriend(self):
        self.controller.refreshClient()
        print("Add Friend:")

    def removeFriend(self):
        if self.selectedFriend >= 0:
            del self.controller.friendsArray[self.selectedFriend]
            self.controller.friendsGroupFrame.delete(0, END)
            self.controller.friendsFrame.delete(0, END)
            for friend in self.controller.friendsArray:
                # button for each friend
                self.controller.friendsGroupFrame.insert(END, friend)
                self.controller.friendsFrame.insert(END, friend)
            self.selectedFriend = -1
            self.controller.refreshClient()


class FailedConnection(Frame):
    def __init__(self, master, controller):
        Frame.__init__(self, master)
        self.controller = controller
        dialog_frame = Frame(self)
        dialog_frame.pack(padx=20, expand=1)
        Label(dialog_frame, text="Failed connecting to server!").grid(row=0, column=0)

        button_frame = Frame(self)
        button_frame.pack(side=BOTTOM)
        self.registerButton = Button(button_frame, bg='red', fg='white', text="Quit", width=320, command=self.quitApp)
        self.registerButton.pack(side=BOTTOM, padx=8, pady=8)
        self.loginButton = Button(button_frame, bg='blue', fg='white', text="Try Again", width=320, command=self.reconnect)
        self.loginButton.pack(side=BOTTOM, padx=8)

    def quitApp(self):
        print("Quitting...")
        quit()

    def reconnect(self):
        print("Trying to reconnect...")
        self.controller.serverSocket = socket(AF_INET, SOCK_STREAM)
        connected = False
        try:
            self.controller.serverSocket.connect((self.controller.serverName, self.controller.serverPort))
            connected = True
        except Exception as e:
            print("Something went wrong:")
            print(e)
            connected = False
            self.controller.serverSocket.close()

        if(connected):
            self.controller.show_frame("LoginApp")


class LoginApp(Frame):
    def __init__(self, master, controller):
        Frame.__init__(self, master)
        self.controller = controller
        dialog_frame = LabelFrame(self, text="Please login to your account:")
        dialog_frame.pack(padx=20, expand=1)

        Label(dialog_frame, text="").grid(row=0, column=0)

        Label(dialog_frame, text="Email:").grid(row=1, column=0, sticky='w', padx=8)
        self.eInput = Entry(dialog_frame, bg='white', width=24)
        self.eInput.grid(columnspan=2, sticky='w', padx=8)
        self.eInput.focus_set()

        Label(dialog_frame, text="Password:").grid(row=3, column=0, sticky='w', padx=8)
        self.pInput = Entry(dialog_frame, bg='white', width=24, show="*")
        self.pInput.grid(columnspan=2, sticky='w', padx=8)

        self.remember = BooleanVar()
        self.stayLogged = Checkbutton(dialog_frame, text="Remember credentials", variable=self.remember)
        self.stayLogged.grid(columnspan=2, padx=8, pady=4)
        Label(dialog_frame, text="").grid(columnspan=2)

        button_frame = Frame(self)
        button_frame.pack(side=BOTTOM)
        self.registerButton = Button(button_frame, bg='red', fg='white', text="Register", width=320, command=self.toRegister)
        self.registerButton.pack(side=BOTTOM, padx=8, pady=8)
        self.loginButton = Button(button_frame, bg='blue', fg='white', text="Login", width=320, command=self.loginUser)
        self.loginButton.pack(side=BOTTOM, padx=8)

        self.loginErrors = Label(self, text="")
        self.loginErrors.pack()

    def loginUser(self):
        error = ""
        self.controller.rememberCreditials = self.remember.get()
        print(self.controller.rememberCreditials)
        message = "CheckLogin\t"
        email = self.eInput.get()
        password = self.pInput.get()

        ext = ""
        isEmail = False
        for i in range(0, len(email)):
            if(email[i] == '@' and (i != 0 or i >= (len(email) - 1))):
                isEmail = True

            if(i >= (len(email) - 4)):
                ext += email[i]

        extensions = {'.com', '.net', '.org', '.edu', '.gov'}
        if(isEmail):
            isEmail = False
            for e in extensions:
                if(e == ext):
                    isEmail = True

        if (password == '' or email == ''):
            error = "Please fill out all fields!"
        elif (isEmail == False):
            error = "Please input an actual email!"
        else:
            message += (email + '\t')
            message += (password + '\r\n')
            if(self.controller.rememberCreditials):
                with open("user.bin", "wb") as myfile:
                    myfile.truncate()
                    coded = (email + '\n' + password)
                    encoded = ''.join(map(bin,bytearray(coded,'utf8')))
                    myfile.write(encoded.encode())
                    myfile.close()
            self.controller.serverSocket.send(message.encode())
            response = self.controller.serverSocket.recv(1024).decode('ascii')
            type = response.split("\t")
            print(message + '\n Status: ' + type[1])
            if("Success".upper() in type[1].upper()):
                #move to the app
                error = "Login Completed!"
                self.controller.show_frame("MessagesApp")
                self.controller.config(menu=self.controller.menu)
                self.controller.refreshClient()
            else:
                error = "Login Failed!"

        self.loginErrors.config(text=error)
        self.loginErrors.pack()

    def toRegister(self):
        self.controller.show_frame("RegisterApp")


class RegisterApp(Frame):
    def __init__(self, master, controller):
        Frame.__init__(self, master)
        self.controller = controller
        dialog_frame = LabelFrame(self, text="Please fill out all the fields below:")
        dialog_frame.pack(padx=20, expand=1)

        Label(dialog_frame, text="").grid(row=0, column=0)

        Label(dialog_frame, text="Email:").grid(row=1, column=0, sticky='w', padx=12)
        self.eInput = Entry(dialog_frame, bg='white', width=28)
        self.eInput.grid(columnspan=2, sticky='w', padx=8)
        self.eInput.focus_set()
        Label(dialog_frame, text="").grid(row=3, column=0)

        Label(dialog_frame, text="First Name:").grid(row=4, column=0, sticky='w', padx=12)
        self.fnInput = Entry(dialog_frame, bg='white', width=28)
        self.fnInput.grid(columnspan=2, sticky='w', padx=8)

        Label(dialog_frame, text="Last Name:").grid(row=6, column=0, sticky='w', padx=12)
        self.lnInput = Entry(dialog_frame, bg='white', width=28)
        self.lnInput.grid(columnspan=2, sticky='w', padx=8)

        Label(dialog_frame, text="").grid(row=8, column=0)

        Label(dialog_frame, text="Password:").grid(row=9, column=0, sticky='w', padx=12)
        self.pInput = Entry(dialog_frame, bg='white', width=28, show="*")
        self.pInput.grid(columnspan=2, sticky='w', padx=8)

        Label(dialog_frame, text="Confirm Password:").grid(row=11, column=0, sticky='w', padx=12)
        self.rpInput = Entry(dialog_frame, bg='white', width=28, show="*")
        self.rpInput.grid(columnspan=2, sticky='w', padx=8)

        Label(dialog_frame, text="").grid(columnspan=2)

        button_frame = Frame(self)
        button_frame.pack(side=BOTTOM)
        self.registerButton = Button(button_frame, bg='red', fg='white', text="Back", width=320, command=self.toLogin)
        self.registerButton.pack(side=BOTTOM, padx=8, pady=8)
        self.loginButton = Button(button_frame, bg='blue', fg='white', text="Register", width=320, command=self.tryRegister)
        self.loginButton.pack(side=BOTTOM, padx=8)

        self.registerErrors = Label(self, text="")
        self.registerErrors.pack()

    def tryRegister(self):
        error = ""
        #request = "RegisterUser\tFirstName\tLastName\tAddress\tEmail\tpassword\r\n"
        message = "RegisterUser\t"
        firstName = self.fnInput.get()
        lastName = self.lnInput.get()
        email = self.eInput.get()
        address = "127.0.0.1"
        password = self.pInput.get()
        checkPassword = self.rpInput.get()

        ext = ""
        isEmail = False
        for i in range(0, len(email)):
            if(email[i] == '@' and (i != 0 or i >= (len(email) - 1))):
                isEmail = True

            if(i >= (len(email) - 4)):
                ext += email[i]

        extensions = {'.com', '.net', '.org', '.edu', '.gov'}
        if(isEmail):
            isEmail = False
            for e in extensions:
                if(e == ext):
                    isEmail = True

        if(password == '' or checkPassword == '' or email == '' or firstName == '' or lastName == ''):
            error = "Please fill out all fields!"
        elif(password != checkPassword):
            error = "Passwords do not match!"
        elif(isEmail == False):
            error = "Please input an actual email!"
        else:
            message += (firstName + '\t')
            message += (lastName + '\t')
            message += (address + '\t')
            message += (email + '\t')
            message += (password + '\r\n')
            self.controller.serverSocket.send(message.encode())
            response = self.controller.serverSocket.recv(1024).decode('ascii')
            type = response.split("\t")
            print(message + '\n Status: ' + type[1])
            if("Success".upper() in type[1].upper()):
                #move to the app
                error = "Registration Completed!"
                self.controller.show_frame("LoginApp")
            else:
                error = "Registration Failed!"

        self.registerErrors.config(text=error)
        self.registerErrors.pack()

    def toLogin(self):
        self.controller.show_frame("LoginApp")


def exithandler():
    #logout user if they are logged in
    print('Logging out')


if __name__ == "__main__":
    atexit.register(exithandler)
    app = Application()
    app.mainloop()

