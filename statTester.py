from burecordbook import *
import coverage

cov = coverage.Coverage()
cov.start()

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

querys=['2019 beanpot results',
 '56 beanpot results',
 '1993 beanpot semi results',
 '37 beanpot championship results',
 '1963 beanpot finish',
 '21 beanpot finish',
 '1995 beanpot 3rd',
 '16 beanpot champion',
 '1961 beanpot mvp',
 '2020 womens beanpot mvp',
 '2017 beanpot eberly',
 '2004 womens beanpot bertgna',
 '33 beanpot mvp',
 '50 beanpot eberly',
 '30 womens beanpot bertgna',
 'BC record in beanpot since 2012',
 'Harvard record in beanpot after 2016',
 'NU record in beanpot before 1954',
 'BU record in beanpot between 1959 and 1972',
 "BC record in beanpot in 1980's",
 'BU record in beanpot semi',
 'Harvard record in beanpot semi1',
 'BC record in beanpot championship since 1997',
 'Harvard record in beanpot semi after 1958',
 'BU record in beanpot championship before 2019',
 'Harvard record in beanpot consolation since 1963',
 'BC record in beanpot final after 2010',
 'BU record in beanpot semi2 before 2001',
 'BC record in beanpot semi between 1981 and 2003',
 'NU record in beanpot semi2 between 1975 and 2009',
 "NU record in beanpot championship in 2020's",
 "BC record in beanpot consolation in 1950's",
 'NU beanpot finish since 1997',
 'BU beanpot finish after 2005',
 'Harvard beanpot finish before 1977',
 'BU beanpot finish between 2007 and 2016 ',
 'BC beanpot finish in 1977',
 'Harvard beanpot 1st since 1954',
 'NU beanpot 1st after 1954',
 'NU beanpot champion before 2013',
 'BC beanpot runnerup between 2001 and 2019',
 'beanpot finish since 1993',
 'beanpot finish after 1983',
 'beanpot finish before 2016',
 'beanpot finish between 1985 and 1985',
 'beanpot finish in the 1990s',
 'womens beanpot finish',
 'nu record in womens beanpot',
 'NU record vs BC in beanpot consolation since 1976',
 'BU record vs BC in beanpot championship after 1965',
 'BC record vs Harvard in beanpot consolation before 1966',
 'BC record vs Harvard in beanpot consolation since 1980',
 'Harvard record vs BU in beanpot semi2 after 1971',
 'BU record vs Harvard in beanpot semi1 before 1974',
 'NU record vs BU in beanpot consolation between 2019 and 2022',
 'Harvard record vs BU in beanpot semi2 between 1957 and 1962',
 '2021 beanpot results',
 'nu record in womens beanpot semi',
 'bu record in beanpot in 90s',
 'bc record in beanpot in 00s',
 'nu record vs bc in womens beanpot',
 'womens beanpot finish',
 '1989 womens beanpot results',
 '2021 beanpot finish',
 '1994 womens beanpot results',
 'bc record vs harvard in beanpot',
 '2000 beanpot 3rd place'
 'beanpot champions',
 'bu beanpot finish in 2021']
for query in querys:
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
  if(result==''):
    result='FAIL'
  print(query,result)

cov.stop()
cov.save()

cov.html_report()