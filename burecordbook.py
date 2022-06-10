import pandas as pd
import re
import operator
import calendar
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
from datetime import datetime

# Get Tourneys
def generateRecordBook():
    global tourneyDict
    fileName=('BURecordBook.txt')
    tourneys=[]
    with open(fileName, 'r', encoding='utf-8') as f:
        read_data = f.read()
        rows=read_data.split('\n')
        conf='Independent'
        for i in rows:
            row=i.split('\t')
            if(len(row[0])>7 and len(row)==1 and ('COACH' not in i and 'OVERALL' not in i and 'ECAC:' not in i and 'CAPTAIN' not in i and 'HOCKEY' not in i and 'NEIHL:' not in i and 'forfeit' not in i)):
                tourneys.append(row[0])
                
                
    tourneyDict={}
    for i in tourneys:
        if(i=='Key to Tournaments'):
            continue
        tourney=i.split(' ')
        tourneyDict[tourney[0]]=' '.join(tourney[1:])
    tourneyDict['nc']='Non-Colleigate'
    tourneyDict['Oly nc']='1932 NEAAU Olympic tryouts-Non-Colleigate'
    tourneyDict['ex']='Exhibition'
    tourneyDict['HF ex']='Hall of Fame Game-Exhibition'
    tourneyDict['IB ex']='Ice Breaker-Exhibition'

    # Get Games
    fileName=('BURecordBook.txt')
    gameList=[]
    with open(fileName, 'r', encoding='utf-8') as f:
        read_data = f.read()
        rows=read_data.split('\n')
        conf='Independent'
        for i in rows:      
            if(len(i)==7):
                season=i
            coachSearch=re.search("COACH: (.*)",i)
            if coachSearch != None:
                coach=coachSearch.group(1)
            captSearch=re.search("CAPTAIN.?: (.*)",i)
            if captSearch != None:
                capt=captSearch.group(1) 
            confSearch=re.search("(NEIHL|ECAC|HOCKEY EAST):",i)
            if confSearch != None:
                conf=confSearch.group(1)
                if(conf=='HOCKEY EAST'):
                    conf='Hockey East'
            if(re.search('\*',i)!=None):
                gameType='Conference'
            else:
                gameType='Non-Conference'
            i=i.replace("* ",'')
            note=''
            if('†' in i):
                note='Loss by forfeit (ineligible player)'
                i=i.replace('†','')
            if('+' in i):
                note='Win by forfeit (opponent left ice – score was 5-1, BU)'
                i=i.replace('+','')
            if('‡' in i):
                note='Win by forfeit (ineligible player)'
                i=i.replace('‡','')
            game=re.search(r"(\d*\/\d*) (\w*) (?:\((.?ot)\))? ?(.*)\t(\S*|\S* \S*|\S* \S* \S*) ?(\(.*\))? (\d*-\d*)",i)
            if game==None:
                continue
            gameDict={'date':game.group(1),
                     'result':game.group(2),
                     'ot':game.group(3),
                     'arena':game.group(4),
                     'opponent':game.group(5),
                     'gameType':gameType,
                     'tourney': game.group(6),
                     'scoreline':game.group(7),
                     'location':'',
                     'coach':coach,
                     'captain':capt,
                     'conference':conf,
                     'season':season,
                     'note':note}
            if(gameDict['gameType']==None):
                gameDict['gameType']='Non-Conference'
            if(gameDict['tourney']=='(ex)' or gameDict['result']=='E'):
                gameDict['gameType']='Exhibition'
                gameDict['result'] = 'E'
                gameDict['tourney'] = None
            if(gameDict['arena']=='Agganis Arena' or gameDict['arena']=='Walter Brown Arena' or gameDict['arena']=='Boston Arena'):
                gameDict['location']='Home'
            elif(gameDict['tourney']==None or gameDict['tourney']=='(nc)' or gameDict['tourney'] == '(B1G/HE)' or ((gameDict['tourney'] == '(HE)' or gameDict['tourney'] == '(ECAC)') and (gameDict['arena'] != 'TD Garden' and gameDict['arena'] != 'Boston Garden' and gameDict['arena'] != 'Providence CC'))):
                gameDict['location']='Away'
            if(gameDict['location']=='' or gameDict['arena']=='Boston Garden' or gameDict['arena']=='VW Arena'):
                gameDict['location']='Neutral'
            if((gameDict['arena']=='Gutterson' and gameDict['opponent']=='Vermont') or (gameDict['arena']=='Houston' and gameDict['opponent']=='Rensselaer') or (gameDict['arena']=='Broadmoor' and gameDict['opponent']=='Colorado College') or (gameDict['arena']=='DEC Center' and gameDict['opponent']=='Minnesota Duluth')or (gameDict['arena']=='Magness Arena' and gameDict['opponent']=='Denver')or (gameDict['arena']=='Mariucci Arena' and gameDict['opponent']=='Minnesota')or (gameDict['arena']=='Munn Ice Arena' and gameDict['opponent']=='Michigan State')or (gameDict['arena']=='Walker Arena' and gameDict['opponent']=='Clarkson')or (gameDict['arena']=='Thompson Arena' and gameDict['opponent']=='Dartmouth')or (gameDict['arena']=='St. Louis Arena' and gameDict['opponent']=='St. Louis') or (gameDict['arena']=='Sullivan Arena' and gameDict['opponent']=='Alaska Anchorage')):
                gameDict['location']='Away'

            if(gameDict['tourney']!=None):
                gameDict['tourney']=tourneyDict[gameDict['tourney'].replace('(','').replace(')','')]
            if((gameDict['tourney'] == gameDict['conference'] +" "+ 'Tournament') or (gameDict['tourney'] == 'NCAA Tournament')):
                gameDict['seasonType'] = 'Playoffs'
            else:
                gameDict['seasonType'] = 'Regular Season'
            gameDict['month'],gameDict['day']=gameDict['date'].split('/')
            gameDict['month']=int(gameDict['month'])
            gameDict['day']=int(gameDict['day'])
            if(gameDict['month'] >=9):
                gameDict['date']+="/" + gameDict['season'][:4]
                gameDict['year']=int(gameDict['season'][:4])
            elif(gameDict['month'] <= 4):
                gameDict['date']+= "/" + str(int(gameDict['season'][:4])+1)
                gameDict['year']=int(gameDict['season'][:4])+1
            gameDict['BUScore'],gameDict['OppoScore']=int(gameDict['scoreline'].split('-')[0]),int(gameDict['scoreline'].split('-')[1])
            gameDict['GD']=abs(gameDict['BUScore']-gameDict['OppoScore'])
            if(gameDict['season']=='1973-74' and gameDict['date']=='12/12/1973'):
                coach='Jack Parker'
            gameDict['date']=pd.Timestamp(gameDict['date'])
            gameDict['dow']=gameDict['date'].weekday()
            gameList.append(gameDict)
    f.close()
    dfGames=pd.DataFrame(gameList)
    return dfGames

def convertToInt(val):
        if(val.isdigit()):
            val=int(val)
        else:
            val=None
        return val
        
def convertToFloat(val):
        try:
            val=float(val)
        except:
            val=float('nan')
        return val        

def convertSeasons(season):
    gap=season.split(',')
    years=season[2:].split('-')
    seasonStr=''
    if(len(gap)>1):
        for i in gap:
            seasonStr+=convertSeasons(i)
    else:
        yearDiff=abs(int(years[0])-int(years[1]))
        if(yearDiff>6):
            yearDiff=100-yearDiff
        firstHalf=season[:4]
        seasonStr=''
        for i in range(yearDiff):
            secondHalf=int(firstHalf)+1
            seasonStr+=str(firstHalf)+'-'+str(secondHalf)[2:]+','
            firstHalf=secondHalf
    return seasonStr[:-1]

