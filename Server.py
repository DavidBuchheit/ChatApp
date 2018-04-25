###Chat Bot

import sqlite3 as lite
from socket import *
from _thread import *
import time
from Utilities import Room, User, OverView


serverPort = 12019
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
def joinRoom(request, connectionSocket):
    request = request.strip("\r\n")
    request = request.split("\t")
    UserID =  int(request[1])
    roomID = int(request[2])

    database = lite.connect('user.db')
    cursor = database.cursor()
    cursor.execute("insert into roomMembers values(roomID = ?, userID = ?)", [roomID, UserID])

    connectionSocket.send("JoinRoom\tSuccess\r\n".encode() )

    return 1

# RoomsInfo \r\n
# YourRooms { RoomName, RoomID } \r\n
def getMyRooms(request, connectionSocket):
    user = OverView.findUserBySocket(connectionSocket)
    print("Get Rooms")
    rooms = OverView.grabRoomsWithUser(user.id)
    send = "YourRooms\t" + rooms.__str__()
    connectionSocket.send( send.encode() )

    return 1

# RoomMembers \t RoomID \r\n
# RoomMembers \t {MemberName, MemberID}
def getRoomMembers(request, connectionSocket):
    request = request.strip("\r\n")
    request = request.split("\t")
    roomID = int(request[1])

    Users = OverView.getRoomMembers(roomID).__str__()
    connectionSocket.send( ("RoomMembers\t" + Users).encode() )
    return 1

# LeaveRoom \t roomID\r\n
# LeaveRoom \t Success \t UserID \t RoomID \r\n
def leaveRoom(connectionSocket, request):
    #Removes User froom Room and sends all the other clients telling them that someone has left the room
    database = lite.connect('user.db')
    cursor = database.cursor()

    request = request.strip("\r\n")
    request = request.split("\t")
    roomID = request[1]

    user = OverView.findUserBySocket(connectionSocket)
    userID = user.id

    delete = cursor.execute("delete from roomMembers where roomID = ? and userID = ?", (roomID, userID))
    database.commit()

    #Send back all room members and delete the room member from list

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
    addTime = int(time.time())
    user = OverView.findUserBySocket(connectionSocket)

    database = lite.connect('user.db')
    cursor = database.cursor()
    insert = cursor.execute("insert into messages(userID, message, timeStamp, roomID) values(?, ? ,? ,? )",[user.id, message, addTime, roomID])
    OverView.sendMessage(roomID, message, OverView.findUserBySocket(connectionSocket))

    print("sendMessage")


# SendPrivateMessage \t ReceiverID \t Message \r\n
# SendPrivateMessage \t Success \r\n
# SendPrivateMessage \t Failure \r\n
# RecievePrivateMessage \t Message \t Sender
def sendPrivateMessage(request, connectionSocket):
    database = lite.connect('user.db')
    cursor = database.cursor()
    print("sendPrivateMessage")
    request = request.strip("\r\n")
    request = request.split("\t")
    sender = OverView.findUserBySocket(connectionSocket)
    receiverID = int(request[1])
    receiver = OverView.findUserByID(receiverID)
    message = request[2]
    timeStamp = time.time()
    receiver = OverView.findUserByID(receiverID)
    insert = cursor.execute("insert into privateMessages(toUser, fromUser, message, timeStamp) values(?, ?, ?, ? )", [receiverID, sender.id, message, timeStamp])
    connectionSocket.send(("SendPrivateMessage\tSuccess").encode())

# GetPrivateMessages \t UserID \r\n   #Where UserID is friend
# PrivateMessages \t { message, time } ] \r\n
def getPrivateMessages(request, connectionSocket):
    database = lite.connect('user.db')
    cursor = database.cursor()
    request = request.strip("\r\n")
    request.split("\t")
    sender = OverView.findUserBySocket(connectionSocket)
    fromUserID = sender.id
    toUserId = request[1]
    messages = cursor.execute("select * from privateMessages where fromUser = ? and toUser = ? ",[fromUserID, toUserId])

    message = []
    for i in range(len(messages)):
        message = messages[i][3]
        time = message[i][4]
        message.append({'Message': message, 'Time': time })

    message = message.__str__()

    connectionSocket.send("PrivateMessages\t" + message + "\r\n")

    return 1


