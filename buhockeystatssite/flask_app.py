from flask import Flask,render_template,request,jsonify
from burecordbook import *
from formatstatsdata import formatResults, formatStats, convertToHtmlTable

dayNames = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'}

print('Generating...')
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
buscore='BU Score'
oppscore='Opp Score'
print('Generated')
  
app = Flask(__name__)


def getOpponentList(dfRes):
  dfRes.loc[dfRes['tourney'].isnull(),'tourney']=''
  nonCollOpps = sorted(list(dfRes[dfRes['tourney'].str.contains("Non-Collegiate")].opponent.unique()))
  exOpps = sorted(list(set(dfRes.query('result=="E"').opponent.unique())-set(dfRes.query('result!="E"').opponent.unique())))
  opps = sorted(list(set(dfRes.opponent.unique())-set(nonCollOpps)-set(exOpps)))
  retList = opps
  if(nonCollOpps!=[]):
    retList += ['Non-Collegiate:'] + nonCollOpps
  if(exOpps!=[]):
    retList += ['Exhibition:'] + exOpps
  return retList 

def getTourneyList(dfRes):
  df=dfRes.copy()
  df.loc[dfRes['tourney'].isnull(),'tourney']=''
  df=df.query('tourney != ""').loc[~df['tourney'].str.contains('1932')]
  retList=['Tournament']+sorted(df.query('tourney != ""').tourney.unique())
  return retList
  
