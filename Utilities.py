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
        # IncomingMessage \t Message \t RoomID \t Sender \t Time \r\n
        message = "IncomingMessage\t"
        message += message + "\t"
        message += self.id.__str__() + "\t"
        message += sender.name + "\t"
        message += time.time().__str__() + "\r\n"

    def lostUser(self, user):
        #if room owner, delete room
        if self.owner == int(user):
            self.owner = -1

        print(self.players.__str__())
        try:
            self.players.remove(int(user))
        except ValueError:
            print("Already removed")

        if len(self.players) == 0:
            OverView.deleteRoom(self.name)
        return 0

    def containsUser(self, userID):
        if self.owner == userID:
            return True
        for player in self.players:
            if player == userID:
                return True
        return False

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
        newRoom = Room(Owner, Roomname, id)
        newRoom.joinUser(Owner)
        self.rooms.append(newRoom)

    def grabRoomsWithUser(self, userID):
        userRooms = []

        for room in self.rooms:
            if room.containsUser(userID):
                #userRooms.push(room)
                userRooms.append({"Name":room.name, "ID": room.id})

        return userRooms

    def grabRooms(self, email=""):
        roomsWithUser = []
        for room in self.rooms:
            # if the email is in the room's players
            for player in room.players:
                if player.email == email:
                    roomsWithUser.append(room)
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
            if(user.socket == connectionSocket):
                user.status = 0
                user.connectionSocket = ""
                break

    def addUser(self, roomID, user):
        for room in self.rooms:
            if(room.id == roomID):
                room.joinUser(user)
                break

    def findUserByID(self, userID):
        for user in self.users:
            if( int(user.id) == userID):
                return user

    def findUserBySocket(self, socket):
        for user in self.users:
            if( user.socket == socket):
                return user

    def findUserByEmail(self, email):
        for user in self.users:
            if (user.email.upper() == email.upper()):
                return user

    def sendMessage(self, roomID, message, socket):
        for room in self.rooms:
            if(room.id == roomID):
                room.sendMessage(self.findUserBySocket(socket), message)
                break

    def getRoomMembers(self, roomID):
        members = []
        for room in self.rooms:
            if( room.id == roomID):
                for member in room.players:
                    members.append({'Name': member.name, 'ID': member.id })
            break
        return members

    def findRoomByID(self, roomID):
        for room in self.rooms:
            print(room.id.__str__() + " : " + roomID.__str__())
            if room.id == int(roomID):
                return room
        return None

    def leaveRoom(self, roomID, userID):
        room = self.findRoomByID(roomID)
        room.lostUser(userID)