# CreateRoom \t RoomName \r\n
# CreateRoom \t Success \r\n
# CreateRoom \t Failure \r\n
def createRoom(request, connectionSocket):
    request = request.strip("\r\n")
    request = request.split("\t")
    roomname = request[1]
    owner = OverView.findUserBySocket(connectionSocket)

    database = lite.connect('user.db')
    cursor = database.cursor()

    cursor.execute("insert into rooms(name, ownerID, deleted) values(?, ?, 0)", [ roomname, owner.id ])
    return 1

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
        now = time.time()
        update = database.execute("update user set lastSeen = ? where email = ?", [int(now), email])
        database.commit()
        print("Login Successful")
        return ["Success"]

# FriendsList \r\n
# FriendsList \t Success \t Array Of Friends \r\n
# ArraySchema: User, Status

def printFriendsList(request, connectionSocket):
    print("printFriendsList")

    database = lite.connect('user.db')
    cursor = database.cursor()
    user = OverView.findUserBySocket(connectionSocket)

    users = cursor.execute("select distinct * from friends as f1, friends as f2 where f1.secondFriendID = f2.firstFriendID and f1.firstFriendID = f2.secondFriendID and (f1.firstFriendID = ?)", [user.id] )
    users = users.fetchall()

    friends = []
    for i in range(len(users)):
        secondPerson = OverView.findUserByID(users[i][1])
        id = users[i][1]
        friends.append( {"Name": secondPerson.name, "Status": secondPerson.status, "ID": id } )

    friends = friends.__str__()
    connectionSocket.send(("FriendsList\t" + friends + "\r\n").encode())

# AddFriend \t NewFriendID \t UserID \r\n
# AddFriend \t Success \r\n
def addFriend(request, connectionSocket):
    database = lite.connect('user.db')
    cursor = database.cursor()

    request = request.strip("\r\n")
    request = request.split("\t")

    newFriend = request[1]
    userID = request[2]
    cursor.execute("insert into friends values(?, ?)", [newFriend, userID])

    connectionSocket.send("AddFriend\tSuccess\r\n".encode())

# RemoveFriend \t UserID \r\n
# RemoveFriend \t Success \r\n
def removeFriend(request, connectionSocket):
    database = lite.connect('user.db')
    cursor = database.cursor()

    request = request.strip("\r\n")
    request = request.split("\t")

    secondFriend = int(request[1])
    firstFriend = OverView.findUserBySocket(connectionSocket)
    remove = cursor.execute("delete from friends where firstFriendID = ? and secondFriendID = ?", [firstFriend, secondFriend])
    database.commit()

    connectionSocket.send("RemoveFriend\tSuccess\r\n")

# FriendStatus \t FriendID \r\n
# FriendStatus \t Success \t Status \r\n
def getFriendStatus(request, connectionSocket):
    print("getFriendStatus")
    request = request.strip("\r\n")
    request = request.split("\t")
    friendID = request[1]

    friend = OverView.findUserByID(friendID)

    connectionSocket.send(("FriendStatus\tSuccess\t" + friend.status + "\r\n").encode())
    return 1


# GetMessages \t roomID \r\n
# GetMessages \t Success \t Messages Array \r\n
# ArraySchema: User, Message, Time, RoomID
# GetMessages \t Failure \r\n

def getOfflineMessages(request, connectionSocket):
    database = lite.connect('user.db')
    cursor = database.cursor()

    request = request.strip("\r\n")
    request = request.split("\t")

    user = OverView.findUserBySocket(connectionSocket)
    userID = user.id
    roomID = request[1]

    loadmessages = cursor.execute("select messages.* from messages join user on user.id = messages.userID where user.id = ? and messages.roomID = ?", [userID, roomID] )
    messages = []
    for i in range(len(loadmessages)):
        user = OverView.findUserByID( loadmessages[i][1])
        messages.append( {'User': user.name, 'Message': loadmessages[i][2], 'Time': loadmessages[i][3], 'RoomID': loadmessages[i][4] })
    print("getOfflineMessages")

# Logout \r\n
# Logout \t Success \r\n
# Logout \t Failure \r\n
def logout(request, connectionSocket):
    print("Logout")
    OverView.userLogout(connectionSocket)
    #update DB where their last online time is now and remove them from current users array



if __name__ == '__main__':
    initiation()
