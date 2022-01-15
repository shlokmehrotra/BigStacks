import socketio
import json
import requests
from uuid import uuid4

def help():
    print('''
    ​------- HELP ------\n
    $create: Create a room.\n
    $display: Display all active rooms.\n
    $help: Shows the default help message (this one).\n
    $join: Join a channel exists.\n
    $leave: Leave a particular channel.\n
    $count: Return the number of rooms.\n
    $status: Displays current status.\n''')

# Get user as a string input
def get_user():
    temp = input("Enter an alias: ")

    # Bools for invalid usernames
    empty_user = (temp == "")
    invalid_chars = (" " in temp)

    # Ensure that user maintains a valid username
    while empty_user or invalid_chars:
        if empty_user:
            temp = input("User can't be blank! Please try again: ")
        else:
            temp = input("Username can't have spaces! Please try again: ")
        
        empty_user = (temp == "")
        invalid_chars = (" " in temp)
    
    return temp

# Get room to join as a string input
def get_room():
    temp = input("Enter a room to talk in: ")

    # Bools for invalid usernames
    empty_room = (temp == "")
    invalid_chars = (" " in temp)
    
    # Ensure that user maintains a valid username
    while empty_room or invalid_chars:
        if empty_room:
            temp = input("Room can't be blank! Please try again: ")
        else:
            temp = input("Room name can't have spaces! Please try again: ")

        empty_room = (temp == "")
        invalid_chars = (" " in temp)

    return temp

help()
user = get_user()
room = get_room()
uuid = str(uuid4())

def create(room):
    params = {"user": user, "room": room, "id": uuid}
    requests.get(f"{URL}/push", params)
    sio.emit("join", params)

def display():
    r = requests.get(f"{URL}/display", {})
    dict_ = r.json()
    rooms = dict_["rooms"]

    if (len(rooms) == 0 or rooms == None):
        print("----- NO ACTIVE ROOMS ----")
        return
    print("​----- ACTIVE ROOMS ----")
    print("\t• ", end="")
    print("\n\t• ".join(rooms))
    return 

def join(room):
    params = {"user": user, "room": room, "id": uuid}
    requests.get(f"{URL}/push", params)
    sio.emit("join", params)

def leave():
    global room
    params = {"key":"id", "value":uuid, "room":room}
    sio.emit("leave", params)
    room = None

def count():
     r = requests.get(f"{URL}/count", {})
     dict = r.json()
     print(dict["count"])

def status():
    if room:
        print(f"currently connected to {room}")
    else:
        print("not part of a room!")

def find_command(text):
    help()
    if (text in commands):
        commands[text]
        return 0
    else:
        return -1
        #This is not a valid command

sio = socketio.Client()

@sio.event
def message(message):
    data = json.loads(message)
    if data["id"] != uuid:
        print(f"\r{data['user']}: {data['msg']}")

@sio.event
def connect():
    print("Connected to the server, type to send messages!")

@sio.event
def connect_error(data):
    print("Connection Error!")

@sio.event
def disconnect():
    print("Disconnected!")

commands = {"create": create, "display": display, "help":help, "join":join, "leave":leave, "count":count, "status":status}
URL = "http://127.0.0.1:3000"
sio.connect(URL)

create(room)

while True:
    message_text = input()
    command = None
    
    for c in commands:
        if message_text.lower().startswith("$" + c):
            command = c
            break

    
    if command != None:
        arguments = message_text.split()

        if command == "join" or command == "create":
            if (len(arguments) < 2):
                print("Please name your room. Retype the command and try again.")
                continue
            # params = {"room": room, "id":uuid, "user":user}
            leave()
            room = arguments[1]
            commands[command](arguments[1])
        else:
            commands[command]()
        
    else:
        data = {"user": user, "msg": message_text, "room": room, "id":uuid}
        message_data = json.dumps(data)
        sio.emit("json", message_data)