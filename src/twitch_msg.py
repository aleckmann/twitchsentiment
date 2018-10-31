#!/usr/bin/python
import collections
import json
import time

class TwitchMsg:
  
  def __init__(self, username, msg):
    
    #initial data
    self.user = username
    self.msg = msg
    self.timestamp = time.time()
    
    #data to be generated
    self.msg_with_emojis = []                     #msg with ref to emoji set indices for complete msg -- type(list) (each word an obj, if emoji then int as str, int is index)
    self.text_msg = ''                            #msg with only the non emoji words in it
    self.emojis = collections.OrderedDict()       #ordered dict set of emojis
    
    #processing info
    self.valence = 0.			
    self.truelen = 0 			#len of msg considering emojis as len(1) chars instead of (<stringdata>)	
    
    #flags
    self.isRef = False    #contains @ to user that isn't channel["name"]
    self.isSpam = False           #is spam, work on spamfilter
    self.isLink = False        #contains link to outside site
    self.isCommand = False      #begins with !, is a command to a bot
    self.isIncluded = True      #should i even be included as a data point
    
    #early rudimentary classification of message to determine whether or not pre/processing steps should be taken
    self.flag()

    #preprocess
    self.refactor()

  def flag(self):
    #is a command to another bot
    if self.msg[0] == '!':
      self.isIncluded = False
      self.isCommand = True

    #is referential
    if self.msg.__contains__('@'):
      self.isIncluded = False
      self.isRef = True

    self.flagged = True
    return

  #prepares the message for processing
  def refactor(self):
  ##turn message into 2 parts, emoji dict and raw text data
    wholemsg = []
    plaintextmsg = []
    
    #populate self.emoji dict object
    for token in self.msg.split():
    
      #word is not an emoji	
      if token not in self.emojis:
        wholemsg.append(token)
        plaintextmsg.append(token)
      
      #word is an emoji
      #goal here is to represent the emoji as a len 1 character but still be able to parse it in string-only environment
      else:	
        #straightforward -- if first occurence of emoji set key to one otherwise increment by 1	
        self.emojis[token] = 1 if token not in self.emojis else self.emojis[token] + 1
        
        #GIVEN THAT the current token is an emoji as is specified in global staticemojis list
        #    extracts a list of the keys from the ordered dict and gets the index of the current token 
        #    then turns that index (type int) into a char of format 'x\00' = 0, 'x\01' = 1 etc
        #    this char is length 1 and can be turned back into type int with a call ord(char)
        #	ex: ord('x\00') = 0
        wholemsg.append(chr(list(self.emojis.keys()).index(token)))
    
    #the individual strings have been modified, now time to update fields
    self.msg_with_emojis = wholemsg
    self.text_msg = ' '.join(plaintextmsg)
    self.truelen = len(self.msg_with_emojis)

if __name__ == '__main__':
  testMsg = TwitchMsg('testuser','KappaPride I LOVE YOU KappaPride')
  print(testMsg.msg_with_emojis)
