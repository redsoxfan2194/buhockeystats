import pandas as pd
import re
import operator
import calendar
# Get Tourneys
def generateRecordBook():
    global tourneyDict
    fileName=('BURecordBook.txt')
    tourneys=[]
    teamSet=set()
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
            if(len(row[0])>7 and len(row)==1 and ('COACH' not in i and 'OVERALL' not in i and 'ECAC:' not in i and 'CAPTAIN' not in i and 'HOCKEY' not in i and 'NEIHL:' not in i and 'forfeit' not in i)):
                tourneys.append(row[0])
                
            coachSearch=re.search("COACH: (.*)",i)
            if coachSearch != None:
                coach=coachSearch.group(1)
            captSearch=re.search("CAPTAIN.?: (.*)",i)
            if captSearch != None:
                capt=captSearch.group(1) 
                #
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
            #
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
            if(gameDict['arena']=='Agganis Arena' or gameDict['arena']=='Brown Arena' or gameDict['arena']=='Boston Arena'):
                gameDict['location']='Home'
            elif(gameDict['tourney']==None or gameDict['tourney']=='(nc)' or gameDict['tourney'] == '(B1G/HE)' or ((gameDict['tourney'] == '(HE)' or gameDict['tourney'] == '(ECAC)') and (gameDict['arena'] != 'TD Garden' and gameDict['arena'] != 'Boston Garden' and gameDict['arena'] != 'Providence CC'))):
                gameDict['location']='Away'
            if(gameDict['location']=='' or gameDict['arena']=='Boston Garden' or gameDict['arena']=='VW Arena'):
                gameDict['location']='Neutral'
            if((gameDict['arena']=='Gutterson' and gameDict['opponent']=='Vermont') or (gameDict['arena']=='Houston' and gameDict['opponent']=='Rensselaer') or (gameDict['arena']=='Broadmoor' and gameDict['opponent']=='Colorado College') or (gameDict['arena']=='DEC Center' and gameDict['opponent']=='Minnesota Duluth')or (gameDict['arena']=='Magness Arena' and gameDict['opponent']=='Denver')or (gameDict['arena']=='Mariucci Arena' and gameDict['opponent']=='Minnesota')or (gameDict['arena']=='Munn Ice Arena' and gameDict['opponent']=='Michigan State')or (gameDict['arena']=='Walker Arena' and gameDict['opponent']=='Clarkson')or (gameDict['arena']=='Thompson Arena' and gameDict['opponent']=='Dartmouth')or (gameDict['arena']=='St. Louis Arena' and gameDict['opponent']=='St. Louis') or (gameDict['arena']=='Sullivan Arena' and gameDict['opponent']=='Alaska Anchorage')):
                gameDict['location']='Away'

            if(gameDict['tourney']!=None):
                #
                gameDict['tourney']=tourneyDict[gameDict['tourney'].replace('(','').replace(')','')]
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
    if(team=='beanpot'):
        team = random.choice(['bu','bc','nu','hu'])
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
        "connecticut" : "UConn",
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
        "icebus" : "UConn",
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
        "slushbus" : "UConn",
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
        "uaf" : "Air Force",
        "uaf" : "Alaska",
        "uah" : "Alabama Huntsville",
        "uconn" : "UConn",
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
    tourneys=[]
    teamSet=set()
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
    tourneys=[]
    teamSet=set()
    skateList=[]
    with open(fileName, 'r', encoding='utf-8') as f:
        read_data = f.read()
        rows=read_data.split('\n')
        number=0
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
    tourneys=[]
    teamSet=set()
    goalieList=[]
    with open(fileName, 'r', encoding='utf-8') as f:
        read_data = f.read()
        rows=read_data.split('\n')
        number=0
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
    
def determineQueryType(query):
    qType=''
    if('record' in query):
        qType='record'
    elif('wins' in query):
        qType='wins'
    elif('loses' in query):
        qType='loses'
    elif('ties' in query):
        qType='ties'
    return qType
    
def tokenizeQuery(query):
    keywords=['vs','at','under','since','after','between','with','before','from','in','on','against']
    keyDict={}
    for i in keywords:
        if(query.find(i+' ')>=0):
            finds=[m.start() for m in re.finditer(i+' ', query)]
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
    for i in range(len(tokens)):
        tokens[i]=tokens[i].rstrip(' ').lstrip(' ')
        keyWordsDict[keyWordList[i]]=tokens[i]
    return keyWordsDict
    
