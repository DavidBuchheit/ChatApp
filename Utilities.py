import socket
import time

AFKTime = 300 #300 seconds (5 mins)

print("hello")
class Room:
    def __init__(self, owner, name, id):
        self.owner = owner #UserID
        self.name = name
        self.id = id
        self.players = []   # Array of all users

    def sendMessage(self, sender, message):
        msg = time.time() + " : " + sender + " : " + message + "\n" # SQL Insert on server end
        for player in self.players:
            if player.status != 1 and player.socket != "":
                player.socket.sendall(msg.encode())

    def lostUser(self, user):
        #if room owner, delete room
        if self.owner == user.id :
            self.players = {}
            OverView.deleteRoom(self.name)
        else:
            self.players.pop(user)
        print("lostUser")

    def joinUser(self, user):
        self.players.append(user)


class User:
    def __init__(self, socket, id, name, email, status):
        self.id = id
        self.name = name
        self.socket = socket
        self.email = email
        self.lastActive = 0
        self.status = status # 0 = Active, 1 = Offline

    def logout(self):
        self.status = 2
        self.socket.close()
        print("logout")

    def __repr__(self):
        return {'id': self.id, 'name': self.name, 'email': self.email, 'lastActive': self.lastActive, 'status': self.status, 'socket':self.socket}.__repr__()


class OverView:
    def __init__(self):
        self.rooms = [] # RoomName : Room object
        self.users = [] # Name : Player Object

    def listRooms(self):
        print("list rooms")

    def deleteRoom(self, roomName):
        self.rooms.pop(roomName)

    def createRoom(self, Owner, Roomname, id):
        self.rooms[Roomname] = Room(Owner, Roomname, id)
        self.rooms[Roomname].joinUser(Owner)

    def grabRooms(self, email=""):
        roomsWithUser = {}
        for room in self.rooms:
            # if the email is in the room's players
            for player in room.players:
                if player.email == email:
                    roomsWithUser.pop(room)
                    break

        return roomsWithUser

    def userLogin(self, userID, socket):
        for user in self.users:
            if(user.id == userID):
                user.status = 0
                user.socket = socket
                break

    def userLogout(self, connectionSocket):
        for user in self.users:
            if(user.connectionSocket == connectionSocket):
                user.status = 0
                user.connectionSocket = ""
                break



    def addUser(self, roomID, user):
        for room in self.rooms:
            if(room.id == roomID):
                room.joinUser(user)
                break