def decodeTeam(team):
    origTeam = team
    team=team.lower()
    team=team.replace(" ","")
    team=team.replace("-","")
    team=team.replace("'","")
    team=team.replace(".","")
    dict={"afa" : "Air Force",
        "aic" : "American International",
        "alabamahuntsville" : "Alabama Huntsville",
        "americanintl" : "American International",
        "au" : "Augustana",
        "amworst" : "Massachusetts",
        "amwurst" : "Massachusetts",
        "anosu" : "Ohio State",
        "army" : "Army West Point",
        "asu" : "Arizona State",
        "bama" : "Alabama Huntsville",
        "bc" : "Boston College",
        "bemidji" : "Bemidji State",
        "bgsu" : "Bowling Green",
        "bigred" : "Cornell",
        "bobbymo" : "Robert Morris",
        "boston" : "Boston University",
        "bostonu" : "Boston University",
        "bowlinggreenstate" : "Bowling Green",
        "bruno" : "Brown",
        "bu" : "Boston University",
        "cambridgewarcriminalfactory" : "Harvard",
        "cc" : "Colorado College",
        "cgate" : "Colgate",
        "gate" : "Colgate",
        "chestnuthillcommunitycollege" : "Boston College",
        "chestnuthilluniversity" : "Boston College",
        "clarky" : "Clarkson",
        "cct" : "Clarkson",
        "cor" : "Cornell",
        "cuse" : "Syracuse",
        "darty" : "Dartmouth",
        "du" : "Denver",
        "duluth" : "Minnesota Duluth",
        "dutchpeople" : "Union",
        "ferris" : "Ferris State",
        "ferriswheel" : "Ferris State",
        "finghawks" : "North Dakota",
        "goofers" : "Minnesota",
        "hc" : "Holy Cross",
        "hu" : "Harvard",
        "howlinhuskies" : "Northeastern",
        "huntsville" : "Alabama Huntsville",
        "icebus" : "Connecticut",
        "keggy" : "Dartmouth",
        "lakestate" : "Lake Superior State",
        "lakesuperior" : "Lake Superior State",
        "lowell" : "UMass Lowell",
        "lowelltech" : "UMass Lowell",
        "ulowell" : "Umass Lowell",
        "lssu" : "Lake Superior State",
        "lu" : "Lindenwood",
        "liu" : "Long Island University",
        "mack" : "Merrimack",
        "mankato" : "Minnesota State",
        "mc" : "Merrimack",
        "mich" : "Michigan",
        "meatchicken" : "Michigan",
        "mnsu" : "Minnesota State",
        "mrbee" : "American International",
        "msu" : "Michigan State",
        "mtu" : "Michigan Tech",
        "nd" : "Notre Dame",
        "nebraskaomaha" : "Omaha",
        "neu" : "Northeastern",
        "newtonsundayschool" : "Boston College",
        "newhavenwarcriminalfactory" : "Yale",
        "nmu" : "Northern Michigan",
        "northern" : "Northern Michigan",
        "nodak" : "North Dakota",
        "nu" : "Northeastern",
        "osu" : "Ohio State",
        "pc" : "Providence",
        "pianohuskies" : "Michigan Tech",
        "prinny" : "Princeton",
        "psu" : "Penn State",
        "purplecows" : "Minnesota State",
        "qu" : "Quinnipiac",
        "quinny" : "Quinnipiac",
        "quinni" : "Quinnipiac",
        "rmu" : "Robert Morris",
        "rpi" : "Rensselaer",
        "rit" : "RIT",
        "saintas" : "Saint Anselm",
        "scsu" : "St. Cloud State",
        "shu" : "Sacred Heart",
        "slu" : "St. Lawrence",
        "slushbus" : "Connecticut",
        "smc" : "Saint Michael's",
        "sparky" : "Arizona State",
        "sparty" : "Michigan State",
        "stanselm" : "Saint Anselm",
        "stcloud" : "St. Cloud State",
        "stmichaels" : "Saint Michael's",
        "stmikes" : "Saint Michael's",
        "stthomas" : "St. Thomas",
        "ust" : "St. Thomas",
        "sootech" : "Lake Superior State",
        "su" : "Syracuse",
        "syracuse" : "Syracuse",
        "toothpaste" : "Colgate",
        "uaa" : "Alaska Anchorage",
        "uaf" : "Alaska",
        "uah" : "Alabama Huntsville",
        "uconn" : "Connecticut",
        "umass" : "Massachusetts",
        "uma" : "Massachusetts",
        "umassamherst" : "Massachusetts",
        "umasslowell" : "UMass Lowell",
        "umd" : "Minnesota Duluth",
        "uml" : "UMass Lowell",
        "umo" : "Maine",
        "umaine" : "Maine",
        "umtc" : "Minnesota",
        "umn" : "Minnesota",
        "und" : "North Dakota",
        "unh" : "New Hampshire",
        "uno" : "Omaha",
        "usma" : "Army West Point",
        "uvm" : "Vermont",
        "uw" : "Wisconsin",
        "wisco" : "Wisconsin",
        "wmu" : "Western Michigan",
        "ziggy" : "Bowling Green",
        "zoomass" : "Massachusetts"}

    if team in dict:
        return dict[team]
    else:
        teamName=''
        teamSplit = origTeam.split(' ')
        for i in range(len(teamSplit)):
            teamName+=teamSplit[i].capitalize()
            if(i<len(teamSplit)-1):
                teamName+=' '
        return teamName

def generateJerseys():
    # Get Jerseys
    fileName=('JerseyNumbers.txt')
    playerList=[]
    with open(fileName, 'r', encoding='utf-8') as f:
        read_data = f.read()
        rows=read_data.split('\n')
        number=0
        numDict={'number':0,'player':'','season':''}
        for i in rows:
            
            numSearch=re.search("#(.*)",i)
            if numSearch != None:
                number=numSearch.group(1)
            if("Retired - " in i):
                    continue
            playerSearch=re.search("(\d*-\d*) (.*)",i)
            if playerSearch != None:
                season=playerSearch.group(1)
                numDict={'number':int(number),
                     'season':convertSeasons(season),
                     'name':playerSearch.group(2)}
                playerList.append(numDict)
    f.close()
    return pd.DataFrame(playerList)
    
    
def generateSkaters():
    fileName=('SkaterStats.txt')
    skateList=[]
    with open(fileName, 'r', encoding='utf-8') as f:
        read_data = f.read()
        rows=read_data.split('\n')
        for i in rows:
            skaterSearch=re.search('(.*),(.*) (\S*) (\S*) (\S*) (\S*) (\S*) (\S*)\/(\S*)',i)
            if skaterSearch!=None:
                skaterDict={'last':skaterSearch.group(1),
                           'first':skaterSearch.group(2),
                            'name':skaterSearch.group(2)+' '+skaterSearch.group(1),
                           'seasons':convertSeasons(skaterSearch.group(3)),
                           'gp':convertToInt(skaterSearch.group(4)),
                           'goals':convertToInt(skaterSearch.group(5)),
                           'assists':convertToInt(skaterSearch.group(6)),
                           'pts':convertToInt(skaterSearch.group(7)),
                           'pen':convertToInt(skaterSearch.group(8)),
                           'pim':convertToInt(skaterSearch.group(9))}
                skateList.append(skaterDict)
    f.close()
    return pd.DataFrame(skateList)

def generateGoalies():
    fileName=('GoalieStats.txt')
    goalieList=[]
    with open(fileName, 'r', encoding='utf-8') as f:
        read_data = f.read()
        rows=read_data.split('\n')
        for i in rows:
            goalieSearch=re.search('(.*),(.*) (\S*) (\S*) (\S*) (\S*) (\S*) (\S*) (\S*) (\S*) (\S*) (\S*)',i)
            if goalieSearch!=None:
                mins=goalieSearch.group(5).split(':')
                if(len(mins)>1):
                    time = "{}:{}".format(*divmod(int(mins[0]), 60)) + ":" + mins[1]
                    time = pd.to_timedelta(time)
                else:
                    time=float('nan')
                goalieDict={'last':goalieSearch.group(1),
                           'first':goalieSearch.group(2),
                           'name':goalieSearch.group(2)+' '+goalieSearch.group(1),
                           'seasons':convertSeasons(goalieSearch.group(3)),
                           'gp':convertToInt(goalieSearch.group(4)),
                           'mins':round(pd.Timedelta(time).total_seconds()/60,2),
                           'ga':convertToInt(goalieSearch.group(6)),
                           'gaa':convertToFloat(goalieSearch.group(7)),
                           'saves':convertToInt(goalieSearch.group(8)),
                           'sv%':convertToFloat(goalieSearch.group(9)),
                           'W':convertToInt(goalieSearch.group(10)),
                           'L':convertToInt(goalieSearch.group(11)),
                           'T':convertToInt(goalieSearch.group(12))}
                goalieList.append(goalieDict)
    f.close()
    return pd.DataFrame(goalieList)   

def generateSeasonLeaders():
    fileName=('SeasonLeaders.txt')
    leadList=[]
    with open(fileName, 'r', encoding='utf-8') as f:
        read_data = f.read()
        rows=read_data.split('\n')
        for i in rows:
            leadSearch=re.search('(\d{4}-\d{2}) (\d*) (.*) (\d*) (.*) (\d*) (.*)',i)
            if leadSearch!=None:
                leadDict={'season':leadSearch.group(1),
                          'year': int(leadSearch.group(1)[:4])+1,
                           'goals':convertToInt(leadSearch.group(2)),
                            'gname':leadSearch.group(3),
                           'assists':convertToInt(leadSearch.group(4)),
                           'aname':leadSearch.group(5),
                           'pts':convertToInt(leadSearch.group(6)),
                           'pname':leadSearch.group(7)}
                leadList.append(leadDict)
    f.close()
    dfLead=pd.DataFrame(leadList)
    return dfLead

