import pandas as pd
import re
import operator
import calendar
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
from datetime import datetime,timedelta

tourneyDict={}
# Get Tourneys
def generateRecordBook():
    global tourneyDict
    fileName=('/home/nmemme/bustatsbot/recordbookdata/BURecordBook.txt')
    tourneys=[]
    with open(fileName, 'r', encoding='utf-8') as f:
        read_data = f.read()
        rows=read_data.split('\n')
        conf='Independent'
        for i in rows:
            row=i.split('\t')
            if(len(row[0])>7 and len(row)==1 and ('COACH' not in i and 'OVERALL' not in i and 'ECAC:' not in i and 'CAPTAIN' not in i and 'HOCKEY' not in i and 'NEIHL:' not in i and 'forfeit' not in i)):
                tourneys.append(row[0])
                
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

    fileName=('/home/nmemme/bustatsbot/recordbookdata/BURecordBook.txt')
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

def generateWomensRecordBook():
    global tourneyDict
    fileName=('/home/nmemme/bustatsbot/recordbookdata/BUWomensRecordBook.txt')
    tourneys=[]
    with open(fileName, 'r', encoding='utf-8') as f:
        read_data = f.read()
        rows=read_data.split('\n')
        conf='Independent'
        for i in rows:
            row=i.split('  ')
            if(len(row)==2):
                tourneyDict[row[0]]=row[1]
      # Get Games
    fileName=('/home/nmemme/bustatsbot/recordbookdata/BUWomensRecordBook.txt')
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
            game=re.search(r"(\d*\/\d*) (\w) (?:\((.?ot)\))? ?(.*) (\w) (#\d*)? ?(\S*|\S* \S*|\S* \S* \S*) ?(\(.*\))? (\d*-\d*)",i)
            if game==None:
                continue
            gameDict={'date':game.group(1),
                     'result':game.group(2),
                     'ot':game.group(3),
                     'arena':game.group(4),
                     'opponent':game.group(7),
                     'gameType':gameType,
                     'tourney': game.group(8),
                     'scoreline':game.group(9),
                     'location':game.group(5),
                     'rank':game.group(6),
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

            if(gameDict['tourney']!=None):
                gameDict['tourney']=tourneyDict[gameDict['tourney'].replace('(','').replace(')','')]
            if((gameDict['tourney'] == gameDict['conference'] +" "+ 'Tournament') or (gameDict['tourney'] == 'NCAA Tournament')):
                gameDict['seasonType'] = 'Playoffs'
            else:
                gameDict['seasonType'] = 'Regular Season'
            if(gameDict['location']=='H'):
                gameDict['location']='Home'
            elif(gameDict['location']=='A'):
                gameDict['location']='Away'
            elif(gameDict['location']=='N'):
                gameDict['location']='Neutral'
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
            gameDict['date']=pd.Timestamp(gameDict['date'])
            gameDict['dow']=gameDict['date'].weekday()
            gameList.append(gameDict)
    f.close()
    dfWomensGames=pd.DataFrame(gameList)
    return dfWomensGames

def convertToInt(val):
        if(val.isdigit()):
            val=int(val)
        else:
            val=None
        return val
        
def convertToIntZ(val):
        if(val.isdigit()):
            val=int(val)
        else:
            val=0
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
    fileName=('/home/nmemme/bustatsbot/recordbookdata/JerseyNumbers.txt')
    playerList=[]
    with open(fileName, 'r', encoding='utf-8') as f:
        read_data = f.read()
        rows=read_data.split('\n')
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


    fileNameW=('/home/nmemme/bustatsbot/recordbookdata/JerseyNumbersWomens.txt')
    playerListW=[]
    with open(fileNameW, 'r', encoding='utf-8') as f:
        read_data = f.read()
        rows=read_data.split('\n')
        numDict={'number':0,'player':'','season':''}
        for i in rows:
            if("Retired - " in i):
                    continue
            playerSearch=re.search("(\d*)\t(.*)\t(.*)",i)
            if playerSearch != None:
                season=playerSearch.group(1)
                numDict={'number':int(playerSearch.group(1)),
                     'season':playerSearch.group(3),
                     'name':playerSearch.group(2)}
                playerListW.append(numDict)
    f.close()
    dfJerseyWomens=pd.DataFrame(playerListW)
    dfJerseyMens=pd.DataFrame(playerList)
    dfJersey=pd.DataFrame(playerList+playerListW)
    return dfJersey,dfJerseyMens,dfJerseyWomens
    
    
def generateSkaters():
    fileName=('/home/nmemme/bustatsbot/recordbookdata/SkaterStats.txt')
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
    fileNameW=('/home/nmemme/bustatsbot/recordbookdata/SkaterStatsWomens.txt')
    skateListW=[]
    with open(fileNameW, 'r', encoding='utf-8') as f:
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
                skateListW.append(skaterDict)
    dfSkate=pd.DataFrame(skateList+skateListW)
    dfSkateMens=pd.DataFrame(skateList)
    dfSkateWomens=pd.DataFrame(skateListW)
    return dfSkate,dfSkateMens,dfSkateWomens

def generateGoalies():
    fileName=('/home/nmemme/bustatsbot/recordbookdata/GoalieStats.txt')
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
    fileName=('/home/nmemme/bustatsbot/recordbookdata/GoalieStatsWomens.txt')
    goalieListW=[]
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
                goalieListW.append(goalieDict)
    dfGoalieWomens=pd.DataFrame(goalieListW)
    dfGoalieMens=pd.DataFrame(goalieList)  
    dfGoalie=pd.DataFrame(goalieList+goalieListW)

    return dfGoalie,dfGoalieMens,dfGoalieWomens

def generateSeasonLeaders():
    fileName=('/home/nmemme/bustatsbot/recordbookdata/SeasonLeaders.txt')
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

    fileNameW=('/home/nmemme/bustatsbot/recordbookdata/SeasonLeadersWomens.txt')
    leadListW=[]
    with open(fileNameW, 'r', encoding='utf-8') as f:
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
                leadListW.append(leadDict)
    f.close()
    dfLeadWomens=pd.DataFrame(leadListW)
    return dfLead,dfLeadWomens

def generateSeasonSkaters():
    fileName=('/home/nmemme/bustatsbot/recordbookdata/SeasonSkaterStats.txt')
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
    seasListW=[]
    fileNameW=('/home/nmemme/bustatsbot/recordbookdata/SeasonSkaterStatsWomens.txt')
    with open(fileNameW, 'r', encoding='utf-8') as f:
        read_data = f.read()
        rows=read_data.split('\n')
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
            seasListW.append(seasDict)
    f.close()
    dfSeasSkateWomens=pd.DataFrame(seasListW)
    dfSeasSkateMens=pd.DataFrame(seasList)
    dfSeasSkate=pd.DataFrame(seasList+seasListW)
    return dfSeasSkate,dfSeasSkateMens,dfSeasSkateWomens
    
def generateSeasonGoalies():    
    fileName=('/home/nmemme/bustatsbot/recordbookdata/SeasonGoalieStats.txt')
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
    fileNameW=('/home/nmemme/bustatsbot/recordbookdata/SeasonGoalieStatsWomens.txt')
    with open(fileNameW, 'r', encoding='utf-8') as f:
        read_data = f.read()
        rows=read_data.split('\n')
        seasGListW=[]
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
            seasGListW.append(seasGDict)
    f.close()
    dfSeasGoalie=pd.DataFrame(seasGList+seasGListW)
    dfSeasGoalieWomens=pd.DataFrame(seasGListW)
    dfSeasGoalieMens=pd.DataFrame(seasGList)
    return dfSeasGoalie,dfSeasGoalieMens,dfSeasGoalieWomens

def generateBeanpotHistory():
    fileName=('/home/nmemme/bustatsbot/recordbookdata/BeanpotHistory.txt')
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

    fileName=('/home/nmemme/bustatsbot/recordbookdata/BeanpotHistoryWomens.txt')
    with open(fileName, 'r', encoding='utf-8') as f:
        read_data = f.read()
        rows=read_data.split('\n')
        beanListW=[]
        for i in rows:
            col=i.split('\t')
            beanDict={  "edition" : int(col[0]),
                        "year" : int(col[1]),
                        "arena" : col[2],
                        "semiDate" : col[3],
                        "note": col[4],
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
                        "semi3Winner" : col[15],
                        "semi3WinnerScore" : convertToIntZ(col[16]),
                        "semi3Loser" : col[17],
                        "semi3LoserScore" : convertToIntZ(col[18]),
                        "champDate" : col[19],
                        "consWinner" : col[20],
                        "consWinnerScore" : convertToIntZ(col[21]),
                        "consLoser" : col[22],
                        "consLoserScore" : convertToIntZ(col[23]),
                        "consOT" : col[24],
                        "champion" : col[25],
                        "championScore" : int(col[26]),
                        "runnerup" : col[27],
                        "runnerupScore" : int(col[28]),
                        "champOT" : col[29]}
            beanDict['semiDate']=beanDict['semiDate'].rstrip(' ').lstrip(' ')
            beanDict['champDate']=beanDict['champDate'].rstrip(' ').lstrip(' ')
            beanDict['semiDate']+='/'+str(beanDict['year'])
            beanDict['champDate']+='/'+str(beanDict['year'])
            beanDict['semiDate']=pd.Timestamp(beanDict['semiDate'])
            beanDict['champDate']=pd.Timestamp(beanDict['champDate'])
            beanDict['semiDOW']=beanDict['semiDate'].weekday()
            beanDict['champDOW']=beanDict['champDate'].weekday()
            beanDict['semi1GD']=beanDict['semi1WinnerScore']-beanDict['semi1LoserScore']
            beanDict['semi2GD']=beanDict['semi2WinnerScore']-beanDict['semi2LoserScore']
            beanDict['consGD']=beanDict['consWinnerScore']-beanDict['consLoserScore']
            beanDict['champGD']=beanDict['championScore']-beanDict['runnerupScore']
            beanListW.append(beanDict)
    f.close()
    dfBeanpotWomens=pd.DataFrame(beanListW)
    return dfBeanpot,dfBeanpotWomens
  
def generateBeanpotAwards():
    fileName=('/home/nmemme/bustatsbot/recordbookdata/BeanpotAwardHistory.txt')
    with open(fileName, 'r', encoding='utf-8') as f:
        read_data = f.read()
        rows=read_data.split('\n')
        awardList=[]
        counter=0
        for i in rows:
            col=i.split('\t')
            awardDict={'year':int(col[0]),
                      'mvpName':col[1],
                      'mvpPos':col[2],
                      'mvpSchool':col[3],
                      'ebName':col[4],
                      'ebSchool':col[5],
                      'ebSaves':col[6],
                      'ebGA':col[7],
                      'ebSV%':col[8],
                      'ebGAA':col[9]}
            awardList.append(awardDict)
    f.close()
    dfBeanpotAwards=pd.DataFrame(awardList)

    fileName=('/home/nmemme/bustatsbot/recordbookdata/BeanpotAwardHistoryWomens.txt')
    with open(fileName, 'r', encoding='utf-8') as f:
        read_data = f.read()
        rows=read_data.split('\n')
        awardListW=[]
        counter=0
        for i in rows:
            col=i.split('\t')
            awardDict={'year':int(col[0]),
                      'mvpName':col[1],
                      'mvpSchool':col[2],
                      'berName':col[3],
                      'berSchool':col[4]}
            awardListW.append(awardDict)
    f.close()
    dfBeanpotAwardsWomens=pd.DataFrame(awardListW)
    
    return dfBeanpotAwards,dfBeanpotAwardsWomens
    
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
    
def determineGender(query):
    query=query.lower()
    wSearch=re.search('(?:^|\s)(wom[a|e]n\S*\s?|female\S*\s?)',query)
    gender=""
    if(wSearch!=None):
        gender='Womens'
        query=query.replace(wSearch.group(1),'')
    mSearch=re.search('(?:^|\s)(m[a|e]n\S*\s?|male\S*\s?)',query)
    if(mSearch!=None):
        gender='Mens'
        query=query.replace(mSearch.group(1),'')
    return query,gender

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
    numStartSearch=re.search("last (\d* )?(?:win|loss|tie)?",query.lstrip())
    numRes=1
    if(numStartSearch!=None):
        query=query.replace('wins','win')
        query=query.replace('losses','loss')
        query=query.replace('ties','tie')
        if(numStartSearch.group(1) !=None):
            query=query.replace(numStartSearch.group(1),'')
            numRes=int(numStartSearch.group(1))
    else:
        numRes=1
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
                queryDict['in']=queryDict['in'].replace('hea tournament','hockey east tournament')
                queryDict['in']=queryDict['in'].replace('he tournament','hockey east tournament')
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
        if(not aDate.isnumeric()):
            aDate=(datetime.strptime(aDate, '%m/%d/%Y')+timedelta(days=1)).strftime('%m/%d/%Y')
        dfQueryList.append("(dfGames['date']>'{}')".format(aDate))
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
            res=(dfResult.loc[(dfResult['result']=='W')].sort_values(sortType,ascending=False)[:numRes])
        elif('tie' in qType and 'GD' not in sortType):
            res=(dfResult.loc[(dfResult['result']=='T')].sort_values(sortType,ascending=False)[:numRes])
        elif('tie' in qType and 'GD' in sortType):
            res=pd.DataFrame()
            return ''
        elif('loss' in qType):
            res=(dfResult.loc[(dfResult['result']=='L')].sort_values(sortType,ascending=False)[:numRes])
        else:
            res=dfResult.sort_values(sortType,ascending=False)[:numRes]
        if(not res.empty):
            resStr=''
            for i in range(len(res)):
                if('Away' in res.iloc[i]['location']):
                    local='at'
                else:
                    local='vs'
                resStr+= "{} {} {} {}".format(datetime.strptime(str(res.iloc[i]['date'])[:10],'%Y-%M-%d').strftime('%M/%d/%Y'),local,res.iloc[i]['opponent'].lstrip(' '),res.iloc[i]['scoreline'].lstrip(' '))
                if(res.iloc[i]['ot'] !=None):
                    resStr+= " " + res.iloc[i]['ot']
                if(res.iloc[i]['tourney'] != None):
                    resStr+=" ("+ res.iloc[i]['tourney'].lstrip(' ') +")"
                resStr+='\n'
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
    nameSearch=re.search('by (\w*) ?(\w*)?',query)
    numQuery=re.search('number (\w* \w*|\w*)',query)
    seasonSearch=re.search('(\w*|\w* \w*)? ?(goal\S*|point\S*|pts|assists|stat\S*|stat line|record|gaa|sv|sv%|save\S*|shut\S*|so)? ?in (\d{4}-\d{2}|\d{4})',query)
    yrSearch=re.search("(\w*|\w* \w*)? ?(goal\S*|point\S*|pts|assists|stat\S*|stat line|record|gaa|sv|sv%|save\S*|shut\S*|so)? ?as (fr|so|jr|junior|senior|sr|gr)",query)
    resStr=''
    if(seasonSearch!=None and numSearch==None):
        season=seasonSearch.group(3)
        if('-' in seasonSearch.group(3)):
            year=int(season[:4])+1
        else:
            year=int(season)
    if(((yrSearch != None and yrSearch.group(1) != None) or (seasonSearch!=None and seasonSearch.group(1) != None)) and 'most' not in query and 'lead' not in query and 'lowest' not in query and 'best' not in query and numSearch==None):
        if(seasonSearch!=None):
            playerName = seasonSearch.group(1)
            dfRes=dfSeasSkate.loc[(dfSeasSkate['year']==year) & (dfSeasSkate['name'].str.contains(playerName,case=False))]
            dfResG=dfSeasGoalie.loc[(dfSeasGoalie['year']==year) & (dfSeasGoalie['name'].str.contains(playerName,case=False))]
        elif(yrSearch != None):
            playerName = yrSearch.group(1)
            if('junior' in yrSearch.group(3)):
                yr='JR'
            elif('senior' in yrSearch.group(3)):
                yr='SR'
            else:
                yr=yrSearch.group(3).upper()
            dfRes=dfSeasSkate.loc[(dfSeasSkate['yr']==yr) & (dfSeasSkate['name'].str.contains(playerName,case=False))]
            dfResG=dfSeasGoalie.loc[(dfSeasGoalie['yr']==yr) & (dfSeasGoalie['name'].str.contains(playerName,case=False))]
 
        resStr=''
        if(dfRes.empty and dfResG.empty):
            return resStr
        if((seasonSearch!=None and seasonSearch.group(2)!=None) or (yrSearch!=None and yrSearch.group(2)!=None)):
            if(seasonSearch!=None and seasonSearch.group(2) != None):
                statType=seasonSearch.group(2)
            elif(yrSearch!=None and yrSearch.group(2) != None):
                statType=yrSearch.group(2)
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
    if('most' in query or 'lead' in query or 'lowest' in query or 'best' in query):
        if(seasonSearch!=None and nameSearch == None):
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
            elif(re.search('sv|sv%|gaa|so|shut\S*',query)):
                gpMin=dfSeasGoalie.loc[dfSeasGoalie['year']==year]['gp'].sum()/len(dfSeasGoalie.loc[dfSeasGoalie['year']==year])
                sortType=True
                if('sv' in query):
                    statType='sv%'
                    sortType=False
                elif('gaa' in query):
                    statType='gaa'
                elif('so' in query or 'shut' in query):
                    statType='SO'
                    sortType=False
                dfRes=dfSeasGoalie.loc[(dfSeasGoalie['year']==year) & (dfSeasGoalie['gp']>gpMin)].sort_values(statType,ascending=sortType)[:1]
                if(not dfRes.empty):
                    return "{}: {}".format(dfRes['name'].to_string(index=False).lstrip(),dfRes[statType].to_string(index=False).lstrip())
                else:
                    return ""
            else:
                return ""
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
        elif(nameSearch!=None and nameSearch.group(1) not in ['fr','so','freshman','sophomore','junior','jr','senior','sr','gr','grad','f','d','forward','dman','d-man','defenseman']):
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
        elif(nameSearch != None and nameSearch.group(1) in ['fr','so','freshman','sophomore','junior','jr','senior','sr','gr','grad','f','d','forward','dman','d-man','defenseman'] and seasonSearch != None):
            yr=''
            if(year<2003):
                return 'Not Available for seasons prior to 2002-03'
            if('freshman' in nameSearch.group(1) or 'freshman' in nameSearch.group(2)):
                yr='FR'
            elif('sophomore' in nameSearch.group(1) or 'sophomore' in nameSearch.group(2)):
                yr='SO'
            elif('junior' in nameSearch.group(1) or 'junior' in nameSearch.group(2)):
                yr='JR'
            elif('senior' in nameSearch.group(1) or 'senior' in nameSearch.group(2)):
                yr='SR'
            elif('grad' in nameSearch.group(1) or 'grad' in nameSearch.group(1)):
                yr='GR'
            elif(len(nameSearch.group(1))==2):
                yr=nameSearch.group(1).upper()
            elif(len(nameSearch.group(2))==2):
                yr=nameSearch.group(2).upper()
            if(yr=='IN'):
                yr=''
            pos=''
            if('forward' == nameSearch.group(1) or 'forward' == nameSearch.group(2)):
                pos='F'
            elif('defenseman' == nameSearch.group(1) or 'dman' == nameSearch.group(1) or 'd-man' == nameSearch.group(2) or 'defenseman' == nameSearch.group(2) or 'dman' == nameSearch.group(2) or 'd-man' == nameSearch.group(2)):
                pos='D'
            elif(len(nameSearch.group(1))==1):
                pos=nameSearch.group(1).upper()
            elif(len(nameSearch.group(2))==1):
                pos=nameSearch.group(2).upper()
            if(pos != 'F' and pos != 'D'):
                dfName=dfSeasSkate.loc[(dfSeasSkate['yr']==yr) & (dfSeasSkate['year']==year)]
            elif(pos != '' and yr !=''):
                dfName=dfSeasSkate.loc[(dfSeasSkate['yr']==yr) & (dfSeasSkate['pos'].str.contains(pos)) & (dfSeasSkate['year']==year)]
            else:
                dfName=dfSeasSkate.loc[(dfSeasSkate['pos'].str.contains(pos)) & (dfSeasSkate['year']==year)]
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
                if(statType!=''):
                    df=dfName.sort_values(statType,ascending=False)[:1]
                    name=df['name'].to_string(index=False).lstrip(' ')
                    stat=df[statType].to_string(index=False).lstrip(' ')
                    if(not df.empty):
                        return "{}: {} {}".format(name,stat,statType)
        elif('by' in query):
            return ""
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
                elif(re.search('sv|sv%|gaa',query)):
                    gpMin=40
                    if('sv' in query):
                        statType='sv%'
                        sortType=False
                    elif('gaa' in query):
                        statType='gaa'
                        sortType=True
                    else:
                        return ""
                    dfRes=dfGoalie.loc[(dfGoalie['gp']>=gpMin)].sort_values(statType,ascending=sortType)[:1]
                    return "{}: {}".format(dfRes['name'].to_string(index=False).lstrip(' '),dfRes[statType].to_string(index=False).lstrip(' '))
                else:
                    return ""
                df=dfSkate.sort_values(statType,ascending=False)[:1]
                name=df['name'].to_string(index=False).lstrip(' ')
                stat=df[statType].to_string(index=False).lstrip(' ')
                if(not df.empty):
                    return "{}: {} {}".format(name,stat,statType) 
            else:
                return ""
    if(numSearch !=None and seasonSearch != None):
        number=int(numSearch.group(1))
        season=seasonSearch.group(3)
        if(not dfJersey.loc[(dfJersey['number']==number) & (dfJersey['season'].str.contains(season))].empty):
            return dfJersey.loc[(dfJersey['number']==number) & (dfJersey['season'].str.contains(season))]['name'].to_string(index=False).lstrip().replace('\n ','\n')
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
                resStr+="{}: {} ({})\n".format(dfRes.iloc[row]['name'].lstrip(),dfRes.iloc[row]['number'],dfRes.iloc[row]['season'])
        return resStr
    if(careerSearch!=None):
        playerName=careerSearch.group(1)
        stat=careerSearch.group(2)
        pStatsLine=dfSkate.loc[dfSkate['name'].str.contains(playerName,case=False)]
        gStatsLine=dfGoalie.loc[dfGoalie['name'].str.contains(playerName,case=False)]
        resStr=''
        if(len(pStatsLine)==1 and pStatsLine['name'].isin(dfSeasSkate['name']).any()):
            if('stat' in stat):
                dfRes=dfSeasSkate.loc[dfSeasSkate['name']==pStatsLine['name'].to_string(index=False).lstrip()]
                resStr="Season  Yr GP G A Pts\n"
                cStats=False
                startYear=dfRes.iloc[0]['year']
                if(startYear==2003 and dfRes.iloc[0]['yr']!='FR'):
                    resStr+="(Season Stats Prior to 2002-03 N/A) \n"
                    cStats=True
                for row in range(len(dfRes)):
                    resStr+="{} {} {} {}-{}-{}\n".format(dfRes.iloc[row]['season'],dfRes.iloc[row]['yr'],dfRes.iloc[row]['gp'],dfRes.iloc[row]['goals'],dfRes.iloc[row]['assists'],dfRes.iloc[row]['pts'])
                if(not cStats):
                    resStr+="----------------------\nCareer     {} {}-{}-{}".format(dfRes.sum()['gp'],dfRes.sum()['goals'],dfRes.sum()['assists'],dfRes.sum()['pts'])
                else:
                    goals=pStatsLine['goals'].to_string(index=False).lstrip()
                    assists=pStatsLine['assists'].to_string(index=False).lstrip()
                    pts=pStatsLine['pts'].to_string(index=False).lstrip()
                    gp=int(float(pStatsLine['gp'].to_string(index=False).lstrip()))
                    resStr+="----------------------\nCareer     {} {}-{}-{}".format(gp,goals,assists,pts)
            elif('goal' in stat):
                dfRes=dfSeasSkate.loc[dfSeasSkate['name']==pStatsLine['name'].to_string(index=False).lstrip()]
                resStr="Season  Yr GP G\n"
                cStats=False
                startYear=dfRes.iloc[0]['year']
                if(startYear==2003 and dfRes.iloc[0]['yr']!='FR'):
                    resStr+="(Season Stats Prior to 2002-03 N/A) \n"
                    cStats=True
                for row in range(len(dfRes)):
                    resStr+="{} {} {} {}\n".format(dfRes.iloc[row]['season'],dfRes.iloc[row]['yr'],dfRes.iloc[row]['gp'],dfRes.iloc[row]['goals'])
                if(not cStats):
                    resStr+="----------------------\nCareer     {} {}".format(dfRes.sum()['gp'],dfRes.sum()['goals'])
                else:
                    goals=pStatsLine['goals'].to_string(index=False).lstrip()
                    gp=int(float(pStatsLine['gp'].to_string(index=False).lstrip()))
                    resStr+="----------------------\nCareer     {} {}".format(gp,goals)
            elif('assist' in stat):
                dfRes=dfSeasSkate.loc[dfSeasSkate['name']==pStatsLine['name'].to_string(index=False).lstrip()]
                resStr="Season  Yr GP A\n"
                cStats=False
                startYear=dfRes.iloc[0]['year']
                if(startYear==2003 and dfRes.iloc[0]['yr']!='FR'):
                    resStr+="(Season Stats Prior to 2002-03 N/A) \n"
                    cStats=True
                for row in range(len(dfRes)):
                    resStr+="{} {} {} {}\n".format(dfRes.iloc[row]['season'],dfRes.iloc[row]['yr'],dfRes.iloc[row]['gp'],dfRes.iloc[row]['assists'])
                if(not cStats):
                    resStr+="----------------------\nCareer     {} {}".format(dfRes.sum()['gp'],dfRes.sum()['assists'])
                else:
                    assists=pStatsLine['assists'].to_string(index=False).lstrip()
                    gp=int(float(pStatsLine['gp'].to_string(index=False).lstrip()))
                    resStr+="----------------------\nCareer     {} {}".format(gp,assists)
            elif('point' in stat or 'pts' in stat):
                dfRes=dfSeasSkate.loc[dfSeasSkate['name']==pStatsLine['name'].to_string(index=False).lstrip()]
                resStr="Season  Yr GP Pts\n"
                cStats=False
                startYear=dfRes.iloc[0]['year']
                if(startYear==2003 and dfRes.iloc[0]['yr']!='FR'):
                    resStr+="(Season Stats Prior to 2002-03 N/A) \n"
                    cStats=True
                for row in range(len(dfRes)):
                    resStr+="{} {} {} {}\n".format(dfRes.iloc[row]['season'],dfRes.iloc[row]['yr'],dfRes.iloc[row]['gp'],dfRes.iloc[row]['pts'])
                if(not cStats):
                    resStr+="----------------------\nCareer     {} {}".format(dfRes.sum()['gp'],dfRes.sum()['pts'])
                else:
                    pts=pStatsLine['pts'].to_string(index=False).lstrip()
                    gp=int(float(pStatsLine['gp'].to_string(index=False).lstrip()))
                    resStr+="----------------------\nCareer     {} {}".format(gp,pts)
            
        elif(len(gStatsLine)==1 and gStatsLine['name'].isin(dfSeasGoalie['name']).any()):
            if('stat' in stat):
                dfRes=dfSeasGoalie.loc[dfSeasGoalie['name']==gStatsLine['name'].to_string(index=False).lstrip()]
                resStr='Season  Yr GP  SV%  GAA SO Record\n'
                cStats=False
                startYear=dfRes.iloc[0]['year']
                if(startYear==2003 and dfRes.iloc[0]['yr']!='FR'):
                    resStr+="(Season Stats Prior to 2002-03 N/A) \n"
                    cStats=True
                for row in range(len(dfRes)):
                    resStr+="{} {} {} {} {} {} {}\n".format(dfRes.iloc[row]['season'],dfRes.iloc[row]['yr'],dfRes.iloc[row]['gp'],dfRes.iloc[row]['sv%'],dfRes.iloc[row]['gaa'],dfRes.iloc[row]['SO'],dfRes.iloc[row]['record'])
                gaa=gStatsLine['gaa'].to_string(index=False).lstrip()
                svper=gStatsLine['sv%'].to_string(index=False).lstrip()
                wins=int(float(gStatsLine['W'].to_string(index=False)))
                loss=int(float(gStatsLine['L'].to_string(index=False)))
                tie=int(float(gStatsLine['T'].to_string(index=False)))
                resStr+="----------------------\nCareer     {} {} {} {} {}-{}-{}".format(dfRes.sum()['gp'],svper,gaa,dfRes.sum()['SO'],wins,loss,tie)
            elif('sv' in stat):
                dfRes=dfSeasGoalie.loc[dfSeasGoalie['name']==gStatsLine['name'].to_string(index=False).lstrip()]
                resStr='Season  Yr GP  SV%\n'
                cStats=False
                startYear=dfRes.iloc[0]['year']
                if(startYear==2003 and dfRes.iloc[0]['yr']!='FR'):
                    resStr+="(Season Stats Prior to 2002-03 N/A) \n"
                    cStats=True
                for row in range(len(dfRes)):
                    resStr+="{} {} {} {}\n".format(dfRes.iloc[row]['season'],dfRes.iloc[row]['yr'],dfRes.iloc[row]['gp'],dfRes.iloc[row]['sv%'])
                svper=gStatsLine['sv%'].to_string(index=False).lstrip()
                resStr+="----------------------\nCareer     {} {}".format(dfRes.sum()['gp'],svper)
            elif('gaa' in stat):
                dfRes=dfSeasGoalie.loc[dfSeasGoalie['name']==gStatsLine['name'].to_string(index=False).lstrip()]
                resStr='Season  Yr GP  GAA\n'
                cStats=False
                startYear=dfRes.iloc[0]['year']
                if(startYear==2003 and dfRes.iloc[0]['yr']!='FR'):
                    resStr+="(Season Stats Prior to 2002-03 N/A) \n"
                    cStats=True
                for row in range(len(dfRes)):
                    resStr+="{} {} {} {}\n".format(dfRes.iloc[row]['season'],dfRes.iloc[row]['yr'],dfRes.iloc[row]['gp'],dfRes.iloc[row]['gaa'])
                gaa=gStatsLine['gaa'].to_string(index=False).lstrip()
                resStr+="----------------------\nCareer     {} {}".format(dfRes.sum()['gp'],gaa)
            elif('record' in stat):
                dfRes=dfSeasGoalie.loc[dfSeasGoalie['name']==gStatsLine['name'].to_string(index=False).lstrip()]
                resStr='Season  Yr GP  Record\n'
                cStats=False
                startYear=dfRes.iloc[0]['year']
                if(startYear==2003 and dfRes.iloc[0]['yr']!='FR'):
                    resStr+="(Season Stats Prior to 2002-03 N/A) \n"
                    cStats=True
                for row in range(len(dfRes)):
                    resStr+="{} {} {} {}\n".format(dfRes.iloc[row]['season'],dfRes.iloc[row]['yr'],dfRes.iloc[row]['gp'],dfRes.iloc[row]['record'])
                wins=int(float(gStatsLine['W'].to_string(index=False)))
                loss=int(float(gStatsLine['L'].to_string(index=False)))
                tie=int(float(gStatsLine['T'].to_string(index=False)))
                resStr+="----------------------\nCareer     {} {}-{}-{}".format(dfRes.sum()['gp'],wins,loss,tie)
            elif('so' in stat or 'shut' in stat):
                dfRes=dfSeasGoalie.loc[dfSeasGoalie['name']==gStatsLine['name'].to_string(index=False).lstrip()]
                resStr='Season  Yr GP  SO\n'
                cStats=False
                startYear=dfRes.iloc[0]['year']
                if(startYear==2003 and dfRes.iloc[0]['yr']!='FR'):
                    resStr+="(Season Stats Prior to 2002-03 N/A) \n"
                    cStats=True
                for row in range(len(dfRes)):
                    resStr+="{} {} {} {}\n".format(dfRes.iloc[row]['season'],dfRes.iloc[row]['yr'],dfRes.iloc[row]['gp'],dfRes.iloc[row]['SO'])
                resStr+="----------------------\nCareer     {} {}".format(dfRes.sum()['gp'],dfRes.sum()['SO'])
        elif(len(pStatsLine)>=1):
            for row in range(len(pStatsLine)):
                resStr+="{}: ".format(pStatsLine.iloc[row]['name'].lstrip())
                goals=pStatsLine.iloc[row]['goals']
                assists=pStatsLine.iloc[row]['assists']
                pts=pStatsLine.iloc[row]['pts']
                if('stats' in stat or 'statline' in stat.replace(' ','')):
                    resStr+=("{}-{}--{}".format(goals,assists,pts))
                elif('goal' in stat):
                    resStr+= str(goals)
                elif('assist' in stat):
                    resStr+= str(assists)
                elif('pts' in stat or 'point' in stat):
                    resStr+= str(pts)
                resStr+="\n"
        elif(len(gStatsLine)>=1):
            for row in range(len(gStatsLine)):
                resStr+="{}: ".format(gStatsLine.iloc[row]['name'])
                gaa=gStatsLine.iloc[row]['gaa']
                svper=gStatsLine.iloc[row]['sv%']
                wins=int(float(gStatsLine.iloc[row]['W']))
                loss=int(float(gStatsLine.iloc[row]['L']))
                tie=int(float(gStatsLine.iloc[row]['T']))
                if('stat' in stat or 'stat line' in stat or 'statline' in stat):
                    resStr+="{}/{}/{}-{}-{}".format(gaa,svper,wins,loss,tie)
                elif('gaa' in stat):
                    resStr+= str(gaa)
                elif('sv' in stat or 'save' in stat):
                    resStr+= str(svper)
                elif('record' in stat):
                    resStr+= "{}-{}-{}".format(wins,loss,tie)
                resStr+="\n"
    return resStr  
    
def getBeanpotStats(dfBean,query):
    dfBeanpot=dfBean['results']
    dfBeanpotAwards=dfBean['awards']
    beanNumSearch=re.search('(\d{4}|\d{1,2})(?:st|nd|rd|th)? beanpot',query)
    typeSearch=re.search('beanpot (semi|consolation|final|championship)?\s?(champ|winner|runner|runner-up|1st|first|2nd|second|third|3rd|fourth|4th|last|result|finish)',query)
    recordSearch=re.search('(bu|boston university|bc|boston college|northeastern|nu|harvard|hu) record in beanpot ?(early|late|semi|cons|final|champ|3rd|third)?(.*(\d))?',query)
    head2headSearch=re.search('(bu|boston university|bc|boston college|northeastern|nu|harvard|hu) record vs (bu|boston university|bc|boston college|northeastern|nu|harvard|hu) in beanpot ?(early|late|semi|cons|final|champ|3rd|third)?(\d)?',query)
    finishSearch=re.search('^(bu|boston university|bc|boston college|northeastern|nu|harvard|hu)? ?beanpot (1st|first|2nd|second|3rd|third|fourth|last|4th|champ|title)? ?(?:place)? ?(finish)?',query)
    timeSearch=re.search('(?:(since|after|before) (\d{4})|(?:between|from) (\d{4}) (?:and|to) (\d{4})|(in) (\d{2,4})s)',query)
    teamFinishYearSearch=re.search('^(bu|boston university|bc|boston college|northeastern|nu|harvard|hu)? ?beanpot finish in (\d{4})',query)
    awardSearch=re.search("(eberly|mvp|most valuable|bert)",query)
    if('semi3Winner' not in dfBeanpot.columns):
        dfBeanpot['semi3Winner']=''
        dfBeanpot['semi3Loser']=''
    tQuery=''
    if(timeSearch!=None):
        timeType=timeSearch.group(1)
        if(timeType==None and timeSearch.group(5)!=None):
            timeType='in'
        elif(timeType==None):
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
        elif(timeType == 'in'):
            if(len(timeSearch.group(6))==2):
                if(int(timeSearch.group(6))>40):
                    decadeStart=int("19"+timeSearch.group(6))
                else:
                    decadeStart=int("20"+timeSearch.group(6))
            else:
                decadeStart=int(timeSearch.group(6))
            tQuery+=' & (dfBeanpot["year"].between({},{}))'.format(decadeStart,decadeStart+9)
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
            semi3Wins=dfBeanpot.loc[eval("(dfBeanpot['semi3Winner']==\"{}\")".format(team)+tQuery)]['year'].count()
            semi3Losses=dfBeanpot.loc[eval("(dfBeanpot['semi3Loser']==\"{}\")".format(team)+tQuery)]['year'].count()
            if(semi3Wins!=0 or semi3Losses!=0):
                recStr+="Semi-Final 3: {}-{}\n".format(semi3Wins,semi3Losses) 
            recStr+='Semi-Finals: {}-{}\n'.format(semi1Wins+semi2Wins+semi3Wins,semi1Losses+semi2Losses+semi3Losses)
        if(qType in ['cons','third','3rd'] or qType == '' ):
            consWins=dfBeanpot.loc[eval("((dfBeanpot['consWinner']==\"{}\") & (dfBeanpot['consGD']!=0))".format(team)+tQuery)]['year'].count()
            consLosses=dfBeanpot.loc[eval("((dfBeanpot['consLoser']==\"{}\") & (dfBeanpot['consGD']!=0))".format(team)+tQuery)]['year'].count()
            consTies=dfBeanpot.loc[eval("((dfBeanpot['consWinner'].str.contains(\"{}\") | (dfBeanpot['consLoser'].str.contains(\"{}\"))) & (dfBeanpot['consGD']==0))".format(team,team)+tQuery)]['year'].count()
            consApp=consWins+consLosses+consTies
            if(consTies>0):
                consLossesStr=str(consLosses)+'-'+str(consTies)
            else:
                consLossesStr=str(consLosses)
            recStr+= "Consolation Game: {}-{} ({} Appearances)\n".format(consWins,consLossesStr,consApp)
        if(qType in ['final','championship','champ'] or qType==''):
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
        finStr=''
        if(qType in ['champ','winner','1st','first'] or qType=='finish'):
            finStr += "Champion: " + dfRes['champion'].to_string(index=False).lstrip(' ') + "\n"
        if(qType in ['runner','2nd','second'] or qType=='finish'):
            finStr += "Runner-Up: " + dfRes['runnerup'].to_string(index=False).lstrip(' ') + "\n"
        if((qType in ['third','3rd','fourth','4th','last'] or qType=='finish') and (dfRes['consGD']>0).bool()):
            if(qType in ['third','3rd'] or qType=='finish'):
                finStr += "3rd Place: " +  dfRes['consWinner'].to_string(index=False).lstrip(' ') + "\n"
            if(qType in ['fourth','4th','last']or qType=='finish'):
                finStr += "4th Place: " + dfRes['consLoser'].to_string(index=False).lstrip(' ') + "\n"
        elif(qType in ['third','3rd','fourth','4th','last'] or qType=='finish') and not (dfRes['consGD']>0).bool():
            if(dfRes['consWinner'].to_string(index=False).lstrip()==""):
                    thirds=list(set(['Boston University','Boston College','Northeastern','Harvard'])-set([dfRes['champion'].to_string(index=False).lstrip()])-set([dfRes['runnerup'].to_string(index=False).lstrip()]))
                    finStr+="No Consolation Game Held: {},{}\n".format(thirds[0],thirds[1])
            else:
                if(qType in ['third','3rd']or qType=='finish'):
                        finStr += "3rd Place: " +  dfRes['consWinner'].to_string(index=False).lstrip(' ') + ',' + dfRes['consLoser'].to_string(index=False).lstrip(' ') + "\n"
                if(qType in ['fourth','4th','last']or qType=='finish'):
                    finStr += "4th Place: None\n"
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
                if('semi3Winner' in dfBeanpot.columns and dfBeanpot.loc[dfBeanpot[numType]==year]['semi3Winner'].to_string(index=False).strip()!=''):
                    beanStr+='\n'
                    for i in ['semi3Winner','semi3WinnerScore','semi3Loser','semi3LoserScore']:
                        beanStr+=dfBeanpot.loc[dfBeanpot[numType]==year][i].to_string(index=False).lstrip(' ')+' '
                    beanStr+='\n'+dfBeanpot.loc[dfBeanpot[numType]==year]['note'].to_string(index=False).lstrip(' ')+' '
            if((typeSearch.group(1)==None or typeSearch.group(1)=='consolation') and dfBeanpot.loc[dfBeanpot[numType]==year]['consWinner'].to_string(index=False).strip()!=''):
                if(typeSearch.group(1)==None):
                    beanStr+='\n\n'
                beanStr+='Consolation Game:\n'
                for i in ['consWinner','consWinnerScore','consLoser','consLoserScore','consOT']:
                    beanStr+=dfBeanpot.loc[dfBeanpot[numType]==year][i].to_string(index=False).lstrip(' ')+' '
            if(typeSearch.group(1)==None or typeSearch.group(1) in ['final','championship']):
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
            semi3Team1Wins=dfBeanpot.loc[eval("(dfBeanpot['semi3Winner']==\"{}\") & (dfBeanpot['semi3Loser']==\"{}\")".format(team1,team2)+tQuery)]['year'].count()
            semi3Team2Wins=dfBeanpot.loc[eval("(dfBeanpot['semi3Winner']==\"{}\") & (dfBeanpot['semi3Loser']==\"{}\")".format(team2,team1)+tQuery)]['year'].count()
            if(semi3Team1Wins!=0 or semi3Team2Wins!=0):
                 h2hStr+="Semi-Final 3: {}-{}\n".format(semi3Team1Wins,semi3Team2Wins) 
            h2hStr+="Semi-Finals (Total): {}-{}\n".format(semi1Team1Wins+semi2Team1Wins+semi3Team1Wins,semi1Team2Wins+semi2Team2Wins+semi3Team2Wins)
        if(qType in ['cons','third','3rd'] or qType==''):
            consTeam1Wins=dfBeanpot.loc[eval("(dfBeanpot['consWinner']==\"{}\") & (dfBeanpot['consLoser']==\"{}\") & (dfBeanpot['consGD']!=0)".format(team1,team2)+tQuery)]['year'].count()
            consTeam2Wins=dfBeanpot.loc[eval("(dfBeanpot['consWinner']==\"{}\") & (dfBeanpot['consLoser']==\"{}\") & (dfBeanpot['consGD']!=0)".format(team2,team1)+tQuery)]['year'].count()
            consTies=dfBeanpot.loc[eval("(((dfBeanpot['consWinner'].str.contains(\"{}\")) & (dfBeanpot['consLoser'].str.contains(\"{}\"))) | (dfBeanpot['consWinner'].str.contains(\"{}\")) & (dfBeanpot['consLoser'].str.contains(\"{}\")))  & (dfBeanpot['consGD']==0)".format(team1,team2,team2,team1) + tQuery)]['year'].count()
            consApp=consTeam1Wins+consTeam2Wins+consTies
            if(consTies>0):
                consLossesStr=str(consTeam2Wins)+'-'+str(consTies)
            else:
                consLossesStr=str(consTeam2Wins)
    
            h2hStr+="Consolation Game: {}-{}\n".format(consTeam1Wins,consLossesStr)
        if(qType in ['final','champ','championship'] or qType==''):
            champWins=dfBeanpot.loc[eval("(dfBeanpot['champion']==\"{}\") & (dfBeanpot['runnerup']==\"{}\")".format(team1,team2)+tQuery)]['year'].count()
            champLosses=dfBeanpot.loc[eval("(dfBeanpot['champion']==\"{}\") & (dfBeanpot['runnerup']==\"{}\")".format(team2,team1)+tQuery)]['year'].count()
            h2hStr+="Championship Game: {}-{}\n".format(champWins,champLosses)
        if(qType==''):
            h2hStr+="Total: {}-{}".format(semi1Team1Wins+semi2Team1Wins+semi3Team1Wins+consTeam1Wins+champWins,semi1Team2Wins+semi2Team2Wins+semi3Team2Wins+consTeam2Wins+champLosses)
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
            if('Brown' in dfBeanpot['champion'].unique()):
                beans['Brown']=[0]
            counter=0
            if(finishSearch.group(2)==None):
                places=['champion','runnerup','consWinner','consLoser']
                header=['1st','2nd','3rd','4th']
                beans={'Boston University':[0,0,0,0],'Boston College':[0,0,0,0],'Northeastern':[0,0,0,0],'Harvard':[0,0,0,0]} 
                if('Brown' in dfBeanpot['champion'].unique()):
                    beans['Brown']=[0,0,0,0]
            else:
                finish=finishSearch.group(2)
                if(finish==None):
                    finish=''
                if(finish in ['champ','title','1st','first']):
                    places=['champion']
                    header=['Titles']
                if(finish in ['2nd','second'] or finish==''):
                    places=['runnerup']
                    header=['Runner-Up']
                if(finish in ['3rd','third'] or finish==''):
                    places=['consWinner']
                    header=['3rd Place Finish']
                if(finish in ['4th','fourth','last'] or finish==''):
                    places=['consLoser']
                    header=['4th Place Finish']
            for place in places:
                if(tQuery==''):
                    rows=(dfBeanpot.groupby([place])[place].count().sort_values(ascending=False).to_string(header=False).split('\n'))
                else:
                    rows=(dfBeanpot.loc[eval(tQuery)].groupby([place])[place].count().sort_values(ascending=False).to_string(header=False).split('\n'))
                for row in rows:
                    i=(list(filter(None,row.split('  '))))
                    if(i[0]=='None' or len(i)==1):
                        continue
                    beans[i[0]][counter]=int(i[1])
                if(place=='consLoser'):
                    if(tQuery==''):
                        tieList=dfBeanpot.loc[(dfBeanpot['consGD']==0) & (dfBeanpot['consWinner']!='')].groupby(['consWinner','consLoser'],as_index=False).count()[['consWinner','consLoser','year']].to_csv(header=False,index=False).split('\n')
                    else:
                        tQuery="& ({})".format(tQuery)
                        tieList=dfBeanpot.loc[eval("(dfBeanpot['consGD']==0) & (dfBeanpot['consWinner']!='')"+tQuery)].groupby(['consWinner','consLoser'],as_index=False).count()[['consWinner','consLoser','year']].to_csv(header=False,index=False).split('\n')
                        if('Empty' not in tieList[0]):
                            for r in tieList:
                                tie=list(filter(None,r.split(',')))
                                if(tie!=[]):
                                  beans[tie[1].strip()][counter-1]+=int(tie[2])
                                  beans[tie[1].strip()][counter]-=int(tie[2])
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
                bSearch=re.search("(Brown\s*(?:0(?:\s*)){1,4}\n)",finStr)
                if(bSearch!=None):
                    finStr=finStr.replace(bSearch.group(1),'')
            return finStr
        if(teamFinishYearSearch != None):
            team=decodeTeam(teamFinishYearSearch.group(1))
            year=int(teamFinishYearSearch.group(2))
            if(year==2021):
                return '2021 Beanpot cancelled due to the COVID-19 pandemic'
            for i in ['champion','runnerup','consWinner','consLoser']:
                if(team in dfBeanpot.loc[dfBeanpot['year']==year][i].to_string(index=False).lstrip(' ')):
                    if(i=='consWinner'):
                        i='3rd Place'
                    elif(i=='consLoser'):
                        i='4th Place'
                    else:
                        i=i.title()
                    return "{} {} {}".format(year,i,team)
                
                
        else:
            team=decodeTeam(finishSearch.group(1))
            finish=finishSearch.group(2)
            if(finish==None):
                finish=''
            champWins=dfBeanpot.loc[eval("(dfBeanpot['champion']==\"{}\")".format(team)+tQuery)]['year'].count()
            champLosses=dfBeanpot.loc[eval("(dfBeanpot['runnerup']==\"{}\")".format(team)+tQuery)]['year'].count()
            consWins=dfBeanpot.loc[eval("(dfBeanpot['consWinner']==\"{}\")".format(team)+tQuery)]['year'].count()
            consLosses=dfBeanpot.loc[eval("(dfBeanpot['consLoser']==\"{}\")".format(team)+tQuery)]['year'].count()
            consTies=dfBeanpot.loc[eval("((dfBeanpot['consWinner'].str.contains(team) | (dfBeanpot['consLoser'].str.contains(team))) & (dfBeanpot['consGD']==0))"+tQuery)]['year'].count()
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
    if(awardSearch != None and beanNumSearch!=None):
        year=int(beanNumSearch.group(1))
        if(len(beanNumSearch.group(1))<=2):
            year=int(dfBeanpot.loc[dfBeanpot['edition']==year]['year'].to_string(index=False))
        if(year==2021):
            return '2021 Beanpot cancelled due to the COVID-19 pandemic'
        dfRes=dfBeanpotAwards.loc[dfBeanpotAwards['year']==year]
        if('ebName' in dfRes.columns and 'eberly' in awardSearch.group(1)):
            if(dfRes['ebName'].any()):
                return('{} ({}) {}/{}'.format(dfRes['ebName'].to_string(index=False).lstrip(' '),dfRes['ebSchool'].to_string(index=False).lstrip(' '),dfRes['ebSV%'].to_string(index=False).lstrip(' '),dfRes['ebGAA'].to_string(index=False).lstrip(' ')))
        elif('mvp' in awardSearch.group(1) or 'most val' in awardSearch.group(1)):
            if(dfRes['mvpName'].any()):
                if('mvpPos' in dfRes.columns):
                    return('{} {} ({})'.format(dfRes['mvpName'].to_string(index=False).lstrip(' '),dfRes['mvpPos'].to_string(index=False).lstrip(' '),dfRes['mvpSchool'].to_string(index=False).lstrip(' ')))
                else:
                    return('{} ({})'.format(dfRes['mvpName'].to_string(index=False).lstrip(' '),dfRes['mvpSchool'].to_string(index=False).lstrip(' ')))
        elif('berName' in dfRes.columns and 'bert' in awardSearch.group(1)):
            if(dfRes['berName'].any()):
                 return('{} ({})'.format(dfRes['berName'].to_string(index=False).lstrip(' '),dfRes['berSchool'].to_string(index=False).lstrip(' ')))
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