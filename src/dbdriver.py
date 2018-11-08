from pymongo import MongoClient
from requests import get
import datetime

#relies on a local mongodb installation

#general schema for project -
# database: stream title

CLIENT = MongoClient('localhost',27017)
EMOTES_DB = CLIENT['emotes']

def updateChannelSubEmotes(channelName):

  a=get('https://api.twitch.tv/api/channels/:channel_name/product',headers={'Client-ID':CLIENT.settings.api_info.find_one()['Client-ID']})

  channel_emote_set_ids = []
  b=get('https://api.twitch.tv/kraken/chat/emoticon_images?emotesets={}'.format(','.join(channel_emote_set_ids)),headers={'Client-ID':CLIENT.settings.api_info.find_one()['Client-ID']})

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
  initializeEmoteDatabases()

  #updateChannelSubEmotes('imaqtpie')

