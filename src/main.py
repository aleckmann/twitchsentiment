#!/usr/bin/python
import twitch_listener as Listener
import json
from appsettings import settings
import argparse
import requests
import datetime

SAVE_API_DATA = False
CLIENT_ID = settings["clientid"]
DEFAULT_CONNECT = 'imaqtpie'
DEFAULT_BLOCK_LIST = []

def updateChannelData(chanName):
  #load data into memory for referencing values
  data = json.load(open('channeldata.json'))

  #if no saved data
  if chanName not in data:
    #open with intention to append and erase the last few EOL characters that satisfy json formatting rules
    datafile = open('channeldata.json','a+')
    datafile.truncate((datafile.seek(0,2)-3))

    #write the initial formatting string and then append a block representing the channel data
    datafile.write(',\n\t"{}": '.format(chanName))
    newdata = {
      "name": chanName,
      "blocked": DEFAULT_BLOCK_LIST
    }

    #dump that json data baby (then append eol formatting chars and close the file)
    json.dump(newdata,datafile)
    datafile.write("\n}")
    datafile.close()
    return 1
  return 0

#determines the channel to connect to - handles checking if channel is live/exists, adding to saved channel array and whatnot
# chanName = name of the channel to connect to as a string
def chooseChannel(args):
  
  #default channel
  chanName = DEFAULT_CONNECT if args == None else args

  #query twitch for channel info
  apiData = requests.get('https://api.twitch.tv/kraken/streams/%s' % chanName,headers={"Client-ID":CLIENT_ID}).json()

  #if the channel is currently offline, prompt for a new channel and recursively attempt that one
  if not apiData['stream']:
    ans = input("Looks like you tried to access a stream that's currently offline. Please enter another channel name: (type quit to exit)\n>>>")
    if str(ans).lower() == 'quit': 
      exit()  #quit the whole program if specified
    chanName = chooseChannel(ans)

  #save the data if provided in arg
  if SAVE_API_DATA: json.dump(apiData, open('api_data_{}_{}.json'.format(chanName,datetime.datetime.now().date()), 'w+'), indent=2, separators=(',',': '))

  if updateChannelData(chanName): print("Updated channel data")

  return chanName


if __name__ == '__main__':                          
  #init parser
  parser = argparse.ArgumentParser(description = 'Creep on a TwitchChannel')
  parser.add_argument('-chan',nargs='?')
  parser.add_argument('-apiref',action='store_true')
  args = parser.parse_args()

  SAVE_API_DATA = args.apiref

  #get channel name
  chanName = chooseChannel(args.chan)

  #make a connection to the channel
  connection = Listener.TwitchListener(chanName)
  connection.run()