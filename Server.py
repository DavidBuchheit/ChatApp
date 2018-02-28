###Chat Bot

import sqlite3 as lite
from socket import *

#list = database.execute("SELECT * FROM User")
# list = list.fetchall()
# print(list)
# Example SQL print

serverPort = 12009
serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(10)
database = lite.connect('user.db')
def main():
    print("main")






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
    main()