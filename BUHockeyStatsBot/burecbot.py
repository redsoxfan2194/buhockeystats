import sys
sys.path.append('../buhockeystatssite')

from burecordbook import *

if __name__ == '__main__':
  dfGames=generateRecordBook()
  dfGamesWomens=generateWomensRecordBook()
  dfJersey,dfJerseyMens,dfJerseyWomens=generateJerseys()
  dfSkate,dfSkateMens,dfSkateWomens=generateSkaters()
  dfGoalie,dfGoalieMens,dfGoalieWomens=generateGoalies()
  dfLead,dfLeadWomens=generateSeasonLeaders()
  dfBeanpot,dfBeanpotWomens=generateBeanpotHistory()
  dfSeasSkate,dfSeasSkateMens,dfSeasSkateWomens=generateSeasonSkaters()
  dfSeasGoalie,dfSeasGoalieMens,dfSeasGoalieWomens=generateSeasonGoalies()
  dfGameStats,dfGameStatsMens,dfGameStatsWomens=generateGameSkaterStats()
  dfGameStatsGoalie,dfGameStatsGoalieMens,dfGameStatsGoalieWomens = generateGameGoalieStats()
  dfBeanpotAwards,dfBeanpotAwardsWomens=generateBeanpotAwards()
  dfBean={'results':dfBeanpot,'awards':dfBeanpotAwards}
  updateCareerStats(dfSkate,dfGoalie,dfSeasSkate,dfSeasGoalie)

  query=input("Query: ")
  while(query!='' and query != 'quit' and query != 'q'): 
    origQuery=query
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
                result=getResults(dfGamesWomens,dfGameStatsWomens,dfGameStatsGoalieWomens,query)
            else:
                result=getResults(dfGames,dfGameStatsMens,dfGameStatsGoalieMens,query) 
        else:
            playerDfs={}
            playerDfs['jerseys']=dfJersey
            playerDfs['seasonleaders']=dfLead
            playerDfs['careerSkaters']=dfSkate
            playerDfs['careerGoalies']=dfGoalie
            playerDfs['seasonSkaters']=dfSeasSkate
            playerDfs['seasonGoalies']=dfSeasGoalie
            playerDfs['gameStats']=dfGameStats
            playerDfs['gameGoalieStats']=dfGameStatsGoalie
            if(gender=='Womens'):
                playerDfs['jerseys']=dfJerseyWomens
                playerDfs['seasonleaders']=dfLeadWomens
                playerDfs['careerSkaters']=dfSkateWomens
                playerDfs['careerGoalies']=dfGoalieWomens
                playerDfs['seasonSkaters']=dfSeasSkateWomens
                playerDfs['seasonGoalies']=dfSeasGoalieWomens
                playerDfs['gameStats']=dfGameStatsWomens
                playerDfs['gameGoalieStats']=dfGameStatsGoalieWomens
            if(gender=='Mens'):
                playerDfs['seasonSkaters']=dfSeasSkateMens
                playerDfs['seasonGoalies']=dfSeasGoalieMens
                playerDfs['jerseys']=dfJerseyMens
                playerDfs['gameStats']=dfGameStatsMens
                playerDfs['gameGoalieStats']=dfGameStatsGoalieMens
            result=getPlayerStats(playerDfs,query)
    print(origQuery.upper(),result,sep='\n')
    print()
    query=input("Query (Enter quit to exit): ")
