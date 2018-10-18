from requests import get

if __name__ == "__main__":
  f = open('emojidata.txt','w')

  #get bttv emotes
  a = get("https://api.betterttv.net/emotes").json()['emotes']
  for line in a:
    f.write('{}\n'.format(line['regex']))

  #get ttv sub emotes, formatted like CHAN_ID:::emotestr
  #ttv sub emotes include all regular emotes as well since TwitchPresents's sub emotes are just regular twitch emotes
  c = get("https://twitchemotes.com/api_cache/v3/subscriber.json").json()
  for line in c:
    for obj in c[line]['emotes']:
      f.write("{}:::{}\n".format(line, obj['code']))

  f.close()
    