###Chat Bot

import sqlite3 as lite
from socket import *
from _thread import *
from datetime import *
from time import *
from Utilities import Room, User, OverView


serverPort = 12010
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(10)

OverView = OverView()
############################
# Responses: Type \t Failure OR Success \r\n
#        Ex: SendMessage \t Success \r\n
#  Requests: Type \t Data \r\n
#        Ex: RegisterUser \t FirstName \t LastName \t Address \t Email \t password1 \r\n
###########################


def initiation():
    print("Server started.")
    createEverything()

    while 1:
        print("Server ready to accept connections.")
        connectionSocket, addr = serverSocket.accept()

        start_new_thread(main, (connectionSocket,))


#Utility function that creates every room and member when server is started.
def createEverything():
    database = lite.connect('user.db')
    cursor = database.cursor()

    #Gets every user and adds them to the list
    users = cursor.execute("select id, firstName, lastName, email from user")
    users = users.fetchall()

    for i in range(len(users)):
        OverView.users.append(User("", users[i][0],  users[i][1] + " " + users[i][2],  users[i][3], 1))

    rooms = cursor.execute("select * from rooms where deleted = '0' ")
    rooms = rooms.fetchall()
    #Makes every room and ends people to it
    for i in range(len(rooms)):

        people = cursor.execute("select distinct u.id, u.firstName, u.lastName, u.email from roomMembers as rm join user as u on u.id = rm.userID where rm.roomID = ?", [rooms[i][0]])
        people = people.fetchall()
        room = Room(rooms[i][2], rooms[i][1], rooms[i][0])
        for j in range(len(people)):
            for k in range(len(OverView.users)):
                if(OverView.users[k].id == people[j][0]):
                    room.joinUser(OverView.users[k])
        OverView.rooms.append(room)

    print("Rooms & Users populated")
    return 0

# JoinRoom \t UserID \t RoomID \r\n
# JoinRoom \t Success \r\n
# JoinedRoom \t User \r\n     Sends user info to clients when seomeone joins room
def joinRoom(connectionSocket, request):
    request = request.strip("\r\n")
    request = request.split("\t")
    UserID =  int(request[1])
    roomID = int(request[2])

    database = lite.connect('user.db')
    cursor = database.cursor()
    cursor.execute("insert into roomMembers values(roomID = ?, userID = ?)", [roomID, UserID])

    connectionSocket.send("JoinRoom\tSuccess\r\n".encode() )
    # connectionSocket.send( OverView.findUserByID(userID).encode() )

    return 1

# RoomsInfo \r\n
# YourRooms { RoomName, RoomID } \r\n
def getMyRooms(connectionSocket, request):
    user = OverView.findUserBySocket(connectionSocket)
    print("Get Rooms")
    rooms = OverView.grabRoomsWithUser(user.id)
    send = "YourRooms\t" + rooms.__str__()
    connectionSocket.send( send.encode() )

    return 1

# LeaveRoom
# LeaveRoom \t Success \r\n
# LeftRoom \t User \r\n Sends user info to clients when someone leaves room
def leaveRoom(connectionSocket, request):
    print("leaveRoom")

def main(connectionSocket):
    print("main")
    while 1:
        request = connectionSocket.recv(1024).decode('ascii')

        type = request.split("\t")
        if type[0] == "RegisterUser":
            RegisterUser(request, connectionSocket)
        elif type[0] == "CheckLogin":
            loginCheck(request, connectionSocket)
        elif type[0] == "SendMessage":
            sendMessage(request, connectionSocket)
        elif type[0] == "sendPrivateMessage":
            sendPrivateMessage(request, connectionSocket)
        elif type[0] == "joinRoom":
            joinRoom(request, connectionSocket)
        elif type[0] == "logout":
            logout(request, connectionSocket)
        elif type[0] == "createRoom":
            createRoom(request, connectionSocket)
        elif type[0] == "getOfflineMessages":
            getOfflineMessages(request, connectionSocket)
        elif type[0] == "FriendsList":
            printFriendsList(request, connectionSocket)
        elif type[0] == "RoomsInfo":
            getMyRooms(request, connectionSocket)



# SendMessage \t Message \t RoomID \r\n
# SendMessage \t Success \r\n
# SendMessage \t Failure \r\n

# IncomingMessage \t Message \t RoomID \r\n
def sendMessage(request, connectionSocket):
    request = request.strip("\r\n")
    request = request.split("\t")
    message = request[1]
    roomID = int(request[2])

    OverView.sendMessage(roomID, message, OverView.findUserBySocket(connectionSocket))

    print("sendMessage")


# SendPrivateMessage \t Sender \t Receiver \t Message \r\n
# SendPrivateMessage \t Success \r\n
# SendPrivateMessage \t Failure \r\n
def sendPrivateMessage(request, connectionSocket):
    print("sendPrivateMessage")

# CreateRoom \t RoomName \r\n
# CreateRoom \t Success \r\n
# CreateRoom \t Failure \r\n
def createRoom(request, connectionSocket):
    print("as")

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
    password = password.strip('\r\n')
    loginValues = (email, password)
    loginCheck = database.execute("select count(*) from user where email = ? and password = ?", loginValues)
    count = loginCheck.fetchall()[0][0]

    if count < 1:
        status = "CheckLogin\tFailure\r\n"
        connectionSocket.send(status.encode())
        database.close()
        print("Login failure")
        return ["Failure"]
    else:

        infoValues = email
        information = database.execute("select id, firstName, lastName, email from user where email = ?", [infoValues])
        info = information.fetchall()
        status = "CheckLogin\tSuccess\r\n"
        connectionSocket.send(status.encode())

        OverView.userLogin(info[0][0], connectionSocket)
        database.close()

        print(OverView.users)
        print("Login Successful")
        return ["Success"]

# FriendsList \r\n
# FriendsList \t Success \t Array Of Friends \r\n
# ArraySchema: User, Status
# FriendsList \t Failure \r\n
def printFriendsList(request, connectionSocket):
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
def getOfflineMessages(request, connectionSocket):
    print("getOfflineMessages")
    #Grab all messages where their logout time is less than all messages

# Logout \r\n
# Logout \t Success \r\n
# Logout \t Failure \r\n
def logout(request, connectionSocket):
    print("Logout")
    OverView.userLogout(connectionSocket)
    #update DB where their last online time is now and remove them from current users array



if __name__ == '__main__':
    initiation()