def generateBeanpotHistory():
    fileName=('BeanpotHistory.txt')
    with open(fileName, 'r', encoding='utf-8') as f:
        read_data = f.read()
        rows=read_data.split('\n')
        beanList=[]
        for i in rows:
            col=i.split('\t')
            if(col[3]!=''):
                beanDict={"edition" : int(col[0]),
                        "year" : int(col[1]),
                        "arena" : col[2],
                        "semiDate" : col[3],
                        "semiAttend" : int(col[4]),
                        "semi1Winner" : col[5],
                        "semi1WinnerScore" : int(col[6]),
                        "semi1Loser" : col[7],
                        "semi1LoserScore" : int(col[8]),
                        "semi1OT" : col[9],
                        "semi2Winner" : col[10],
                        "semi2WinnerScore" : int(col[11]),
                        "semi2Loser" : col[12],
                        "semi2LoserScore" : int(col[13]),
                        "semi2OT" : col[14],
                        "champDate" : col[15],
                        "champAttend" : int(col[16]),
                        "consWinner" : col[17],
                        "consWinnerScore" : int(col[18]),
                        "consLoser" : col[19],
                        "consLoserScore" : int(col[20]),
                        "consOT" : col[21],
                        "champion" : col[22],
                        "championScore" : int(col[23]),
                        "runnerup" : col[24],
                        "runnerupScore" : int(col[25]),
                        "champOT" : col[26]}
                beanDict['semiDOW'],beanDict['semiDate']=beanDict['semiDate'].split(',')
                beanDict['champDOW'],beanDict['champDate']=beanDict['champDate'].split(',')
                beanDict['semiDate']=beanDict['semiDate'].rstrip(' ').lstrip(' ')
                beanDict['champDate']=beanDict['champDate'].rstrip(' ').lstrip(' ')
                beanDict['semiDate']+='/'+str(beanDict['year'])
                beanDict['champDate']+='/'+str(beanDict['year'])
                beanDict['semiDate']=pd.Timestamp(beanDict['semiDate'])
                beanDict['champDate']=pd.Timestamp(beanDict['champDate'])
                beanDict['semi1GD']=beanDict['semi1WinnerScore']-beanDict['semi1LoserScore']
                beanDict['semi2GD']=beanDict['semi2WinnerScore']-beanDict['semi2LoserScore']
                beanDict['consGD']=beanDict['consWinnerScore']-beanDict['consLoserScore']
                beanDict['champGD']=beanDict['championScore']-beanDict['runnerupScore']
                beanList.append(beanDict)
    f.close()
    dfBeanpot=pd.DataFrame(beanList) 
    return dfBeanpot
  
def determineQueryType(query):
    qType=''
    if('record' in query and 'career' not in query and cleanupQuery(query,'').startswith('record')):
        qType='record'
    elif('wins' in query):
        qType='wins'
    elif('losses' in query):
        qType='losses'
    elif('ties' in query):
        qType='ties'
    elif('last win' in query):
        qType='last win'
    elif('last loss' in query):
        qType='last loss'
    elif('last tie' in query):
        qType='last tie'
    elif('last' in query):
        qType='last'
    elif('biggest win' in query):
        qType='biggest win'
    elif('biggest loss' in query):
        qType='biggest loss'
    elif('biggest tie' in query):
        qType='biggest tie'
    elif('biggest' in query):
        qType='biggest'
    else:
        qType='player'
    return qType

def tokenizeResultsQuery(query):
    keywords=['vs','at','under','since','after','between','with','before','from','in','on','against','when']
    keyDict={}
    keyWordsDict={}
    for i in keywords:
        if(query.find(i+' ')>=0):
            finds=[m.start() for m in re.finditer(i+' ', query)]
            for d in range(len(finds)):
                if(finds[d]>0 and query[finds[d]-1]!=' '):
                    finds.pop(d)
            if(finds==[]):
                continue
            elif(len(finds)>1):
                counter=0
                for d in range(len(finds)):
                    if(finds[d]==0):
                        finds[d]=1
                        query=' '+query
                    keyDict[i+'_'+str(counter)]=finds[d]
                    counter+=1
            else:
                if(finds[0]==0):
                    finds[0]=1
                    query=' '+query
                keyDict[i]=finds[0]
    sorted_key = sorted(keyDict.items(), key=operator.itemgetter(1))
    keyWordList=[]
    for i in sorted_key:
        keyWordList.append(i[0])
        keyWordsDict={}
    tokens=re.split(" | ".join(keywords),query)
    if(tokens[0]==' ' or tokens[0]==''):
        tokens.pop(0)
    if(keyWordList!=[]):
        if(len(tokens)==len(keyWordList)):            
            for i in range(len(tokens)):
                tokens[i]=tokens[i].rstrip(' ').lstrip(' ')
                keyWordsDict[keyWordList[i]]=tokens[i]
    return keyWordsDict
    
def cleanupQuery(query,qType):
    cleanlist=['the','of','what','is',"what's",'number of','games','was','game','his','arena','rink', "a", "an","did"]
    if(qType!='bean'):
        cleanlist.insert(0,"bu")
        cleanlist.insert(0,"bu's")
    for i in cleanlist:
        if(re.search("\w"+i,query)==None):
            query=query.replace(i+' ','')
    query=query.replace("'s",'')
    if(qType!=''):
        query=query.replace(qType+' ','')
    return query.lower()
    