@app.route('/players', methods = ['POST', 'GET'])
def players():
    global dfGames,dfGamesWomens,dfJersey,dfJerseyMens,dfJerseyWomens,dfSkate,dfSkateMens,dfSkateWomens,dfGoalie,dfGoalieMens,dfGoalieWomens,dfLead,dfLeadWomens,dfBeanpot,dfBeanpotWomens,dfSeasSkate,dfSeasSkateMens,dfSeasSkateWomens,dfSeasGoalie,dfSeasGoalieMens,dfSeasGoalieWomens,dfBeanpotAwards,dfBeanpotAwardsWomens,dfGameStats,dfGameStatsMens,dfGameStatsWomens,dfGameStatsGoalie,dfGameStatsGoalieMens,dfGameStatsGoalieWomens
    if request.method == 'GET':
        dfStat=dfSkateMens
        seasVals=sorted(set(dfStat['seasons'].to_string(index=False).replace(' ','').replace('\n',',').split(',')))
        return render_template('players.html',statTable=formatStats(dfStat),season_values=seasVals,selected_startSeas=seasVals[0],selected_endSeas=seasVals[-1],name="Name",number="Number",date="Date")
    if request.method == 'POST':
        form_data = request.form
        dfStat=pd.DataFrame()
        seasVals=[]
        sortVal=''
        if(form_data['gender']=='Mens'):
           if(form_data['type']=='career'):
              if(form_data['position']=='skater'):
                dfStat=dfSkateMens
              elif(form_data['position']=='goalie'):
                dfStat=dfGoalieMens
              seasVals=sorted(set(dfStat['seasons'].to_string(index=False).replace(' ','').replace('\n',',').split(',')))
           elif(form_data['type']=='season'):
              if(form_data['position']=='skater'):
                dfStat=dfSeasSkateMens
              elif(form_data['position']=='goalie'):
                dfStat=dfSeasGoalieMens
                rec=dfStat.record.str.split('-',expand=True)
                dfStat['W']=rec[0].astype(int)
                dfStat['L']=rec[1].astype(int)
                dfStat['T']=rec[2].astype(int)
           elif(form_data['type']=='game'):
              if(form_data['position']=='skater'):
                dfStat=dfGameStatsMens
              elif(form_data['position']=='goalie'):
                dfStat=dfGameStatsGoalieMens
        elif(form_data['gender']=='Womens'):
           if(form_data['type']=='career'):
              if(form_data['position']=='skater'):
                dfStat=dfSkateWomens
              elif(form_data['position']=='goalie'):
                dfStat=dfGoalieWomens
              seasVals=sorted(set(dfStat['seasons'].to_string(index=False).replace(' ','').replace('\n',',').split(',')))
           elif(form_data['type']=='season'):
              if(form_data['position']=='skater'):
                dfStat=dfSeasSkateWomens
              elif(form_data['position']=='goalie'):
                dfStat=dfSeasGoalieWomens
                rec=dfStat.record.str.split('-',expand=True)
                dfStat['W']=rec[0].astype(int)
                dfStat['L']=rec[1].astype(int)
                dfStat['T']=rec[2].astype(int)
           elif(form_data['type']=='game'):
              if(form_data['position']=='skater'):
                dfStat=dfGameStatsWomens
              elif(form_data['position']=='goalie'):
                dfStat=dfGameStatsGoalieWomens
        if(seasVals==[]):
          seasVals=list(dfStat.season.unique())
        sSeas=form_data['seasonStart']
        eSeas=form_data['seasonEnd']
        if(form_data['season']!='all'):
          if(form_data['type']=='career'):
            dfStat=dfStat.loc[dfStat['seasons'].str.contains(form_data['season'])]
          else:
            dfStat=dfStat.query(f"season == '{form_data['season']}'")
        else:
          if(sSeas not in seasVals):
            sIdx=0
            sSeas=seasVals[0]
          else:
            sIdx=seasVals.index(sSeas)
          eIdx=seasVals.index(eSeas)+1
          if(sIdx>eIdx):
            temp=sIdx
            sIdx=eIdx
            eIdx=temp
            sSeas=seasVals[sIdx]
            eSeas=seasVals[eIdx]
          valSeas=seasVals[sIdx:eIdx]
          if(form_data['type']=='career'):
            idx=[]
            for seas in valSeas:
                idx+=(list(dfStat.loc[dfStat['seasons'].str.contains(seas)].index))
            idx=list(set(idx))
            dfStat=dfStat.loc[idx]
            dfStat.reset_index(inplace=True)
          else:
            dfStat=dfStat.loc[dfStat['season'].isin(valSeas)]
        if(form_data['type']!='career'):
          if(form_data['pos']!='all' and form_data['position']!='goalie'):
            dfStat=dfStat.query(f"pos=='{form_data['pos']}'")
          if(form_data['yr']!='all'):
            dfStat=dfStat.query(f"yr=='{form_data['yr']}'")
        if(form_data['type']=='game'):
          oppList=sorted(list(dfStat.opponent.unique()))
          if(form_data['opponent']!='all'):
            dfStat=dfStat.query(f"opponent==\"{form_data['opponent']}\"")
          if(form_data['date']!='Date'):
            dfStat=dfStat.query(f"date==\"{form_data['date']}\"")
        else:
          oppList=[]
        if(form_data['name']!='Name'):
          dfStat=dfStat.loc[dfStat['name'].str.contains(form_data['name'].strip(),case=False)]
        if(form_data['number']!=''):
          dfStat=dfStat.query(f"number == {form_data['number']}")
          num=form_data['number'].strip()
        else:
          num="Number"
        if(form_data['group']!='' and form_data['position']=='skater'):
          dfStat=dfStat.groupby(['name','opponent']).sum(numeric_only=True)
          dfStat=dfStat.reset_index()
          dfStat=dfStat[['name','opponent','gp','goals','assists','pts']]
        if(form_data['group']!='' and form_data['position']=='goalie'):
          dfStat=determineRecord(dfStat)
          dfStat=dfStat.groupby(['name','opponent']).sum(numeric_only=True)
          dfStat=dfStat.reset_index()
          dfStat['sv%']=dfStat['sv']/(dfStat['sv']+dfStat['ga'])
          dfStat['gaa']=(dfStat['ga']/dfStat['mins'])*60
          dfStat=dfStat[['name','opponent','gp','ga','gaa','sv','sv%','SO','W','L','T']]    
        if(form_data['isAscending']!=''):
          if(form_data['sortval']!='' and form_data['sortval'].lower() in dfStat.columns or form_data['sortval'] in ['W','L','T','SO'] ):
            sortType=eval(form_data['isAscending'].capitalize())
            if(form_data['sortval'].lower()!='date' and sortType!='' and form_data['sortval'].lower()!='career' and form_data['sortval'].lower()!='season'):
               sortType=not sortType
            if(form_data['sortval'].lower()=='name' and 'last' in dfStat.columns):
               sortVal='last'
            else:
               if(form_data['sortval'] not in ['W','L','T','SO']):
                  sortVal=form_data['sortval'].lower()
               else:
                  sortVal=form_data['sortval']
            if(sortVal in dfStat.columns):
              dfStat=dfStat.sort_values(sortVal,ascending=sortType)
            sortVal=form_data['sortval']
        else:
          sortVal=''
          sortType=''
        if(form_data['type']=='game'):
          dfStat=dfStat[:1000]
        return jsonify(statTable=formatStats(dfStat),
                season_values=seasVals,
                opponents_values=oppList,
                sortval=sortVal,
                isAscending=form_data['isAscending'])
        
