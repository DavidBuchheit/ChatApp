###Chat Bot

import sqlite3 as lite
from socket import *
from _thread import *

#list = database.execute("SELECT * FROM User")
# list = list.fetchall()
# print(list)
# Example SQL print

serverPort = 12009
serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(10)
database = lite.connect('user.db')

############################
# Responses: Type \t Failure OR Success \r\n
#        Ex: SendMessage \t Success \r\n
#  Requests: Type \t Data \r\n
#        Ex: RegisterUser \t FirstName \t LastName \t Address \t Email \t password1 \t password2 \r\n
###########################

def initiation():
    while 1:
        connectionSocket, addr = serverSocket.accept()
        print(addr)
        start_new_thread(main, (connectionSocket,))

def main(connectionSocket):
    print("main")
    request = connectionSocket.recv(1024).decode('ascii')


def sendMessage():
    print("sendMessage")


def sendPrivateMessage():
    print("sendPrivateMessage")


def RegisterUser():
    print("RegisterUser")


def loginCheck():
    print("checkUser")


def printFriendsList():
    print("printFriendsList")


def getFriendStatus():
    print("getFriendStatus")


def getOfflineMessages():
    print("getOfflineMessages")


if __name__ == '__main__':
    initiation()
