import sys
from tkinter import *
from socket import *
import threading
import platform
import atexit
import os
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
    def __init__(self, message, sender, roomId):
        self.message = message
        self.sender = sender
        self.roomId = roomId


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
        self.groupsFrame = Listbox(self)


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


    def exit(self):
        # logout user if they are logged in
        #looper.cancel()
        try:
            self.serverSocket.send("logout".encode())
            self.serverSocket.close()
        except:
            print("Already logged out")
        os._exit(0)


    def refreshClient(self):
        '''refresh messages, groups, and friends'''
        #refresh rooms
        self.roomsArray = []
        command = "RoomsInfo"
        self.serverSocket.send(command.encode())
        returnedRooms = self.serverSocket.recv(1024).decode('ascii')
        print(returnedRooms)
        returnedRooms = returnedRooms.split('\t')
        if(len(returnedRooms) > 1):
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
        self.friendsArray = []
        command = "FriendsList"
        self.serverSocket.send(command.encode())
        returnedFriends = self.serverSocket.recv(1024).decode('ascii')
        print(returnedFriends)
        returnedFriends = returnedFriends.split('\t')
        if(len(returnedFriends) > 1):
            returnedFriends = returnedFriends[1].__str__()

        friends = self.grabObjectsFromString(returnedFriends)

        for f in friends:
            print(f)
            friendName = (f.split(',')[0].__str__().split(':')[1])
            friendName = friendName[2:-1]
            friendId = int((f.split(',')[2].__str__().split(':')[1].split(' ')[1]))
            newFriend = Friend(friendName, friendId)
            print(friendName + " : " + friendId.__str__())
            self.friendsArray.append(newFriend)

        #refresh messages
        self.messagesArray = []
        for room in self.roomsArray:
            command = "getOfflineMessages\t" + room.roomId.__str__()
            self.serverSocket.send(command.encode())
            returnedMessage = self.serverSocket.recv(1024).decode('ascii')
            returnedMessage = returnedMessage.split('\t')
            returnedMessage = returnedMessage[1].__str__()

            messages = self.grabObjectsFromString(returnedMessage)

            for m in messages:
                print(m)
                sender = m.split(',')[0].__str__().split(':')[1]
                sender = sender[2:-1]
                message = m.split(',')[1].__str__().split(':')[1]
                message = message[2:-1]
                rId = int(m.split(',')[3].__str__().split(':')[1].split(' ')[1])
                newMessage = Message(message, sender, rId)
                print("(" + rId.__str__() + ") " + sender + ": " + message)
                self.messagesArray.append(newMessage)


        #refresh lists
        self.groupsFrame.delete(0, END)
        self.friendsFrame.delete(0, END)
        self.friendsGroupFrame.delete(0, END)
        for friend in self.friendsArray:
            # button for each friend
            self.friendsFrame.insert(END, friend.name)
            self.friendsGroupFrame.insert(END, friend.name)

        for group in self.roomsArray:
            # button for each group
            self.groupsFrame.insert(END, group.name)


    def toMessages(self):
        self.show_frame("MessagesApp")
        self.refreshClient()

    def toFriends(self):
        self.show_frame("FriendsApp")
        self.refreshClient()

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
                    objectStr.strip('\n')
                    objectStr.strip('/')
                    objectStr.strip(ascii(92))
                    objects.append(objectStr)
                    objectStr = ""
                    created = True
            elif created == False:
                objectStr += arrString[i]

        return objects

    def isEmail(self, email):
        ext = ""
        isEmail = False
        for i in range(0, len(email)):
            if (email[i] == '@' and (i != 0 or i >= (len(email) - 1))):
                isEmail = True

            if (i >= (len(email) - 4)):
                ext += email[i]

        extensions = {'.com', '.net', '.org', '.edu', '.gov'}
        if (isEmail):
            isEmail = False
            for e in extensions:
                if (e == ext):
                    isEmail = True

        return isEmail


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
        self.selectedGroup = -1
        self.yScroll = Scrollbar(roomsFrame, orient=VERTICAL)
        self.yScroll.pack(side=RIGHT, fill=Y)
        self.controller.groupsFrame = Listbox(roomsFrame, selectmode=SINGLE, width=320, yscrollcommand=self.yScroll.set)
        self.controller.groupsFrame.bind('<<ListboxSelect>>', self.CurSelet)
        self.controller.groupsFrame.pack(side=TOP)
        self.yScroll['command'] = self.controller.groupsFrame.yview

        openButton = Button(self, bg='blue', fg='white', text='Open Group', width=320, command= lambda: self.create_room_window(self.selectedGroup))
        openButton.pack(side=TOP, pady=2)
        leaveButton = Button(self, bg='red', fg='white', text='Leave Group', width=320,
                            command=lambda: self.leaveGroup(self.selectedGroup))
        leaveButton.pack(side=TOP, pady=2)

        addGroupFrame = Frame(self)
        addGroupFrame.pack(side=BOTTOM)
        addButton = Button(addGroupFrame, bg='blue', fg='white', text='Create New Group', width=320, command=self.createGroup)
        addButton.pack(side=BOTTOM, padx=16, pady=8)

    def createGroup(self):
        self.controller.show_frame("CreateGroupApp")


    def CurSelet(self, evt):
        if len(self.controller.groupsFrame.curselection()) > 0:
            self.selectedGroup = self.controller.groupsFrame.curselection()[0]


    def create_room_window(self, roomNumber):
        if roomNumber > -1:
            self.room = self.controller.roomsArray[roomNumber]
            large_font = ('Verdana', 30)
            window = Toplevel(self, takefocus=None)
            window.lift(aboveThis=None)
            window.minsize(320, 320)
            window.resizable(0, 1)
            window.iconbitmap('groupIcon.ico')
            toolbar = Frame(window, bg="blue")
            Label(toolbar, text=self.room.name, bg="blue", fg="white", justify=CENTER).pack(side=TOP, padx=16, pady=2, expand=1)
            toolbar.pack(side=TOP, fill=X)

            messageFrame = Frame(window, bg='gray')
            messageFrame.pack(side=TOP, fill=X)
            messageSend = Button(messageFrame, text='SEND', bg='blue', fg='white',
                                 command=lambda: self.sendMessage(self.messageInput.get(), self.room.roomId))
            messageSend.pack(side=RIGHT)
            self.messageInput = Entry(messageFrame)
            self.messageInput.pack(padx=2, pady=2, fill=X)
            self.messageInput.focus_set()

            messageList = Frame(window)
            self.messages = Text(messageList)


            self.refreshMessages(self.room)

            self.messages.pack()
            messageList.pack(side=TOP)


    def refreshMessages(self, room):
        try:
            self.roomThread = threading.Timer(1.0, self.refreshMessages, [room], {})
        except:
            self.roomThread.cancel()
        else:
            self.roomThread.start()
            self.controller.refreshClient()
            try:
                self.messages.config(state=NORMAL)
                self.messages.delete('1.0', END)
                for i in range(len(self.controller.messagesArray)):
                    m = self.controller.messagesArray[(len(self.controller.messagesArray) - i - 1)]
                    if m.roomId == room.roomId:
                        self.messages.insert(INSERT, m.sender + ": " + m.message + "\n", "a")
                self.messages.config(state=DISABLED)
            except:
                self.roomThread.cancel()



    def leaveGroup(self, roomNumber):
        if roomNumber > -1:
            room = self.controller.roomsArray[roomNumber]
            command = "LeaveRoom\t" + room.roomId.__str__()
            self.controller.serverSocket.send(command.encode())
            print("leaveRoom")
            print(self.controller.serverSocket.recv(1024).decode('ascii'))
            self.controller.refreshClient()


    def sendMessage(self, message, roomId):
        if message != "" and message != "\n" and message.strip(' ') != "":
            print("Send : " + message + " : " + roomId.__str__())
            command = "SendMessage\t" + message + "\t" + roomId.__str__()
            self.controller.serverSocket.send(command.encode())
            print(self.controller.serverSocket.recv(1024).decode('ascii'))
            self.controller.refreshClient()
            self.refreshMessages(self.room)
            self.messageInput.delete(0, 'end')


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
        self.groupLabel.config(state=NORMAL)
        self.groupLabel.insert(INSERT, "Please select group members", "a")
        self.groupLabel.config(state=DISABLED)
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
        self.groupLabel.config(state=NORMAL)
        self.groupLabel.delete('1.0', END)
        self.groupLabel.insert(INSERT, self.groupNames, "a")
        self.groupLabel.config(state=DISABLED)

    def createGroup(self):
        if len(self.selectedMemebers) > 0:
            name = self.gNameInput.get()
            friends = []
            for index in self.selectedMemebers:
                friends.append(self.controller.friendsArray[index])

            command = "CreateRoom\t" + name
            self.controller.serverSocket.send(command.encode())
            roomMessage = self.controller.serverSocket.recv(1024).decode('ascii')
            roomId = roomMessage.split('\t')[1]
            ownerId = roomMessage.split('\t')[2]
            self.controller.serverSocket.send(
                ("joinRoom\t" + ownerId + "\t" + roomId).encode())
            print(self.controller.serverSocket.recv(1024).decode('ascii'))
            for friend in friends:
                print(friend.friendId.__str__() + " : " + roomId)
                self.controller.serverSocket.send(
                    ("joinRoom\t" + friend.friendId.__str__() + "\t" + roomId.__str__()).encode())
                print(self.controller.serverSocket.recv(1024).decode('ascii'))

            print("Create Group: ")
        self.toMessages()

    def toMessages(self):
        self.controller.show_frame("MessagesApp")
        self.controller.refreshClient()


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

        removeButton = Button(self, bg='red', fg='white', text='Remove Friend', width=320, command=self.removeFriend)
        removeButton.pack(side=TOP)

        addFriendFrame = LabelFrame(self, text="Input an email to add friends:", width=320)
        addFriendFrame.pack(side=BOTTOM)
        addButton = Button(addFriendFrame, bg='blue', fg='white', text='Add Friend', width=320,
                           command= lambda : self.addFriend(self.fInput.get()))
        addButton.pack(side=BOTTOM, padx=16, pady=4)
        self.fInput = Entry(addFriendFrame, bg='white', width=320)
        self.fInput.pack(side=BOTTOM, padx=16, pady=4)


    def CurSelet(self, evt):
        if len(self.controller.friendsGroupFrame.curselection()) > 0:
            self.selectedFriend = self.controller.friendsGroupFrame.curselection()[0]

    def addFriend(self, email):
        if self.controller.isEmail(email):
            command = "AddFriend\t" + email
            print(command)
            self.controller.serverSocket.send(command.encode())
            print(self.controller.serverSocket.recv(1024).decode('ascii'))
            self.controller.refreshClient()
            print("Add Friend:")

    def removeFriend(self):
        if self.selectedFriend >= 0:
            friendId = self.controller.friendsArray[self.selectedFriend].friendId
            command = "RemoveFriend\t"+friendId.__str__()
            self.controller.serverSocket.send(command.encode())
            print(self.controller.serverSocket.recv(1024).decode('ascii'))
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

        isEmail = self.controller.isEmail(email)

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

def exit():
    print("EXIT")

if __name__ == "__main__":
    atexit.register(exit)
    app = Application()
    app.mainloop()