def getResults(dfGames,query):
    global tourneyDict
    months=[x.lower() for x in list(calendar.month_name)]
    months_short=[x.lower() for x in list(calendar.month_abbr)]
    days=[x.lower() for x in list(calendar.day_name)]
    days_short=[x.lower() for x in list(calendar.day_abbr)]
    qType=determineQueryType(query)
    queryDict=tokenizeResultsQuery(cleanupQuery(query,qType))
    
    if (queryDict=={} or qType=='' or qType=='player'):
        return ''
    inList=[]
    for i in queryDict.keys():
        if('in' == i or 'in_' in i):
            inList.append(queryDict[i])
            
    numGames=''
    ascen=True
    dfQueryList = []
    if('vs' in queryDict.keys()):
        if((dfGames['opponent']==decodeTeam(queryDict['vs']).title()).any()):
            dfQueryList.append("(dfGames['opponent']=='{}')".format(decodeTeam(queryDict['vs'])))
        else:
            dfQueryList.append("(dfGames['opponent'].str.contains('{}',case=False))".format(decodeTeam(queryDict['vs'])))
    if('against' in queryDict.keys()):
        if((dfGames['opponent']==decodeTeam(queryDict['against']).title()).any()):
            dfQueryList.append("(dfGames['opponent']=='{}')".format(decodeTeam(queryDict['against'])))
        else:
            dfQueryList.append("(dfGames['opponent'].str.contains('{}',case=False))".format(decodeTeam(queryDict['against'])))
    if('under' in queryDict.keys()):
        if(queryDict['under']=='AOC'.lower()):
            queryDict['under']="Albie O'Connell"
        dfQueryList.append("(dfGames['coach'].str.contains(\"{}\",case=False))".format(queryDict['under']))
    if('with' in queryDict.keys()):
        if(queryDict['with']=='AOC'.lower()):
            queryDict['with']="Albie O'Connell"
        dfQueryList.append("(dfGames['coach'].str.contains(\"{}\",case=False))".format(queryDict['with']))
    if('at' in queryDict.keys()):
        if('neutral' in queryDict['at']):
            queryDict['at']='Neutral'
        if(queryDict['at'].capitalize() in ['Home','Away','Neutral']):
            dfQueryList.append("(dfGames['location']==(\"{}\"))".format(queryDict['at'].capitalize()))
        elif(dfGames.loc[(dfGames['opponent']==decodeTeam(queryDict['at']))]['opponent'].count()>0):
            if((dfGames['opponent']==decodeTeam(queryDict['at']).title()).any()):
                dfQueryList.append("(dfGames['opponent']=='{}')".format(decodeTeam(queryDict['at'])))
            else:
                dfQueryList.append("(dfGames['opponent'].str.contains('{}',case=False))".format(decodeTeam(queryDict['at'])))
            dfQueryList.append("(dfGames['location']=='Away')")
        else:
            dfQueryList.append("(dfGames['arena'].str.contains(\"{}\",case=False))".format(queryDict['at']))
    if('on' in queryDict.keys()):
        dateSearch=re.search('(\w*).(\d*)',queryDict['on'])
        if(dateSearch !=None and '' not in dateSearch.groups()):            
            for i in range(len(months_short)):
                if(months_short[i] in dateSearch.group(1)):                
                    dfQueryList.append("(dfGames['month']=={})".format(int(dateSearch.group(1))))
                    break
            dfQueryList.append("(dfGames['day']=={})".format(int(dateSearch.group(2))))
        else:
            for i in range(len(days_short)):
                if(days_short[i] in queryDict['on']):
                    dfQueryList.append("(dfGames['dow']=={})".format(i))
                    break
    if('in' in queryDict.keys() or len(inList)>1):
        for i in inList:
            queryDict['in']=i
            digSearch=re.search('\d',queryDict['in'])
            decSearch=re.search('(\d{2,4})s',queryDict['in'])
            seaSearch=re.search('(\d{4}-\d{2})',queryDict['in'])
            #confSearch=re.search('(nc|ooc|non-conference|conference|hockey east|hea|ecac|neihl)',queryDict['in'])
            if(queryDict['in'] in ['ot','overtime']):
                    dfQueryList.append("(dfGames['ot'].notnull())")
            elif(queryDict['in'] in ['reg','regulation']):
                    dfQueryList.append("(dfGames['ot'].isnull())")
            elif(queryDict['in'] in ['nc','ooc','non-conference']):
                    dfQueryList.append("(dfGames['gameType']=='Non-Conference')")
            elif(queryDict['in'] == 'conference'):
                    dfQueryList.append("(dfGames['gameType']=='Conference')")
            elif(('hockey east' in queryDict['in'] or 'hea' in queryDict['in']) and 'tourn' not in queryDict['in']):
                    dfQueryList.append("(dfGames['gameType']=='Conference')") 
                    dfQueryList.append("(dfGames['conference']=='Hockey East')") 
            elif('ecac' in queryDict['in'] and 'tourn' not in queryDict['in']):
                    dfQueryList.append("(dfGames['gameType']=='Conference')") 
                    dfQueryList.append("(dfGames['conference']=='ECAC')") 
            elif('neihl' in queryDict['in'] and 'tourn' not in queryDict['in']):
                    dfQueryList.append("(dfGames['gameType']=='Conference')") 
                    dfQueryList.append("(dfGames['conference']=='NEIHL')") 
            elif('regular' == queryDict['in'] or 'rs' == queryDict['in'] or 'regular season' == queryDict['in']):
                    dfQueryList.append("(dfGames['seasonType']=='Regular Season')") 
            elif('playoff' in queryDict['in']):
                    dfQueryList.append("(dfGames['seasonType']=='Playoffs')")
            elif(digSearch==None and not(queryDict['in'] in months) and not(queryDict['in'] in months_short)):
                queryDict['in']=queryDict['in'].replace('tourney','tournament')
                if('NCAA' in queryDict['in'].upper()):
                    queryDict['in']=queryDict['in'].replace('s','')
                if(queryDict['in'].upper() in tourneyDict.keys()):
                    queryDict['in']=tourneyDict[queryDict['in'].upper()]
                dfQueryList.append("(dfGames['tourney'].str.contains(\"{}\",case=False))".format(queryDict['in']))
                dfQueryList.append("(dfGames['tourney'].notnull())")
            elif(decSearch!=None):
                if(len(decSearch.group(1))==2):
                    if(int(decSearch.group(1))>20):
                        decadeStart=int("19"+decSearch.group(1))
                    else:
                        decadeStart=int("20"+decSearch.group(1))
                else:
                    decadeStart=int(decSearch.group(1))
                dfQueryList.append("(dfGames['date'].between('{}','{}'))".format(decadeStart,decadeStart+9))
            elif(seaSearch!=None):
                dfQueryList.append("(dfGames['season']==\"{}\")".format(queryDict['in']))
            elif('first' in queryDict['in']):
                numGamesSearch=re.search('first (\d*)',queryDict['in'])
                if(numGamesSearch!=None):
                    numGames=int(numGamesSearch.group(1))
            elif('last' in queryDict['in']):
                numGamesSearch=re.search('last (\d*)',queryDict['in'])
                if(numGamesSearch!=None):
                    numGames=int(numGamesSearch.group(1))
                    ascen=False
            elif('goal' in queryDict['in']):
                goalSearch=re.search('(\d{1,3})(\+)?',queryDict['in'])
                if(goalSearch!=None):
                    if(goalSearch.group(2)!=None):
                        diff=">="
                    else:
                        diff='=='
                    dfQueryList.append("(dfGames['GD']{}{})".format(diff,int(goalSearch.group(1))))
            else:
                if(queryDict['in'].isdigit()):
                    dfQueryList.append("(dfGames['year']=={})".format(queryDict['in']))
                elif(queryDict['in'] in months):                
                    dfQueryList.append("(dfGames['month']=={})".format(months.index(queryDict['in'])))
                elif(queryDict['in'] in months_short):
                    dfQueryList.append("(dfGames['month']=={})".format(months_short.index(queryDict['in'])))

    if('since' in queryDict.keys()):
        timeSearch=re.search('(\d{4})-(\d{2})',queryDict['since'])
        if(timeSearch != None):
            sDate='9/1/{}'.format(timeSearch.group(1))
        else:      
            sDate=queryDict['since']
        dfQueryList.append("(dfGames['date']>='{}')".format(sDate))
            
    if('before' in queryDict.keys()):
        timeSearch=re.search('(\d{4})-(\d{2})',queryDict['before'])
        if(timeSearch != None):
            bDate='9/1/{}'.format(timeSearch.group(1))
        else:      
            bDate=queryDict['before']
        dfQueryList.append("(dfGames['date']<'{}')".format(bDate))
    if('after' in queryDict.keys()):
        timeSearch=re.search('(\d{4})-(\d{2})',queryDict['after'])
        if(timeSearch != None):
            if(int(timeSearch.group(2))>20):
                aStart=int("19"+timeSearch.group(2))
            else:
                aStart=int("20"+timeSearch.group(2))
            aDate='5/1/{}'.format(aStart)
        else:      
            aDate=queryDict['after']
        dfQueryList.append("(dfGames['date']>'{}')".format(int(aDate)+1))
    if('between' in queryDict.keys()):
        dates=queryDict['between'].split(' and ')
        dfQueryList.append("(dfGames['date'].between('{}','{}'))".format(dates[0],dates[1]))
    if('from' in queryDict.keys()):
        dates=queryDict['from'].split(' to ')
        dfQueryList.append("(dfGames['date'].between('{}','{}'))".format(dates[0],dates[1]))
    if('when' in queryDict.keys()):
        goalSearch=re.search("(\>|\<|\>\=|\<=)? ?(\d{1,3})(\+)?",queryDict['when'])
        if(goalSearch!=None):
            goals=int(goalSearch.group(2))
            if(goalSearch.group(1)!=None):
                diff=goalSearch.group(1)
            elif(goalSearch.group(3)!=None):
                diff='>='
            else:
                diff='=='
            if('allow' in queryDict['when']):
                dfQueryList.append("(dfGames['OppoScore']{}{})".format(diff,goals))
            if('scor' in queryDict['when']):
                dfQueryList.append("(dfGames['BUScore']{}{})".format(diff,goals))
    dfQuery =''
    for i in dfQueryList:
        dfQuery += i + " & "
    dfQuery=dfQuery[:-2]
    result=''
    if(dfQuery=='' and numGames!=''):
        dfResult=eval("dfGames.sort_values('date',ascending={})[:{}]".format(ascen,numGames))
    elif(dfQuery!=''):
        dfResult=eval("dfGames.loc[{}].sort_values('date',ascending={})[:{}]".format(dfQuery,ascen,numGames))
    else:
        return "No Results Found"
    if('last' in qType or 'biggest' in qType):
        if('last' in qType):
            sortType='date'
        elif('biggest' in qType):
            sortType=['GD','date']  
        if('win' in qType):
            res=(dfResult.loc[(dfResult['result']=='W')].sort_values(sortType,ascending=False)[:1])
        elif('tie' in qType and 'GD' not in sortType):
            res=(dfResult.loc[(dfResult['result']=='T')].sort_values(sortType,ascending=False)[:1])
        elif('tie' in qType and 'GD' in sortType):
            res=pd.DataFrame()
            return ''
        elif('loss' in qType):
            res=(dfResult.loc[(dfResult['result']=='L')].sort_values(sortType,ascending=False)[:1])
        else:
            res=dfResult.sort_values(sortType,ascending=False)[:1]
        if(not res.empty):
            resStr= "{} {} {}".format(datetime.strptime(res['date'].to_string(index=False),'%Y-%M-%d').strftime('%M/%d/%Y'),res['opponent'].to_string(index=False).lstrip(' '),res['scoreline'].to_string(index=False).lstrip(' '))
            if('None' not in res['ot'].to_string(index=False)):
                resStr+= res['ot'].to_string(index=False)
            if('None' not in res['tourney'].to_string(index=False)):
                resStr+=" ("+ res['tourney'].to_string(index=False).lstrip(' ') +")"
        else:
            resStr='No Results Found'
        return resStr
    if(qType=='record'):
        for i in ['W','L','T']:
            if((dfResult['result']==i).any()):
                res=dfResult.groupby('result').count()['date'][i]
            else:
                res=0
            result+=str(res)+'-'
    if(qType=='wins'):
            if((dfResult['result']=='W').any()):
                res=dfResult.groupby('result').count()['date']['W']
            else:
                res=0
            result=str(res)
    elif(qType=='losses'):
            if((dfResult['result']=='L').any()):
                res=dfResult.groupby('result').count()['date']['L']
            else:
                res=0
            result=str(res)
    elif(qType=='ties'):
            if((dfResult['result']=='T').any()):
                res=dfResult.groupby('result').count()['date']['T']
            else:
                res=0
            result=str(res)
    if(result[-1]=='-'):   
        result=result[:-1]
    if(result!=''):
        return result
    else:
        return "No Results Found"

