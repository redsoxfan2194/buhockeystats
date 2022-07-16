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
  "NU record in beanpot championship in 2020s",
  "BC record in beanpot consolation in 1950s",
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
  '1992 womens beanpot finish',
  'bc record vs harvard in beanpot',
  '2000 beanpot 3rd place',
  'beanpot champions',
  'beanpot 2nd place',
  'beanpot 3rd place',
  'beanpot 4th place',
  'womens beanpot finish since 2000',
  'bu beanpot finish in 2021',
  '16th womens beanpot results',
  '2022 beanpot finish',
  'bu beanpot finish in 2019',
  'nu beanpot finish in 1988',
  'Skoog career goals',
  'Parker career assists',
  'Skoog career pts',
  'Skoog career statline',
  'Oettinger career gaa',
  'Oettinger career sv%',
  'Daskalakis career record',
  'Oettinger career statline',
  'most pts by #22',
  'most goals by #2',
  'most assists by #33',
  'most pts by jack',
  'most goals by john',
  'most assists by amonte',
  'most pts in 1994-95',
  'leading goals in 2020-21',
  'best assists in 2000-01',
  'most pts by forward in 2003-04',
  'leading goals by dman in 2009-10',
  'best assists by f in 2021-22',
  'most pts by fr in 2003-04',
  'most goals by senior in 2009-10',
  'most assists by sophomore in 2021-22',
  'most pts by freshman forward in 2003-04',
  'leading goals by sophomore dman in 2009-10',
  'best assists by senior f in 2021-22',
  'amonte pts in 2021',
  'ty amonte goals in 2021-22',
  'skoog goals as jr',
  'wise statline as fr',
  'jake shutouts as junior',
  'cockerill assists as senior',
  'commesso statline in 2021-22',
  'best sv% in 2020-21',
  'most shutouts in 2020-21',
  'best gaa in 2021-22',
  '#33 in 2021-22',
  'mens #6 in 2020-21',
  'mens #24 in 2010-11',
  'number matt brown',
  'ty pts in 2021-22',
  'ty goals in 2021-22',
  'ty assists in 2021-22',
  'jake record in 2017-18',
  'ty in 2021-22',
  'skoog career assists',
  'Ryan Priem career goals',
  'drew career shutouts',
  'jake career record',
  'most career pts',
  'most career goals',
  'most career assists',
  'best career sv%',
  'last 1 win vs Miami',
  'last 4 game against Minnesota',
  'last tie at Maine',
  'wins at St. Paul CC',
  'ties at home',
  'biggest win at away',
  'last tie at neutral',
  'last tie under George Gaw',
  "biggest win with John O'Hare",
  'ties since 2004',
  'wins since 2019-20',
  'ties since 06/26/1973',
  'wins after 2019',
  'record after 1978-79',
  'losses after 01/12/2018',
  'last 6 win before 1956',
  'last tie before 1927-28',
  'ties before 03/08/2000',
  'ties from 1954 to 1986',
  'losses from 12/21/1987 to 01/21/2001',
  'last 1 loss between 1950 and 1996',
  'last 5 loss between 01/26/2000 and 07/22/2001',
  'biggest win in 1981',
  'biggest loss in 1956 in playoffs',
  'last 4 win in 1984 in overtime',
  'wins in 1941 in regulation',
  'wins in 1999 in non-conference',
  'ties in 1962 in conference',
  'last 5 game in 1973 in ECAC',
  'last 2 win in 1968 in first 2',
  'last 4 game in 1936 in last 1',
  'ties in 2016 in 1 goal',
  'biggest win in 1999-00 in playoffs',
  'last 4 win in 1976-77 in overtime',
  'wins in 2004-05 in regulation',
  'wins in 1946-47 in non-conference',
  'last tie in 1993-94 in conference',
  'last 2 loss in 1966-67 in Hockey East',
  'biggest loss in 2015-16 in first 4',
  'last tie in 1989-90 in last 5',
  'record in 1978-79 in 6 goal',
  "losses in 1970's in playoffs",
  "biggest loss in 1990's in overtime",
  "last 4 game in 1960's in regulation",
  "losses in 1920's in non-conference",
  "last 3 win in 2020's in conference",
  "biggest win in 1920's in Hockey East",
  "last tie in 1920's in first 6",
  "record in 1990's in last 1",
  "wins in 2020's in 4 goal",
  'last 3 win in Silverado Shootout in 1984-85',
  'last 2 game in Big Ten/Hockey East Challenge in playoffs',
  'biggest loss in NYE Frontier Classic in overtime',
  'biggest loss in NYE Frontier Classic in regulation',
  'last tie in NCAA Tournament in non-conference',
  'biggest loss in Hall of Fame Game in conference',
  'biggest win in Silverado Shootout in Hockey East',
  'last 5 win in ECAC Tournament in first 2',
  'record in Boston Christmas Holiday Festival in last 6',
  'biggest loss in New Brunswick Invitational in 1 goal',
  'wins in regular season in 1958-59',
  'last tie in regular season',
  'last tie in playoffs',
  'last tie in regular season in overtime',
  'wins in regular season in regulation',
  'ties in regular season in non-conference',
  'ties in regular season in conference',
  'last 5 win in regular season in Hockey East',
  'last tie in regular season in first 4',
  'losses in regular season in last 2',
  'last 4 loss in regular season in 4 goal',
  'last 5 game on 01/09/1997',
  'last 1 game on 05/11',
  'last tie on sat',
  'last 6 game when scoring > 2+ goals',
  'ties when scoring > 5 goals',
  'losses when scoring >= 5+ goals',
  'ties when scoring >= 6 goals',
  'last 1 game when scoring < 5+ goals',
  'last tie when scoring < 6 goals',
  'last 6 win when scoring <= 3+ goals',
  'biggest loss when scoring <= 4 goals',
  'last 2 win when allowing > 5+ goals',
  'last 1 win when allowing > 5 goals',
  'ties when allowing >= 4+ goals',
  'record when allowing >= 4 goals',
  'ties when allowing < 5+ goals',
  'last 5 loss when allowing < 3 goals',
  'biggest loss when allowing <= 1+ goals',
  'ties when allowing <= 4 goals']
  
for query in querys:
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
  print(origQuery.upper(),result,sep='\n')

cov.stop()
cov.save()

cov.html_report()