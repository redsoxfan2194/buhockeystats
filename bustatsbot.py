from burecordbook import *
from credentials import *
import tweepy

dfGames=generateRecordBook()


auth = tweepy.OAuthHandler(API_KEY, API_SECRET_KEY)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

# Create API object
api = tweepy.API(auth, wait_on_rate_limit=True)

# check DMs
messages = api.get_direct_messages()

myUID='1525076436603871233'    
for message in reversed(messages):
  # who is sending?  
  sender_id = message.message_create["sender_id"]
  if(sender_id!=myUID):
      # what is she saying?
      text = message.message_create["message_data"]["text"]
      # delete by ID
      result=getResults(dfGames,text)
      if(result!=''):
        api.send_direct_message(sender_id, "{}: {}".format(text,result))
      u=api.get_user(user_id=sender_id)
      print(u.name,u.screen_name)    
  api.delete_direct_message(message.id)

# Check Mentions 
for mentions in tweepy.Cursor(api.mentions_timeline).items():
    # process mentions here
    print("{}-{}:{}".format(mentions.user.name,mentions.user.screen_name,mentions.text))
    tweetid=mentions.id
    query=mentions.text.lstrip('@BUStatsBot ')
    result=getResults(dfGames,query)
    if(result!=''):
        print(result)
        api.update_status(status = result, in_reply_to_status_id = tweetid , auto_populate_reply_metadata=True)
  