def getPlayerStats(playerDfs,query):
    dfSkate=playerDfs['careerSkaters']
    dfGoalie=playerDfs['careerGoalies']
    dfJersey=playerDfs['jerseys']
    dfLead=playerDfs['seasonleaders']
    dfSeasSkate=playerDfs['seasonSkaters']
    dfSeasGoalie=playerDfs['seasonGoalies']
    query=cleanupQuery(query,'')
    careerSearch=re.search('(.*) career (.*)',query)
    numSearch=re.search('\#(\d*)',query)
    nameSearch=re.search('by (\w*)',query)
    numQuery=re.search('number (\w* \w*|\w*)',query)
    seasonSearch=re.search('(\w* \w*|\w*)? ?(goal\S*|point\S*|pts|assists|stat\S*|record|gaa|sv|save|shut|so)? ?in (\d{4}-\d{2}|\d{4})',query)
    if(seasonSearch!=None and numSearch==None):
        season=seasonSearch.group(3)
        if('-' in seasonSearch.group(3)):
            year=int(season[:4])+1
        else:
            year=int(season)
        if(seasonSearch.group(1) != None):
            playerName = seasonSearch.group(1)
            dfRes=dfSeasSkate.loc[(dfSeasSkate['year']==year) & (dfSeasSkate['name'].str.contains(playerName,case=False))]
            dfResG=dfSeasGoalie.loc[(dfSeasGoalie['year']==year) & (dfSeasGoalie['name'].str.contains(playerName,case=False))]
            resStr=''
            if(dfRes.empty and dfResG.empty):
                return resStr
            if(seasonSearch.group(2)!=None):
                statType=seasonSearch.group(2)
                if(not dfResG.empty):
                    gaa=dfResG['gaa'].to_string(index=False).lstrip()
                    svper=dfResG['sv%'].to_string(index=False).lstrip()
                    record=dfResG['record'].to_string(index=False).lstrip()
                    so=dfResG['SO'].to_string(index=False).lstrip()
                    if('stat' in statType or 'stat line' in statType.replace(' ','')):
                        if(len(dfResG)>1):
                            for row in range(len(dfResG)):
                                resStr+= "{}: {}/{}/{}".format(dfResG.iloc[row]['name'].to_string(index=False).lstrip(' '),dfResG.iloc[row]['gaa'].to_string(index=False).lstrip(),dfResG.iloc[row]['sv%'].to_string(index=False).lstrip(),dfResG.iloc[row]['record'].to_string(index=False).lstrip())
                        else:
                            resStr= "{}: {}/{}/{}".format(dfResG['name'].to_string(index=False).lstrip(' '),gaa,svper,record)
                    elif('gaa' in statType):
                        if(len(dfResG)>1):
                            for row in range(len(dfResG)):
                                resStr+= "{}: {}".format(dfResG.iloc[row]['name'].to_string(index=False).lstrip(' '),dfResG.iloc[row]['gaa'].to_string(index=False).lstrip())
                        else:    
                            resStr = "{}: {}".format(dfResG['name'].to_string(index=False).lstrip(' '),gaa)
                    elif('sv' in statType or 'save' in statType):
                        if(len(dfResG)>1):
                            for row in range(len(dfResG)):
                                resStr+= "{}: {}".format(dfResG.iloc[row]['name'].to_string(index=False).lstrip(' '),dfResG.iloc[row]['sv%'].to_string(index=False).lstrip())
                        else:
                            resStr = "{}: {}".format(dfResG['name'].to_string(index=False).lstrip(' '),svper)
                    elif('so' in statType or 'shut' in statType):
                        if(len(dfResG)>1):
                            for row in range(len(dfResG)):
                                resStr+= "{}: {}".format(dfResG.iloc[row]['name'].to_string(index=False).lstrip(' '),dfResG.iloc[row]['SO'].to_string(index=False).lstrip())
                        else:
                            resStr = "{}: {}".format(dfResG['name'].to_string(index=False).lstrip(' '),so)
 
                    elif('record' in statType):
                        if(len(dfResG)>1):
                            for row in range(len(dfResG)):
                                resStr+= "{}: {}".format(dfResG.iloc[row]['name'].to_string(index=False).lstrip(' '),dfResG.iloc[row]['record'].to_string(index=False).lstrip())
                        else:
                            resStr= "{}: {}".format(dfResG['name'].to_string(index=False).lstrip(' '),record)
                else:
                    if('goal' in statType):
                        if(len(dfRes)>1):
                            for row in range(len(dfRes)):
                                resStr += dfRes.iloc[row]['name'] + " " + str(dfRes.iloc[row]['goals']) + "\n"
                        else:
                            resStr = "{}: {}".format(dfRes['name'].to_string(index=False).lstrip(),dfRes['goals'].to_string(index=False).lstrip())
                    elif('assists' in statType):
                        if(len(dfRes)>1):
                            for row in range(len(dfRes)):
                                resStr += dfRes.iloc[row]['name'].lstrip() + " " + str(dfRes.iloc[row]['assists']) + "\n"
                        else:
                            resStr = "{}: {}".format(dfRes['name'].lstrip(),dfRes['assists'].to_string(index=False).lstrip())
                    elif('pts' in statType or 'point' in statType or 'stat' in statType):
                        if(len(dfRes)>1):
                            for row in range(len(dfRes)):
                                resStr+= "{}: {}-{}--{}\n".format(dfRes.iloc[row]['name'].lstrip(' '),dfRes.iloc[row]['goals'],dfRes.iloc[row]['assists'],dfRes.iloc[row]['pts'])
                        else:
                            resStr= "{}: {}-{}--{}".format(dfRes['name'].to_string(index=False).lstrip(' '),dfRes['goals'].to_string(index=False).lstrip(' '),dfRes['assists'].to_string(index=False).lstrip(' '),dfRes['pts'].to_string(index=False).lstrip(' '))
            else:
                if(dfResG.empty):
                    if(len(dfRes)>1):
                        for row in range(len(dfRes)):
                            resStr+= "{}: {}-{}--{}\n".format(dfRes.iloc[row]['name'].lstrip(' '),dfRes.iloc[row]['goals'],dfRes.iloc[row]['assists'],dfRes.iloc[row]['pts'])
                    else:
                        resStr= "{}: {}-{}--{}".format(dfRes['name'].to_string(index=False).lstrip(' '),dfRes['goals'].to_string(index=False).lstrip(' '),dfRes['assists'].to_string(index=False).lstrip(' '),dfRes['pts'].to_string(index=False).lstrip(' '))
                else:
                    gaa=dfResG['gaa'].to_string(index=False).lstrip()
                    svper=dfResG['sv%'].to_string(index=False).lstrip()
                    record=dfResG['record'].to_string(index=False).lstrip()
                    so=dfResG['SO'].to_string(index=False).lstrip()
                    if(len(dfResG)>1):
                        for row in range(len(dfResG)):
                                resStr+= "{}: {}/{}/{}".format(dfResG.iloc[row]['name'].to_string(index=False).lstrip(' '),dfResG.iloc[row]['gaa'].to_string(index=False).lstrip(),dfResG.iloc[row]['sv%'].to_string(index=False).lstrip(),dfResG.iloc[row]['record'].to_string(index=False).lstrip())
                    else:
                        resStr= "{}: {}/{}/{}".format(dfResG['name'].to_string(index=False).lstrip(' '),gaa,svper,record)
 
            return resStr
    if('most' in query or 'lead' in query):

        if(seasonSearch!=None):
            if(re.search('goal\S',query)):
                statType='goals'
                name='gname'
            elif(re.search('pts|point|scor',query)):
                statType='pts'
                name='pname'
                return "{}:{}-{}--{}".format(dfLead.loc[(dfLead['year']==year)][name].to_string(index=False).lstrip(),dfLead.loc[(dfLead['year']==year)]['goals'].to_string(index=False).lstrip(),dfLead.loc[(dfLead['year']==year)]['assists'].to_string(index=False).lstrip(),dfLead.loc[(dfLead['year']==year)]['pts'].to_string(index=False).lstrip())

            elif(re.search('assist\S',query)):
                statType='assists'
                name='aname'
               
            return "{}:{} {}".format(dfLead.loc[(dfLead['year']==year)][name].to_string(index=False).lstrip(),dfLead.loc[(dfLead['year']==year)][statType].to_string(index=False).lstrip(),statType)
        elif(numSearch!=None):
            number=int(numSearch.group(1))
            dfNum=dfSkate.loc[dfSkate['name'].isin((dfJersey.loc[dfJersey['number']==number]['name']))]
            if(not dfNum.empty):
                if(re.search('goal\S',query)):
                    statType='goals'
                elif(re.search('pts|point|scor',query)):
                    statType='pts'
                    df=dfNum.sort_values(statType,ascending=False)[:1]
                    name=df['name'].to_string(index=False).lstrip(' ')
                    pts=df['pts'].to_string(index=False).lstrip(' ')
                    goals=df['goals'].to_string(index=False).lstrip(' ')
                    assists=df['assists'].to_string(index=False).lstrip(' ')
                    if(not df.empty):
                        return "{}:{}-{}--{}".format(name,goals,assists,pts)
                elif(re.search('assist\S',query)):
                    statType='assists'
                df=dfNum.sort_values(statType,ascending=False)[:1]
                if(not df.empty):
                    name=df['name'].to_string(index=False).lstrip(' ')
                    stat=df[statType].to_string(index=False).lstrip(' ')
                    return "{}: {} {}".format(name,stat,statType)
        elif(nameSearch!=None):
            name=nameSearch.group(1)
            dfName=dfSkate.loc[dfSkate['name'].str.contains(name,case=False)]
            if(not dfName.empty):
                if(re.search('goal\S',query)):
                    statType='goals'
                elif(re.search('pts|point|scor',query)):
                    statType='pts'
                    df=dfName.sort_values(statType,ascending=False)[:1]
                    name=df['name'].to_string(index=False).lstrip(' ')
                    pts=df['pts'].to_string(index=False).lstrip(' ')
                    goals=df['goals'].to_string(index=False).lstrip(' ')
                    assists=df['assists'].to_string(index=False).lstrip(' ')
                    if(not df.empty):
                        return "{}:{}-{}--{}".format(name,goals,assists,pts)
                elif(re.search('assist\S',query)):
                    statType='assists'
                df=dfName.sort_values(statType,ascending=False)[:1]
                name=df['name'].to_string(index=False).lstrip(' ')
                stat=df[statType].to_string(index=False).lstrip(' ')
                if(not df.empty):
                    return "{}: {} {}".format(name,stat,statType)
        else:
            if(not dfSkate.empty):
                if(re.search('goal\S',query)):
                    statType='goals'
                elif(re.search('pts|point|scor',query)):
                    statType='pts'
                    df=dfSkate.sort_values(statType,ascending=False)[:1]
                    name=df['name'].to_string(index=False).lstrip(' ')
                    pts=df['pts'].to_string(index=False).lstrip(' ')
                    goals=df['goals'].to_string(index=False).lstrip(' ')
                    assists=df['assists'].to_string(index=False).lstrip(' ')
                    if(not df.empty):
                        return "{}:{}-{}--{}".format(name,goals,assists,pts)
                elif(re.search('assist\S',query)):
                    statType='assists'
                df=dfSkate.sort_values(statType,ascending=False)[:1]
                name=df['name'].to_string(index=False).lstrip(' ')
                stat=df[statType].to_string(index=False).lstrip(' ')
                if(not df.empty):
                    return "{}: {} {}".format(name,stat,statType) 
    if(numSearch !=None and seasonSearch != None):
        number=int(numSearch.group(1))
        season=seasonSearch.group(3)
        if(not dfJersey.loc[(dfJersey['number']==number) & (dfJersey['season'].str.contains(season))].empty):
            return dfJersey.loc[(dfJersey['number']==number) & (dfJersey['season'].str.contains(season))]['name'].to_string(index=False).lstrip()
        elif(number==6 and int(season[:4])>=2014):
            return "Retired - Jack Parker"
        elif(number==24 and int(season[:4])>=1999):
            return "Retired - Travis Roy"
        else:
            return "No one"
    if(numQuery != None):
        name=numQuery.group(1)
        dfRes=dfJersey.loc[(dfJersey['name'].str.contains(name,case=False))]
        resStr=''
        if(not dfRes.empty):
            for row in range(len(dfRes)):
                resStr+="{}: {} ({})\n".format(dfRes.iloc[row]['name'],dfRes.iloc[row]['number'],dfRes.iloc[row]['season'])
        return resStr
    if(careerSearch!=None):
        playerName=careerSearch.group(1)
        stat=careerSearch.group(2)
        pStatsLine=dfSkate.loc[dfSkate['name'].str.contains(playerName,case=False)]
        gStatsLine=dfGoalie.loc[dfGoalie['name'].str.contains(playerName,case=False)]
        if(len(pStatsLine)==1):
            goals=pStatsLine['goals'].to_string(index=False).lstrip()
            assists=pStatsLine['assists'].to_string(index=False).lstrip()
            pts=pStatsLine['pts'].to_string(index=False).lstrip()
            if('stats' in stat or 'stat line' in stat.replace(' ','')):
                return("{}-{}--{}".format(goals,assists,pts))
            elif('goal' in stat):
                return goals
            elif('assist' in stat):
                return assists
            elif('pts' in stat or 'point' in stat):
                return pts
        elif(len(gStatsLine)==1):
            gaa=gStatsLine['gaa'].to_string(index=False).lstrip()
            svper=gStatsLine['sv%'].to_string(index=False).lstrip()
            wins=int(float(gStatsLine['W'].to_string(index=False).lstrip()))
            loss=int(float(gStatsLine['L'].to_string(index=False).lstrip()))
            tie=int(float(gStatsLine['T'].to_string(index=False).lstrip()))
            if('stats' in stat or 'stat line' in stat.replace(' ','')):
                return("{}/{}/{}-{}-{}".format(gaa,svper,wins,loss,tie))
            elif('gaa' in stat):
                return gaa
            elif('sv' in stat or 'save' in stat):
                return svper
            elif('record' in stat):
                return "{}-{}-{}".format(wins,loss,tie)
            
    return ''
    
