#!/usr/bin/python
from data.appsettings import settings
import twitch_msg as TwitchMsg
import socket
import sys
import datetime
import collections
import json
from requests import get

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

  def getCurrentViewers(self):
    return get('https://api.twitch.tv/kraken/streams/%s' % self.channel['name'],headers={"Client-ID":settings['clientid']}).json()['stream']['viewers']

  #connects to a specified channel on the specified server using the pass/nick combo
  #info is contained in settings file
  def connect(self):
    
    print("Connecting to: {}#{}".format(settings['domain'],self.channel['name']))
    print("There are {} viewers in this channel currently.".format(self.getCurrentViewers()))
    
    #attempt connection
    try:
      self.irc.connect((settings['domain'], settings['port']))
      self.irc.send(("USER {0} {0} {0}\n".format(settings['nick'])).encode('utf-8'))
      self.irc.send(("PASS {}\n".format(settings['oauthpw'])).encode('utf-8'))
      self.irc.send(("NICK {}\n".format(settings['nick'])).encode('utf-8'))              
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
    
    if shouldProcessMessage(username, msg, self.blocked, settings['nick']):
      return TwitchMsg.TwitchMsg(username, msg)

  def run(self):
    self.connect()

    while True:
      # get username/msg for blocked user checking
      try:            
        message = self.getmsg()
      except OSError and KeyboardInterrupt:
        return

      #u can pass
      if message and message.isIncluded:
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
                  






      

  


