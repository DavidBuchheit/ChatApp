import socket
import time

AFKTime = 300 #300 seconds (5 mins)

print("hello")
class Room:
    def __init__(self, owner, name):
        self.owner = owner
        self.name = name
        self.players = []   # Array of all users

    def sendMessage(self, sender, message):
        msg = time.time() + " : " + sender + " : " + message + "\n" # SQL Insert on server end
        for player in self.players:
            player.socket.sendall(msg.encode())

    def lostUser(self, user):
        #if room owner, delete room
        if self.owner == user :
            self.players = {}
            OverView.deleteRoom(self.name)
        else:
            self.players.pop(user)
        print("lostUser")

    def joinUser(self, user):
        self.players.append(user)


class User:
    def __init__(self, socket, name="", email=""):
        socket.setblocking(0)
        self.name = name
        self.socket = socket
        self.email = email
        self.lastActive = 0
        self.status = 0 # 0 = Active, 1 = AFK, 2 = Offline

    def logout(self):
        self.status = 2
        print("logout")





class OverView:
    def __init__(self):
        self.rooms = {} # RoomName : Room object
        self.users = {} # Name : Player Object

    def listRooms(self):
        print("listrooms")

    def deleteRoom(self, roomName):
        self.rooms.pop(roomName)

    def createRoom(self, Owner, Roomname):
        self.rooms[Roomname] = Room(Owner, Roomname)
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
