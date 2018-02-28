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
    print("Server started.")
    while 1:
        SessionData = {
            'id': '',
            'FirstName': '',
            'LastName': '',
            'LastActive': '',
        }

        print("Server ready to accept connections.")
        connectionSocket, addr = serverSocket.accept()
        print(addr)
        start_new_thread(main, (connectionSocket,))

def main(connectionSocket):
    print("main")
    request = connectionSocket.recv(1024).decode('ascii')


# SendMessage \t Message \r\n
def sendMessage():
    print("sendMessage")

# SendPrivateMessage \t Sender \t Receiver \t Message
def sendPrivateMessage():
    print("sendPrivateMessage")

# RegisterUser \t FirstName \t LastName \t Address \t Email \t password1 \t password2 \r\n
def RegisterUser():
    print("RegisterUser")

# CheckLogin \t Username \t Password \r\n
def loginCheck():
    print("checkUser")

# FriendsList \r\n
def printFriendsList():
    print("printFriendsList")

# FriendStatus \t Requester \t Friend \r\n
def getFriendStatus():
    print("getFriendStatus")

# OfflineMessages \r\n
def getOfflineMessages():
    print("getOfflineMessages")


if __name__ == '__main__':
    initiation()
