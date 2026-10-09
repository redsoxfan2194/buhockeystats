import requests
import pandas as pd
import burecordbook as burb
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import time
season=20262027

def validateRequest(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response
    elif (response.status_code == 429):
        retry_after = int(response.headers.get("Retry-After", 1))
        print(f'Failed...Retrying after {retry_after} sec')
        time.sleep(retry_after)
        for i in range(5):
            response = requests.get(url)
            if(response.status_code == 200):
                return response
            elif (response.status_code == 429):
                retry_after = int(response.headers.get("Retry-After", 1))
                print(f'Fail...Retrying after {retry_after} sec')
                time.sleep(retry_after)
    return ''

def getPlayerStats(name,date,season='20232024'):
    global pDict
    pId=pDict[name]
    url=f"https://api-web.nhle.com/v1/player/{pId}/landing"
    response = validateRequest(url)
    if response == '':
        return ''
    data = response.json()
    if('last5Games' not in data.keys()):
      return ''
    if(date==data['last5Games'][0]['gameDate']):
      gameStats=data['last5Games'][0]
      return gameStats
    else:
      return ''
      #gStr=f"{gameStats['goals']}-{gameStats['assists']}--{gameStats['points']} TOI: {gameStats['toi']}"

def getGameResults(gId):
    url=f"https://api-web.nhle.com/v1/gamecenter/{gId}/boxscore"
    response = validateRequest(url)
    if response == '':
        return ''
    data = response.json()
    aScore=data['awayTeam']['score']
    hScore=data['homeTeam']['score']
    aTeam=data['awayTeam']['abbrev']
    hTeam=data['homeTeam']['abbrev']
    ot=''
    if(data['regPeriods']!=3):
        ot+=" ("+data['periodDescriptor']['periodType']+")"
    scoreStr=f"{aTeam} {aScore} {hTeam} {hScore}{ot}"
    return scoreStr

def formatStats(name,stats):
    opp=stats['opponentAbbrev']
    team=stats['teamAbbrev']
    statline=stats
    outStr=f'{name} ({team})<br>'
    if('goals' not in statline):
        if('saves' not in statline):
            saves= statline['shotsAgainst']+statline['goalsAgainst']
        else:
            saves=statline['saves']
        if('savePercentage' in statline):
            svPerc=round(statline['savePercentage'],3)
        else:
            svPerc=round(statline['savePctg'],3)
        outStr+=f"GA: {statline['goalsAgainst']}<br>Saves: {saves}<br>SV%: {svPerc}<br>TOI: {statline['toi']}"
        if('decision' in statline):
         outStr+=f"<br>Decision: {statline['decision']}"
    else:
        outStr+=f"{statline['goals']}-{statline['assists']}--{statline['points']} TOI: {statline['toi']}"
    return outStr

def generatePlayerStatLine(name,date):
    stats=getPlayerStats(name,date)
    if(stats is None or stats==''):
        return
    scoreStr=getGameResults(stats['gameId'])
    pStr=formatStats(name,stats)
    return pStr,scoreStr

def generateSeasonStats():
    global pDict
    seasList=[]
    gList=[]
    for player in pDict:
        url=f"https://api-web.nhle.com/v1/player/{pDict[player]}/landing"
        response = validateRequest(url)
        if response == '':
            continue
        data = response.json()
        seasStats={'Name':player,'gamesPlayed':0,'goals':0,'assists':0,'points':0,'powerPlayGoals':0,'gameWinningGoals':0,'plusMinus':0,'avgToi':"0:00"}
        for leagues in data['seasonTotals']:
          if(leagues['leagueAbbrev']=='NHL' and leagues['season']==season):
            seasStats= data['featuredStats']['regularSeason']['subSeason']
            break
        if('currentTeamAbbrev' not in data.keys()):
          continue
        team=data['currentTeamAbbrev']
        if('points' not in seasStats):
            stats=['Name','gamesPlayed', 'gamesStarted', 'goalsAgainst', 'goalsAgainstAvg', 'wins', 'losses', 'otLosses', 'ties',  'savePctg', 'shutouts', 'timeOnIce']
        else:
            stats=['Name','gamesPlayed','goals','assists','points','powerPlayGoals','gameWinningGoals','plusMinus','avgToi']
        seasDict={}
        for stat in stats:
            if(stat=='Name'):
                seasDict[stat]=player+' ('+team+')'
                continue
            if(stat not in seasStats.keys()):
                seasDict[stat]=0
            else:
                seasDict[stat]=seasStats[stat]
        if('points' in seasStats):
            seasList.append(seasDict)
        else:
            gList.append(seasDict)
    dfSkate=pd.DataFrame(seasList).sort_values('points',ascending=False)
    dfSkate.rename(inplace=True,columns={'gamesPlayed':'GP', 'goals': "G",'assists':"A",'points':'Pts','plusMinus':"+/-","powerPlayGoals":"PPG","gameWinningGoals":"GWG",'avgToi':'AvgTOI'})
    skateStr=dfSkate.to_html(index=False)
    dfGoalie=pd.DataFrame(gList)
    if(not dfGoalie.empty):
      dfGoalie['goalsAgainstAvg']=round(dfGoalie['goalsAgainstAvg'],2)
      dfGoalie['savePctg']=round(dfGoalie['savePctg'],3)
      dfGoalie.rename(inplace=True, columns={'gamesPlayed':'GP', 'gamesStarted': "GS",'goalsAgainst':"GA",'goalsAgainstAvg':'GAA','wins':"W","losses":"L","ties":"T",'otLosses':'OTL',"savePctg":"SV%","shutouts":"SO",'timeOnIce':"TOI"})
    goalieStr=dfGoalie.to_html(index=False)
    seasStr="Skater Stats:<br>"
    seasStr+=skateStr+'<br><br>'
    seasStr+='Goalie Stats:<br>'
    seasStr+=goalieStr
    return seasStr

def send_stats(date,stats,email):
  # Set up the SMTP server for Gmail
  smtp_server = 'smtp.gmail.com'
  smtp_port = 587

  # Sender's email address and login credentials
  sender_email = 'buhockeystats@gmail.com'
  sender_password = 'pdml gntf igzb sezh'

  # Recipient's email address
  receiver_email = email

  dt = datetime.strptime(date, '%Y-%m-%d')

  # Extract year, month, and day
  year = dt.year
  month = dt.month
  day = dt.day

  # Format as m/d/y
  formatted_date = f"{month}/{day}/{year}"

  # Create a MIMEText object to represent the email
  message = MIMEMultipart()
  message['From'] = sender_email
  message['To'] = receiver_email
  message['Subject'] = f'Terrier NHL Stats Digest - {formatted_date}'

  # Attach the body of the email
  body = MIMEText(f'{stats}', 'HTML')
  message.attach(body)

  # Connect to the SMTP server
  with smtplib.SMTP(smtp_server, smtp_port) as server:
      server.starttls()  # Upgrade the connection to a secure TLS connection
      server.login(sender_email, sender_password)
      server.sendmail(sender_email, receiver_email, message.as_string())
#'''
burb.initializeRecordBook()

f=open('/home/buhockeystats/mysite/nhl_players.csv','w')
print("name,pos,id",file=f)
for team in ['ANA', 'BOS', 'BUF', 'CAR', 'CBJ', 'CGY', 'CHI', 'COL', 'DAL', 'DET', 'EDM', 'FLA', 'LAK', 'MIN', 'MTL', 'NJD', 'NSH', 'NYI', 'NYR', 'OTT', 'PHI', 'PIT', 'SEA', 'SJS', 'STL', 'TBL', 'TOR', 'UTA', 'VAN', 'VGK', 'WPG', 'WSH']:
  url=f"https://api-web.nhle.com/v1/roster/{team}/{season}"
  response = requests.get(url)
  data=response.json()
  for pos in data.keys():
      for i in data[pos]:
          try:
            print(f"{i['firstName']['default']} {i['lastName']['default']},{i['positionCode']},{i['id']}",file=f)
          except:
              continue
f.close()

dfnhl=pd.read_csv('/home/buhockeystats/mysite/nhl_players.csv',encoding='latin1')
dfnhl=dfnhl.loc[dfnhl['name'].isin(list(burb.dfSkateMens.name.unique())+list(burb.dfGoalieMens.name.unique()))].drop_duplicates()
dfnhl = dfnhl[~(dfnhl['name'] == 'Jack Hughes')]
pIdDict=dfnhl.to_dict('records')
pDict={}
for i in pIdDict:
    pDict[i['name']]=i['id']
#'''
scores=set()

#pDict={'Charlie McAvoy': 8479325, 'Jordan Greenway': 8478413, 'Domenick Fensore': 8481562, 'Charlie Coyle': 8475745, 'Dante Fabbro': 8479371, 'Joel Farabee': 8480797, 'Ryan Greene': 8483450, 'Matt Grzelcyk': 8476891, 'Alex Vlasic': 8481568, 'Jake Oettinger': 8479979, 'A.J. Greer': 8478421, 'Evan Rodrigues': 8478542, 'Lane Hutson': 8483457, 'Brady Tkachuk': 8480801, 'Trevor Zegras': 8481533, 'Macklin Celebrini': 8484801, 'Clayton Keller': 8479343, 'Tom Willander': 8484240, 'Jack Eichel': 8478403}
statsStr=''
isStats=False

# Get today's date
today = datetime.today()

# Calculate yesterday's date
date = today - timedelta(days=1)

dateStr=date.strftime('%Y-%m-%d')
for p in pDict.keys():
    ret=generatePlayerStatLine(p,dateStr)
    if(ret is not None):
        if(not isStats):
          statsStr+="Stats:<br>"
          isStats=True
        pStatLine=ret[0]
        scoreline=ret[1]
        statsStr+=pStatLine
        statsStr+='<br><br>'
        scores.add(scoreline)
if(isStats):
  statsStr+="Scores:<br>"
  for score in scores:
      statsStr+=(score)
      statsStr+='<br><br>'

if(not isStats):
  statsStr = "No BU Player Stats Today<br>"

statsStr+=generateSeasonStats()
#emailList=['buhockeystats@gmail.com','nmemme2194@gmail.com']
emailList=['buhockeystats@gmail.com','Jmarkenriquez@gmail.com']
#print(statsStr)
#emailList=[]


for email in emailList:
  print(f"Sending stats to...{email}")
  send_stats(dateStr,statsStr,email)