def generateSeasonSkaters():
    fileName=('SeasonSkaterStats.txt')
    with open(fileName, 'r', encoding='utf-8') as f:
        read_data = f.read()
        rows=read_data.split('\n')
        seasList=[]
        for i in rows:
            col=i.split('\t')
            seasDict={'number':col[0],
                     'name':col[1],
                     'pos':col[2],
                     'yr':col[3],
                     'gp':int(col[4]),
                     'goals':int(col[5]),
                     'assists':int(col[6]),
                     'pts':int(col[7]),
                     'pens':col[8],
                     'season':col[9],
                     'year':int(col[9][:4])+1}
            seasList.append(seasDict)
    f.close()
    dfSeasSkate=pd.DataFrame(seasList)  
    return dfSeasSkate
    
def generateSeasonGoalies():    
    fileName=('SeasonGoalieStats.txt')
    with open(fileName, 'r', encoding='utf-8') as f:
        read_data = f.read()
        rows=read_data.split('\n')
        seasGList=[]
        for i in rows:
            col=i.split('\t')
            seasGDict={'number':col[0],
                     'name':col[1],
                     'yr':col[2],
                     'gp':int(col[3]),
                     'mins':col[4],
                     'ga':int(col[5]),
                     'saves':int(col[6]),
                     'sv%':float(col[7]),
                     'gaa':float(col[8]),
                     'record':col[9],
                     'SO':int(col[10]),
                     'season':col[11],
                     'year':int(col[11][:4])+1}
            seasGList.append(seasGDict)
    f.close()
    dfSeasGoalie=pd.DataFrame(seasGList)
    return dfSeasGoalie
    
