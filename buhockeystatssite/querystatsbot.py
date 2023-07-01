import burecordbook as burb
from burecordbook import determineGender, determineQueryType, cleanupQuery, getBeanpotStats, getResults, getPlayerStats
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