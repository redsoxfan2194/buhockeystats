from burecordbook import *
from credentials import *
import tweepy
import time
import traceback

def getListOfTweets(api):
    tweetList=[]
    for tweets in api.user_timeline(count=200):
        tweetList.append(tweets.in_reply_to_status_id)
    return tweetList

print("[{}]".format(datetime.now()),"Populating Record Book...")
dfGames=generateRecordBook()
dfGamesWomens=generateWomensRecordBook()
dfJersey,dfJerseyMens,dfJerseyWomens=generateJerseys()
dfSkate,dfSkateMens,dfSkateWomens=generateSkaters()
dfGoalie,dfGoalieMens,dfGoalieWomens=generateGoalies()
dfLead,dfLeadWomens=generateSeasonLeaders()
dfBeanpot,dfBeanpotWomens=generateBeanpotHistory()
dfSeasSkate,dfSeasSkateMens,dfSeasSkateWomens=generateSeasonSkaters()
dfSeasGoalie,dfSeasGoalieMens,dfSeasGoalieWomens=generateSeasonGoalies()
dfBeanpotAwards,dfBeanpotAwardsWomens=generateBeanpotAwards()
dfBean={'results':dfBeanpot,'awards':dfBeanpotAwards}
auth = tweepy.OAuthHandler(API_KEY, API_SECRET_KEY)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
replyList=[]
# Create API object
api = tweepy.API(auth, wait_on_rate_limit=True)
print("[{}]".format(datetime.now()),"Starting up BUStatsBot...")
while(True):
    try:
      if(replyList==[]):
          replyList = getListOfTweets(api)
      # check DMs
      messages = api.get_direct_messages()

      myUID='1525076436603871233'    
      for message in reversed(messages):
        # who is sending?  
        sender_id = message.message_create["sender_id"]
        if(sender_id!=myUID):
            # what are they saying?
            query = message.message_create["message_data"]["text"]
            origQuery=query
            # delete by ID
            query,gender=determineGender(query)
            query=query.lstrip(' ')
            if(gender=='Womens'):
                query=cleanupQuery(query,'bean')
                dfBean={'results':dfBeanpotWomens,'awards':dfBeanpotAwardsWomens}
                result=getBeanpotStats(dfBean,query)
            else:
                query=cleanupQuery(query,'bean')
                dfBean={'results':dfBeanpot,'awards':dfBeanpotAwards}
                result=getBeanpotStats(dfBean,query)
            if(result==''):
                if(determineQueryType(query)!='player'):
                    if(gender=='Womens'):
                        result=getResults(dfGamesWomens,query)  
                    else:
                        result=getResults(dfGames,query)  
                else:
                    playerDfs={}
                    playerDfs['jerseys']=dfJersey
                    playerDfs['seasonleaders']=dfLead
                    playerDfs['careerSkaters']=dfSkate
                    playerDfs['careerGoalies']=dfGoalie
                    playerDfs['seasonSkaters']=dfSeasSkate
                    playerDfs['seasonGoalies']=dfSeasGoalie
                    if(gender=='Womens'):
                        playerDfs['jerseys']=dfJerseyWomens
                        playerDfs['seasonleaders']=dfLeadWomens
                        playerDfs['careerSkaters']=dfSkateWomens
                        playerDfs['careerGoalies']=dfGoalieWomens
                        playerDfs['seasonSkaters']=dfSeasSkateWomens
                        playerDfs['seasonGoalies']=dfSeasGoalieWomens
                    if(gender=='Mens'):
                        playerDfs['seasonSkaters']=dfSeasSkateMens
                        playerDfs['seasonGoalies']=dfSeasGoalieMens
                        playerDfs['jerseys']=dfJerseyMens
                    result=getPlayerStats(playerDfs,query)
            if(result!=''):
              api.send_direct_message(sender_id, "{}: {}".format(origQuery,result))
            u=api.get_user(user_id=sender_id)
            print("[{}]".format(datetime.now()),u.name,u.screen_name,"{}: {}".format(origQuery,result))    
        api.delete_direct_message(message.id)

      # Check Mentions 
      for mentions in tweepy.Cursor(api.mentions_timeline).items():
          # process mentions here
          tweetid=mentions.id
          if(tweetid in replyList):
              continue
          query=mentions.text.lstrip('@BUStatsBot ')
          query,gender=determineGender(query)
          query=query.lstrip(' ')
          if(gender=='Womens'):
              query=cleanupQuery(query,'bean')
              dfBean={'results':dfBeanpotWomens,'awards':dfBeanpotAwardsWomens}
              result=getBeanpotStats(dfBean,query)
          else:
              query=cleanupQuery(query,'bean')
              dfBean={'results':dfBeanpot,'awards':dfBeanpotAwards}
              result=getBeanpotStats(dfBean,query)
          if(result==''):
              if(determineQueryType(query)!='player'):
                  if(gender=='Womens'):
                      result=getResults(dfGamesWomens,query)  
                  else:
                      result=getResults(dfGames,query)  
              else:
                  playerDfs={}
                  playerDfs['jerseys']=dfJersey
                  playerDfs['seasonleaders']=dfLead
                  playerDfs['careerSkaters']=dfSkate
                  playerDfs['careerGoalies']=dfGoalie
                  playerDfs['seasonSkaters']=dfSeasSkate
                  playerDfs['seasonGoalies']=dfSeasGoalie
                  if(gender=='Womens'):
                      playerDfs['jerseys']=dfJerseyWomens
                      playerDfs['seasonleaders']=dfLeadWomens
                      playerDfs['careerSkaters']=dfSkateWomens
                      playerDfs['careerGoalies']=dfGoalieWomens
                      playerDfs['seasonSkaters']=dfSeasSkateWomens
                      playerDfs['seasonGoalies']=dfSeasGoalieWomens
                  if(gender=='Mens'):
                      playerDfs['seasonSkaters']=dfSeasSkateMens
                      playerDfs['seasonGoalies']=dfSeasGoalieMens
                      playerDfs['jerseys']=dfJerseyMens
                  result=getPlayerStats(playerDfs,query)

          print("[{}]".format(datetime.now()),"{}-{}:{}:{}".format(mentions.user.name,mentions.user.screen_name,mentions.text,result))
          if(result!=''):
              api.update_status(status = result, in_reply_to_status_id = tweetid , auto_populate_reply_metadata=True)
          replyList.append(tweetid)
    except Exception:
      traceback.print_exc()
      
    time.sleep(60)
    
print("[{}]".format(datetime.now()),"BUStatsBot Exitiing...")