def cleanupQuery(query,qType):
    cleanlist=['the','of',"bu","bu's",'what','is',"what's",'number of','games','game','his','arena','rink']
    for i in cleanlist:
        query=query.replace(i+' ','')
    query=query.replace(qType+' ','')
    return query
    
def getResults(dfGames,query):
    global tourneyDict
    query=query.lower()
    months=[x.lower() for x in list(calendar.month_name)]
    months_short=[x.lower() for x in list(calendar.month_abbr)]
    qType=determineQueryType(query)
    queryDict=tokenizeQuery(cleanupQuery(query,qType))
    numGames=''
    ascen=True
    dfQueryList = []
    if('vs' in queryDict.keys()):
        
        dfQueryList.append("(dfGames['opponent'].str.contains('{}',case=False))".format(decodeTeam(queryDict['vs'])))
    if('against' in queryDict.keys()):
        
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
        if(queryDict['at'].capitalize() in ['Home','Away','Neutral']):
            
            dfQueryList.append("(dfGames['location']==(\"{}\"))".format(queryDict['at']))
        elif(dfGames.loc[(dfGames['opponent']==decodeTeam(queryDict['at']))]['opponent'].count()>0):
            
            dfQueryList.append("(dfGames['opponent'].str.contains('{}',case=False))".format(decodeTeam(queryDict['at'])))
            
            dfQueryList.append("(dfGames['location']=='Away')".format(queryDict['at']))
        else:
            
            dfQueryList.append("(dfGames['arena'].str.contains(\"{}\",case=False))".format(queryDict['at']))
    if('in' in queryDict.keys()):
        digSearch=re.search('\d',queryDict['in'])
        decSearch=re.search('(\d{2,4})s',queryDict['in'])
        if(digSearch==None and not(queryDict['in'] in months) and not(queryDict['in'] in months_short)):
            if('NCAA' in queryDict['in'].upper()):
                queryDict['in']=queryDict['in'].replace('s','')
            if(queryDict['in'].upper() in tourneyDict.keys()):
                queryDict['in']=tourneyDict[queryDict['in'].upper()]
            dfQueryList.append("(dfGames['tourney'].str.contains(\"{}\",case=False))".format(queryDict['in']))
        elif(decSearch!=None):
            if(len(decSearch.group(1))==2):
                if(int(decSearch.group(1))>20):
                    decadeStart=int("19"+decSearch.group(1))
                else:
                    decadeStart=int("20"+decSearch.group(1))
            else:
                decadeStart=int(decSearch.group(1))
            dfQueryList.append("(dfGames['date'].between('{}','{}'))".format(decadeStart,decadeStart+9))
        elif('first' in queryDict['in']):
            numGamesSearch=re.search('first (\d*)',queryDict['in'])
            if(numGamesSearch!=None):
                numGames=int(numGamesSearch.group(1))
        elif('last' in queryDict['in']):
            numGamesSearch=re.search('last (\d*)',queryDict['in'])
            if(numGamesSearch!=None):
                numGames=int(numGamesSearch.group(1))
                ascen=False
        else:
            if(queryDict['in'].isdigit()):
                dfQueryList.append("(dfGames['year']=={})".format(queryDict['in']))
            elif(queryDict['in'] in months):                
                dfQueryList.append("(dfGames['month']=={})".format(months.index(queryDict['in'])))
            elif(queryDict['in'] in months_short):
                dfQueryList.append("(dfGames['month']=={})".format(months_short.index(queryDict['in'])))
                                                         
    if('since' in queryDict.keys()):
        dfQueryList.append("(dfGames['date']>'{}')".format(queryDict['since']))
    if('before' in queryDict.keys()):
        dfQueryList.append("(dfGames['date']<'{}')".format(queryDict['before']))
    if('after' in queryDict.keys()):
        dfQueryList.append("(dfGames['date']>'{}')".format(queryDict['after']))
    if('between' in queryDict.keys()):
        dates=queryDict['between'].split(' and ')
        dfQueryList.append("(dfGames['date'].between('{}','{}'))".format(dates[0],dates[1]))
    if('from' in queryDict.keys()):
        dates=queryDict['from'].split(' to ')
        dfQueryList.append("(dfGames['date'].between('{}','{}'))".format(dates[0],dates[1]))
    dfQuery =''
    for i in dfQueryList:
        dfQuery += i + " & "
    dfQuery=dfQuery[:-2]
    result=''
    dfResult=eval("dfGames.loc[{}].sort_values('date',ascending={})[:{}]".format(dfQuery,ascen,numGames))
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
    elif(qType=='loses'):
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