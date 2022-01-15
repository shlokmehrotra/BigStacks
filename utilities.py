import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import os 


# FIREBASE CONFIG
with open("config.txt", "r") as f:  
    config = []
    for line in f:
        config.append(line.strip())

os.environ["BOT_TOKEN"] = str(config[0].split("=")[1])
os.environ["FB_CRED"] = str(config[1].split("=")[1])
os.environ["FB_DB_URL"] = str(config[2].split("=")[1])

# fb_cred = str(config[1].split("=")[1])
# db_url = str(config[2].split("=")[1])

cred = credentials.Certificate(os.getenv("FB_CRED"))

firebase_admin.initialize_app(cred, {
    'databaseURL': os.getenv("FB_DB_URL")
})

ref = db.reference('/channels')

# Check if a room exists within the firebase
def room_exists(target):
    values = db.reference('/channels').get()
    return values and target in values

# Display all the active rooms
def get_rooms():
    values = db.reference('/channels').get()
    return values if values else []

# Return the amount of rooms
def count_rooms():
    values = db.reference('/channels').get()
    return len(values)

# Create a room in DB
def create_room(data):
    join_room(data)

# Add a room object to DB
def join_room(params):
    channel_ = ref.child(params.get("room")) #room is the name of the room
    channel_.push(params)

# Delete a room from DB
def delete_room(name):
    ref.child(name).delete()    

# Leave a room ()
# key is the name of the field, value is its value
def leave_room(key, value):
    values = ref.get()
    room = find_room(key, value)
    if not room:
        return
    for i, data in values[room].items():
        if data[key] == value:
            values[room].pop(i)
            ref.set(values)
            return

    if num_connections(room) == 0:
        delete_room(room)

# Return a room name, given a key and value to look for
def find_room(key, value):
    values = ref.get()
    for room_name, room_data in values.items():
        for _, data in room_data.items():
            if key in data and value == str(data[key]):
                return room_name
    return None

def num_connections(room):
    values = db.reference('/channels').get()
    return len(values[room])
