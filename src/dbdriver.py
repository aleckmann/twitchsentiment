from pymongo import MongoClient
from requests import get
from functools import reduce
import datetime

#relies on a local mongodb installation

CLIENT = MongoClient('localhost',27017)
EMOTES_DB = CLIENT['emotes']
CHANNELS_DB = CLIENT['channels']

def updateChannelSubEmotes(channelName):

  channel_collection = CHANNELS_DB[channelName]
  emote_collection = EMOTES_DB[channelName]

  def getTwitchChannelEmotes():
    print("Getting {}'s Sub Emotes...".format(channelName))
    channelReferenceJson = get('https://api.twitch.tv/api/channels/{}/product'.format(channelName),headers={'Client-ID':CLIENT.settings.api_info.find_one()['Client-ID']}).json()
    
    channel_emote_set_ids = []
    for refset in channelReferenceJson['plans']:
      [channel_emote_set_ids.append(str(item)) if str(item) not in channel_emote_set_ids else 0 for item in refset['emoticon_set_ids']]

    emote_set_items = get('https://api.twitch.tv/kraken/chat/emoticon_images?emotesets={}'.format(','.join(channel_emote_set_ids)),headers={'Client-ID':CLIENT.settings.api_info.find_one()['Client-ID']}).json()

    already_stored_count = emote_collection.count_documents({'src':'twitchsub'})
    live_value = reduce(lambda x,y:x+y,[len(emote_set_items['emoticon_sets'][setid]) for setid in emote_set_items['emoticon_sets']])

    if live_value == already_stored_count:
      print("No update necessary.")
      return

    else:
      for set_id in emote_set_items['emoticon_sets']:
        [emote_collection.insert_one({'emote_name':str(x['code']),'src':'twitchsub'}) for x in emote_set_items['emoticon_sets'][set_id]]
      print("Successfully fetched {} sub emotes for channel {}".format(emote_collection,channelName))

  #TODO
  def getBTTVChannelEmotes():
    #https://api.betterttv.net/2/channels/imaqtpie
    return

  def getFFZChannelEmotes():
    #https://api.frankerfacez.com/v1/room/imaqtpie
    return

  getTwitchChannelEmotes()
  getBTTVChannelEmotes()
  getFFZChannelEmotes()

def initializeEmoteDatabases():

  def BTTVInit():
    collection = EMOTES_DB['BTTV']
    json = get("https://api.betterttv.net/emotes").json()
    emote_endpoint = json['emotes']
    ref_key = 'regex'

    #prevent overwriting/doublerecording
    if len(emote_endpoint) == collection.count_documents({}):
      print("BTTV collection already full!")

    else:
      print('Populating the BTTV collection ...')

      for emotes in emote_endpoint:
        collection.insert_one({'emote_name':str(emotes[ref_key])})

      print('There are {} emotes in the BTTV collection.'.format(collection.count_documents({})))
  
  def GlobalInit():
    collection = EMOTES_DB['GLOBAL']
    json = get("https://twitchemotes.com/api_cache/v3/global.json").json()

    #prevent overwriting/doublerecording
    if len(json) == collection.count_documents({}):
      print("Global collection already full!")

    else:
      print("Populating the global TTV collection ...")

      for emote in json:
        collection.insert_one({'emote_name':emote})

      print('There are {} emotes in the Global collection.'.format(collection.count_documents({})))

  BTTVInit()
  GlobalInit()

if __name__ == "__main__":
  #initializeEmoteDatabases()

  updateChannelSubEmotes('imaqtpie')

