from burecordbook import *
from credentials import *
import tweepy
import time

def getListOfTweets(api):
    tweetList=[]
    for tweets in api.user_timeline(count=200):
        tweetList.append(tweets.in_reply_to_status_id)
    return tweetList

dfGames=generateRecordBook()

auth = tweepy.OAuthHandler(API_KEY, API_SECRET_KEY)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
replyList=[]
# Create API object
api = tweepy.API(auth, wait_on_rate_limit=True)
print("Starting up BUStatsBot...")
while(True):
    if(replyList==[]):
        replyList = getListOfTweets(api)
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
          print(u.name,u.screen_name,"{}: {}".format(text,result))    
      api.delete_direct_message(message.id)

    # Check Mentions 
    for mentions in tweepy.Cursor(api.mentions_timeline).items():
        # process mentions here
        tweetid=mentions.id
        if(tweetid in replyList):
            continue
        query=mentions.text.lstrip('@BUStatsBot ')
        result=getResults(dfGames,query)
        print("{}-{}:{}:{}".format(mentions.user.name,mentions.user.screen_name,mentions.text,result))
        if(result!=''):
            api.update_status(status = result, in_reply_to_status_id = tweetid , auto_populate_reply_metadata=True)
            replyList.append(tweetid)
      
    time.sleep(60)