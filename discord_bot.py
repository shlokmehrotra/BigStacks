import discord
from discord.ext import commands
from datetime import datetime, timedelta, timezone
import os
import requests

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db


with open("config.txt", "r") as f:  
    config = []
    for line in f:
        config.append(line.strip())


os.environ["BOT_TOKEN"] = str(config[0].split("=")[1])
os.environ["FB_CRED"] = str(config[1].split("=")[1])
os.environ["FB_DB_URL"] = str(config[2].split("=")[1])


#cred = credentials.Certificate(os.getenv("FB_CRED"))


#firebase_admin.initialize_app(cred, {
#    'databaseURL': os.getenv("FB_DB_URL")
#})

ref = db.reference('/channels')
client = commands.Bot(command_prefix = "$")

'''
Send to All
'''
async def socket_receive(bot, data):
  ref = db.reference('/channels')
  print(type(data), data)
  room_name = data["room"]
  room = ref.child(room_name).get()
  user = data["user"]
  print(type(room))
  print(room)
  for _, chnl_info in room.items():
    if ("id" not in chnl_info):
      print(chnl_info["Channel"], "\n")
      receiver = bot.get_channel(int(chnl_info["Channel"]))
      print("POST-CREATION OF RECEIVER")
      print("\n\n\n")
      print(receiver==None)
      # await receiver.send("**" + str(user) + "**"+ ": " + data["msg"])
      await receiver.send("msg")
  
async def send_to_all(ctx, room_name):
  ref = db.reference('/channels')
  room = dict(ref.child(room_name).get())

  for _, chnl_info in room.items():
    if "id" in chnl_info:
      #room is of type socket
      continue
    sender_chnl = str(ctx.channel.id)
    sender_gld = str(ctx.guild.id)
    if(sender_chnl == str(chnl_info["Channel"]) and sender_gld == str(chnl_info["Guild"])):
      continue
    else:
      receiver = client.get_channel(int(chnl_info["Channel"]))
      await receiver.send("**" + ctx.author.name + "**"+ ": " + ctx.content)


#the room is initialized with the channel that requested it

#check if a particular guild, channel is already in a room
def checkInRoom(channel, guild):
  ref = db.reference('/channels')
  values = ref.get()
  if(values == None):
    return -1
  for key, room in values.items():
    for random, data in room.items():
      #print(data, room)
      if "id" in data:
        #print("room name: ", room, " is a socket with id", data["id"])
        continue
      if(str(channel) == str(data["Channel"]) and str(guild) == str(data["Guild"])):
        return key
  return -1

def joinRoom(name, channel, guild):
  channel_ = ref.child(str(name))
  channel_.push({"Guild": str(guild), "Channel": str(channel)})



# REFACTORED
@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))
  guilds = client.guilds


@client.command()
async def ping(ctx):
  await ctx.send(f'pong! **{round(client.latency * 1000)}ms**.')


@client.command()
async def numrooms(ctx):
  ref = db.reference('/channels')
  values = ref.get()
  grammar_msg = "is 1 room" if len(values) == 1 else "are " + str(len(values)) + " rooms"
  await ctx.send(str("There " + grammar_msg + " available."))



@client.command()
async def joinroom(ctx, name):
  
  '''
  check if the channel you want to join exists
  if yes -> join channel
  if no -> send error message
  '''
  read_channel = ref.child(str(name))
  if(read_channel.get() != None):
    rv = checkInRoom(ctx.channel.id, ctx.guild.id)
    if(rv != -1):
      await ctx.send("You are already part of room: **" + rv + "**. Please leave the room before creating or joining another one." )
      return
    joinRoom(name, ctx.channel.id, ctx.guild.id)
    await ctx.send("You have joined the room.")
  else:
    await ctx.send("Room **" + str(name) + "** is not found. Maybe try creating a room by that name?")


@client.command()
async def createroom(ctx, name):
  rv = checkInRoom(ctx.channel.id, ctx.guild.id)
  if(rv != -1):
    await ctx.send("You are already part of room: **" + rv + "**. Please leave the room before joining another one." )
    return
  '''
  check if room by name `name` is already created
  if yes -> send error message
  if no -> create room
  '''

  read_channel = ref.child(str(name))

  if(read_channel.get() == None):
    joinRoom(name, ctx.channel.id, ctx.guild.id)
    await ctx.send("Room **" + str(name) +  "** was successfully created")
  else:
    await ctx.send("Room **" + str(name) + "** already exists. Consider joining this room or creating a room with a different name.")

@client.command()
async def status(ctx):
  rv = checkInRoom(ctx.channel.id, ctx.guild.id)
  if(rv == -1):
    await ctx.send("You are not connected to a room.")
    return
  await ctx.send("You are connected to room: **" + rv + "**" )

@client.command()
async def leaveroom(ctx):
  rv = checkInRoom(ctx.channel.id, ctx.guild.id)
  if(rv == -1):
    await ctx.send("This channel is not in a room.")
    return
  ref = db.reference('/channels')
  rooms = dict(ref.child(rv).get())
  for name, room in rooms.items():
    if("id" in room):
      continue
    if(str(room["Channel"]) == str(ctx.channel.id) and str(room["Guild"]) == str(ctx.guild.id)):
      rooms.pop(name)
      await ctx.send("Successfully left room **" + str(rv) + "**")
      break
  if rooms == {}:
    #room is deleted because there it has 0 channels
    ref.child(rv).delete()
    await ctx.send("Room: **" + str(rv) + "** was successfully deleted")
  ref.child(rv).set(rooms)
  #rv = name of room channel is in

@client.command()
async def displayrooms(ctx):
  ref = db.reference('/channels')
  embed = discord.Embed(
    title = "Rooms Available",
    color = discord.Color.blue()
  )  
  if(ref.get() == None):
    await ctx.send("No rooms have been created")
    return
  for room in ref.get():
    embed.add_field(name=f"`{room}`", value = f"`Active Channels:  {len(ref.child(room).get())}`", inline=False)
  await ctx.send(embed=embed)

# ON MESSAGE
@client.event
async def on_message(ctx):
  msg_content = ctx.content  
  if [c.name for c in client.commands if msg_content.lower().startswith("$" + c.name)] != []:
    await client.process_commands(ctx)
    return

  room_name = checkInRoom(ctx.channel.id, ctx.guild.id)
  if ctx.author == client.user or room_name == -1:
        return
  
  await send_to_all(ctx, room_name)

def testing():
  return client

client.run(os.getenv("BOT_TOKEN"))
