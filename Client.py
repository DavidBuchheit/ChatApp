import sys
from tkinter import *
from socket import *
import platform
import atexit
import unicodedata

class User():
    def __init__(self, email, name):
        self.email = email
        self.name = name


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

        self.serverPort = 12010
        self.serverName = "localhost" #I.P Address
        self.clientSocket = socket(AF_INET, SOCK_STREAM)

        self.currentUser = User('', '')

        connected = False
        try:
            self.clientSocket.connect((self.serverName, self.serverPort))
            connected = True
        except Exception as e:
            print("Something went wrong:")
            print(e)
            connected = False
            self.clientSocket.close()

        self.frames = {}
        for F in (MessagesApp, FriendsApp, FailedConnection, LoginApp, RegisterApp):
            page_name = F.__name__
            frame = F(master=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        if(connected):
            self.show_frame("LoginApp")
            #self.show_frame("MessagesApp")
        else:
            self.show_frame("FailedConnection")


    def toMessages(self):
        self.show_frame("MessagesApp")

    def toFriends(self):
        self.show_frame("FriendsApp")

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()



class MessagesApp(Frame):
    def __init__(self, master, controller):
        Frame.__init__(self, master)
        self.controller = controller

        toolbar = Frame(self, bg="blue")
        self.controller.menu.add_cascade(label="MENU", menu=self.controller.selectionMenu)
        Label(toolbar, text="MESSAGES", bg="blue", fg="white", justify=CENTER).pack(side=TOP, padx=16, pady=2, expand=1)
        toolbar.pack(side=TOP, fill=X)


class FriendsApp(Frame):
    def __init__(self, master, controller):
        Frame.__init__(self, master)
        self.controller = controller

        toolbar = Frame(self, bg="blue")
        Label(toolbar, text="FRIENDS", bg="blue", fg="white", justify=CENTER).pack(side=TOP, padx=16, pady=2, expand=1)
        toolbar.pack(side=TOP, fill=X)

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
        self.controller.clientSocket = socket(AF_INET, SOCK_STREAM)
        connected = False
        try:
            self.controller.clientSocket.connect((self.controller.serverName, self.controller.serverPort))
            connected = True
        except Exception as e:
            print("Something went wrong:")
            print(e)
            connected = False
            self.controller.clientSocket.close()

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
            self.controller.clientSocket.send(message.encode())
            response = self.controller.clientSocket.recv(1024).decode('ascii')
            type = response.split("\t")
            print(message + '\n Status: ' + type[1])
            if("Success".upper() in type[1].upper()):
                #move to the app
                error = "Login Completed!"
                self.controller.show_frame("MessagesApp")
                self.controller.config(menu=self.controller.menu)
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
            self.controller.clientSocket.send(message.encode())
            response = self.controller.clientSocket.recv(1024).decode('ascii')
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