@app.route('/statsbot', methods = ['POST', 'GET'])
def statsbot():
  global dfGames,dfGamesWomens,dfJersey,dfJerseyMens,dfJerseyWomens,dfSkate,dfSkateMens,dfSkateWomens,dfGoalie,dfGoalieMens,dfGoalieWomens,dfLead,dfLeadWomens,dfBeanpot,dfBeanpotWomens,dfSeasSkate,dfSeasSkateMens,dfSeasSkateWomens,dfSeasGoalie,dfSeasGoalieMens,dfSeasGoalieWomens,dfBeanpotAwards,dfBeanpotAwardsWomens,dfGameStats,dfGameStatsMens,dfGameStatsWomens,dfGameStatsGoalie,dfGameStatsGoalieMens,dfGameStatsGoalieWomens
  if request.method == 'GET':
        return render_template('statsbot.html',result='',query='')
  if request.method == 'POST':
    form_data = request.form
    if('query' in form_data.keys()):
      query,gender=determineGender(form_data['query'])
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
      result=result.split('\n')
      result=convertToHtmlTable(result)
      
      return render_template(
        'statsbot.html',
        result = result,
        query=form_data['query'].upper())

@app.route('/', methods = ['POST', 'GET'])
@app.route('/records', methods = ['POST', 'GET'])
def records():
    global buscore,oppscore,dfGames,dfGamesWomens
    dfRes=dfGames
    dfOrig=dfGames
    minYear=dfRes.year.min()
    maxYear=dfRes.year.max()
    result=''
    for i in ['W','L','T']:
        if((dfRes['result']==i).any()):
            res=dfRes.groupby('result').count()['date'][i]
        else:
            res=0
        result+=str(res)+'-'
    result=result.rstrip('-')
    if request.method == 'GET':
    
        return render_template(
          'records.html',
          result=result,
          query='',
          resTable=formatResults(dfRes),
          opponents_values=getOpponentList(dfOrig),
          season_values=list(dfOrig.season.unique()),
          arena_values=sorted(list(dfOrig.arena.unique())),
          buscore=buscore,
          oppscore=oppscore,
          isAscending=True,
          selected_sort='date',
          startYear=dfOrig.year.min(),
          endYear=dfOrig.year.max(),
          minYear=minYear,
          maxYear=maxYear,
          selected_startSeas=dfOrig.season.min(),
          selected_endSeas=dfOrig.season.max(),
          selected_range='season',
          hideExStatus="true",
          tourney_values=getTourneyList(dfOrig),
          coach_values=list(dfOrig.coach.unique()),
          selected_day=0)
            
    if request.method == 'POST':
        form_data = request.form
        if(form_data['gender']=='Mens'):
          dfRes=dfGames
          dfOrig=dfGames
        else:
          dfRes=dfGamesWomens
          dfOrig=dfGamesWomens
        minYear=dfRes.year.min()
        maxYear=dfRes.year.max()
        if('startYear' in form_data):
          if(form_data['startYear']==''):
            sYear=dfRes.year.min()
          else:
            sYear=form_data['startYear']
            if(form_data['gender']=='Womens'):
              sYear=max(2005,int(sYear))
          if(form_data['endYear']==''):
            eYear=dfRes.year.max()
          else:
            eYear=form_data['endYear']
          dfRes=dfRes.query(f"year>={sYear} and year<={eYear}")
          seasonStart=dfRes.season.min()
          seasonEnd=dfRes.season.max()
        else:
          
          sSearch=re.search('(\d{4})-(\d{2})',form_data['seasonStart'])
          if(sSearch != None):
              sDate='9/1/{}'.format(sSearch.group(1))
          else:
              sDate='9/1/{}'.format(dfRes.min.max())
          eSearch=re.search('(\d{4})-(\d{2})',form_data['seasonEnd'])
          if(eSearch != None):
              eDate='5/1/{}'.format(int(eSearch.group(1))+1)
          else:
              eDate='5/1/{}'.format(dfRes.year.max())
          
          dfRes=dfRes.query(f"date>='{sDate}' and date<='{eDate}'")
          sYear=dfRes.year.min()
          eYear=dfRes.year.max()
          seasonStart=dfRes.season.min()
          seasonEnd=dfRes.season.max()
          
        if(form_data['DOW']!='-1'):
          dfRes=dfRes.query(f"dow == {form_data['DOW']}")
        if(form_data['month']!='0'):
          dfRes=dfRes.query(f"month == {form_data['month']}")
        if('day' in form_data and form_data['day']!='0'):
          dfRes=dfRes.query(f"day == {form_data['day']}")
          dayVal=form_data['day']
        else:
          dayVal=0
        if(form_data['opponent']!='all'):
          if(form_data['opponent']=='Exhibition:'):
            dfRes=dfRes.query("result=='E'")
          elif(form_data['opponent']=='Non-Collegiate:'):
            dfRes=dfRes.query('tourney=="Non-Collegiate"')
          else:
            dfRes=dfRes.query(f'opponent==\"{form_data["opponent"]}\"')
        result=''
        if(form_data['season']!='all'):
            dfRes=dfRes.query(f"season==\'{form_data['season']}\'")
        if(form_data['tourney']!='Tournament'):
            dfRes=dfRes.query(f"tourney==\'{form_data['tourney']}\'")
        if(form_data['location']!='all'):
            dfRes=dfRes.query(f"location==\'{form_data['location']}\'")
        if(form_data['coach']!='all'):
            dfRes=dfRes.query(f"coach==\"{form_data['coach']}\"")
        if(form_data['arena']!='all'):
            dfRes=dfRes.query(f"arena==\'{form_data['arena']}\'")
        if(form_data['buscore']!=''):
            dfRes=dfRes.query(f"BUScore {form_data['buscoreop']} {form_data['buscore']}")
            buscore=form_data['buscore']
        else:
            buscore="BU Score"
        if(form_data['oppscore']!=''):
            dfRes=dfRes.query(f"OppoScore {form_data['oppscoreop']} {form_data['oppscore']}")
            oppscore=form_data['oppscore']
        else:
            oppscore="Opp Score"
       
        for i in ['W','L','T']:
            if((dfRes['result']==i).any()):
                res=dfRes.groupby('result').count()['date'][i]
            else:
                res=0
            result+=str(res)+'-'
        result=result.rstrip('-')
        sortType=eval(form_data['isAscending'].capitalize())
        if form_data['sortval']!='date':
           sortType=not sortType
        if('hideEx' in form_data):
          dfRes=dfRes.query("result !='E'")
          hideEx="true"
        else:
          hideEx=""
        if('grouping' in form_data and form_data['grouping']!=''):
          if(form_data['grouping']=='Month'):
              dfRes=dfRes.copy()
              dfRes.loc[:,'month'] = pd.to_datetime(dfRes['month'], format='%m').dt.strftime('%B')
          elif(form_data['grouping']=='DOW'):
              dfRes=dfRes.copy()
              dfRes.loc[:,'dow'] = dfRes['dow'].map(dayNames)
          if(form_data['tabletype']=='record'):
            grouped_data = dfRes.groupby([form_data['grouping'].lower(),'result']).count()['date']
            records = grouped_data.unstack().fillna(0).astype(int).to_dict(orient='index')
            recsList=[]
            for team in records.keys():
                recDict={form_data['grouping']:team}
                for res in ['W','L','T']:
                  if(res not in records[team]):
                    recDict[res]=0
                  else:
                    recDict[res]=records[team][res]
                    
                if((recDict['W']+recDict['L']+recDict['T'])!=0):
                    recDict['Win%']=round((recDict['W']+recDict['T']*.5)/(recDict['W']+recDict['L']+recDict['T']),3)
                    recsList.append(recDict)
            dfRes=pd.DataFrame(recsList)
          elif(form_data['tabletype']=='first'):
              dfRes=dfRes.copy()
              dfRes.fillna('', inplace=True)
              dfRes=dfRes.groupby(form_data['grouping'].lower()).first()
              dfRes.reset_index(inplace=True)
          elif(form_data['tabletype']=='last'):
              dfRes=dfRes.copy()
              dfRes.fillna('', inplace=True)
              dfRes=dfRes.groupby(form_data['grouping'].lower()).last()
              dfRes.reset_index(inplace=True)
        if(form_data['sortval'] in ["date","GD", "BUScore", "OppoScore"] and 'date' not in dfRes.columns):
          if(form_data['sortval']!='date'):
            sortType=not sortType
          dfRes=dfRes.sort_values(form_data['grouping'],ascending=sortType)
        elif(form_data['sortval'] in ['Win%','W','L','T','sort'] and 'Win%' not in dfRes.columns):
          sortType=not sortType
          dfRes=dfRes.sort_values('date',ascending=sortType)
        elif(form_data['sortval']=='sort'):
          sortType=not sortType
          dfRes=dfRes.sort_values(form_data['grouping'],ascending=sortType)
        else:
          dfRes=dfRes.sort_values(form_data['sortval'],ascending=sortType)
        
        return jsonify(resTable=formatResults(dfRes),
            result=result,
            opponents_values=getOpponentList(dfOrig),
            season_values=list(dfOrig.season.unique()),
            arena_values=sorted(list(dfOrig.arena.unique())),
            tourney_values=getTourneyList(dfOrig),
            coach_values=list(dfOrig.coach.unique()),
            minYear=int(minYear))

