import burecordbook as burb
from burecordbook import determineGender, determineQueryType, cleanupQuery, getBeanpotStats, getResults, getPlayerStats
import random
from datetime import datetime
def querystatsbot(query):
    """ Parses the query and determines the correct results to send back

        Returns:
          Results of querying the statsbot
    """
    query, gender = determineGender(query)
    query = query.lstrip(' ')
    query = cleanupQuery(query, 'bean')

    result = attemptbeanpotquery(query, gender)

    # Compute results for non-Beanpot queries
    # (result will be null for non-Beanpot queries)
    if result == '':
        if determineQueryType(query) == 'player':
            result = queryplayers(query, gender)
        else:
            result = queryrecords(query, gender)

    return result.split('\n')

def attemptbeanpotquery(query, gender):
    if gender == 'Womens':
        dfBean = {
            'results': burb.dfBeanpotWomens,
            'awards': burb.dfBeanpotAwardsWomens}
    else:
        dfBean = {'results': burb.dfBeanpot, 'awards': burb.dfBeanpotAwards}

    return getBeanpotStats(dfBean, query)

def queryplayers(query, gender):
    playerDfs = {}

    if gender == 'Womens':
        playerDfs['careerGoalies'] = burb.dfGoalieWomens
        playerDfs['careerSkaters'] = burb.dfSkateWomens
        playerDfs['seasonGoalies'] = burb.dfSeasGoalieWomens
        playerDfs['gameGoalieStats'] = burb.dfGameStatsGoalieWomens
        playerDfs['gameStats'] = burb.dfGameStatsWomens
        playerDfs['jerseys'] = burb.dfJerseyWomens
        playerDfs['seasonleaders'] = burb.dfLeadWomens
        playerDfs['seasonSkaters'] = burb.dfSeasSkateWomens
    else:
        playerDfs['careerGoalies'] = burb.dfGoalie
        playerDfs['careerSkaters'] = burb.dfSkate
        playerDfs['seasonleaders'] = burb.dfLead

        if gender == 'Mens':
            playerDfs['gameGoalieStats'] = burb.dfGameStatsGoalieMens
            playerDfs['gameStats'] = burb.dfGameStatsMens
            playerDfs['jerseys'] = burb.dfJerseyMens
            playerDfs['seasonGoalies'] = burb.dfSeasGoalieMens
            playerDfs['seasonSkaters'] = burb.dfSeasSkateMens
        else:
            playerDfs['gameGoalieStats'] = burb.dfGameStatsGoalie
            playerDfs['gameStats'] = burb.dfGameStats
            playerDfs['jerseys'] = burb.dfJersey
            playerDfs['seasonGoalies'] = burb.dfSeasGoalie
            playerDfs['seasonSkaters'] = burb.dfSeasSkate

    return getPlayerStats(playerDfs, query)

def queryrecords(query, gender):
    if gender == 'Womens':
        return getResults(burb.dfGamesWomens, burb.dfGameStatsWomens, burb.dfGameStatsGoalieWomens, query)
    else:
        return getResults(burb.dfGames, burb.dfGameStatsMens, burb.dfGameStatsGoalieMens, query)
        
def generaterandomstat():

  queryList=['record','last win','last loss','last tie','last game','biggest win']
  opsDict={'opponent':{'type':'vs','choice':''},
           'tourney':{'type':'in the','choice':''},
           'arena':{'type':'at','choice':''},
           'coach':{'type':'under','choice':''},
           'date':{'type':'on','choice':''}}
  validQuery=False
  resStr=""
  while(not validQuery):
    opsDict['opponent']['choice']=random.choice(burb.dfGames.query('result !="E" and tourney!="Non-Collegiate"').opponent.unique())
    opsDict['tourney']['choice']=random.choice(burb.dfGames.tourney.unique())
    opsDict['arena']['choice']=random.choice(burb.dfGames.arena.unique())
    opsDict['coach']['choice']=random.choice(burb.dfGames.coach.unique())
    randLoc=random.choice(['Home','Away','Neutral'])
    randMonth,randDay=random.choice(burb.dfGames.groupby(['month','day']).count().index)
    opsDict['date']['choice']=f"{randMonth}/{randDay}"
    qChoice=random.choice(queryList)
    opsChoice=random.choice(list(opsDict.keys()))
    if(opsDict[opsChoice]['choice'] is None or 'NEAAU' in opsDict[opsChoice]['choice'] or 'Non-Collegiate' in opsDict[opsChoice]['choice'] or "Challenge" in opsDict[opsChoice]['choice'] ):
      continue
    query=f"{qChoice} {opsDict[opsChoice]['type']} {opsDict[opsChoice]['choice']}"
    result=querystatsbot(query)
    if(result[0]!='0-0-0' and result[0]!="No Results Found" and result[0]!='' and 'Non-Collegiate' not in result[0]):
      validQuery=True
      result[0]=result[0].replace("()",'')
    qChoice=random.choice(queryList)
    opsChoice=random.choice(list(opsDict.keys()))
    if(opsChoice=='date'):
      qText=f"month == {randMonth} and day == {randDay}"
    else:
      qText=f"{opsChoice} == \"{opsDict[opsChoice]['choice']}\""
    if('win' in qChoice):
        qText+=" and result == 'W'"
    if('tie' in qChoice):
        qText+=" and result == 'T'"
    if('loss' in qChoice):
        qText+="and result == 'L'"
    dfRes=burb.dfGames.query(qText)
    if(dfRes.empty):
        validQuery=False
        continue
    else:

        if(qChoice=='record'):
            recDict=dfRes.groupby('result').count()['date'].to_dict()
            recStr=""
            for i in ['W','L','T']:
                if i in recDict:
                    recStr+=str(recDict[i])+'-'
                else:
                    recStr+='0'+'-'

            res=(recStr.rstrip('-'))
            resStr=f"BU has a {res} record {opsDict[opsChoice]['type']} {opsDict[opsChoice]['choice']}"
        else:
            if('last' in qChoice):
                res=dfRes.sort_values('date',ascending=False).iloc[0]
                date=datetime.strptime(str(res['date'])[:10],'%Y-%m-%d').strftime('%b %d, %Y')
                if(res['ot'] is not None):
                    otStr=f" in {res['ot'].upper()}"
                else:
                    otStr=""
                if('game' not in qChoice):
                    resStr=f"BU's {qChoice} {opsDict[opsChoice]['type']} {opsDict[opsChoice]['choice']} occured on {date} with a score of {res['scoreline']}{otStr}"
                else:
                    resStr=f"BU's {qChoice} {opsDict[opsChoice]['type']} {opsDict[opsChoice]['choice']} was a {res['result'].replace('W','win').replace('L','loss').replace('T','tie')} with a score of {res['scoreline']}{otStr} on {date}"
            if('biggest' in qChoice):
                res=dfRes.sort_values('GD',ascending=False).iloc[0]
                date=datetime.strptime(str(res['date'])[:10],'%Y-%m-%d').strftime('%b %d, %Y')
                if(res['ot'] is not None):
                    otStr=f" in {res['ot'].upper()}"
                else:
                    otStr=""
                resStr=f"BU's {qChoice} {opsDict[opsChoice]['type']} {opsDict[opsChoice]['choice']} occured on {date} with a score of {res['scoreline']}{otStr}"
            if(opsChoice!='opponent'):
                resStr+=f" vs {res['opponent']}"
            if(opsChoice!='arena'):
                resStr+=f" at {res['arena']}"
            if(opsChoice!='tourney' and res['tourney'] is not None):
                resStr+=f" in the {res['tourney']}"
  return resStr