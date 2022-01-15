
from flask import Flask, request
from flask_socketio import SocketIO
from flask_socketio import join_room, leave_room
import asyncio
import json
import os

import threading, queue

# Utilities functions
import utilities
import discord_bot

with open("config.txt", "r") as f:  
    config = []
    for line in f:
        config.append(line.strip())

os.environ["BOT_TOKEN"] = str(config[0].split("=")[1])
os.environ["FB_CRED"] = str(config[1].split("=")[1])
os.environ["FB_DB_URL"] = str(config[2].split("=")[1])


q = queue.Queue()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
sio = SocketIO(app)
client = discord_bot.testing()

@app.route("/")
def index():
    return "Server is up and running!"

# Route to create a room
@app.route("/push", methods=['GET', 'POST'])
def push():
    data = request.values.to_dict()
    utilities.create_room(data)
    return json.dumps({"status": "1"})


# Route to return JSON value of all the rooms
@app.route("/display", methods=['GET', 'POST'])
def display():
    rooms = utilities.get_rooms()
    return json.dumps({"rooms": rooms})

# Route to return count of all connections to a ROOM
@app.route("/connections", methods=["GET", "POST"])
def connections():
     target = request.values.get("room")
     connections = utilities.num_connections(target)
     return json.dumps({"connections": connections})

# Route to return count of all connections to a ROOM
@app.route("/count", methods=["GET", "POST"])
def count():
     count = utilities.count_rooms()
     return json.dumps({"count": count})

@app.route("/leave", methods=["GET", "POST"])
def leave():
    print("in leave!")
    params = request.values.to_dict()
    utilities.leave_room("id", params["id"])

async def send_discord(bot, data):
    await discord_bot.socket_receive(bot, data)
    
# Gets a message in JSON format
@sio.on('json')
def handle_json(message):
    data = json.loads(message)
    q.put(message)
    room = data["room"]
    sio.send(message, to=room)

    #res = asyncio.run_coroutine_threadsafe(send_discord(client, data), client_loop)
    # wait for the coroutine to finish
    #res.result()


    # asyncio.run(send_discord(client, data))
    # loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)
    # loop.run_until_complete(send_discord(data))
    # loop.close()

# Handle someone joining a room
@sio.on("join")
def on_join(data):
    room = data["room"]
    join_room(room)

# Handle someone leaving a room
@sio.on("leave")
def on_leave(data):
    key = "id"
    leave_room(data["room"]) 
    utilities.leave_room(key, data["value"])

@sio.on('connect')
def test_connect(auth):
    print("Client connected to the server!")


# async def run_discord_bot():
#     print("in!")
    

def run_server():
    sio.run(app, port=3000)

def run_worker():
    while True:
        item = q.get()
        print(f'Current: {item}')

if __name__ == '__main__':
    # asyncio.run(client.start(os.getenv("BOT_TOKEN")))
    
    # turn-on the worker thread
    # bot_thread = threading.Thread(target=run_discord_bot)
    server_thread = threading.Thread(target=run_server)
    # worker_thread = threading.Thread(target=run_worker)
    
    # bot_thread.start()
    server_thread.start()
    
    client.run(os.getenv("BOT_TOKEN"))
    # bot_thread.join()
    # server_thread.join()
