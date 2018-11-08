#!/usr/bin/python
import twitch_msg as TwitchMsg
import socket
import sys
import datetime
import collections
import json
from requests import get
from pymongo import MongoClient
import dbdriver

CLIENT = MongoClient('localhost',27017)

#filters a message returning a use code to be read by the processing loop
# 0 = do not process
# 1 = process
def shouldProcessMessage(user, msg, blocked, nick):

  #incomplete message, don't print
  if (len(user) + len(msg)) < 2:
    return 0
  #USER IS ON THE BLOCKED LIST GET OUTTA HERE
  if user in blocked:
    return 0
  #filter out bullshit irc flags
  if nick in user:
    return 0

  return 1

class TwitchListener:

  irc = socket.socket()
  
  #setup socket object
  def __init__(self,channelname):
    self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.channel_info = json.load(open('data/channeldata.json'))
    self.channel = self.channel_info[channelname]
    self.blocked = self.channel['blocked']

    self.twitchChannelID = "0"
    self.channel_emojis = []
    self.currentViewers = 0

    self.name = CLIENT.settings.irc_info.find()[0]['name']
    self.domain = CLIENT.settings.irc_info.find()[1]['domain']
    self.nick = CLIENT.settings.irc_info.find()[2]['nick']
    self.port = int(CLIENT.settings.irc_info.find()[3]['port'])
    self.oauthpw = CLIENT.settings.irc_info.find()[4]['oauthpw']

  #pings api to get current number of viewers, live updates.
  def getApiInfo(self):
    apidata = get('https://api.twitch.tv/kraken/streams/%s' % self.channel['name'],headers={"Client-ID":CLIENT.settings.api_info.find_one()['Client-ID']}).json()

    self.twitchChannelID = str(apidata['stream']['channel']['_id'])
    self.currentViewers = apidata['stream']['viewers']

  #connects to a specified channel on the specified server using the pass/nick combo
  #info is contained in settings file
  def connect(self):
    
    self.getApiInfo()

    print("Connecting to: {}#{}".format(self.domain,self.channel['name']))
    print("There are {} viewers in this channel currently.".format(self.currentViewers))
    
    #attempt connection
    try:
      self.irc.connect((self.domain, self.port))
      self.irc.send(("USER {0} {0} {0}\n".format(self.nick)).encode('utf-8'))
      self.irc.send(("PASS {}\n".format(self.oauthpw)).encode('utf-8'))
      self.irc.send(("NICK {}\n".format(self.nick)).encode('utf-8'))              
      self.irc.send(("JOIN #{}\n".format(self.channel['name'])).encode('utf-8'))
      print("Connection successful!")
    
    #catch error
    except ConnectionRefusedError:
      print("Error! Connection Refused. Server connection is either incorrectly configured or not running.")
      sys.exit()

  #receive all text info from twitch chat
  def getmsg(self):
    text = self.irc.recv(4096)

    #pong that ping, let 'em know you're still around
    if b'PING' in text:
      self.irc.send((b'PONG %b\r\n' % text.split()[1]))
      time = datetime.datetime.now().time()
      return TwitchMsg.TwitchMsg("PING","PONGED @ {}:{}:{}".format(time.hour,time.minute,time.second))
      
    #scrub username/message body from bytebuffer and cast to str so it is .join()able
    username = text[1:text.find(b'!')].decode('utf-8')
    msg = text[text.rfind(b'#' + bytes(self.channel['name'].encode('utf-8'))) + len(self.channel['name']) + 3 : -1].decode('utf-8')
    
    if shouldProcessMessage(username, msg, self.blocked, self.nick):
      return TwitchMsg.TwitchMsg(username, msg)


## MAKE ME MONGO
  def getChannelEmojis(self):
    emojiFile = open('data/emojidata.txt','r')

    ## PHASE ONE - IMPORT EMOJIS FROM PULLED FILE
    reachedSubEmotes = False

    for line in emojiFile:

      #if the line isn't a channel specific ID or it contains the generic twitchpresents channel ID, include the emojis to those to reference
      if not line.__contains__(':::'):
        self.channel_emojis.append(line.strip())
        
      if line.startswith('149747285'):
        self.channel_emojis.append(line[line.rfind(':::')+3:].strip())

      #if the line contains the ID of the channel we're looking for, make a note that we've reached where we want to be and skip the final check
      if line.startswith(self.twitchChannelID + ":::"):
        if not reachedSubEmotes: 
          reachedSubEmotes = True
        self.channel_emojis.append(line[line.rfind(':::')+3:].strip())
        continue

      #if we are here it means that we passed the twitchpresents section and are not looking at our currently connected channel
      #in this case, if we have reached the channel we need to already, it means that we don't need to be looking anymore
      if reachedSubEmotes:
        break
    
    emojiFile.close()

    ## PHASE 2 - PULL CHANNEL SPECIFIC EMOJI DATA FROM FRANKERFACEZ
    #bless open APIs holy shit

    channelSpecificEmojiSet = get('https://api.frankerfacez.com/v1/room/{}'.format(self.channel['name'])).json()
    setID = str(channelSpecificEmojiSet['room']["set"])

    for emojiInfoBlocks in channelSpecificEmojiSet['sets'][setID]['emoticons']:
      #iterate through the json pull and add the names of the channels emoji sets to self.channel_emojis
      self.channel_emojis.append(emojiInfoBlocks['name'])
    
      
  def run(self):
    #connect to the channel
    self.connect()

    while True:
      # get username/msg for blocked user checking
      try:            
        message = self.getmsg()
      except OSError and KeyboardInterrupt:
        return

      #u can pass
      if message and message.isIncluded:

        #do emoji processing shit here
        message.refactor(self.channel_emojis)

        #pray to jeebus that there aren't any unreadable things in the message (figure out how to fix this damn you)
        try:
    
          ## HERE BE WORK ##	
          #somevars = process msg
          #what to be returned? <<msg object>, <data vector>>
          # <msg object> = <emoji ref ordereddict, str with ref index chars, plaintext msg (justwords)>
          # <data vector> = <vader score, keyword(s?), ...>
          ##################

          print("{} -- {}: {}".format(message.timestamp, message.user, message.msg))

        #na boo
        except UnicodeDecodeError:
          print("Message contained shit we can't read")






      

  