def getBeanpotStats(dfBeanpot,query):
    beanNumSearch=re.search('(\d{4}|\d{1,2}|first|second|third)(?:st|nd|rd|th)? beanpot',query)
    typeSearch=re.search('beanpot (semi|consolation|final|championship)?\s?(champ|winner|runner|runner-up|1st|first|2nd|second|third|3rd|fourth|4th|last|result|finish)',query)
    recordSearch=re.search('(bu|boston university|bc|boston college|northeastern|nu|harvard|hu) record in beanpot ?(early|late|semi|cons|final|champ|3rd|third)?(.*(\d))?',query)
    head2headSearch=re.search('(bu|boston university|bc|boston college|northeastern|nu|harvard|hu) record vs (bu|boston university|bc|boston college|northeastern|nu|harvard|hu) in beanpot ?(early|late|semi|cons|final|champ|3rd|third)?(\d)?',query)
    finishSearch=re.search('^(bu|boston university|bc|boston college|northeastern|nu|harvard|hu)? ?beanpot (1st|first|2nd|second|3rd|third|fourth|last|4th|champ|title)? ?(?:place)? ?(finish)?',query)
    timeSearch=re.search('(since|after|before) (\d{4})|(?:between|from) (\d{4}) (?:and|to) (\d{4})',query)
    tQuery=''
    if(timeSearch!=None):
        timeType=timeSearch.group(1)
        if(timeType==None):
            timeType='between'
        if(timeType =='since'):
            year=int(timeSearch.group(2))
            tQuery+=' & (dfBeanpot["year"]>={})'.format(year)
        if(timeType =='after'):
            year=int(timeSearch.group(2))
            tQuery+=' & (dfBeanpot["year"]>{})'.format(year)
        elif(timeType in ['before']):
            year=int(timeSearch.group(2))
            tQuery+=' & (dfBeanpot["year"]<{})'.format(year) 
        elif(timeType == 'between'):
            sYear=int(timeSearch.group(3))
            eYear=int(timeSearch.group(4))
            tQuery+=' & (dfBeanpot["year"].between({},{}))'.format(sYear,eYear) 

    if(recordSearch != None and 'vs' not in query):
        team=decodeTeam(recordSearch.group(1))
        qType=recordSearch.group(2)
        if(qType==None):
            qType=''
        if(recordSearch.group(3) != None and recordSearch.group(3).isdigit()):
            semiNum=int(recordSearch.group(3))
        else:
            semiNum=0
        recStr=''     
        if((qType in ['semi','early'] and semiNum==0) or (qType in 'semi' and semiNum==1) or qType==''):
            semi1Wins=dfBeanpot.loc[eval("(dfBeanpot['semi1Winner']==\"{}\")".format(team)+tQuery)]['year'].count()
            semi1Losses=dfBeanpot.loc[eval("(dfBeanpot['semi1Loser']==\"{}\")".format(team)+tQuery)]['year'].count()
            recStr+=("Semi-Final 1: {}-{}\n".format(semi1Wins,semi1Losses))
        if((qType in ['semi','late'] and semiNum==0) or (qType in 'semi' and semiNum==2) or qType==''):
            semi2Wins=dfBeanpot.loc[eval("(dfBeanpot['semi2Winner']==\"{}\")".format(team)+tQuery)]['year'].count()
            semi2Losses=dfBeanpot.loc[eval("(dfBeanpot['semi2Loser']==\"{}\")".format(team)+tQuery)]['year'].count()
            recStr+="Semi-Final 2: {}-{}\n".format(semi2Wins,semi2Losses)
        if((qType in ['semi'] and semiNum==0) or qType == ''):
            recStr+='Semi-Finals: {}-{}\n'.format(semi1Wins+semi2Wins,semi1Losses+semi2Losses)
        if(qType in ['cons','third','3rd'] or qType == '' ):
            consWins=dfBeanpot.loc[eval("(dfBeanpot['consWinner']==\"{}\")".format(team)+tQuery)]['year'].count()
            consLosses=dfBeanpot.loc[eval("(dfBeanpot['consLoser']==\"{}\")".format(team)+tQuery)]['year'].count()
            consTies=dfBeanpot.loc[eval("(dfBeanpot['consWinner'].str.contains(team)) & (dfBeanpot['consWinner'].str.contains(','))"+tQuery)]['year'].count()
            consApp=consWins+consLosses+consTies
            if(consTies>0):
                consLossesStr=str(consLosses)+'-'+str(consTies)
            else:
                consLossesStr=str(consLosses)
            recStr+= "Consolation Game: {}-{} ({} Appearances)\n".format(consWins,consLossesStr,consApp)
        if(qType in ['final','champ'] or qType==''):
            champWins=dfBeanpot.loc[eval("(dfBeanpot['champion']==\"{}\")".format(team)+tQuery)]['year'].count()
            champLosses=dfBeanpot.loc[eval("(dfBeanpot['runnerup']==\"{}\")".format(team)+tQuery)]['year'].count()
            recStr+= "Championship Game: {}-{} ({} Appearances)\n".format(champWins,champLosses,champWins+champLosses)
        if(qType==''):
            recStr+="Total: {}-{}".format(semi1Wins+semi2Wins+consWins+champWins,semi1Losses+semi2Losses+consLosses+champLosses)
            if(consTies>0):
                recStr+="-{}\n".format(consTies)
            else:
                recStr+='\n'
        return recStr
    if(typeSearch!=None and beanNumSearch != None):
        qType=typeSearch.group(2)
        year=int(beanNumSearch.group(1))
        if(year==2021):
            return '2021 Beanpot cancelled due to the COVID-19 pandemic'
        if(len(beanNumSearch.group(1))==4):
            dfRes=dfBeanpot.loc[dfBeanpot['year']==year]
            numType='year'
        elif(len(beanNumSearch.group(1))<=2):
            dfRes=dfBeanpot.loc[dfBeanpot['edition']==year]
            numType='edition'
        elif(year=='first'):
            dfRes=dfBeanpot.loc[dfBeanpot['edition']==1]
            year=1
            numType='edition'
        elif(year=='second'):
            dfRes=dfBeanpot.loc[dfBeanpot['edition']==2]
            year=2
            numType='edition'
        elif(year=='third'):
            dfRes=dfBeanpot.loc[dfBeanpot['edition']==3]
            year=3
            numType='edition'
        finStr=''
        if(qType in ['champ','winner','1st','first'] or qType=='finish'):
            finStr += "Champion: " + dfRes['champion'].to_string(index=False).lstrip(' ') + "\n"
        if(qType in ['runner','2nd','second'] or qType=='finish'):
            finStr += "Runner-Up: " + dfRes['runnerup'].to_string(index=False).lstrip(' ') + "\n"
        if(qType in ['third','3rd']or qType=='finish'):
            finStr += "3rd Place: " +  dfRes['consWinner'].to_string(index=False).lstrip(' ') + "\n"
        if(qType in ['fourth','4th','last']or qType=='finish'):
            finStr += "4th Place: " + dfRes['consLoser'].to_string(index=False).lstrip(' ') + "\n"
        if(finStr!=''):
            return finStr
        if('result' in qType):
            beanStr=''
            if(typeSearch.group(1)==None or typeSearch.group(1)=='semi'):
                beanStr+='Semi-Finals:\n'
                for i in ['semi1Winner','semi1WinnerScore','semi1Loser','semi1LoserScore','semi1OT']:
                    beanStr+=dfBeanpot.loc[dfBeanpot[numType]==year][i].to_string(index=False).lstrip(' ')+' '
                beanStr+='\n'
                for i in ['semi2Winner','semi2WinnerScore','semi2Loser','semi2LoserScore','semi2OT']:
                    beanStr+=dfBeanpot.loc[dfBeanpot[numType]==year][i].to_string(index=False).lstrip(' ')+' '
            if(typeSearch.group(1)==None or typeSearch.group(1)=='consolation'):
                if(typeSearch.group(1)==None):
                    beanStr+='\n\n'
                beanStr+='Consolation Game:\n'
                for i in ['consWinner','consWinnerScore','consLoser','consLoserScore','consOT']:
                    beanStr+=dfBeanpot.loc[dfBeanpot[numType]==year][i].to_string(index=False).lstrip(' ')+' '
            if(typeSearch.group(1)==None or typeSearch.group(1) in ['final','champ']):
                if(typeSearch.group(1)==None):
                    beanStr+='\n\n'
                beanStr+='Championship:\n'
                for i in ['champion','championScore','runnerup','runnerupScore','champOT']:
                    beanStr+=dfBeanpot.loc[dfBeanpot[numType]==year][i].to_string(index=False).lstrip(' ')+' '
            return beanStr
    if(head2headSearch !=None):
        team1=decodeTeam(head2headSearch.group(1))
        team2=decodeTeam(head2headSearch.group(2))
        qType=head2headSearch.group(3)
        if(head2headSearch.group(4) != None):
            semiNum=int(head2headSearch.group(4))
        else:
            semiNum=0
        if(qType==None):
            qType=''
        h2hStr=''
        if((qType in ['semi','early'] and semiNum==0) or (qType in 'semi' and semiNum==1) or qType == ''):
            semi1Team1Wins=dfBeanpot.loc[eval("(dfBeanpot['semi1Winner']==\"{}\") & (dfBeanpot['semi1Loser']==\"{}\")".format(team1,team2)+tQuery)]['year'].count()
            semi1Team2Wins=dfBeanpot.loc[eval("(dfBeanpot['semi1Winner']==\"{}\") & (dfBeanpot['semi1Loser']==\"{}\")".format(team2,team1)+tQuery)]['year'].count()
            h2hStr+="Semi-Final 1: {}-{}\n".format(semi1Team1Wins,semi1Team2Wins)
        if((qType in ['semi','late'] and semiNum==0) or (qType in 'semi' and semiNum==2) or qType==''):
            semi2Team1Wins=dfBeanpot.loc[eval("(dfBeanpot['semi2Winner']==\"{}\") & (dfBeanpot['semi2Loser']==\"{}\")".format(team1,team2)+tQuery)]['year'].count()
            semi2Team2Wins=dfBeanpot.loc[eval("(dfBeanpot['semi2Winner']==\"{}\") & (dfBeanpot['semi2Loser']==\"{}\")".format(team2,team1)+tQuery)]['year'].count()
            h2hStr+="Semi-Final 2: {}-{}\n".format(semi2Team1Wins,semi2Team2Wins)
        if((qType in ['semi'] and semiNum==0) or qType==''): 
            h2hStr+="Semi-Finals (Total): {}-{}\n".format(semi1Team1Wins+semi2Team1Wins,semi1Team2Wins+semi2Team2Wins)
        if(qType in ['cons','third','3rd'] or qType==''):
            consTeam1Wins=dfBeanpot.loc[eval("(dfBeanpot['consWinner']==\"{}\") & (dfBeanpot['consLoser']==\"{}\")".format(team1,team2)+tQuery)]['year'].count()
            consTeam2Wins=dfBeanpot.loc[eval("(dfBeanpot['consWinner']==\"{}\") & (dfBeanpot['consLoser']==\"{}\")".format(team2,team1)+tQuery)]['year'].count()
            consTies=dfBeanpot.loc[(dfBeanpot['consWinner'].str.contains(team1)) & (dfBeanpot['consWinner'].str.contains(','))]['year'].count()
            consApp=consTeam1Wins+consTeam2Wins+consTies
            if(consTies>0):
                consLossesStr=str(consTeam2Wins)+'-'+str(consTies)
            else:
                consLossesStr=str(consTeam2Wins)
    
            h2hStr+="Consolation Game: {}-{}\n".format(consTeam1Wins,consLossesStr)
        if(qType in ['final','champ'] or qType==''):
            champWins=dfBeanpot.loc[eval("(dfBeanpot['champion']==\"{}\") & (dfBeanpot['runnerup']==\"{}\")".format(team1,team2)+tQuery)]['year'].count()
            champLosses=dfBeanpot.loc[eval("(dfBeanpot['champion']==\"{}\") & (dfBeanpot['runnerup']==\"{}\")".format(team2,team1)+tQuery)]['year'].count()
            h2hStr+="Championship Game: {}-{}\n".format(champWins,champLosses)
        if(qType==''):
            h2hStr+="Total: {}-{}".format(semi1Team1Wins+semi2Team1Wins+consTeam1Wins+champWins,semi1Team2Wins+semi2Team2Wins+consTeam2Wins+champLosses)
            if(consTies>0):
                h2hStr+="-{}\n".format(consTies)
            else:
                h2hStr+='\n'
        return h2hStr
    if(finishSearch != None):
        noneCheck=True
        for i in finishSearch.groups():
            if(i != None):
                noneCheck=False
        if(noneCheck):
            return ""
        if(finishSearch.group(1)==None):
            tQuery=tQuery.replace(' &','')
            beans={'Boston University':[0],'Boston College': [0],'Northeastern':[0],'Harvard':[0]} 
            counter=0
            if(finishSearch.group(2)==None):
                places=['champion','runnerup','consWinner','consLoser']
                beans={'Boston University':[0,0,0,0],'Boston College':[0,0,0,0],'Northeastern':[0,0,0,0],'Harvard':[0,0,0,0]} 
            else:
                finish=finishSearch.group(2)
                if(finish==None):
                    finish=''
                if(finish in ['champ','title','1st','first']):
                    places=['champion']
                if(finish in ['2nd','second'] or finish==''):
                    places=['runnerup']
                if(finish in ['3rd','third'] or finish==''):
                    places=['consWinner']
                if(finish in ['4th','fourth','last'] or finish==''):
                    places=['consLoser']
            for place in places:
                if(tQuery==''):
                    rows=(dfBeanpot.groupby([place])[place].count().sort_values(ascending=False).to_string(header=False).split('\n'))
                else:
                    rows=(dfBeanpot.loc[eval(tQuery)].groupby([place])[place].count().sort_values(ascending=False).to_string(header=False).split('\n'))
                for row in rows:
                    i=(list(filter(None,row.split('  '))))
                    if(i[0]=='None'):
                        continue
                    if(',' in i[0]):
                        team=i[0].split(',')
                        beans[team[0]][counter]+=int(i[1])
                        beans[team[1]][counter]+=int(i[1])
                    else:
                        beans[i[0]][counter]=int(i[1])
                counter+=1
            if(counter>1):
                sorted_finish=dict(sorted(beans.items(), key=lambda item: (item[1][0],item[1][1],item[1][2],item[1][3]),reverse=True))
            else:
                sorted_finish=dict(sorted(beans.items(), key=lambda item: (item[1][0]),reverse=True))
            finStr=''
            for i in sorted_finish.keys():
                finStr+="{0: <18}".format(i)
                for d in sorted_finish[i]:
                    finStr+= "{0: <3} ".format(d)
                finStr+='\n'
            return finStr
        else:
            team=decodeTeam(finishSearch.group(1))
            finish=finishSearch.group(2)
            if(finish==None):
                finish=''
            champWins=dfBeanpot.loc[eval("(dfBeanpot['champion']==\"{}\")".format(team)+tQuery)]['year'].count()
            champLosses=dfBeanpot.loc[eval("(dfBeanpot['runnerup']==\"{}\")".format(team)+tQuery)]['year'].count()
            consWins=dfBeanpot.loc[eval("(dfBeanpot['consWinner']==\"{}\")".format(team)+tQuery)]['year'].count()
            consLosses=dfBeanpot.loc[eval("(dfBeanpot['consLoser']==\"{}\")".format(team)+tQuery)]['year'].count()
            consTies=dfBeanpot.loc[eval("(dfBeanpot['consWinner'].str.contains(\"{}\")) & (dfBeanpot['consWinner'].str.contains(','))".format(team)+tQuery)]['year'].count()
            consApp=consWins+consLosses+consTies
            if(consTies>0):
                consLossesStr=str(consLosses)+'-'+str(consTies)
            else:
                consLossesStr=str(consLosses)

            finStr=''
            if(finish in ['champ','title']):
                return "{} Beanpot Titles".format(champWins)
            if(finish in ['1st','first'] or finish==''):
                finStr+='1st {}\n'.format(champWins)
            if(finish in ['2nd','second'] or finish==''):
                finStr+='2nd {}\n'.format(champLosses)
            if(finish in ['3rd','third'] or finish==''):
                finStr+='3rd {}\n'.format(consWins+consTies)
            if(finish in ['4th','fourth','last'] or finish==''):
                finStr+='4th {}\n'.format(consLosses)
            return finStr
    return ''
    
