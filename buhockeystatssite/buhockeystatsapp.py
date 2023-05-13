from flask import Flask,render_template,request
from burecordbook import *

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
#    return render_template('form.html')

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
  
@app.route('/', methods = ['POST', 'GET'])
def data():
    global buscore,oppscore,dfGames,dfGamesWomens,dfJersey,dfJerseyMens,dfJerseyWomens,dfSkate,dfSkateMens,dfSkateWomens,dfGoalie,dfGoalieMens,dfGoalieWomens,dfLead,dfLeadWomens,dfBeanpot,dfBeanpotWomens,dfSeasSkate,dfSeasSkateMens,dfSeasSkateWomens,dfSeasGoalie,dfSeasGoalieMens,dfSeasGoalieWomens,dfBeanpotAwards,dfBeanpotAwardsWomens,dfGameStats,dfGameStatsMens,dfGameStatsWomens,dfGameStatsGoalie,dfGameStatsGoalieMens,dfGameStatsGoalieWomens
    dfRes=dfGames
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
        return render_template('form.html',result=result,query='',resTable=formatResults(dfRes),opponents_values=getOpponentList(dfRes),season_values=list(dfRes.season.unique()),arena_values=sorted(list(dfRes.arena.unique())),buscore=buscore,oppscore=oppscore,isAscending=True,selected_sort='date',startYear=dfRes.year.min(),endYear=dfRes.year.max(),minYear=minYear,maxYear=maxYear,selected_startSeas=dfRes.season.min(),selected_endSeas=dfRes.season.max(),selected_range='season',hideExStatus="true")
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
            
        if(form_data['location']!='all'):
            dfRes=dfRes.query(f"location==\'{form_data['location']}\'")
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
        return render_template('form.html',result=result,query='',resTable=formatResults(dfRes),opponents_values=getOpponentList(dfRes),\
        season_values=list(dfOrig.season.unique()),selected_gender=form_data['gender'],selected_opponent=form_data['opponent'],selected_season=form_data['season'],selected_location=form_data['location'],arena_values=sorted(list(dfRes.arena.unique())),selected_arena=form_data['arena'],buscore=buscore,selected_buop=form_data['buscoreop'],selected_oppop=form_data['oppscoreop'],oppscore=oppscore,\
        isAscending=form_data['isAscending'].capitalize(),selected_sort=form_data['sortval'],startYear=sYear,endYear=eYear,minYear=minYear,maxYear=maxYear,selected_startSeas=seasonStart,selected_endSeas=seasonEnd,selected_range=form_data['range'],hideExStatus=hideEx)
        if(query in form_data.keys()):
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
                      result,dfRes=getResults(dfGamesWomens,dfGameStatsWomens,dfGameStatsGoalieWomens,query)
                  else:
                      result,dfRes=getResults(dfGames,dfGameStatsMens,dfGameStatsGoalieMens,query) 
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
          if(dfRes is not None):
              dfRes.rename(columns={'date': 'Date', 'opponent': 'Opponent', 'result': 'Result','scoreline':'Score','arena':'Location','tourney':'Tournament'}, inplace=True)
              style = dfRes.style.apply(colorwinner,axis=1).hide(axis='index')
              headers = {
                  'selector': 'th:not(.index_name)',
                  'props': 'color: white;'
              }
              style.set_table_styles([headers])
              dfRes=style.to_html(index_names=False,render_links=True)
          else:
             dfRes=''
             
          return render_template('form.html',result = result, query=query.upper(),resTable=dfRes)
 
def convertToHtml(result):
 pass

    
if __name__=='__main__':
  app.run(host='localhost', port=5000)