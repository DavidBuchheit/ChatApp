###Chat Bot

import sqlite3 as lite
from socket import *
from _thread import *
from datetime import *
from time import *


serverPort = 12010
serverSocket = socket(AF_INET, SOCK_STREAM)
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
    while 1:
        request = connectionSocket.recv(1024).decode('ascii')
        #request = "RegisterUser\tFirstName\tLastName\tAddress\tEmail\tpassword\r\n"

        type = request.split("\t")
        if type[0] == "RegisterUser":
            RegisterUser(request, connectionSocket)
        elif type[0] == "CheckLogin":
            loginCheck(request, connectionSocket)




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
    database = lite.connect('user.db')
    print("Register user")
    type = request.split("\t")
    firstName = type[1]
    lastName = type[2]
    address = type[3]
    email = type[4]
    password = type[5]
    # Query for checking if user has an account already
    # Checks if all the current data exists and checks if email already is in database
    values = (firstName, lastName, address, email)
    check = database.cursor()
    test = check.execute("select count(*) from user where ( firstName = ? and lastName = ? and address = ?) or email = ?", values)
    if test.fetchone()[0] > 0: #if user already has info in DB. Send failure response
        print("Registration failure")
        database.close()
        response = "RegisterUser\tFailure\r\n"
        connectionSocket.send(response.encode())
        return ["Failure"]
    else:
        print("Registration successful")
        vals = [firstName, lastName, address, email, password]
        cur = database.cursor()
        insert = cur.execute("insert into user(firstName, lastName, address, email, password) values (?, ?, ?, ?, ?)", vals)
        lastRowID = cur.lastrowid
        database.commit()
        database.close()
        response = "RegisterUser\tSuccess\r\n"
        connectionSocket.send(response.encode())
        return ["Success", lastRowID, vals[0], vals[1], vals[3]]


#
# -----------We should use the username and not the email for this-----------
#
# CheckLogin \t email \t Password \r\n
# CheckLogin \t Success \r\n
# CheckLogin \t Failure \r\n
def loginCheck(request, connectionSocket):
    database = lite.connect('user.db')
    type = request.split("\t")
    email = type[1]
    password = type[2]
    print("Checking " + email + " with " + password)
    loginValues = (email, password)
    loginCheck = database.execute("select count(*) from user where email = ? and password = ?", loginValues)
    if loginCheck.fetchone()[0] > 0:
        status = "CheckLogin \t Success \r\n"
        connectionSocket.send(status.encode())
        database.close()
        print(status)
        return ["Failure"]
    else:
        infoValues = email
        information = database.execute("select id, firstName, lastName from user where email = ?", infoValues)
        information = information.fetchone()
        status = "CheckLogin \t Failure \r\n"
        connectionSocket.send(status.encode())
        database.close()
        print(status)
        return ["Success", information[0], information[1], information[2]]

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
    #Grab all messages where their logout time is less than all messages

# Logout \r\n
# Logout \t Success \r\n
# Logout \t Failure \r\n
def logout():
    print("Logout")
    #update DB where their last online time is now and remove them from current users array

if __name__ == '__main__':
    initiation()