def updateCurrentSeasonStats():
    currSeason='2022-23'
    url = "https://goterriers.com/sports/mens-ice-hockey/stats?path=mhockey"
    f=urllib.request.urlopen(url)
    html = f.read()
    f.close()
    soup = BeautifulSoup(html, 'html.parser')
    head=soup.find('h1')
    if(currSeason not in head):
        pass
    else:
        curSkate=soup.find('section',{'id':'individual-overall-skaters'})
        rows=curSkate.find_all('tr')
        currSkaters=[]
        for i in rows:
            col=i.find_all('td')
            name=i.find('span')
            if(name!=None):
                lastName,firstName=name.get_text().split(', ')
                skateDict={'number':int(col[0].get_text()),
                           'last':lastName,
                           'first':firstName,
                           'name':firstName+' '+lastName,
                            'gp':int(col[1].get_text()),
                            'goals':int(col[2].get_text()),
                            'assists':int(col[3].get_text()),
                            'pts':int(col[4].get_text()),
                            'pen':col[16].get_text().replace('-','/')}
                currSkaters.append(skateDict)
        curSkateDf=pd.DataFrame(currSkaters)



        curGoals=soup.find('section',{'id':'individual-overall-goaltenders'})
        rows=curGoals.find_all('tr')
        currGoalies=[]
        for i in rows:
            col=i.find_all('td')
            name=i.find('span')

            if(name!=None):
                lastName,firstName=name.get_text().split(',')
                goalDict={'number':int(col[0].get_text()),
                           'last':lastName,
                           'first':firstName,
                           'name':firstName+' '+lastName,
                            'gp':int(col[1].get_text().split('-')[0]),
                            'mins':col[2].get_text(),
                            'ga':col[3].get_text(),
                            'gaa':col[4].get_text(),
                            'saves':col[8].get_text(),
                            'sv%':col[9].get_text(),
                            'W':col[10].get_text(),
                            'L':col[11].get_text(),
                            'T':col[12].get_text(),
                            'SO':col[13].get_text()}
                currGoalies.append(goalDict)

        curGoaldf=pd.DataFrame(currGoalies)
    return curSkateDf,curGoaldf