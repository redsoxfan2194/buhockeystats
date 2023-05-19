from flask import Flask,render_template,request
from burecordbook_site import *

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
  
# cd env
# Scripts\activate
#set FLASK_APP=app.py
#flask run

app = Flask(__name__)

#@app.route('/')
#def home():
#  return "<h1> Hello World </h1>"
#@app.route('/form')
#def form():
#    return render_template('records.html')

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
  return render_template('players.html')
  
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
      #if('stats' in query):
      result=convertToHtmlTable(result)
      return render_template('statsbot.html',result = result, query=form_data['query'].upper())

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
        return render_template('records.html',result=result,query='',resTable=formatResults(dfRes),opponents_values=getOpponentList(dfOrig),season_values=list(dfOrig.season.unique()),arena_values=sorted(list(dfOrig.arena.unique())),buscore=buscore,oppscore=oppscore,isAscending=True,selected_sort='date',startYear=dfOrig.year.min(),endYear=dfOrig.year.max(),minYear=minYear,maxYear=maxYear,selected_startSeas=dfOrig.season.min(),selected_endSeas=dfOrig.season.max(),selected_range='season',hideExStatus="true",tourney_values=getTourneyList(dfOrig),coach_values=list(dfOrig.coach.unique()),selected_day=0)
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
        dfRes=dfRes.sort_values(form_data['sortval'],ascending=sortType)
        return render_template('records.html',result=result,query='',resTable=formatResults(dfRes),opponents_values=getOpponentList(dfOrig),\
        season_values=list(dfOrig.season.unique()),selected_gender=form_data['gender'],selected_opponent=form_data['opponent'],selected_season=form_data['season'],selected_location=form_data['location'],arena_values=sorted(list(dfOrig.arena.unique())),selected_arena=form_data['arena'],buscore=buscore,selected_buop=form_data['buscoreop'],selected_oppop=form_data['oppscoreop'],oppscore=oppscore,\
        isAscending=form_data['isAscending'].capitalize(),selected_sort=form_data['sortval'],startYear=sYear,endYear=eYear,minYear=minYear,maxYear=maxYear,selected_startSeas=seasonStart,selected_endSeas=seasonEnd,selected_range=form_data['range'],hideExStatus=hideEx,selected_dow=int(form_data['DOW']),selected_month=int(form_data['month']),selected_day=int(dayVal),tourney_values=getTourneyList(dfOrig),selected_tourney=form_data['tourney'],coach_values=list(dfOrig.coach.unique()),selected_coach=form_data['coach'])

 
def convertToHtmlTable(input_string):
    rows = input_string  
    
    # Create the HTML table structure
    html_table = '<table class="stat-table">\n<thead>\n<tr>'
    
    # Process the first row as the header
    headers = rows[0].split()
    if(headers==[]):
      return ''
    if('Season' in headers[0]):
      for header in headers:
          html_table += f'<th>{header}</th>'
      html_table += '</tr>\n</thead>\n<tbody>'
      
      # Process the remaining rows as data rows
      for row in rows[1:]:
          columns = row.split()
          pts=columns[-1].split('-')
          if(len(pts)>1 and pts[0]!='' and 'Record' not in rows[0]):
            columns.pop()
            columns+=pts
          if(columns[0]=='Career'):
            columns.insert(1,'')
          html_table += '\n<tr>'
          for column in columns:
              html_table += f'<td class="stat-row">{column}</td>'
          html_table += '</tr>'
    else:
      # Process the remaining rows as data rows
      pattern = r'\s+(?![^()]*\))'
      for row in rows:
          columns=re.split(pattern, row)
          html_table += '\n<tr>'
          for column in columns:
              html_table += f'<td class="stat-row">{column}</td>'
          html_table += '</tr>'
    html_table += '\n</tbody>\n</table>'
    return html_table


    
if __name__=='__main__':
  app.run(host='localhost', port=5000)