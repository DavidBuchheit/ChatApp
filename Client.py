import sys
from tkinter import *
from socket import *
import platform

class Application(Tk):
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        self.title("Group Chat")
        self.iconbitmap('groupIcon.ico')
        self.geometry("320x600")
        self.minsize(320, 400)
        self.resizable(0, 1)

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.serverPort = 12009
        self.serverName = "localhost" #I.P Address
        self.clientSocket = socket(AF_INET, SOCK_STREAM)
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
        for F in (FailedConnection, LoginApp, RegisterApp):
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

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()

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

        Label(dialog_frame, text="Username:").grid(row=1, column=0, sticky='w', padx=8)
        self.uInput = Entry(dialog_frame, bg='white', width=24)
        self.uInput.grid(columnspan=2, sticky='w', padx=8)
        self.uInput.focus_set()

        Label(dialog_frame, text="Password:").grid(row=3, column=0, sticky='w', padx=8)
        self.pInput = Entry(dialog_frame, bg='white', width=24)
        self.pInput.grid(columnspan=2, sticky='w', padx=8)

        self.stayLogged = Checkbutton(dialog_frame, text="Remember credentials")
        self.stayLogged.grid(columnspan=2, padx=8, pady=4)
        Label(dialog_frame, text="").grid(columnspan=2)

        button_frame = Frame(self)
        button_frame.pack(side=BOTTOM)
        self.registerButton = Button(button_frame, bg='red', fg='white', text="Register", width=320, command=self.toRegister)
        self.registerButton.pack(side=BOTTOM, padx=8, pady=8)
        self.loginButton = Button(button_frame, bg='blue', fg='white', text="Login", width=320)
        self.loginButton.pack(side=BOTTOM, padx=8)

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

        Label(dialog_frame, text="").grid(row=3, column=0)

        Label(dialog_frame, text="Username:").grid(row=4, column=0, sticky='w', padx=12)
        self.uInput = Entry(dialog_frame, bg='white', width=28)
        self.uInput.grid(columnspan=2, sticky='w', padx=8)
        self.uInput.focus_set()

        Label(dialog_frame, text="").grid(row=6, column=0)

        Label(dialog_frame, text="Password:").grid(row=7, column=0, sticky='w', padx=12)
        self.pInput = Entry(dialog_frame, bg='white', width=28)
        self.pInput.grid(columnspan=2, sticky='w', padx=8)

        Label(dialog_frame, text="Confirm Password:").grid(row=9, column=0, sticky='w', padx=12)
        self.rpInput = Entry(dialog_frame, bg='white', width=28)
        self.rpInput.grid(columnspan=2, sticky='w', padx=8)

        Label(dialog_frame, text="").grid(columnspan=2)

        button_frame = Frame(self)
        button_frame.pack(side=BOTTOM)
        self.registerButton = Button(button_frame, bg='red', fg='white', text="Back", width=320, command=self.toLogin)
        self.registerButton.pack(side=BOTTOM, padx=8, pady=8)
        self.loginButton = Button(button_frame, bg='blue', fg='white', text="Register", width=320, command=self.tryRegister)
        self.loginButton.pack(side=BOTTOM, padx=8)

    def tryRegister(self):
        print("Registering...")

    def toLogin(self):
        self.controller.show_frame("LoginApp")


if __name__ == "__main__":
    app = Application()
    app.mainloop()
