###Chat Bot

import sqlite3 as lite
from socket import *
from _thread import *
from datetime import *
from time import *


serverPort = 12009
serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(10)

UserConnectionList = []
############################
# Responses: Type \t Failure OR Success \r\n
#        Ex: SendMessage \t Success \r\n
#  Requests: Type \t Data \r\n
#        Ex: RegisterUser \t FirstName \t LastName \t Address \t Email \t password1 \r\n
###########################

def initiation():
    print("Server started.")
    print(time())
    while 1:
        print("Server ready to accept connections.")
        connectionSocket, addr = serverSocket.accept()

        print(addr)
        start_new_thread(main, (connectionSocket,))


def main(connectionSocket):
    print("main")
    # request = connectionSocket.recv(1024).decode('ascii')
    #RegisterUser("", connectionSocket)
    SessionData = {
        'id': '',
        'FirstName': '',
        'LastName': '',
        'LastActive': '',
    }
    UserConnectionList.append(SessionData)



# SendMessage \t Message \r\n
# SendMessage \t Success \r\n
# SendMessage \t Failure \r\n
def sendMessage():

    print("sendMessage")


# SendPrivateMessage \t Sender \t Receiver \t Message \r\n
# SendPrivateMessage \t Success \r\n
# SendPrivateMessage \t Failure \r\n
def sendPrivateMessage():
    print("sendPrivateMessage")


# RegisterUser \t FirstName \t LastName \t Address \t Email \t password1 \r\n
# RegisterUser \t Success \r\n
# RegisterUser \t Failure \r\n
def RegisterUser(request, connectionSocket):
    database = lite.connect('Users.db')
    print("Register user")
    firstName = 'David23'
    lastName = 'Buchhei12t'
    address = 'address0jj1'
    email = 'asdkj'
    password = '1234125'
    # Query for checking if user has an account already
    # Checks if all the current data exists and checks if email already is in database
    values = (firstName, lastName, address, email, email)
    check = database.cursor()
    test = check.execute("SELECT COUNT(*)" +
                            " FROM User" +
                            " WHERE " +
                            "( firstName = ? AND lastName = ? AND address = ?) OR email = ?", values)

    if test.fetchone()[0] > 0: #if user already has info in DB. Send failure response
        print("Registration failure")
        response = "RegisterUser\tFailure\r\n"
        connectionSocket.send(response.encode())
    else:
        print("Registration successful")
        values = (firstName, lastName, address, email, password)


        cur = database.cursor()

        insert = cur.execute("insert into User('firstName', 'lastName', 'address', 'email', 'password') values (?, ?, ?, ?, ?)", values)
        print(cur.fetchall())
    database.close()


# CheckLogin \t email \t Password \r\n
# CheckLogin \t Success \r\n
# CheckLogin \t Failure \r\n
def loginCheck(request, connectionSocket):
    database = lite.connect('Users.db')
    email = ""
    password = ""
    loginValues = (email, password)
    loginCheck = database.execute("SELECT COUNT(*) FROM User WHERE email = ? AND password = ?", loginValues)
    if loginCheck.fetchone()[0] > 0:
        connectionSocket.send("CheckLogin \t Success \r\n".encode())
        database.close()
        return ["Failure"]
    else:
        infoValues = email
        information = database.execute("SELECT id, firstName, lastName FROM User WHERE email = ?", infoValues)
        information = information.fetchone()
        connectionSocket.send("CheckLogin \t Failure \r\n".encode())
        database.close()
        return ["Success", connectionSocket[0], connectionSocket[1], connectionSocket[2]]




# FriendsList \r\n
# FriendsList \t Success \t Array Of Friends \r\n
# ArraySchema: User, Status
# FriendsList \t Failure \r\n
def printFriendsList():
    print("printFriendsList")


# FriendStatus \t Friend \r\n
# FriendStatus \t Success \t Status \r\n
# FriendStatus \t Requester \t Friend \r\n
def getFriendStatus():
    print("getFriendStatus")


# OfflineMessages \r\n
# OfflineMessages \t Success \t Messages Array \r\n
# ArraySchema: User, Message, Time
# OfflineMessages \t Failure \r\n

# OfflinePrivateMessages \t Success \t Messages Array \r\n
# OfflinePrivateMessages \t Failure \t \r\n
# ArraySchema: User, Message, Time
def getOfflineMessages():
    print("getOfflineMessages")
    print()

if __name__ == '__main__':
    initiation()