def determineRecord(dfRes):
  dfStat=dfRes.groupby(['name','opponent']).sum(numeric_only=True)
  dfStat.reset_index(inplace=True)
  dfStat['W']=0
  dfStat['L']=0
  dfStat['T']=0
  dfRec=dfRes.groupby(['name','opponent','result']).count()
  dfRec.reset_index(inplace=True)
  for res in ['W','L','T']:
      dfRec[res]=dfRec.query(f'result=="{res}"')['date']
      dfRec[res]=dfRec[res].fillna(0).astype(int)
  dfRec=dfRec.groupby(['name','opponent']).sum(numeric_only=True)
  dfRec.reset_index(inplace=True)
  # Merge dfStat and dfRec based on name and opponent columns
  merged_df = pd.merge(dfStat, dfRec[['name','opponent','W','L','T']], on=['name', 'opponent'], how='left')

  # Sum the 'W', 'L', 'T' columns from dfRec and assign the values to corresponding columns in dfStat
  dfStat['W'] = merged_df.groupby(['name', 'opponent'])['W_y'].transform(sum)
  dfStat['L'] = merged_df.groupby(['name', 'opponent'])['L_y'].transform(sum)
  dfStat['T'] = merged_df.groupby(['name', 'opponent'])['T_y'].transform(sum,numeric_only=True)

  return dfStat
if __name__=='__main__':
  app.run(host='localhost', port=5000)