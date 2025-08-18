''' Module for Generating BU Hockey Record Book Data and Processing it'''
import re
import os
import operator
import calendar
from math import floor
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import numpy as np
from pandas import Timestamp
import pandas as pd

try:
    from burecbookpath import RECBOOK_DATA_PATH
except ImportError:
    RECBOOK_DATA_PATH = './'

currSeason = '2024-25'

tourneyDict = {}
# Get Tourneys

# initialize DataFrames
dfGames = pd.DataFrame()
dfGamesWomens = pd.DataFrame()
dfJersey = pd.DataFrame()
dfJerseyMens = pd.DataFrame()
dfJerseyWomens = pd.DataFrame()
dfPollsMens = pd.DataFrame()
dfPollsWomens = pd.DataFrame()
dfSkate = pd.DataFrame()
dfSkateMens = pd.DataFrame()
dfSkateWomens = pd.DataFrame()
dfGoalie = pd.DataFrame()
dfGoalieMens = pd.DataFrame()
dfGoalieWomens = pd.DataFrame()
dfLead = pd.DataFrame()
dfLeadWomens = pd.DataFrame()
dfBeanpot = pd.DataFrame()
dfBeanpotWomens = pd.DataFrame()
dfSeasSkate = pd.DataFrame()
dfSeasSkateMens = pd.DataFrame()
dfSeasSkateWomens = pd.DataFrame()
dfSeasGoalie = pd.DataFrame()
dfSeasGoalieMens = pd.DataFrame()
dfSeasGoalieWomens = pd.DataFrame()
dfGameStats = pd.DataFrame()
dfGameStatsMens = pd.DataFrame()
dfGameStatsWomens = pd.DataFrame()
dfGameStatsGoalie = pd.DataFrame()
dfGameStatsGoalieMens = pd.DataFrame()
dfGameStatsGoalieWomens = pd.DataFrame()
dfBeanpotAwards = pd.DataFrame()
dfBeanpotAwardsWomens = pd.DataFrame()

def generateRecordBook():
    '''Generate BU Men's Hockey Record Book'''

    # load in conference data
    dfConf = pd.read_csv(RECBOOK_DATA_PATH + 'OpponentConferenceData.csv')
    dfConf['season'] = dfConf['season'].apply(convertSeasons, args=(True,))
    fileName = RECBOOK_DATA_PATH + 'BURecordBook.txt'
    tourneys = []

    # read in record book
    with open(fileName, 'r', encoding='utf-8') as f:
        readData = f.read()
        rows = readData.split('\n')
        conf = 'Independent'
        # loop through record book and find all the tournaments
        for i in rows:
            row = i.split('\t')
            if (len(row[0]) > 7 and len(row) == 1 and (
                    'COACH' not in i and 'OVERALL' not in i and 'ECAC:' not in i and 'CAPTAIN' not in i and 'HOCKEY' not in i and 'NEIHL:' not in i and 'forfeit' not in i)):
                tourneys.append(row[0])

    # create dict for tournament lookup
    for i in tourneys:
        if i == 'Key to Tournaments':
            continue
        tourney = i.split(' ')
        tourneyDict[tourney[0]] = ' '.join(tourney[1:])
    tourneyDict['nc'] = 'Non-Collegiate'
    tourneyDict['Oly nc'] = '1932 NEAAU Olympic tryouts-Non-Collegiate'
    tourneyDict['ex'] = 'Exhibition'
    tourneyDict['HF ex'] = 'Hall of Fame Game-Exhibition'
    tourneyDict['IB ex'] = 'Ice Breaker-Exhibition'

    fileName = RECBOOK_DATA_PATH + 'BURecordBook.txt'
    gameList = []
    with open(fileName, 'r', encoding='utf-8') as f:
        readData = f.read()
        rows = readData.split('\n')
        conf = 'Independent'

        # loop through record book
        for i in rows:

            # row contains the season
            if len(i) == 7:
                season = i

            # find coach if in line
            coachSearch = re.search("COACH: (.*)", i)
            if coachSearch is not None:
                coach = coachSearch.group(1)

            # find captain if in line
            captSearch = re.search("CAPTAIN.?: (.*)", i)
            if captSearch is not None:
                capt = captSearch.group(1)

            # find conference if in line
            confSearch = re.search("(NEIHL|ECAC|HOCKEY EAST):", i)
            if confSearch is not None:
                conf = confSearch.group(1)
                if conf == 'HOCKEY EAST':
                    conf = 'Hockey East'

            # '*' denotes conference games in record book
            if re.search('\\*', i) is not None:
                gameType = 'Conference'
            else:
                gameType = 'Non-Conference'

            # remove '*' to make the lines uniform
            i = i.replace("* ", '')
            note = ''

            # save off the notes and remove the special character
            if '†' in i:
                note = 'Loss by forfeit (ineligible player)'
                i = i.replace('†', '')
            if '+' in i:
                note = 'Win by forfeit (opponent left ice – score was 5-1, BU)'
                i = i.replace('+', '')
            if '‡' in i:
                note = 'Win by forfeit (ineligible player)'
                i = i.replace('‡', '')

            # search for a valid line and separate out the regex
            game = re.search(
                r"(\d*\/\d*) (\w*) (?:\((.?ot)\))? ?(.*)\t(\S*|\S* \S*|\S* \S* \S*) ?(\(.*\))? (\d*-\d*)",
                i)
            if game is None:
                continue
            gameDict = {'date': game.group(1),
                        'result': game.group(2),
                        'ot': game.group(3),
                        'arena': game.group(4),
                        'opponent': game.group(5),
                        'gameType': gameType,
                        'tourney': game.group(6),
                        'scoreline': game.group(7),
                        'location': '',
                        'coach': coach,
                        'captain': capt,
                        'conference': conf,
                        'season': season,
                        'note': note}

            # if not a conference game set as non-conference
            if gameDict['gameType'] is None:
                gameDict['gameType'] = 'Non-Conference'

            # set result of and exhibition as 'E' so it doesn't appear in the
            # record
            if (gameDict['tourney'] == '(ex)' or gameDict['result'] == 'E'):
                gameDict['gameType'] = 'Exhibition'
                gameDict['result'] = 'E'
                gameDict['tourney'] = None

            # determine home games by arena
            if (gameDict['arena'] == 'Agganis Arena' or
                gameDict['arena'] == 'Walter Brown Arena' or
                    gameDict['arena'] == 'Boston Arena'):
                gameDict['location'] = 'Home'

            # anything that isn't a tournament is an away game
            elif (gameDict['tourney'] is None or
                  gameDict['tourney'] == '(nc)' or
                  gameDict['tourney'] == '(B1G/HE)' or
                  ((gameDict['tourney'] == '(HE)' or gameDict['tourney'] == '(ECAC)') and
                  (gameDict['arena'] != 'TD Garden' and gameDict['arena'] != 'Boston Garden' and
                   gameDict['arena'] != 'Providence CC'))):
                gameDict['location'] = 'Away'

            # everything else is neutral
            if (gameDict['location'] == '' or gameDict['arena'] ==
                    'Boston Garden' or gameDict['arena'] == 'VW Arena'):
                gameDict['location'] = 'Neutral'

            # tourney games vs hosts are road games
            if ((gameDict['arena'] == 'Gutterson' and gameDict['opponent'] == 'Vermont') or (
                    gameDict['arena'] == 'Houston' and gameDict['opponent'] == 'Rensselaer') or (
                    gameDict['arena'] == 'Broadmoor' and gameDict['opponent'] == 'Colorado College') or (
                    gameDict['arena'] == 'DEC Center' and gameDict['opponent'] == 'Minnesota Duluth') or (
                    gameDict['arena'] == 'Magness Arena' and gameDict['opponent'] == 'Denver') or (
                    gameDict['arena'] == 'Mariucci Arena' and gameDict['opponent'] == 'Minnesota') or (
                    gameDict['arena'] == 'Munn Ice Arena' and gameDict['opponent'] == 'Michigan State') or (
                    gameDict['arena'] == 'Walker Arena' and gameDict['opponent'] == 'Clarkson') or (
                    gameDict['arena'] == 'Thompson Arena' and gameDict['opponent'] == 'Dartmouth') or (
                    gameDict['arena'] == 'St. Louis Arena' and gameDict['opponent'] == 'St. Louis') or (
                    gameDict['arena'] == 'Sullivan Arena' and gameDict['opponent'] == 'Alaska Anchorage')):
                gameDict['location'] = 'Away'

            # clear parens from tournys
            if gameDict['tourney'] is not None:
                gameDict['tourney'] = tourneyDict[gameDict['tourney'].replace(
                    '(', '').replace(')', '')]

            # conference and ncaa tournament games are playoff games
            if ((gameDict['tourney'] == gameDict['conference'] + " " +
                    'Tournament') or (gameDict['tourney'] == 'NCAA Tournament')):
                gameDict['seasonType'] = 'Playoffs'
            else:
                gameDict['seasonType'] = 'Regular Season'

            # get month and day from date
            gameDict['month'], gameDict['day'] = gameDict['date'].split('/')
            gameDict['month'] = int(gameDict['month'])
            gameDict['day'] = int(gameDict['day'])

            # determine year from season
            if gameDict['month'] >= 9:
                gameDict['date'] += "/" + gameDict['season'][:4]
                gameDict['year'] = int(gameDict['season'][:4])
            elif gameDict['month'] <= 4:
                gameDict['date'] += "/" + str(int(gameDict['season'][:4]) + 1)
                gameDict['year'] = int(gameDict['season'][:4]) + 1

            # get goals scored from scoreline
            gameDict['BUScore'], gameDict['OppoScore'] = int(
                gameDict['scoreline'].split('-')[0]), int(gameDict['scoreline'].split('-')[1])
            gameDict['GD'] = gameDict['BUScore'] - gameDict['OppoScore']

            # set Jack Parker as coach for second half of 73-74 season
            if (gameDict['season'] ==
                    '1973-74' and gameDict['date'] == '12/12/1973'):
                coach = 'Jack Parker'
            gameDict['date'] = pd.Timestamp(gameDict['date'])
            gameDict['dow'] = gameDict['date'].weekday()
            gameList.append(gameDict)

    f.close()
    dfGames = pd.DataFrame(gameList)
    # get conference of all opponents
    dfGames['oppconference'] = dfGames.apply(
        lambda row: getConference(
            dfConf, row['opponent'], row['season']), axis=1)
            
    # get ranking 
    dfGames = pd.merge_asof(
      dfGames, 
      dfPollsMens[['DATE']].drop_duplicates(),
      left_on='date', 
      right_on='DATE', 
      direction='backward',  # Change direction to 'forward'
      tolerance=pd.Timedelta('7 days'))
    
    dfGames['BURank']=100
    dfGames['OppRank']=100
    
    dfGames[['BURank','OppRank']]=dfGames.apply(getMRank,axis=1)
    
    return dfGames

def getMRank(row):
    return getRank(row,'Mens')

def getWRank(row):
    return getRank(row,'Womens')

def getRank(row,gender):
    if(gender=="Mens"):
      dfPolls=dfPollsMens.copy()
    elif(gender=="Womens"):
      dfPolls=dfPollsWomens.copy()
    poll=dfPolls.loc[dfPolls['DATE']==row['DATE']]
    burank=poll.query('TEAM=="Boston University"')['RK']
    opprank=poll.query(f'TEAM=="{row["opponent"]}"')['RK']
    if(burank.empty):
        burank=100
    else:
        burank=int(burank.to_string(index=False,header=False))
    if(opprank.empty):
        opprank=100
    else:
        opprank=int(opprank.to_string(index=False,header=False))
   
    return pd.Series([burank,opprank])
def generateWomensRecordBook():
    '''Generate Womens Hockey Record Book'''

    # load in conference data
    dfConf = pd.read_csv(
        RECBOOK_DATA_PATH +
        'OpponentConferenceDataWomens.csv')
    dfConf['season'] = dfConf['season'].apply(convertSeasons, args=(True,))

    fileName = RECBOOK_DATA_PATH + 'BUWomensRecordBook.txt'
    with open(fileName, 'r', encoding='utf-8') as f:
        readData = f.read()
        rows = readData.split('\n')
        conf = 'Independent'
        # create tourney lookup
        for i in rows:
            row = i.split('  ')
            if len(row) == 2:
                tourneyDict[row[0]] = row[1]
    # Get Games
    fileName = RECBOOK_DATA_PATH + 'BUWomensRecordBook.txt'
    gameList = []
    with open(fileName, 'r', encoding='utf-8') as f:
        readData = f.read()
        rows = readData.split('\n')
        conf = 'Independent'
        for i in rows:
            # row contains season
            if len(i) == 7:
                season = i

            # find coach in row
            coachSearch = re.search("COACH: (.*)", i)
            if coachSearch is not None:
                coach = coachSearch.group(1)

            # find captain in row
            captSearch = re.search("CAPTAIN.?: (.*)", i)
            if captSearch is not None:
                capt = captSearch.group(1)

            # determine conference
            confSearch = re.search("(NEIHL|ECAC|HOCKEY EAST):", i)
            if confSearch is not None:
                conf = confSearch.group(1)
                if conf == 'HOCKEY EAST':
                    conf = 'Hockey East'

            # '*' indicates conference games
            if re.search('\\*', i) is not None:
                gameType = 'Conference'
            else:
                gameType = 'Non-Conference'

            # remove '*' since its no longer needed
            i = i.replace("* ", '')
            note = ''
            if '†' in i:
                note = 'Loss by forfeit (ineligible player)'
                i = i.replace('†', '')
            if '+' in i:
                note = 'Win by forfeit (opponent left ice – score was 5-1, BU)'
                i = i.replace('+', '')
            if '‡' in i:
                note = 'Win by forfeit (ineligible player)'
                i = i.replace('‡', '')

            # separate out record book line using regex
            game = re.search(
                r"(\d*\/\d*) (\w) (?:\((.?ot)\))? ?(.*) (\w) (#\d*)? ?(\S*|\S* \S*|\S* \S* \S*) ?(\(.*\))? (\d*-\d*)", i)
            if game is None:
                continue
            gameDict = {'date': game.group(1),
                        'result': game.group(2),
                        'ot': game.group(3),
                        'arena': game.group(4),
                        'opponent': game.group(7),
                        'gameType': gameType,
                        'tourney': game.group(8),
                        'scoreline': game.group(9),
                        'location': game.group(5),
                        'rank': game.group(6),
                        'coach': coach,
                        'captain': capt,
                        'conference': conf,
                        'season': season,
                        'note': note}
            if gameDict['gameType'] is None:
                gameDict['gameType'] = 'Non-Conference'
            if (gameDict['tourney'] == '(ex)' or gameDict['result'] == 'E'):
                gameDict['gameType'] = 'Exhibition'
                gameDict['result'] = 'E'
                gameDict['tourney'] = None

            if gameDict['tourney'] is not None:
                gameDict['tourney'] = tourneyDict[gameDict['tourney'].replace(
                    '(', '').replace(')', '')]
            if ((gameDict['tourney'] == gameDict['conference'] + " " +
                    'Tournament') or (gameDict['tourney'] == 'NCAA Tournament')):
                gameDict['seasonType'] = 'Playoffs'
            else:
                gameDict['seasonType'] = 'Regular Season'

            # home/away/neutral is in dict expand it out
            if gameDict['location'] == 'H':
                gameDict['location'] = 'Home'
            elif gameDict['location'] == 'A':
                gameDict['location'] = 'Away'
            elif gameDict['location'] == 'N':
                gameDict['location'] = 'Neutral'
            gameDict['month'], gameDict['day'] = gameDict['date'].split('/')
            gameDict['month'] = int(gameDict['month'])
            gameDict['day'] = int(gameDict['day'])

            # determine year by season
            if gameDict['month'] >= 9:
                gameDict['date'] += "/" + gameDict['season'][:4]
                gameDict['year'] = int(gameDict['season'][:4])
            elif gameDict['month'] <= 4:
                gameDict['date'] += "/" + str(int(gameDict['season'][:4]) + 1)
                gameDict['year'] = int(gameDict['season'][:4]) + 1

            # separate goals scored from scoreline
            gameDict['BUScore'], gameDict['OppoScore'] = int(
                gameDict['scoreline'].split('-')[0]), int(gameDict['scoreline'].split('-')[1])
            gameDict['GD'] = gameDict['BUScore'] - gameDict['OppoScore']
            gameDict['date'] = pd.Timestamp(gameDict['date'])
            gameDict['dow'] = gameDict['date'].weekday()
            gameList.append(gameDict)

    f.close()
    dfWomensGames = pd.DataFrame(gameList)

    # set conference for opponents
    dfWomensGames['oppconference'] = dfWomensGames.apply(
        lambda row: getConference(dfConf, row['opponent'], row['season']), axis=1)
        
    # get ranking 
    dfWomensGames = pd.merge_asof(
    dfWomensGames, 
    dfPollsWomens[['DATE']].drop_duplicates(),
    left_on='date', 
    right_on='DATE', 
    direction='backward',  # Change direction to 'forward'
    tolerance=pd.Timedelta('7 days'))
    
    dfWomensGames['BURank']=np.nan
    dfWomensGames['OppRank']=np.nan
    dfWomensGames[['BURank','OppRank']]=dfWomensGames.apply(getWRank,axis=1)
    
    return dfWomensGames


def convertToInt(val):
    '''check str is int if it isn't make it none'''
    if val.isdigit():
        val = int(val)
    else:
        val = None
    return val


def convertToIntZ(val):
    '''check if str is int if it isn't make it 0'''
    if val.isdigit():
        val = int(val)
    else:
        val = 0
    return val


def convertToFloat(val):
    '''try to make str a float if can't make it nan'''
    try:
        val = float(val)
    except BaseException:
        val = float('nan')
    return val


def convertSeasons(season, isConf=False, strip=True):
    '''convert range of seasons to a list of seasons expanded'''
    if season == '':
        return ''
    gap = season.split(',')
    years = season[2:].split('-')
    seasonStr = ''
    # determine if the span encompasses more than one season
    # if it does, expand it out
    if len(gap) > 1:
        for i in gap:
            seasonStr += convertSeasons(i, isConf, False)
    else:
        # check if year crosses a millennium
        yearDiff = abs(int(years[0]) - int(years[1]))
        if (yearDiff > 6 and not isConf):
            # if it does figure out the real diff
            yearDiff = 100 - yearDiff
        if isConf:
            if int(years[1]) < int(years[0]):
                yearDiff = abs(int("19" + years[0]) - int("20" + years[1]))
            else:
                yearDiff = abs(int(years[0]) - int(years[1]))
        firstHalf = season[:4]
        seasonStr = ''
        # loop through until and make the list of seasons
        for i in range(yearDiff):
            secondHalf = int(firstHalf) + 1
            seasonStr += str(firstHalf) + '-' + str(secondHalf)[2:] + ','
            firstHalf = secondHalf
    if not strip:
        return seasonStr
    return seasonStr[:-1]


def getConference(dfConf, team, season):
    '''look up a teams conference in specified season'''
    dfConf = dfConf.copy()
    conf = dfConf.loc[(dfConf['opponent'] == team) & (
        dfConf['season'].str.contains(season))]['OppoConference']
    if conf.empty:
        return ''
    return conf.to_string(index=False)


def decodeTeam(team):
    '''create short form look up for teams'''
    origTeam = team
    team = team.lower()
    team = team.replace(" ", "")
    team = team.replace("-", "")
    team = team.replace("'", "")
    team = team.replace(".", "")
    teamDict = {"afa": "Air Force",
            "aic": "American International",
            "alabamahuntsville": "Alabama Huntsville",
            "americanintl": "American International",
            "au": "Augustana",
            "amworst": "Massachusetts",
            "amwurst": "Massachusetts",
            "anosu": "Ohio State",
            "army": "Army",
            "asu": "Arizona State",
            "bama": "Alabama Huntsville",
            "bc": "Boston College",
            "bemidji": "Bemidji State",
            "bgsu": "Bowling Green",
            "bigred": "Cornell",
            "bobbymo": "Robert Morris",
            "boston": "Boston University",
            "bostonu": "Boston University",
            "bowlinggreenstate": "Bowling Green",
            "bruno": "Brown",
            "bu": "Boston University",
            "cambridgewarcriminalfactory": "Harvard",
            "cc": "Colorado College",
            "cgate": "Colgate",
            "gate": "Colgate",
            "chestnuthillcommunitycollege": "Boston College",
            "chestnuthilluniversity": "Boston College",
            "clarky": "Clarkson",
            "cct": "Clarkson",
            "cor": "Cornell",
            "cuse": "Syracuse",
            "darty": "Dartmouth",
            "du": "Denver",
            "duluth": "Minnesota Duluth",
            "dutchpeople": "Union",
            "ferris": "Ferris State",
            "ferriswheel": "Ferris State",
            "finghawks": "North Dakota",
            "goofers": "Minnesota",
            "hc": "Holy Cross",
            "hu": "Harvard",
            "howlinhuskies": "Northeastern",
            "huntsville": "Alabama Huntsville",
            "icebus": "Connecticut",
            "keggy": "Dartmouth",
            "lakestate": "Lake Superior State",
            "lakesuperior": "Lake Superior State",
            "lowell": "UMass Lowell",
            "lowelltech": "UMass Lowell",
            "ulowell": "Umass Lowell",
            "lssu": "Lake Superior State",
            "lu": "Lindenwood",
            "liu": "Long Island University",
            "mack": "Merrimack",
            "mankato": "Minnesota State",
            "mc": "Merrimack",
            "mich": "Michigan",
            "meatchicken": "Michigan",
            "mnsu": "Minnesota State",
            "mrbee": "American International",
            "msu": "Michigan State",
            "mtu": "Michigan Tech",
            "nd": "Notre Dame",
            "nebraskaomaha": "Omaha",
            "neu": "Northeastern",
            "newtonsundayschool": "Boston College",
            "newhavenwarcriminalfactory": "Yale",
            "nmu": "Northern Michigan",
            "northern": "Northern Michigan",
            "nodak": "North Dakota",
            "nu": "Northeastern",
            "osu": "Ohio State",
            "pc": "Providence",
            "pianohuskies": "Michigan Tech",
            "prinny": "Princeton",
            "psu": "Penn State",
            "purplecows": "Minnesota State",
            "qu": "Quinnipiac",
            "quinny": "Quinnipiac",
            "quinni": "Quinnipiac",
            "rmu": "Robert Morris",
            "rpi": "Rensselaer",
            "rit": "RIT",
            "saintas": "Saint Anselm",
            "scsu": "St. Cloud State",
            "shu": "Sacred Heart",
            "slu": "St. Lawrence",
            "slushbus": "Connecticut",
            "smc": "Saint Michael's",
            "sparky": "Arizona State",
            "sparty": "Michigan State",
            "stanselm": "Saint Anselm",
            "stcloud": "St. Cloud State",
            "stmichaels": "Saint Michael's",
            "stmikes": "Saint Michael's",
            "stthomas": "St. Thomas",
            "ust": "St. Thomas",
            "sootech": "Lake Superior State",
            "su": "Syracuse",
            "syracuse": "Syracuse",
            "toothpaste": "Colgate",
            "uaa": "Alaska Anchorage",
            "uaf": "Alaska",
            "uah": "Alabama Huntsville",
            "uconn": "Connecticut",
            "umass": "Massachusetts",
            "uma": "Massachusetts",
            "umassamherst": "Massachusetts",
            "umasslowell": "UMass Lowell",
            "umd": "Minnesota Duluth",
            "uml": "UMass Lowell",
            "umo": "Maine",
            "umaine": "Maine",
            "umtc": "Minnesota",
            "umn": "Minnesota",
            "und": "North Dakota",
            "unh": "New Hampshire",
            "uno": "Omaha",
            "usma": "Army West Point",
            "uvm": "Vermont",
            "uw": "Wisconsin",
            "wisco": "Wisconsin",
            "wmu": "Western Michigan",
            "ziggy": "Bowling Green",
            "zoomass": "Massachusetts"}

    if team in teamDict:
        return teamDict[team]
    teamName = ''
    teamSplit = origTeam.split(' ')
    for i in range(len(teamSplit)):
        teamName += teamSplit[i].capitalize()
        if i < len(teamSplit) - 1:
            teamName += ' '
    return teamName


def generateJerseys():
    '''create data frame containing uniform numbers for men's and women's
     players'''
    fileName = RECBOOK_DATA_PATH + 'JerseyNumbers.txt'
    playerList = []
    with open(fileName, 'r', encoding='utf-8') as f:
        readData = f.read()
        rows = readData.split('\n')
        numDict = {'number': 0, 'player': '', 'season': ''}
        for i in rows:
            # determine if row contains a number if it does save it off
            numSearch = re.search("#(.*)", i)
            if numSearch is not None:
                number = numSearch.group(1)
            if "Retired - " in i:
                continue
            # determine which year each player wore said number
            playerSearch = re.search("(\\d*-\\d*) (.*)", i)
            if playerSearch is not None:
                season = playerSearch.group(1)
                numDict = {'number': int(number),
                           'season': convertSeasons(season),
                           'name': playerSearch.group(2)}
                playerList.append(numDict)
    f.close()

    fileNameW = RECBOOK_DATA_PATH + 'JerseyNumbersWomens.txt'
    playerListW = []
    with open(fileNameW, 'r', encoding='utf-8') as f:
        readData = f.read()
        rows = readData.split('\n')
        numDict = {'number': 0, 'player': '', 'season': ''}
        for i in rows:
            if "Retired - " in i:
                continue
            # determine which year each player wore said number
            playerSearch = re.search("(\\d*)\t(.*)\t(.*)", i)
            if playerSearch is not None:
                season = playerSearch.group(1)
                numDict = {'number': int(playerSearch.group(1)),
                           'season': playerSearch.group(3),
                           'name': playerSearch.group(2)}
                playerListW.append(numDict)
    f.close()
    dfJerseyWomens = pd.DataFrame(playerListW)
    dfJerseyMens = pd.DataFrame(playerList)
    dfJersey = pd.DataFrame(playerList + playerListW)
    return dfJersey, dfJerseyMens, dfJerseyWomens


def generateSkaters():
    '''create DataFrame containing career stats for skaters'''
    fileName = RECBOOK_DATA_PATH + 'SkaterStats.txt'
    skateList = []
    with open(fileName, 'r', encoding='utf-8') as f:
        readData = f.read()
        rows = readData.split('\n')
        for i in rows:
            # loop through and use regex to determine career stats
            skaterSearch = re.search(
                '(.*),(.*) (\\S*) (\\S*) (\\S*) (\\S*) (\\S*) (\\S*)\\/(\\S*)', i)
            if skaterSearch is not None:
                skaterDict = {
                    'last': skaterSearch.group(1),
                    'first': skaterSearch.group(2),
                    'name': skaterSearch.group(2) + ' ' + skaterSearch.group(1),
                    'career': skaterSearch.group(3),
                    'seasons': convertSeasons(
                        skaterSearch.group(3)),
                    'gp': convertToInt(
                        skaterSearch.group(4)),
                    'goals': convertToInt(
                        skaterSearch.group(5)),
                    'assists': convertToInt(
                        skaterSearch.group(6)),
                    'pts': convertToInt(
                        skaterSearch.group(7)),
                    'pens': convertToInt(
                        skaterSearch.group(8)),
                    'pim': convertToInt(
                        skaterSearch.group(9))}
                skateList.append(skaterDict)

    fileNameW = RECBOOK_DATA_PATH + 'SkaterStatsWomens.txt'
    skateListW = []
    with open(fileNameW, 'r', encoding='utf-8') as f:
        readData = f.read()
        rows = readData.split('\n')
        for i in rows:
            # loop through and use regex to determine career stats
            skaterSearch = re.search(
                '(.*),(.*) (\\S*) (\\S*) (\\S*) (\\S*) (\\S*) (\\S*)\\/(\\S*)', i)
            if skaterSearch is not None:
                skaterDict = {
                    'last': skaterSearch.group(1),
                    'first': skaterSearch.group(2),
                    'name': skaterSearch.group(2) + ' ' + skaterSearch.group(1),
                    'career': skaterSearch.group(3),
                    'seasons': convertSeasons(
                        skaterSearch.group(3)),
                    'gp': convertToInt(
                        skaterSearch.group(4)),
                    'goals': convertToInt(
                        skaterSearch.group(5)),
                    'assists': convertToInt(
                        skaterSearch.group(6)),
                    'pts': convertToInt(
                        skaterSearch.group(7)),
                    'pens': convertToInt(
                        skaterSearch.group(8)),
                    'pim': convertToInt(
                        skaterSearch.group(9))}
                skateListW.append(skaterDict)
    dfSkate = pd.DataFrame(skateList + skateListW)
    dfSkateMens = pd.DataFrame(skateList)
    dfSkateWomens = pd.DataFrame(skateListW)
    return dfSkate, dfSkateMens, dfSkateWomens


def generateGoalies():
    '''create DataFrame containing career stats for goalies'''
    fileName = RECBOOK_DATA_PATH + 'GoalieStats.txt'
    goalieList = []
    with open(fileName, 'r', encoding='utf-8') as f:
        readData = f.read()
        rows = readData.split('\n')
        for i in rows:
            # loop through and use regex to determine career stats
            goalieSearch = re.search(
                '(.*),(.*) (\\S*) (\\S*) (\\S*) (\\S*) (\\S*) (\\S*) (\\S*) (\\S*) (\\S*) (\\S*)', i)
            if goalieSearch is not None:
                mins = goalieSearch.group(5).split(':')
                if len(mins) > 1:
                    time = "{}:{}".format(
                        *divmod(int(mins[0]), 60)) + ":" + mins[1]
                    time = pd.to_timedelta(time)
                else:
                    time = float('nan')
                goalieDict = {
                    'last': goalieSearch.group(1),
                    'first': goalieSearch.group(2),
                    'name': goalieSearch.group(2) + ' ' + goalieSearch.group(1),
                    'career': goalieSearch.group(3),
                    'seasons': convertSeasons(
                        goalieSearch.group(3)),
                    'gp': convertToInt(
                        goalieSearch.group(4)),
                    'mins': round(
                        pd.Timedelta(time).total_seconds() / 60,
                        2),
                    'ga': convertToInt(
                        goalieSearch.group(6)),
                    'gaa': convertToFloat(
                        goalieSearch.group(7)),
                    'saves': convertToInt(
                        goalieSearch.group(8)),
                    'sv%': convertToFloat(
                        goalieSearch.group(9)),
                    'W': convertToInt(
                        goalieSearch.group(10)),
                    'L': convertToInt(
                        goalieSearch.group(11)),
                    'T': convertToInt(
                        goalieSearch.group(12))}
                goalieList.append(goalieDict)

    fileName = RECBOOK_DATA_PATH + 'GoalieStatsWomens.txt'
    goalieListW = []
    with open(fileName, 'r', encoding='utf-8') as f:
        readData = f.read()
        rows = readData.split('\n')
        for i in rows:
            # loop through and use regex to determine career stats
            goalieSearch = re.search(
                '(.*),(.*) (\\S*) (\\S*) (\\S*) (\\S*) (\\S*) (\\S*) (\\S*) (\\S*) (\\S*) (\\S*)', i)
            if goalieSearch is not None:
                mins = goalieSearch.group(5).split(':')
                if len(mins) > 1:
                    time = "{}:{}".format(
                        *divmod(int(mins[0]), 60)) + ":" + mins[1]
                    time = pd.to_timedelta(time)
                else:
                    time = float('nan')
                goalieDict = {
                    'last': goalieSearch.group(1),
                    'first': goalieSearch.group(2),
                    'name': goalieSearch.group(2) + ' ' + goalieSearch.group(1),
                    'career': goalieSearch.group(3),
                    'seasons': convertSeasons(
                        goalieSearch.group(3)),
                    'gp': convertToInt(
                        goalieSearch.group(4)),
                    'mins': round(
                        pd.Timedelta(time).total_seconds() / 60,
                        2),
                    'ga': convertToInt(
                        goalieSearch.group(6)),
                    'gaa': convertToFloat(
                        goalieSearch.group(7)),
                    'saves': convertToInt(
                        goalieSearch.group(8)),
                    'sv%': convertToFloat(
                        goalieSearch.group(9)),
                    'W': convertToInt(
                        goalieSearch.group(10)),
                    'L': convertToInt(
                        goalieSearch.group(11)),
                    'T': convertToInt(
                        goalieSearch.group(12))}
                goalieListW.append(goalieDict)
    dfGoalieWomens = pd.DataFrame(goalieListW)
    dfGoalieMens = pd.DataFrame(goalieList)
    dfGoalie = pd.DataFrame(goalieList + goalieListW)

    return dfGoalie, dfGoalieMens, dfGoalieWomens


def generateSeasonLeaders():
    '''create DataFrame containing the season stats leaders for skaters'''
    fileName = RECBOOK_DATA_PATH + 'SeasonLeaders.txt'
    leadList = []
    with open(fileName, 'r', encoding='utf-8') as f:
        readData = f.read()
        rows = readData.split('\n')
        for i in rows:
            leadSearch = re.search(
                '(\\d{4}-\\d{2}) (\\d*) (.*) (\\d*) (.*) (\\d*) (.*)', i)
            if leadSearch is not None:
                leadDict = {'season': leadSearch.group(1),
                            'year': int(leadSearch.group(1)[:4]) + 1,
                            'goals': convertToInt(leadSearch.group(2)),
                            'gname': leadSearch.group(3),
                            'assists': convertToInt(leadSearch.group(4)),
                            'aname': leadSearch.group(5),
                            'pts': convertToInt(leadSearch.group(6)),
                            'pname': leadSearch.group(7)}
                leadList.append(leadDict)
    f.close()
    dfLead = pd.DataFrame(leadList)

    fileNameW = RECBOOK_DATA_PATH + 'SeasonLeadersWomens.txt'
    leadListW = []
    with open(fileNameW, 'r', encoding='utf-8') as f:
        readData = f.read()
        rows = readData.split('\n')
        for i in rows:
            leadSearch = re.search(
                '(\\d{4}-\\d{2}) (\\d*) (.*) (\\d*) (.*) (\\d*) (.*)', i)
            if leadSearch is not None:
                leadDict = {'season': leadSearch.group(1),
                            'year': int(leadSearch.group(1)[:4]) + 1,
                            'goals': convertToInt(leadSearch.group(2)),
                            'gname': leadSearch.group(3),
                            'assists': convertToInt(leadSearch.group(4)),
                            'aname': leadSearch.group(5),
                            'pts': convertToInt(leadSearch.group(6)),
                            'pname': leadSearch.group(7)}
                leadListW.append(leadDict)
    f.close()
    dfLeadWomens = pd.DataFrame(leadListW)
    return dfLead, dfLeadWomens


def generateSeasonSkaters():
    '''create DataFrame containing the season stats for skaters from 2002-03 on'''
    fileName = RECBOOK_DATA_PATH + 'SeasonSkaterStats.txt'
    with open(fileName, 'r', encoding='utf-8') as f:
        readData = f.read()
        rows = readData.split('\n')
        seasList = []
        for i in rows:
            col = i.split('\t')
            seasDict = {'number': convertToInt(col[0]),
                        'name': col[1],
                        'pos': col[2],
                        'yr': col[3],
                        'gp': convertToInt(col[4]),
                        'goals': convertToInt(col[5]),
                        'assists': convertToInt(col[6]),
                        'pts': convertToInt(col[7]),
                        'pens': col[8],
                        'season': col[9],
                        'year': int(col[9][:4]) + 1}
            seasList.append(seasDict)
    f.close()

    # create DataFrame containing the season stats for all skaters
    seasListW = []
    fileNameW = RECBOOK_DATA_PATH + 'SeasonSkaterStatsWomens.txt'
    with open(fileNameW, 'r', encoding='utf-8') as f:
        readData = f.read()
        rows = readData.split('\n')
        for i in rows:
            col = i.split('\t')
            seasDict = {'number': int(col[0]),
                        'name': col[1],
                        'pos': col[2],
                        'yr': col[3],
                        'gp': int(col[4]),
                        'goals': int(col[5]),
                        'assists': int(col[6]),
                        'pts': int(col[7]),
                        'pens': col[8],
                        'season': col[9],
                        'year': int(col[9][:4]) + 1}
            seasListW.append(seasDict)
    f.close()
    dfSeasSkateWomens = pd.DataFrame(seasListW)
    dfSeasSkateMens = pd.DataFrame(seasList)
    dfSeasSkate = pd.DataFrame(seasList + seasListW)
    return dfSeasSkate, dfSeasSkateMens, dfSeasSkateWomens


def generateSeasonGoalies():
    '''create DataFrame containing the season stats for goalies from 2002-03 on'''
    fileName = RECBOOK_DATA_PATH + 'SeasonGoalieStats.txt'
    with open(fileName, 'r', encoding='utf-8') as f:
        readData = f.read()
        rows = readData.split('\n')
        seasGList = []
        for i in rows:
            col = i.split('\t')
            seasGDict = {'number': convertToInt(col[0]),
                         'name': col[1],
                         'yr': col[2],
                         'gp': convertToInt(col[3]),
                         'mins': col[4],
                         'ga': convertToInt(col[5]),
                         'saves': convertToInt(col[6]),
                         'sv%': convertToFloat(col[7]),
                         'gaa': convertToFloat(col[8]),
                         'record': col[9],
                         'SO': convertToInt(col[10]),
                         'season': col[11],
                         'year': int(col[11][:4]) + 1}
            if ":" in seasGDict['mins']:
                mins = seasGDict['mins'].split(':')
                seasGDict['min'] = round(int(mins[0]) + int(mins[1]) / 60, 3)
            elif seasGDict['mins'] == '':
                seasGDict['min'] = np.nan
            else:
                seasGDict['min'] = convertToFloat(seasGDict['mins'])
            seasGList.append(seasGDict)
    f.close()

    # create DataFrame containing the season stats for all goalies
    fileNameW = RECBOOK_DATA_PATH + 'SeasonGoalieStatsWomens.txt'
    with open(fileNameW, 'r', encoding='utf-8') as f:
        readData = f.read()
        rows = readData.split('\n')
        seasGListW = []
        for i in rows:
            col = i.split('\t')
            seasGDict = {'number': int(col[0]),
                         'name': col[1],
                         'yr': col[2],
                         'gp': int(col[3]),
                         'mins': col[4],
                         'ga': int(col[5]),
                         'saves': int(col[6]),
                         'sv%': float(col[7]),
                         'gaa': float(col[8]),
                         'record': col[9],
                         'SO': int(col[10]),
                         'season': col[11],
                         'year': int(col[11][:4]) + 1}
            if ":" in seasGDict['mins']:
                mins = seasGDict['mins'].split(':')
                seasGDict['min'] = round(int(mins[0]) + int(mins[1]) / 60, 3)
            elif seasGDict['mins'] == '':
                seasGDict['min'] = np.nan
            else:
                seasGDict['min'] = convertToFloat(seasGDict['mins'])
            seasGListW.append(seasGDict)
    f.close()
    dfSeasGoalie = pd.DataFrame(seasGList + seasGListW)
    dfSeasGoalieWomens = pd.DataFrame(seasGListW)
    dfSeasGoalieMens = pd.DataFrame(seasGList)
    return dfSeasGoalie, dfSeasGoalieMens, dfSeasGoalieWomens


def generateBeanpotHistory():
    '''create DataFrame containing all Beanpot Results'''
    fileName = RECBOOK_DATA_PATH + 'BeanpotHistory.txt'
    with open(fileName, 'r', encoding='utf-8') as f:
        readData = f.read()
        rows = readData.split('\n')
        beanList = []
        for i in rows:
            col = i.split('\t')
            if col[3] != '':
                beanDict = {"edition": int(col[0]),
                            "year": int(col[1]),
                            "arena": col[2],
                            "semiDate": col[3],
                            "semiAttend": int(col[4]),
                            "semi1Winner": col[5],
                            "semi1WinnerScore": int(col[6]),
                            "semi1Loser": col[7],
                            "semi1LoserScore": int(col[8]),
                            "semi1OT": col[9],
                            "semi2Winner": col[10],
                            "semi2WinnerScore": int(col[11]),
                            "semi2Loser": col[12],
                            "semi2LoserScore": int(col[13]),
                            "semi2OT": col[14],
                            "champDate": col[15],
                            "champAttend": int(col[16]),
                            "consWinner": col[17],
                            "consWinnerScore": int(col[18]),
                            "consLoser": col[19],
                            "consLoserScore": int(col[20]),
                            "consOT": col[21],
                            "champion": col[22],
                            "championScore": int(col[23]),
                            "runnerup": col[24],
                            "runnerupScore": int(col[25]),
                            "champOT": col[26]}
                beanDict['semiDOW'], beanDict['semiDate'] = beanDict['semiDate'].split(
                    ',')
                beanDict['champDOW'], beanDict['champDate'] = beanDict['champDate'].split(
                    ',')
                beanDict['semiDate'] = beanDict['semiDate'].rstrip(
                    ' ').lstrip(' ')
                beanDict['champDate'] = beanDict['champDate'].rstrip(
                    ' ').lstrip(' ')
                beanDict['semiDate'] += '/' + str(beanDict['year'])
                beanDict['champDate'] += '/' + str(beanDict['year'])
                beanDict['semiDate'] = pd.Timestamp(beanDict['semiDate'])
                beanDict['champDate'] = pd.Timestamp(beanDict['champDate'])
                beanDict['semi1GD'] = beanDict['semi1WinnerScore'] - \
                    beanDict['semi1LoserScore']
                beanDict['semi2GD'] = beanDict['semi2WinnerScore'] - \
                    beanDict['semi2LoserScore']
                beanDict['consGD'] = beanDict['consWinnerScore'] - \
                    beanDict['consLoserScore']
                beanDict['champGD'] = beanDict['championScore'] - \
                    beanDict['runnerupScore']
                beanList.append(beanDict)
    f.close()
    dfBeanpot = pd.DataFrame(beanList)

    fileName = RECBOOK_DATA_PATH + 'BeanpotHistoryWomens.txt'
    with open(fileName, 'r', encoding='utf-8') as f:
        readData = f.read()
        rows = readData.split('\n')
        beanListW = []
        for i in rows:
            col = i.split('\t')
            beanDict = {"edition": int(col[0]),
                        "year": int(col[1]),
                        "arena": col[2],
                        "semiDate": col[3],
                        "note": col[4],
                        "semi1Winner": col[5],
                        "semi1WinnerScore": int(col[6]),
                        "semi1Loser": col[7],
                        "semi1LoserScore": int(col[8]),
                        "semi1OT": col[9],
                        "semi2Winner": col[10],
                        "semi2WinnerScore": int(col[11]),
                        "semi2Loser": col[12],
                        "semi2LoserScore": int(col[13]),
                        "semi2OT": col[14],
                        "semi3Winner": col[15],
                        "semi3WinnerScore": convertToIntZ(col[16]),
                        "semi3Loser": col[17],
                        "semi3LoserScore": convertToIntZ(col[18]),
                        "champDate": col[19],
                        "consWinner": col[20],
                        "consWinnerScore": convertToIntZ(col[21]),
                        "consLoser": col[22],
                        "consLoserScore": convertToIntZ(col[23]),
                        "consOT": col[24],
                        "champion": col[25],
                        "championScore": int(col[26]),
                        "runnerup": col[27],
                        "runnerupScore": int(col[28]),
                        "champOT": col[29]}
            beanDict['semiDate'] = beanDict['semiDate'].rstrip(' ').lstrip(' ')
            beanDict['champDate'] = beanDict['champDate'].rstrip(
                ' ').lstrip(' ')
            beanDict['semiDate'] += '/' + str(beanDict['year'])
            beanDict['champDate'] += '/' + str(beanDict['year'])
            beanDict['semiDate'] = pd.Timestamp(beanDict['semiDate'])
            beanDict['champDate'] = pd.Timestamp(beanDict['champDate'])
            beanDict['semiDOW'] = beanDict['semiDate'].weekday()
            beanDict['champDOW'] = beanDict['champDate'].weekday()
            beanDict['semi1GD'] = beanDict['semi1WinnerScore'] - \
                beanDict['semi1LoserScore']
            beanDict['semi2GD'] = beanDict['semi2WinnerScore'] - \
                beanDict['semi2LoserScore']
            beanDict['consGD'] = beanDict['consWinnerScore'] - \
                beanDict['consLoserScore']
            beanDict['champGD'] = beanDict['championScore'] - \
                beanDict['runnerupScore']
            beanListW.append(beanDict)
    f.close()
    dfBeanpotWomens = pd.DataFrame(beanListW)
    return dfBeanpot, dfBeanpotWomens


def generateBeanpotAwards():
    '''create DataFrame containing all Beanpot Awards'''
    fileName = RECBOOK_DATA_PATH + 'BeanpotAwardHistory.txt'
    with open(fileName, 'r', encoding='utf-8') as f:
        readData = f.read()
        rows = readData.split('\n')
        awardList = []
        for i in rows:
            col = i.split('\t')
            awardDict = {'year': int(col[0]),
                         'mvpName': col[1],
                         'mvpPos': col[2],
                         'mvpSchool': col[3],
                         'ebName': col[4],
                         'ebSchool': col[5],
                         'ebSaves': col[6],
                         'ebGA': col[7],
                         'ebSV%': col[8],
                         'ebGAA': col[9]}
            awardList.append(awardDict)
    f.close()
    dfBeanpotAwards = pd.DataFrame(awardList)

    fileName = RECBOOK_DATA_PATH + 'BeanpotAwardHistoryWomens.txt'
    with open(fileName, 'r', encoding='utf-8') as f:
        readData = f.read()
        rows = readData.split('\n')
        awardListW = []
        for i in rows:
            col = i.split('\t')
            awardDict = {'year': int(col[0]),
                         'mvpName': col[1],
                         'mvpSchool': col[2],
                         'berName': col[3],
                         'berSchool': col[4]}
            awardListW.append(awardDict)
    f.close()
    dfBeanpotAwardsWomens = pd.DataFrame(awardListW)

    return dfBeanpotAwards, dfBeanpotAwardsWomens


def generateGameSkaterStats():
    '''create DataFrame game stats for skaters from 2002-03 on'''
    fileName = RECBOOK_DATA_PATH + 'GameStatsData.txt'
    gameStatsList = []
    with open(fileName, 'r', encoding='utf-8') as f:
        readData = f.read()
        rows = readData.split('\n')
        for i in rows:
            col = i.split(',')
            gameStatDict = {'date': pd.to_datetime(col[0]),
                            'opponent': col[1],
                            'name': col[2],
                            'pos': col[3],
                            'yr': col[4],
                            'gp': 1,
                            'goals': int(col[5]),
                            'assists': int(col[6]),
                            'pts': int(col[7]),
                            'season': col[8],
                            'year': int(col[8][:4]) + 1}
            gameStatsList.append(gameStatDict)
    f.close()
    dfGameStatsMens = pd.DataFrame(gameStatsList)

    # create DataFrame game stats for all skaters
    fileName = RECBOOK_DATA_PATH + 'GameStatsDataWomens.txt'
    gameStatsWList = []
    with open(fileName, 'r', encoding='utf-8') as f:
        readData = f.read()
        rows = readData.split('\n')
        for i in rows:
            col = i.split(',')
            gameStatWDict = {'date': pd.to_datetime(col[0]),
                             'opponent': col[1],
                             'name': col[2],
                             'pos': col[3],
                             'yr': col[4],
                             'gp': 1,
                             'goals': int(col[5]),
                             'assists': int(col[6]),
                             'pts': int(col[7]),
                             'season': col[8],
                             'year': int(col[8][:4]) + 1}
            gameStatsWList.append(gameStatWDict)
    f.close()
    dfGameStatsWomens = pd.DataFrame(gameStatsWList)
    dfGameStats = pd.DataFrame(gameStatsList + gameStatsWList)

    return dfGameStats, dfGameStatsMens, dfGameStatsWomens


def generateGameGoalieStats():
    '''create DataFrame containing game stats for goalies from 2002-03 on'''
    fileName = RECBOOK_DATA_PATH + 'GameStatsGoalieData.txt'
    gameStatsGoalieList = []
    with open(fileName, 'r', encoding='utf-8') as f:
        readData = f.read()
        rows = readData.split('\n')
        for i in rows:
            col = i.split(',')
            gameStatGoalieDict = {'date': pd.to_datetime(col[0]),
                                  'opponent': col[1],
                                  'name': col[2],
                                  'yr': col[3],
                                  'sv': int(col[4]),
                                  'ga': int(col[5]),
                                  'gp': int(col[6]),
                                  'SO': int(col[7]),
                                  'mins': float(col[8]),
                                  'result': col[9],
                                  'season': col[10],
                                  'year': int(col[10][:4]) + 1}

            # Calculate GAA - Goals Against Average = (Goals Allowed / Minutes
            # Played )* 60
            gameStatGoalieDict['gaa'] = round(
                (gameStatGoalieDict['ga'] / gameStatGoalieDict['mins']) * 60, 2)

            # if no saves or goals allowed set sv% to 0
            if (gameStatGoalieDict['sv'] + gameStatGoalieDict['ga']) == 0:
                gameStatGoalieDict['sv%'] = 0
            else:
                # calculate sv% - Save Percentage = Saves/(Saves+Goals Allowed)
                gameStatGoalieDict['sv%'] = gameStatGoalieDict['sv'] / \
                    (gameStatGoalieDict['sv'] + gameStatGoalieDict['ga'])
            gameStatsGoalieList.append(gameStatGoalieDict)
    f.close()
    dfGameStatsGoalieMens = pd.DataFrame(gameStatsGoalieList)

    # create DataFrame containing game stats for all goalies
    fileName = RECBOOK_DATA_PATH + 'GameStatsGoalieDataWomens.txt'
    gameStatsGoalieWList = []
    with open(fileName, 'r', encoding='utf-8') as f:
        readData = f.read()
        rows = readData.split('\n')
        for i in rows:
            col = i.split(',')
            gameStatGoalieWDict = {'date': pd.to_datetime(col[0]),
                                   'opponent': col[1],
                                   'name': col[2],
                                   'yr': col[3],
                                   'sv': int(col[4]),
                                   'ga': int(col[5]),
                                   'gp': int(col[6]),
                                   'SO': int(col[7]),
                                   'mins': float(col[8]),
                                   'result': col[9],
                                   'season': col[10],
                                   'year': int(col[10][:4]) + 1}

            # Calculate GAA - Goals Against Average = (Goals Allowed / Minutes
            # Played )* 60
            gameStatGoalieWDict['gaa'] = round(
                (gameStatGoalieWDict['ga'] / gameStatGoalieWDict['mins']) * 60, 2)

            # if no saves or goals allowed set sv% to 0
            if (gameStatGoalieWDict['sv'] + gameStatGoalieWDict['ga']) == 0:
                gameStatGoalieWDict['sv%'] = 0
            else:
                # calculate sv% - Save Percentage = Saves/(Saves+Goals Allowed)
                gameStatGoalieWDict['sv%'] = gameStatGoalieWDict['sv'] / \
                    (gameStatGoalieWDict['sv'] + gameStatGoalieWDict['ga'])
            gameStatsGoalieWList.append(gameStatGoalieWDict)
    f.close()
    dfGameStatsGoalieWomens = pd.DataFrame(gameStatsGoalieWList)
    dfGameStatsGoalie = pd.DataFrame(
        gameStatsGoalieList + gameStatsGoalieWList)
    return dfGameStatsGoalie, dfGameStatsGoalieMens, dfGameStatsGoalieWomens

def generatePolls():

  dfPollsMens = pd.read_csv(RECBOOK_DATA_PATH + "mpolls.csv")
  dfPollsWomens = pd.read_csv(RECBOOK_DATA_PATH + "wpolls.csv")
  
  dfPollsMens['DATE'] = pd.to_datetime(dfPollsMens['DATE'])
  dfPollsMens['RK']=dfPollsMens['RK'].astype(int)
  
  dfPollsWomens['DATE'] = pd.to_datetime(dfPollsWomens['DATE'])
  dfPollsWomens['RK']=dfPollsWomens['RK'].astype(int)
  return dfPollsMens, dfPollsWomens

def determineQueryType(query):
    '''determine type of query entered'''
    qType = ''
    if ('record' in query and 'career' not in query and cleanupQuery(
            query, '').startswith('record')):
        qType = 'record'
    elif 'wins' in query:
        qType = 'wins'
    elif 'losses' in query:
        qType = 'losses'
    elif 'ties' in query:
        qType = 'ties'
    elif 'last win' in query:
        qType = 'last win'
    elif 'last loss' in query:
        qType = 'last loss'
    elif 'last tie' in query:
        qType = 'last tie'
    elif 'last' in query:
        qType = 'last'
    elif 'biggest win' in query:
        qType = 'biggest win'
    elif 'biggest loss' in query:
        qType = 'biggest loss'
    elif 'biggest tie' in query:
        qType = 'biggest tie'
    elif 'biggest' in query:
        qType = 'biggest'
    else:
        qType = 'player'
    return qType


def determineGender(query):
    '''determine gender of query'''
    query = query.lower()
    wSearch = re.search('(?:^|\\s)(wom[a|e]n\\S*\\s?|female\\S*\\s?)', query)
    gender = ""
    if wSearch is not None:
        gender = 'Womens'
        query = query.replace(wSearch.group(1), '')
    mSearch = re.search('(?:^|\\s)(m[a|e]n\\S*\\s?|male\\S*\\s?)', query)
    if mSearch is not None:
        gender = 'Mens'
        query = query.replace(mSearch.group(1), '')
    return query, gender


def tokenizeResultsQuery(query):
    '''split up query tokens'''
    keywords = [
        'vs',
        'at',
        'under',
        'since',
        'after',
        'between',
        'with',
        'before',
        'from',
        'in',
        'on',
        'against',
        'when']
    keyDict = {}
    keyWordsDict = {}
    for i in keywords:
        if query.find(i + ' ') >= 0:
            finds = [m.start() for m in re.finditer(i + ' ', query)]
            for d in range(len(finds)):
                if (finds[d] > 0 and query[finds[d] - 1] != ' '):
                    finds.pop(d)
            if finds == []:
                continue
            if len(finds) > 1:
                counter = 0
                for d in range(len(finds)):
                    if finds[d] == 0:
                        finds[d] = 1
                        query = ' ' + query
                    keyDict[i + '_' + str(counter)] = finds[d]
                    counter += 1
            else:
                if finds[0] == 0:
                    finds[0] = 1
                    query = ' ' + query
                keyDict[i] = finds[0]
    sortedKey = sorted(keyDict.items(), key=operator.itemgetter(1))
    keyWordList = []
    for i in sortedKey:
        keyWordList.append(i[0])
        keyWordsDict = {}
    tokens = re.split(" | ".join(keywords), query)
    if (tokens[0] == ' ' or tokens[0] == ''):
        tokens.pop(0)
    if keyWordList:
        if len(tokens) == len(keyWordList):
            for i in range(len(tokens)):
                tokens[i] = tokens[i].rstrip(' ').lstrip(' ')
                keyWordsDict[keyWordList[i]] = tokens[i]
    return keyWordsDict


def cleanupQuery(query, qType):
    '''remove unnecessary parts of query'''
    cleanlist = [
        'the',
        'of',
        'what',
        'is',
        "what's",
        'number of',
        'games',
        'was',
        'game',
        'his',
        'arena',
        'rink',
        "a",
        "an",
        "did",
        "all time",
        "all-time"]
    if qType != 'bean':
        cleanlist.insert(0, "bu")
        cleanlist.insert(0, "bu's")
    for i in cleanlist:
        if re.search("\\w" + i, query) is None:
            query = query.replace(i + ' ', '')
    query = query.replace("'s", '')
    query = query.replace("vs.","vs")
    if qType != '':
        query = query.replace(qType + ' ', '')
    return query.lower()


def getResults(dfGames, dfGameStats, dfGameStatsGoalie, query):
    '''return record/results for given query'''
    months = [x.lower() for x in list(calendar.month_name)]
    monthsShort = [x.lower() for x in list(calendar.month_abbr)]
    daysShort = [x.lower() for x in list(calendar.day_abbr)]
    numStartSearch = re.search(
        "^(?:\s*)?last (\\d* )?(?:win|loss|tie)?",
        query.lstrip())
    numRes = 1

    if numStartSearch is not None:
        query = query.replace('wins', 'win')
        query = query.replace('losses', 'loss')
        query = query.replace('ties', 'tie')
        if numStartSearch.group(1) is not None:
            query = query.replace(numStartSearch.group(1), '')
            numRes = int(numStartSearch.group(1))
    else:
        numRes = 1
    qType = determineQueryType(query)

    queryDict = tokenizeResultsQuery(cleanupQuery(query, qType))
    if (not queryDict or qType == '' or qType == 'player'):
        return ''
    inList = []
    for i in queryDict.keys():
        if ('in' == i or 'in_' in i):
            inList.append(queryDict[i])

    whenList = []
    for i in queryDict.keys():
        if ('when' == i or 'when_' in i):
            whenList.append(queryDict[i])

    numGames = ''
    ascen = True
    dfQueryList = []
    if 'vs' in queryDict.keys():
        if ((dfGames['opponent'] == decodeTeam(
                queryDict['vs']).title()).any()):
            dfQueryList.append(
                "(dfGames['opponent']=='{}')".format(
                    decodeTeam(
                        queryDict['vs'])))
        else:
            dfQueryList.append(
                "(dfGames['opponent'].str.contains('{}',case=False))".format(
                    decodeTeam(
                        queryDict['vs'])))
    if 'against' in queryDict.keys():
        if ((dfGames['opponent'] == decodeTeam(
                queryDict['against']).title()).any()):
            dfQueryList.append(
                "(dfGames['opponent']=='{}')".format(
                    decodeTeam(
                        queryDict['against'])))
        else:
            dfQueryList.append(
                "(dfGames['opponent'].str.contains('{}',case=False))".format(
                    decodeTeam(
                        queryDict['against'])))
    if 'under' in queryDict.keys():
        if queryDict['under'] == 'AOC'.lower():
            queryDict['under'] = "Albie O'Connell"
        dfQueryList.append(
            "(dfGames['coach'].str.contains(\"{}\",case=False))".format(
                queryDict['under']))
    if 'with' in queryDict.keys():
        if queryDict['with'] == 'AOC'.lower():
            queryDict['with'] = "Albie O'Connell"
        dfQueryList.append(
            "(dfGames['coach'].str.contains(\"{}\",case=False))".format(
                queryDict['with']))
    if 'at' in queryDict.keys():
        if 'neutral' in queryDict['at']:
            queryDict['at'] = 'Neutral'
        if (queryDict['at'].capitalize() in ['Home', 'Away', 'Neutral']):
            dfQueryList.append(
                "(dfGames['location']==(\"{}\"))".format(
                    queryDict['at'].capitalize()))
        elif dfGames.loc[(dfGames['opponent'] == decodeTeam(queryDict['at']))]['opponent'].count() > 0:
            if ((dfGames['opponent'] == decodeTeam(
                    queryDict['at']).title()).any()):
                dfQueryList.append(
                    "(dfGames['opponent']=='{}')".format(
                        decodeTeam(
                            queryDict['at'])))
            else:
                dfQueryList.append(
                    "(dfGames['opponent'].str.contains('{}',case=False))".format(
                        decodeTeam(
                            queryDict['at'])))
            dfQueryList.append("(dfGames['location']=='Away')")
        else:
            dfQueryList.append(
                "(dfGames['arena'].str.contains(\"{}\",case=False))".format(
                    queryDict['at']))
    if 'on' in queryDict.keys():
        dateSearch = re.search('(\\w*).(\\d*)', queryDict['on'])
        if (dateSearch is not None and '' not in dateSearch.groups()):
            for i in range(len(monthsShort)):
                if monthsShort[i] in dateSearch.group(1):
                    dfQueryList.append("(dfGames['month']=={})".format(
                        int(dateSearch.group(1))))
                    break
            dfQueryList.append("(dfGames['day']=={})".format(
                int(dateSearch.group(2))))
        else:
            for i in range(len(daysShort)):
                if daysShort[i] in queryDict['on']:
                    dfQueryList.append("(dfGames['dow']=={})".format(i))
                    break
    if ('in' in queryDict.keys() or len(inList) > 1):
        for i in inList:
            queryDict['in'] = i
            digSearch = re.search('\\d', queryDict['in'])
            decSearch = re.search('(\\d{2,4})s', queryDict['in'])
            seaSearch = re.search('(\\d{4}-\\d{2})', queryDict['in'])
            if queryDict['in'] in ['ot', 'overtime']:
                dfQueryList.append("(dfGames['ot'].notnull())")
            elif queryDict['in'] in ['reg', 'regulation']:
                dfQueryList.append("(dfGames['ot'].isnull())")
            elif queryDict['in'] in ['nc', 'ooc', 'non-conference']:
                dfQueryList.append("(dfGames['gameType']=='Non-Conference')")
            elif queryDict['in'] == 'conference':
                dfQueryList.append("(dfGames['gameType']=='Conference')")
            elif (('hockey east' in queryDict['in'] or 'hea' in queryDict['in']) and 'tourn' not in queryDict['in']):
                dfQueryList.append("(dfGames['gameType']=='Conference')")
                dfQueryList.append("(dfGames['conference']=='Hockey East')")
            elif ('ecac' in queryDict['in'] and 'tourn' not in queryDict['in']):
                dfQueryList.append("(dfGames['gameType']=='Conference')")
                dfQueryList.append("(dfGames['conference']=='ECAC')")
            elif ('neihl' in queryDict['in'] and 'tourn' not in queryDict['in']):
                dfQueryList.append("(dfGames['gameType']=='Conference')")
                dfQueryList.append("(dfGames['conference']=='NEIHL')")
            elif ('regular' == queryDict['in'] or 'rs' == queryDict['in'] or 'regular season' == queryDict['in']):
                dfQueryList.append("(dfGames['seasonType']=='Regular Season')")
            elif 'playoff' in queryDict['in']:
                dfQueryList.append("(dfGames['seasonType']=='Playoffs')")
            elif (digSearch is None and queryDict['in'] not in months and queryDict['in'] not in monthsShort):
                queryDict['in'] = queryDict['in'].replace(
                    'tourney', 'tournament')
                queryDict['in'] = queryDict['in'].replace(
                    'hea tournament', 'hockey east tournament')
                queryDict['in'] = queryDict['in'].replace(
                    'he tournament', 'hockey east tournament')
                if 'NCAA' in queryDict['in'].upper():
                    queryDict['in'] = queryDict['in'].replace('s', '')
                if queryDict['in'].upper() in tourneyDict.keys():
                    queryDict['in'] = tourneyDict[queryDict['in'].upper()]
                dfQueryList.append(
                    "(dfGames['tourney'].str.contains(\"{}\",case=False))".format(
                        queryDict['in']))
                dfQueryList.append("(dfGames['tourney'].notnull())")
            elif decSearch is not None:
                if len(decSearch.group(1)) == 2:
                    if int(decSearch.group(1)) > 20:
                        decadeStart = int("19" + decSearch.group(1))
                    else:
                        decadeStart = int("20" + decSearch.group(1))
                else:
                    decadeStart = int(decSearch.group(1))
                dfQueryList.append(
                    "(dfGames['date'].between('{}','{}'))".format(
                        decadeStart, decadeStart + 9))
            elif seaSearch is not None:
                dfQueryList.append(
                    "(dfGames['season']==\"{}\")".format(
                        queryDict['in']))
            elif 'first' in queryDict['in']:
                numGamesSearch = re.search('first (\\d*)', queryDict['in'])
                if numGamesSearch is not None:
                    numGames = int(numGamesSearch.group(1))
            elif 'last' in queryDict['in']:
                numGamesSearch = re.search('last (\\d*)', queryDict['in'])
                if numGamesSearch is not None:
                    numGames = int(numGamesSearch.group(1))
                    ascen = False
            elif 'goal' in queryDict['in']:
                goalSearch = re.search('(\\d{1,3})(\\+)?', queryDict['in'])
                if goalSearch is not None:
                    if goalSearch.group(2) is not None:
                        diff = ">="
                    else:
                        diff = '=='
                    dfQueryList.append(
                        "(dfGames['GD']{}{})".format(
                            diff, int(
                                goalSearch.group(1))))
            else:
                if queryDict['in'].isdigit():
                    dfQueryList.append(
                        "(dfGames['year']=={})".format(
                            queryDict['in']))
                elif queryDict['in'] in months:
                    dfQueryList.append(
                        "(dfGames['month']=={})".format(
                            months.index(
                                queryDict['in'])))
                elif queryDict['in'] in monthsShort:
                    dfQueryList.append(
                        "(dfGames['month']=={})".format(
                            monthsShort.index(
                                queryDict['in'])))

    if 'since' in queryDict.keys():
        timeSearch = re.search('(\\d{4})-(\\d{2})', queryDict['since'])
        if timeSearch is not None:
            sDate = '9/1/{}'.format(timeSearch.group(1))
        else:
            sDate = queryDict['since']
        dfQueryList.append("(dfGames['date']>='{}')".format(sDate))

    if 'before' in queryDict.keys():
        timeSearch = re.search('(\\d{4})-(\\d{2})', queryDict['before'])
        if timeSearch is not None:
            bDate = '9/1/{}'.format(timeSearch.group(1))
        else:
            bDate = queryDict['before']
        dfQueryList.append("(dfGames['date']<'{}')".format(bDate))
    if 'after' in queryDict.keys():
        timeSearch = re.search('(\\d{4})-(\\d{2})', queryDict['after'])
        if timeSearch is not None:
            if int(timeSearch.group(2)) > 20:
                aStart = int("19" + timeSearch.group(2))
            else:
                aStart = int("20" + timeSearch.group(2))
            aDate = '5/1/{}'.format(aStart)
        else:
            aDate = queryDict['after']
        if not aDate.isnumeric():
            aDate = (
                datetime.strptime(
                    aDate,
                    '%m/%d/%Y') +
                timedelta(
                    days=1)).strftime('%m/%d/%Y')
        dfQueryList.append("(dfGames['date']>'{}')".format(aDate))
    if 'between' in queryDict.keys():
        dates = queryDict['between'].split(' and ')
        dfQueryList.append(
            "(dfGames['date'].between('{}','{}'))".format(
                dates[0], dates[1]))
    if 'from' in queryDict.keys():
        dates = queryDict['from'].split(' to ')
        dfQueryList.append(
            "(dfGames['date'].between('{}','{}'))".format(
                dates[0], dates[1]))
    if ('when' in queryDict.keys() or len(whenList) > 1):
        for i in whenList:
            queryDict['when'] = i
            goalSearch = re.search(
                "(\\>\\=|\\<=|\\>|\\<)? ?(\\d{1,3})(\\+)?",
                queryDict['when'])
            pSearch = re.search(
                '(.*) (make\\S*|scor\\S*|allow\\S*|get\\S*|has) ?(\\>\\=|\\<=|\\>|\\<)? ?(a|\\d{1,3})?(\\+)? ?(pt\\S*|point\\S*|goal\\S*|assist\\S*|ga|save\\S*|g|a)?',
                queryDict['when'])
            if pSearch is not None:
                pName = pSearch.group(1)
                opt = pSearch.group(2)
                diff = ''
                stat=''
                if (pSearch.group(4) is None and 'scor' in pSearch.group(2)):
                    stat = 'goals'
                    diff = '>='
                    statNum = 1
                if pSearch.group(4) is not None:
                    if pSearch.group(4) == 'a':
                        statNum = 1
                        diff = '>='
                    else:
                        statNum = int(pSearch.group(4))
                elif (pSearch.group(4) is None and pSearch.group(6) is not None):
                    statNum = 1
                if diff == '':
                    if pSearch.group(3) is not None:
                        diff = pSearch.group(3)
                    elif pSearch.group(5) is not None:
                        diff = '>='
                    else:
                        diff = '=='
                if pSearch.group(6) is not None:
                    statGrp = pSearch.group(6)
                    if ('pt' in statGrp or 'point' in statGrp):
                        stat = 'pts'
                    elif (('goal' in statGrp or statGrp == 'g') and 'allow' not in opt):
                        stat = 'goals'
                    elif ('assist' in statGrp or statGrp == 'a'):
                        stat = 'assists'
                    elif (('allow' in opt and 'goal' in statGrp or statGrp == 'g') or 'ga' in statGrp):
                        stat = 'ga'
                    elif 'save' in statGrp:
                        stat = 'sv'
                if stat in ['sv', 'ga']:
                    dfRes = dfGameStatsGoalie.groupby(
                        ['date', 'name']).sum(numeric_only=True)
                    dfRes.reset_index(inplace=True)
                    gameDays = list(set(dfRes.loc[eval("(dfRes['name'].str.contains('{}',case=False)) & (dfRes['{}']{}{})".format(
                        pName, stat, diff, statNum))]['date'].to_list()))
                    dfQueryList.append(
                        "(dfGames['date'].isin({}))".format(gameDays))
                elif stat in ['pts', 'goals', 'assists']:
                    gameDays = list(set(dfGameStats.loc[eval("(dfGameStats['name'].str.contains('{}',case=False)) & (dfGameStats['{}']{}{})".format(
                        pName, stat, diff, statNum))]['date'].to_list()))
                    dfQueryList.append(
                        "(dfGames['date'].isin({}))".format(gameDays))
            elif goalSearch is not None:
                goals = int(goalSearch.group(2))
                if goalSearch.group(1) is not None:
                    diff = goalSearch.group(1)
                elif goalSearch.group(3) is not None:
                    diff = '>='
                else:
                    diff = '=='
                if 'allow' in queryDict['when']:
                    dfQueryList.append(
                        "(dfGames['OppoScore']{}{})".format(
                            diff, goals))
                if 'scor' in queryDict['when']:
                    dfQueryList.append(
                        "(dfGames['BUScore']{}{})".format(
                            diff, goals))
    dfQueryList.append("(dfGames['result']!='N')")
    dfQueryList.append("(dfGames['result']!='E')")
    dfQuery = ''
    for i in dfQueryList:
        dfQuery += i + " & "
    dfQuery = dfQuery[:-2]
    result = ''
    if (dfQuery == '' and numGames != ''):
        dfResult = eval(
            "dfGames.sort_values('date',ascending={})[:{}]".format(
                ascen, numGames))
    elif dfQuery != '':
        dfResult = eval(
            "dfGames.loc[{}].sort_values('date',ascending={})[:{}]".format(
                dfQuery, ascen, numGames))
    else:
        return "No Results Found"
    if ('last' in qType or 'biggest' in qType):
        if 'last' in qType:
            sortType = 'date'
        elif 'biggest' in qType:
            sortType = ['GD', 'date']
        if 'win' in qType:
            res = (dfResult.loc[(dfResult['result'] == 'W')].sort_values(
                sortType, ascending=False)[:numRes])
        elif ('tie' in qType and 'GD' not in sortType):
            res = (dfResult.loc[(dfResult['result'] == 'T')].sort_values(
                sortType, ascending=False)[:numRes])
        elif ('tie' in qType and 'GD' in sortType):
            res = pd.DataFrame()
            return ''
        elif 'loss' in qType:
            res = (dfResult.loc[(dfResult['result'] == 'L')].sort_values(
                sortType, ascending=False)[:numRes])
        else:
            res = dfResult.loc[(dfResult['result'] != 'N') & (
                dfResult['result'] != 'E')].sort_values(sortType, ascending=False)[:numRes]
        if not res.empty:
            resStr = ''
            for i in range(len(res)):
                if 'Away' in res.iloc[i]['location']:
                    local = 'at'
                else:
                    local = 'vs'
                resStr += "{} {} {} {} {}".format(
                    datetime.strptime(
                        str(
                            res.iloc[i]['date'])[
                            :10],
                        '%Y-%M-%d').strftime('%M/%d/%Y'),
                    local,
                    res.iloc[i]['opponent'].lstrip(' '),
                    res.iloc[i]['scoreline'].lstrip(' '),
                    res.iloc[i]['result'].lstrip(' '))
                if res.iloc[i]['ot'] is not None:
                    resStr += " " + res.iloc[i]['ot']
                if res.iloc[i]['tourney'] is not None:
                    resStr += " (" + res.iloc[i]['tourney'].lstrip(' ') + ")"
                resStr += '\n'
        else:
            resStr = 'No Results Found'
        return resStr
    if qType == 'record':
        for i in ['W', 'L', 'T']:
            if (dfResult['result'] == i).any():
                res = dfResult.groupby('result').count()['date'][i]
            else:
                res = 0
            result += str(res) + '-'
    if qType == 'wins':
        if (dfResult['result'] == 'W').any():
            res = dfResult.groupby('result').count()['date']['W']
        else:
            res = 0
        result = str(res)
    elif qType == 'losses':
        if (dfResult['result'] == 'L').any():
            res = dfResult.groupby('result').count()['date']['L']
        else:
            res = 0
        result = str(res)
    elif qType == 'ties':
        if (dfResult['result'] == 'T').any():
            res = dfResult.groupby('result').count()['date']['T']
        else:
            res = 0
        result = str(res)
    if result[-1] == '-':
        result = result[:-1]
    if result != '':
        return result
    return "No Results Found"


def getPlayerStats(playerDfs, query):
    '''return player stats for given query'''
    dfSkate = playerDfs['careerSkaters']
    dfSkate['gp']=dfSkate['gp'].astype('Int64')
    dfSkate['pim']=dfSkate['pim'].astype('Int64')

    dfGoalie = playerDfs['careerGoalies']
    dfGoalie['gp']=dfGoalie['gp'].astype('Int64')
    dfGoalie['ga']=dfGoalie['ga'].astype('Int64')
    dfGoalie['saves']=dfGoalie['saves'].astype('Int64')
    dfGoalie['W']=dfGoalie['W'].astype('Int64')
    dfGoalie['L']=dfGoalie['L'].astype('Int64')
    dfGoalie['T']=dfGoalie['T'].astype('Int64')

    dfJersey = playerDfs['jerseys']
    dfLead = playerDfs['seasonleaders']
    dfSeasSkate = playerDfs['seasonSkaters']
    dfSeasSkate['gp']=dfSeasSkate['gp'].astype('Int64')
    dfSeasSkate['goals']=dfSeasSkate['goals'].astype('Int64')
    dfSeasSkate['assists']=dfSeasSkate['assists'].astype('Int64')
    dfSeasSkate['pts']=dfSeasSkate['pts'].astype('Int64')

    dfSeasGoalie = playerDfs['seasonGoalies']
    dfSeasGoalie['gp']=dfSeasGoalie['gp'].astype('Int64')
    dfSeasGoalie['ga']=dfSeasGoalie['ga'].astype('Int64')
    dfSeasGoalie['saves']=dfSeasGoalie['saves'].astype('Int64')
    dfSeasGoalie['SO']=dfSeasGoalie['SO'].astype('Int64')

    dfGameStats = playerDfs['gameStats']
    dfGameStatsGoalie = playerDfs['gameGoalieStats']
    opponent = ''
    vsSearch = re.search('(vs|vers\\S*) (.*)', query)
    if vsSearch is not None:
        opponent = decodeTeam(vsSearch.group(2))
    query = cleanupQuery(query, '')
    careerSearch = re.search('(.*) career (.*)', query)
    numSearch = re.search('\\#(\\d*)', query)
    nameSearch = re.search('by (\\w*) ?(\\w*)?', query)
    numQuery = re.search('number (\\w* \\w*|\\w*)', query)
    seasonSearch = re.search(
        '(\\w*|\\w* \\w*)? ?(goal\\S*|point\\S*|pts|assists|stat\\S*|stat line|record|gaa|sv|sv%|save\\S*|shut\\S*|so)? ?in (\\d{4}-\\d{2}|\\d{4})',
        query)
    yrSearch = re.search(
        "(\\w*|\\w* \\w*)? ?(goal\\S*|point\\S*|pts|assists|stat\\S*|stat line|record|gaa|sv|sv%|save\\S*|shut\\S*|so)? ?as (fr|so|jr|junior|senior|sr|gr)",
        query)
    resStr = ''
    if (seasonSearch is not None and numSearch is None):
        season = seasonSearch.group(3)
        if '-' in seasonSearch.group(3):
            year = int(season[:4]) + 1
        else:
            year = int(season)
    if (((yrSearch is not None and yrSearch.group(1) is not None) or (seasonSearch is not None and seasonSearch.group(1) is not None))
            and 'most' not in query and 'lead' not in query and 'lowest' not in query and 'best' not in query and numSearch is None):
        if seasonSearch is not None:
            playerName = seasonSearch.group(1)
            if opponent != '':
                dfRes = dfGameStats.loc[(dfGameStats['year'] == year) & (dfGameStats['name'].str.contains(
                    playerName, case=False)) & (dfGameStats['opponent'] == opponent)].groupby('name').sum(numeric_only=True)
                dfRes.reset_index(inplace=True)
                dfResG = dfGameStatsGoalie.loc[(dfGameStatsGoalie['year'] == year) & (
                    dfGameStatsGoalie['name'].str.contains(playerName, case=False)) & (dfGameStatsGoalie['opponent'] == opponent)]
                dfResG.reset_index(inplace=True)
                if not dfResG.empty:
                    recDict = dfResG.groupby('result').count()[
                        'date'].to_dict()
                    for i in ['W', 'L', 'T']:
                        if i not in recDict:
                            recDict[i] = 0
                    record = "{}-{}-{}".format(recDict['W'],
                                               recDict['L'], recDict['T'])
                    ga = dfResG['ga'].sum(numeric_only=True)
                    sv = dfResG['sv'].sum(numeric_only=True)
                    so = dfResG['SO'].sum(numeric_only=True)
                    mTime = 0
                    for row in range(len(dfResG)):
                        mins = dfResG.iloc[row]['mins'].split(':')
                        time = "{}:{}".format(
                            *divmod(int(mins[0]), 60)) + ":" + mins[1]
                        time = pd.to_timedelta(time)
                        mTime += round(pd.Timedelta(time).total_seconds() / 60, 2)
                    gaa = round(
                        (dfResG['ga'].sum(
                            numeric_only=True) / mTime) * 60, 2)
                    svperc = round(sv / (ga + sv), 3)
                    resDict = {'name': dfResG['name'].unique()[0],
                               'gaa': gaa,
                               'sv%': svperc,
                               'SO': so,
                               'record': record}
                    dfResG = pd.DataFrame([resDict])
            else:
                dfRes = dfSeasSkate.loc[(dfSeasSkate['year'] == year) & (
                    dfSeasSkate['name'].str.contains(playerName, case=False))]
                dfResG = dfSeasGoalie.loc[(dfSeasGoalie['year'] == year) & (
                    dfSeasGoalie['name'].str.contains(playerName, case=False))]
        elif yrSearch is not None:
            playerName = yrSearch.group(1)
            if 'junior' in yrSearch.group(3):
                yr = 'JR'
            elif 'senior' in yrSearch.group(3):
                yr = 'SR'
            else:
                yr = yrSearch.group(3).upper()
            if opponent != '':
                dfRes = dfGameStats.loc[(dfGameStats['yr'] == yr) & (dfGameStats['name'].str.contains(
                    playerName, case=False)) & (dfGameStats['opponent'] == opponent)].groupby('name').sum(numeric_only=True)
                dfRes.reset_index(inplace=True)
                dfResG = dfGameStatsGoalie.loc[(dfGameStatsGoalie['yr'] == yr) & (dfGameStatsGoalie['name'].str.contains(
                    playerName, case=False)) & (dfGameStatsGoalie['opponent'] == opponent)]
                dfResG.reset_index(inplace=True)
                if not dfResG.empty:
                    recDict = dfResG.groupby('result').count()[
                        'date'].to_dict()
                    for i in ['W', 'L', 'T']:
                        if i not in recDict:
                            recDict[i] = 0
                    record = "{}-{}-{}".format(recDict['W'],
                                               recDict['L'], recDict['T'])
                    ga = dfResG['ga'].sum(numeric_only=True)
                    sv = dfResG['sv'].sum(numeric_only=True)
                    so = dfResG['SO'].sum(numeric_only=True)
                    mTime = 0
                    for row in range(len(dfResG)):
                        mins = dfResG.iloc[row]['mins'].split(':')
                        time = "{}:{}".format(
                            *divmod(int(mins[0]), 60)) + ":" + mins[1]
                        time = pd.to_timedelta(time)
                        mTime += round(pd.Timedelta(time).total_seconds() / 60, 2)
                    gaa = round(
                        (dfResG['ga'].sum(
                            numeric_only=True) / mTime) * 60, 2)
                    svperc = round(sv / (ga + sv), 3)
                    resDict = {'name': dfResG['name'].unique()[0],
                               'gaa': gaa,
                               'sv%': svperc,
                               'SO': so,
                               'record': record}
                    dfResG = pd.DataFrame([resDict])
            else:
                dfRes = dfSeasSkate.loc[(dfSeasSkate['yr'] == yr) & (
                    dfSeasSkate['name'].str.contains(playerName, case=False))]
                dfResG = dfSeasGoalie.loc[(dfSeasGoalie['yr'] == yr) & (
                    dfSeasGoalie['name'].str.contains(playerName, case=False))]
        resStr = ''
        if (dfRes.empty and dfResG.empty):
            return resStr
        if ((seasonSearch is not None and seasonSearch.group(2) is not None)
                or (yrSearch is not None and yrSearch.group(2) is not None)):
            if (seasonSearch is not None and seasonSearch.group(2) is not None):
                statType = seasonSearch.group(2)
            elif (yrSearch is not None and yrSearch.group(2) is not None):
                statType = yrSearch.group(2)
            if not dfResG.empty:
                gaa = dfResG['gaa'].to_string(
                    index=False, header=False).lstrip()
                svper = dfResG['sv%'].to_string(
                    index=False, header=False).lstrip()
                record = dfResG['record'].to_string(
                    index=False, header=False).lstrip()
                so = dfResG['SO'].to_string(index=False, header=False).lstrip()
                if ('stat' in statType or 'stat line' in statType.replace(' ', '')):
                    if len(dfResG) > 1:
                        for row in range(len(dfResG)):
                            resStr += "{}: {}/{}/{}".format(
                                dfResG.iloc[row]['name'].to_string(
                                    index=False, header=False).lstrip(' '), dfResG.iloc[row]['gaa'].to_string(
                                    index=False, header=False).lstrip(), dfResG.iloc[row]['sv%'].to_string(
                                    index=False, header=False).lstrip(), dfResG.iloc[row]['record'].to_string(
                                    index=False, header=False).lstrip())
                    else:
                        resStr = "{}: {}/{}/{}".format(dfResG['name'].to_string(
                            index=False, header=False).lstrip(' '), gaa, svper, record)
                elif 'gaa' in statType:
                    if len(dfResG) > 1:
                        for row in range(len(dfResG)):
                            resStr += "{}: {}".format(
                                dfResG.iloc[row]['name'].to_string(
                                    index=False, header=False).lstrip(' '), dfResG.iloc[row]['gaa'].to_string(
                                    index=False, header=False).lstrip())
                    else:
                        resStr = "{}: {}".format(
                            dfResG['name'].to_string(
                                index=False, header=False).lstrip(' '), gaa)
                elif ('sv' in statType or 'save' in statType):
                    if len(dfResG) > 1:
                        for row in range(len(dfResG)):
                            resStr += "{}: {}".format(
                                dfResG.iloc[row]['name'].to_string(
                                    index=False, header=False).lstrip(' '), dfResG.iloc[row]['sv%'].to_string(
                                    index=False, header=False).lstrip())
                    else:
                        resStr = "{}: {}".format(dfResG['name'].to_string(
                            index=False, header=False).lstrip(' '), svper)
                elif ('so' in statType or 'shut' in statType):
                    if len(dfResG) > 1:
                        for row in range(len(dfResG)):
                            resStr += "{}: {}".format(
                                dfResG.iloc[row]['name'].to_string(
                                    index=False, header=False).lstrip(' '), dfResG.iloc[row]['SO'].to_string(
                                    index=False, header=False).lstrip())
                    else:
                        resStr = "{}: {}".format(
                            dfResG['name'].to_string(
                                index=False, header=False).lstrip(' '), so)

                elif 'record' in statType:
                    if len(dfResG) > 1:
                        for row in range(len(dfResG)):
                            resStr += "{}: {}".format(
                                dfResG.iloc[row]['name'].to_string(
                                    index=False, header=False).lstrip(' '), dfResG.iloc[row]['record'].to_string(
                                    index=False, header=False).lstrip())
                    else:
                        resStr = "{}: {}".format(dfResG['name'].to_string(
                            index=False, header=False).lstrip(' '), record)
            else:
                if 'goal' in statType:
                    if len(dfRes) > 1:
                        for row in range(len(dfRes)):
                            resStr += dfRes.iloc[row]['name'] + " " + \
                                str(dfRes.iloc[row]['goals']) + "\n"
                    else:
                        resStr = "{}: {}".format(
                            dfRes['name'].to_string(
                                index=False, header=False).lstrip(), dfRes['goals'].to_string(
                                index=False, header=False).lstrip())
                elif 'assists' in statType:
                    if len(dfRes) > 1:
                        for row in range(len(dfRes)):
                            resStr += dfRes.iloc[row]['name'].lstrip() + \
                                " " + str(dfRes.iloc[row]['assists']) + "\n"
                    else:
                        resStr = "{}: {}".format(
                            dfRes['name'].lstrip(), dfRes['assists'].to_string(
                                index=False, header=False).lstrip())
                elif ('pts' in statType or 'point' in statType or 'stat' in statType):
                    if len(dfRes) > 1:
                        for row in range(len(dfRes)):
                            resStr += "{}: {}-{}--{}\n".format(
                                dfRes.iloc[row]['name'].lstrip(' '),
                                dfRes.iloc[row]['goals'],
                                dfRes.iloc[row]['assists'],
                                dfRes.iloc[row]['pts'])
                    else:
                        resStr = "{}: {}-{}--{}".format(
                            dfRes['name'].to_string(
                                index=False, header=False).lstrip(' '), dfRes['goals'].to_string(
                                index=False, header=False).lstrip(' '), dfRes['assists'].to_string(
                                index=False, header=False).lstrip(' '), dfRes['pts'].to_string(
                                index=False, header=False).lstrip(' '))
        else:
            if dfResG.empty:
                if len(dfRes) > 1:
                    for row in range(len(dfRes)):
                        resStr += "{}: {}-{}--{}\n".format(
                            dfRes.iloc[row]['name'].lstrip(' '),
                            dfRes.iloc[row]['goals'],
                            dfRes.iloc[row]['assists'],
                            dfRes.iloc[row]['pts'])
                else:
                    resStr = "{}: {}-{}--{}".format(
                        dfRes['name'].to_string(
                            index=False, header=False).lstrip(' '), dfRes['goals'].to_string(
                            index=False, header=False).lstrip(' '), dfRes['assists'].to_string(
                            index=False, header=False).lstrip(' '), dfRes['pts'].to_string(
                            index=False, header=False).lstrip(' '))
            else:
                gaa = dfResG['gaa'].to_string(
                    index=False, header=False).lstrip()
                svper = dfResG['sv%'].to_string(
                    index=False, header=False).lstrip()
                record = dfResG['record'].to_string(
                    index=False, header=False).lstrip()
                so = dfResG['SO'].to_string(index=False, header=False).lstrip()
                if len(dfResG) > 1:
                    for row in range(len(dfResG)):
                        resStr += "{}: {}/{}/{}".format(
                            dfResG.iloc[row]['name'].to_string(
                                index=False, header=False).lstrip(' '), dfResG.iloc[row]['gaa'].to_string(
                                index=False, header=False).lstrip(), dfResG.iloc[row]['sv%'].to_string(
                                index=False, header=False).lstrip(), dfResG.iloc[row]['record'].to_string(
                                index=False, header=False).lstrip())
                else:
                    resStr = "{}: {}/{}/{}".format(dfResG['name'].to_string(
                        index=False, header=False).lstrip(' '), gaa, svper, record)

        return resStr
    if ('most' in query or 'lead' in query or 'lowest' in query or 'best' in query):
        if (seasonSearch is not None and nameSearch is None):
            if re.search('goal\\S', query):
                statType = 'goals'
                name = 'gname'
            elif re.search('pts|point|scor', query):
                statType = 'pts'
                name = 'pname'
                return "{}:{}-{}--{}".format(dfLead.loc[(dfLead['year'] == year)][name].to_string(index=False,
                                                                                                  header=False).lstrip(),
                                             dfLead.loc[(dfLead['year'] == year)]['goals'].to_string(index=False,
                                                                                                     header=False).lstrip(),
                                             dfLead.loc[(dfLead['year'] == year)]['assists'].to_string(index=False,
                                                                                                       header=False).lstrip(),
                                             dfLead.loc[(dfLead['year'] == year)]['pts'].to_string(index=False,
                                                                                                   header=False).lstrip())

            elif re.search('assist\\S', query):
                statType = 'assists'
                name = 'aname'
            elif re.search('sv|sv%|gaa|so|shut\\S*', query):
                gpMin = dfSeasGoalie.loc[dfSeasGoalie['year'] == year]['gp'].sum(
                    numeric_only=True) / len(dfSeasGoalie.loc[dfSeasGoalie['year'] == year])
                sortType = True
                if 'sv' in query:
                    statType = 'sv%'
                    sortType = False
                elif 'gaa' in query:
                    statType = 'gaa'
                elif ('so' in query or 'shut' in query):
                    statType = 'SO'
                    sortType = False
                dfRes = dfSeasGoalie.loc[(dfSeasGoalie['year'] == year) & (
                    dfSeasGoalie['gp'] > gpMin)].sort_values(statType, ascending=sortType)[:1]
                if not dfRes.empty:
                    return "{}: {}".format(
                        dfRes['name'].to_string(
                            index=False, header=False).lstrip(), dfRes[statType].to_string(
                            index=False, header=False).lstrip())
                else:
                    return ""
            else:
                return ""
            return "{}:{} {}".format(dfLead.loc[(dfLead['year'] == year)][name].to_string(index=False, header=False).lstrip(
            ), dfLead.loc[(dfLead['year'] == year)][statType].to_string(index=False, header=False).lstrip(), statType)
        elif numSearch is not None:
            number = int(numSearch.group(1))
            dfNum = dfSkate.loc[dfSkate['name'].isin(
                (dfJersey.loc[dfJersey['number'] == number]['name']))]
            if not dfNum.empty:
                if re.search('goal\\S', query):
                    statType = 'goals'
                elif re.search('pts|point|scor', query):
                    statType = 'pts'
                    df = dfNum.sort_values(statType, ascending=False)[:1]
                    name = df['name'].to_string(
                        index=False, header=False).lstrip(' ')
                    pts = df['pts'].to_string(
                        index=False, header=False).lstrip(' ')
                    goals = df['goals'].to_string(
                        index=False, header=False).lstrip(' ')
                    assists = df['assists'].to_string(
                        index=False, header=False).lstrip(' ')
                    if not df.empty:
                        return "{}:{}-{}--{}".format(name, goals, assists, pts)
                elif re.search('assist\\S', query):
                    statType = 'assists'
                df = dfNum.sort_values(statType, ascending=False)[:1]
                if not df.empty:
                    name = df['name'].to_string(
                        index=False, header=False).lstrip(' ')
                    stat = df[statType].to_string(
                        index=False, header=False).lstrip(' ')
                    return "{}: {} {}".format(name, stat, statType)
        elif (nameSearch is not None and nameSearch.group(1) not in ['fr', 'so', 'freshman', 'sophomore', 'junior', 'jr', 'senior', 'sr', 'gr', 'grad', 'f', 'd', 'forward', 'dman', 'd-man', 'defenseman']):
            name = nameSearch.group(1)
            dfName = dfSkate.loc[dfSkate['name'].str.contains(
                name, case=False)]
            if not dfName.empty:
                if re.search('goal\\S', query):
                    statType = 'goals'
                elif re.search('pts|point|scor', query):
                    statType = 'pts'
                    df = dfName.sort_values(statType, ascending=False)[:1]
                    name = df['name'].to_string(
                        index=False, header=False).lstrip(' ')
                    pts = df['pts'].to_string(
                        index=False, header=False).lstrip(' ')
                    goals = df['goals'].to_string(
                        index=False, header=False).lstrip(' ')
                    assists = df['assists'].to_string(
                        index=False, header=False).lstrip(' ')
                    if not df.empty:
                        return "{}:{}-{}--{}".format(name, goals, assists, pts)
                elif re.search('assist\\S', query):
                    statType = 'assists'
                df = dfName.sort_values(statType, ascending=False)[:1]
                name = df['name'].to_string(
                    index=False, header=False).lstrip(' ')
                stat = df[statType].to_string(
                    index=False, header=False).lstrip(' ')
                if not df.empty:
                    return "{}: {} {}".format(name, stat, statType)
        elif (nameSearch is not None and nameSearch.group(1) in ['fr', 'so', 'freshman', 'sophomore', 'junior', 'jr', 'senior', 'sr', 'gr', 'grad', 'f', 'd', 'forward', 'dman', 'd-man', 'defenseman'] and seasonSearch is not None):
            yr = ''
            if year < 2003:
                return 'Not Available for seasons prior to 2002-03'
            if ('freshman' in nameSearch.group(1)
                    or 'freshman' in nameSearch.group(2)):
                yr = 'FR'
            elif ('sophomore' in nameSearch.group(1) or 'sophomore' in nameSearch.group(2)):
                yr = 'SO'
            elif ('junior' in nameSearch.group(1) or 'junior' in nameSearch.group(2)):
                yr = 'JR'
            elif ('senior' in nameSearch.group(1) or 'senior' in nameSearch.group(2)):
                yr = 'SR'
            elif ('grad' in nameSearch.group(1) or 'grad' in nameSearch.group(1)):
                yr = 'GR'
            elif len(nameSearch.group(1)) == 2:
                yr = nameSearch.group(1).upper()
            elif len(nameSearch.group(2)) == 2:
                yr = nameSearch.group(2).upper()
            if yr == 'IN':
                yr = ''
            pos = ''
            if ('forward' == nameSearch.group(1)
                    or 'forward' == nameSearch.group(2)):
                pos = 'F'
            elif ('defenseman' == nameSearch.group(1) or 'dman' == nameSearch.group(1) or 'd-man' == nameSearch.group(2) or 'defenseman' == nameSearch.group(2) or 'dman' == nameSearch.group(2) or 'd-man' == nameSearch.group(2)):
                pos = 'D'
            elif len(nameSearch.group(1)) == 1:
                pos = nameSearch.group(1).upper()
            elif len(nameSearch.group(2)) == 1:
                pos = nameSearch.group(2).upper()
            if pos not in ('F','D'):
                dfName = dfSeasSkate.loc[(dfSeasSkate['yr'] == yr) & (
                    dfSeasSkate['year'] == year)]
            elif pos != '' and yr != '':
                dfName = dfSeasSkate.loc[(dfSeasSkate['yr'] == yr) & (
                    dfSeasSkate['pos'].str.contains(pos)) & (dfSeasSkate['year'] == year)]
            else:
                dfName = dfSeasSkate.loc[(dfSeasSkate['pos'].str.contains(pos)) & (
                    dfSeasSkate['year'] == year)]
            if not dfName.empty:
                if re.search('goal\\S', query):
                    statType = 'goals'
                elif re.search('pts|point|scor', query):
                    statType = 'pts'
                    df = dfName.sort_values(statType, ascending=False)[:1]
                    name = df['name'].to_string(
                        index=False, header=False).lstrip(' ')
                    pts = df['pts'].to_string(
                        index=False, header=False).lstrip(' ')
                    goals = df['goals'].to_string(
                        index=False, header=False).lstrip(' ')
                    assists = df['assists'].to_string(
                        index=False, header=False).lstrip(' ')
                    if not df.empty:
                        return "{}:{}-{}--{}".format(name, goals, assists, pts)
                elif re.search('assist\\S', query):
                    statType = 'assists'
                if statType != '':
                    df = dfName.sort_values(statType, ascending=False)[:1]
                    name = df['name'].to_string(
                        index=False, header=False).lstrip(' ')
                    stat = df[statType].to_string(
                        index=False, header=False).lstrip(' ')
                    if not df.empty:
                        return "{}: {} {}".format(name, stat, statType)
        elif 'by' in query:
            return ""
        else:
            if not dfSkate.empty:
                if re.search('goal\\S', query):
                    statType = 'goals'
                elif re.search('pts|point|scor', query):
                    statType = 'pts'
                    df = dfSkate.sort_values(statType, ascending=False)[:1]
                    name = df['name'].to_string(
                        index=False, header=False).lstrip(' ')
                    pts = df['pts'].to_string(
                        index=False, header=False).lstrip(' ')
                    goals = df['goals'].to_string(
                        index=False, header=False).lstrip(' ')
                    assists = df['assists'].to_string(
                        index=False, header=False).lstrip(' ')
                    if not df.empty:
                        return "{}:{}-{}--{}".format(name, goals, assists, pts)
                elif re.search('assist\\S', query):
                    statType = 'assists'
                elif re.search('sv|sv%|gaa', query):
                    gpMin = 40
                    if 'sv' in query:
                        statType = 'sv%'
                        sortType = False
                    elif 'gaa' in query:
                        statType = 'gaa'
                        sortType = True
                    else:
                        return ""
                    dfRes = dfGoalie.loc[(dfGoalie['gp'] >= gpMin)].sort_values(
                        statType, ascending=sortType)[:1]
                    return "{}: {}".format(
                        dfRes['name'].to_string(
                            index=False, header=False).lstrip(' '), dfRes[statType].to_string(
                            index=False, header=False).lstrip(' '))
                else:
                    return ""
                df = dfSkate.sort_values(statType, ascending=False)[:1]
                name = df['name'].to_string(
                    index=False, header=False).lstrip(' ')
                stat = df[statType].to_string(
                    index=False, header=False).lstrip(' ')
                if not df.empty:
                    return "{}: {} {}".format(name, stat, statType)
            else:
                return ""
    if (numSearch is not None and seasonSearch is not None):
        number = int(numSearch.group(1))
        season = seasonSearch.group(3)
        jStr = ''
        if (not dfJersey.loc[(dfJersey['number'] == number) & (
                dfJersey['season'].str.contains(season))].empty):
            jStrList = dfJersey.loc[(dfJersey['number'] == number) & (dfJersey['season'].str.contains(
                season))]['name'].to_string(index=False, header=False).split('\n')
            for j in jStrList:
                jStr += j.strip() + "\n"
            return jStr[:-1]
        elif (number == 6 and int(season[:4]) >= 2014):
            return "Retired - Jack Parker"
        elif (number == 24 and int(season[:4]) >= 1999):
            return "Retired - Travis Roy"
        else:
            return "No one"
    elif(numSearch is not None):
        number = int(numSearch.group(1))
        jStr = ''
        if (not dfJersey.loc[(dfJersey['number'] == number)].empty):
            jStrList = dfJersey.loc[(dfJersey['number'] == number)
            ][['name','season']].to_string(index=False, header=False).split('\n')
            for j in jStrList:
                j = re.sub(r"(.*) (.*)", "\\1:\\2", j)
                jStr += j.strip() + "\n"
            return jStr[:-1]
        return "Never Worn"
    if numQuery is not None:
        name = numQuery.group(1)
        dfRes = dfJersey.loc[(dfJersey['name'].str.contains(name, case=False))]
        resStr = ''
        if not dfRes.empty:
            for row in range(len(dfRes)):
                resStr += "{}: {} ({})\n".format(
                    dfRes.iloc[row]['name'].lstrip(),
                    dfRes.iloc[row]['number'],
                    dfRes.iloc[row]['season'])
        return resStr
    if careerSearch is not None:
        playerName = careerSearch.group(1)
        stat = careerSearch.group(2)
        pStatsLine = dfSkate.loc[dfSkate['name'].str.contains(
            playerName, case=False)]
        gStatsLine = dfGoalie.loc[dfGoalie['name'].str.contains(
            playerName, case=False)]
        resStr = ''
        if (len(pStatsLine) == 1 and pStatsLine['name'].isin(
                dfSeasSkate['name']).any()):
            if 'stat' in stat:
                if opponent != '':
                    dfRes = dfGameStats.loc[(dfGameStats['name'] == pStatsLine['name'].to_string(index=False, header=False).lstrip()) & (
                        dfGameStats['opponent'] == opponent)].groupby(['season', 'yr', 'year']).sum(numeric_only=True)
                    dfRes.reset_index(inplace=True)
                    if dfRes.empty:
                        return ''
                else:
                    dfRes = dfSeasSkate.loc[dfSeasSkate['name'] == pStatsLine['name'].to_string(
                        index=False, header=False).lstrip()]
                resStr = "Season  Yr GP G A Pts\n"
                cStats = False
                startYear = dfRes.iloc[0]['year']
                if (startYear == 2003 and dfRes.iloc[0]['yr'] != 'FR'):
                    resStr += "(Season Stats Prior to 2002-03 N/A) \n"
                    cStats = True
                for row in range(len(dfRes)):
                    resStr += "{} {} {} {}-{}-{}\n".format(
                        dfRes.iloc[row]['season'],
                        dfRes.iloc[row]['yr'],
                        dfRes.iloc[row]['gp'],
                        dfRes.iloc[row]['goals'],
                        dfRes.iloc[row]['assists'],
                        dfRes.iloc[row]['pts'])
                if not cStats:
                    resStr += "----------------------\nCareer     {} {}-{}-{}".format(
                        dfRes.sum(
                            numeric_only=True)['gp'].astype(int), dfRes.sum(
                            numeric_only=True)['goals'].astype(int), dfRes.sum(
                            numeric_only=True)['assists'].astype(int), dfRes.sum(
                            numeric_only=True)['pts'].astype(int))
                else:
                    goals = pStatsLine['goals'].astype(int).to_string(
                        index=False, header=False).astype(int).lstrip()
                    assists = pStatsLine['assists'].astype(int).to_string(
                        index=False, header=False).lstrip()
                    pts = pStatsLine['pts'].astype(int).to_string(
                        index=False, header=False).lstrip()
                    gp = int(
                        float(
                            pStatsLine['gp'].to_string(
                                index=False,
                                header=False).lstrip()))
                    resStr += "----------------------\nCareer     {} {}-{}-{}".format(
                        gp, goals, assists, pts)
            elif 'goal' in stat:
                if opponent != '':
                    dfRes = dfGameStats.loc[(dfGameStats['name'] == pStatsLine['name'].to_string(index=False, header=False).lstrip()) & (
                        dfGameStats['opponent'] == opponent)].groupby(['yr', 'season']).sum(numeric_only=True)
                    dfRes.reset_index(inplace=True)
                    if dfRes.empty:
                        return ''
                else:
                    dfRes = dfSeasSkate.loc[dfSeasSkate['name'] == pStatsLine['name'].to_string(
                        index=False, header=False).lstrip()]
                resStr = "Season  Yr GP G\n"
                cStats = False
                startYear = dfRes.iloc[0]['year']
                if (startYear == 2003 and dfRes.iloc[0]['yr'] != 'FR'):
                    resStr += "(Season Stats Prior to 2002-03 N/A) \n"
                    cStats = True
                for row in range(len(dfRes)):
                    resStr += "{} {} {} {}\n".format(
                        dfRes.iloc[row]['season'],
                        dfRes.iloc[row]['yr'],
                        dfRes.iloc[row]['gp'],
                        dfRes.iloc[row]['goals'])
                if not cStats:
                    resStr += "----------------------\nCareer     {} {}".format(
                        dfRes.sum(numeric_only=True)['gp'].astype(int), dfRes.sum(numeric_only=True)['goals'].astype(int))
                else:
                    goals = pStatsLine['goals'].to_string(
                        index=False, header=False).lstrip()
                    gp = int(
                        float(
                            pStatsLine['gp'].to_string(
                                index=False,
                                header=False).lstrip()))
                    resStr += "----------------------\nCareer     {} {}".format(
                        gp, goals)
            elif 'assist' in stat:
                if opponent != '':
                    dfRes = dfGameStats.loc[(dfGameStats['name'] == pStatsLine['name'].to_string(index=False, header=False).lstrip()) & (
                        dfGameStats['opponent'] == opponent)].groupby(['yr', 'season']).sum(numeric_only=True)
                    dfRes.reset_index(inplace=True)
                    if dfRes.empty:
                        return ''
                else:
                    dfRes = dfSeasSkate.loc[dfSeasSkate['name'] == pStatsLine['name'].to_string(
                        index=False, header=False).lstrip()]
                resStr = "Season  Yr GP A\n"
                cStats = False
                startYear = dfRes.iloc[0]['year']
                if (startYear == 2003 and dfRes.iloc[0]['yr'] != 'FR'):
                    resStr += "(Season Stats Prior to 2002-03 N/A) \n"
                    cStats = True
                for row in range(len(dfRes)):
                    resStr += "{} {} {} {}\n".format(
                        dfRes.iloc[row]['season'],
                        dfRes.iloc[row]['yr'],
                        dfRes.iloc[row]['gp'],
                        dfRes.iloc[row]['assists'])
                if not cStats:
                    resStr += "----------------------\nCareer     {} {}".format(
                        dfRes.sum(numeric_only=True)['gp'].astype(int), dfRes.sum(numeric_only=True)['assists'].astype(int))
                else:
                    assists = pStatsLine['assists'].astype(int).to_string(
                        index=False, header=False).lstrip()
                    gp = int(
                        float(
                            pStatsLine['gp'].to_string(
                                index=False,
                                header=False).lstrip()))
                    resStr += "----------------------\nCareer     {} {}".format(
                        gp, assists)
            elif ('point' in stat or 'pts' in stat):
                if opponent != '':
                    dfRes = dfGameStats.loc[(dfGameStats['name'] == pStatsLine['name'].to_string(index=False, header=False).lstrip()) & (
                        dfGameStats['opponent'] == opponent)].groupby(['yr', 'season']).sum(numeric_only=True).astype(int)
                    dfRes.reset_index(inplace=True)
                    if dfRes.empty:
                        return ''
                else:
                    dfRes = dfSeasSkate.loc[dfSeasSkate['name'] == pStatsLine['name'].to_string(
                        index=False, header=False).lstrip()]
                resStr = "Season  Yr GP Pts\n"
                cStats = False
                startYear = dfRes.iloc[0]['year']
                if (startYear == 2003 and dfRes.iloc[0]['yr'] != 'FR'):
                    resStr += "(Season Stats Prior to 2002-03 N/A) \n"
                    cStats = True
                for row in range(len(dfRes)):
                    resStr += "{} {} {} {}\n".format(
                        dfRes.iloc[row]['season'],
                        dfRes.iloc[row]['yr'],
                        dfRes.iloc[row]['gp'],
                        dfRes.iloc[row]['pts'])
                if not cStats:
                    resStr += "----------------------\nCareer     {} {}".format(
                        dfRes.sum(numeric_only=True)['gp'].astype(int), dfRes.sum(numeric_only=True)['pts'].astype(int))
                else:
                    pts = pStatsLine['pts'].astype(int).to_string(
                        index=False, header=False).lstrip()
                    gp = int(
                        float(
                            pStatsLine['gp'].to_string(
                                index=False,
                                header=False).lstrip()))
                    resStr += "----------------------\nCareer     {} {}".format(
                        gp, pts)

        elif (len(gStatsLine) == 1 and gStatsLine['name'].isin(dfSeasGoalie['name']).any()):
            wins = 0
            loss = 0
            tie = 0
            if opponent != '':
                dfRes = dfGameStatsGoalie.loc[(dfGameStatsGoalie['name'].str.contains(
                    playerName, case=False)) & (dfGameStatsGoalie['opponent'] == opponent)]
                if dfRes.empty:
                    return ''
                yrs = dfRes.yr.unique()
                yrList = []
                for yr in yrs:
                    dfRes = dfGameStatsGoalie.loc[(dfGameStatsGoalie['yr'] == yr) & (dfGameStatsGoalie['name'].str.contains(
                        playerName, case=False)) & (dfGameStatsGoalie['opponent'] == opponent)]

                    recDict = dfRes.groupby('result').count()['date'].to_dict()
                    for i in ['W', 'L', 'T']:
                        if i not in recDict:
                            recDict[i] = 0
                    record = "{}-{}-{}".format(recDict['W'],
                                               recDict['L'], recDict['T'])
                    ga = dfRes['ga'].sum(numeric_only=True)
                    sv = dfRes['sv'].sum(numeric_only=True)
                    so = dfRes['SO'].sum(numeric_only=True)
                    mTime = 0
                    for row in range(len(dfRes)):
                        mins = dfRes.iloc[row]['mins'].split(':')
                        time = "{}:{}".format(
                            *divmod(int(mins[0]), 60)) + ":" + mins[1]
                        time = pd.to_timedelta(time)
                        mTime += round(pd.Timedelta(time).total_seconds() / 60, 2)
                    mins = "{}:{}".format(
                        floor(mTime), (round((mTime % 1) * 60)))
                    gaa = round(
                        (dfRes['ga'].sum(
                            numeric_only=True) / mTime) * 60, 2)
                    svperc = round(sv / (ga + sv), 3)
                    resDict = {'name': dfRes['name'].unique()[0],
                               'yr': yr,
                               'year': dfRes['year'].unique()[0],
                               'season': dfRes['season'].unique()[0],
                               'gp': len(dfRes['date'].unique()),
                               'ga': ga,
                               'saves': sv,
                               'gaa': gaa,
                               'sv%': svperc,
                               'SO': so,
                               'mins': mins,
                               'record': record}
                    yrList.append(resDict)
                dfRes = pd.DataFrame(yrList)
            else:
                dfRes = dfSeasGoalie.loc[dfSeasGoalie['name'] == gStatsLine['name'].to_string(
                    index=False, header=False).lstrip()]
            mTime = 0
            incompleteData=False
            for row in range(len(dfRes)):
                rec = dfRes.iloc[row]['record'].split('-')
                if rec[0]!='':
                  wins += int(rec[0])
                else:
                  incompleteData=True
                if rec[1]!='':
                  loss += int(rec[1])
                else:
                  incompleteData=True
                if rec[2]!='':
                  tie += int(rec[2])
                else:
                  incompleteData=True
                if(not incompleteData):
                    mins = dfRes.iloc[row]['mins'].split(':')
                    if(mins[0]!=''):
                      time = "{}:{}".format(
                          *divmod(int(mins[0]), 60)) + ":" + mins[1]
                      time = pd.to_timedelta(time)
                      mTime += round(pd.Timedelta(time).total_seconds() / 60, 2)
            if(mTime==0):
              gaa=0
            else:
              gaa = round((dfRes['ga'].sum(numeric_only=True) / mTime) * 60, 2)
            svper = round(dfRes.sum(numeric_only=True)[
                          'saves'] / (dfRes.sum(numeric_only=True)['saves'] + dfRes.sum(numeric_only=True)['ga']), 3)
            if 'stat' in stat:
                resStr = 'Season  Yr GP  SV%  GAA SO Record\n'
                cStats = False
                startYear = dfRes.iloc[0]['year']
                for row in range(len(dfRes)):
                    resStr += "{} {} {} {} {} {} {}\n".format(
                        dfRes.iloc[row]['season'],
                        dfRes.iloc[row]['yr'],
                        dfRes.iloc[row]['gp'],
                        dfRes.iloc[row]['sv%'],
                        dfRes.iloc[row]['gaa'],
                        dfRes.iloc[row]['SO'],
                        dfRes.iloc[row]['record'])
                if (startYear == 2003 and dfRes.iloc[0]['yr'] != 'FR'):
                    resStr += "(Season Stats Prior to 2002-03 N/A) \n"
                    cStats = True
                if(not incompleteData):
                  resStr += "----------------------\nCareer     {} {} {} {} {}-{}-{}".format(
                      dfRes.sum(
                          numeric_only=True)['gp'], svper, gaa, dfRes.sum(
                          numeric_only=True)['SO'], wins, loss, tie)
                else:
                  resStr += "----------------------\nCareer     {} {} {} {} {}-{}-{}".format(
                      gStatsLine['gp'].astype(int).to_string(index=False),gStatsLine['sv%'].to_string(index=False),gStatsLine['gaa'].to_string(index=False),'',gStatsLine['W'].astype(int).to_string(index=False),gStatsLine['L'].astype(int).to_string(index=False),gStatsLine['T'].astype(int).to_string(index=False))

            elif 'sv' in stat:
                resStr = 'Season  Yr GP  SV%\n'
                cStats = False
                startYear = dfRes.iloc[0]['year']
                if (startYear == 2003 and dfRes.iloc[0]['yr'] != 'FR'):
                    resStr += "(Season Stats Prior to 2002-03 N/A) \n"
                    cStats = True
                for row in range(len(dfRes)):
                    resStr += "{} {} {} {}\n".format(
                        dfRes.iloc[row]['season'],
                        dfRes.iloc[row]['yr'],
                        dfRes.iloc[row]['gp'],
                        dfRes.iloc[row]['sv%'])
                resStr += "----------------------\nCareer     {} {}".format(
                    dfRes.sum(numeric_only=True)['gp'].astype(int), svper)
            elif 'gaa' in stat:
                resStr = 'Season  Yr GP  GAA\n'
                cStats = False
                startYear = dfRes.iloc[0]['year']
                if (startYear == 2003 and dfRes.iloc[0]['yr'] != 'FR'):
                    resStr += "(Season Stats Prior to 2002-03 N/A) \n"
                    cStats = True
                for row in range(len(dfRes)):
                    resStr += "{} {} {} {}\n".format(
                        dfRes.iloc[row]['season'],
                        dfRes.iloc[row]['yr'],
                        dfRes.iloc[row]['gp'],
                        dfRes.iloc[row]['gaa'])
                if(not incompleteData):
                  resStr += "----------------------\nCareer     {} {}".format(
                      dfRes.sum(numeric_only=True)['gp'].astype(int), gaa)
                else:
                  resStr += "----------------------\nCareer     {} {}".format(
                      gStatsLine['gp'].astype(int).to_string(index=False),gStatsLine['gaa'].to_string(index=False))
            elif 'record' in stat:
                resStr = 'Season  Yr GP  Record\n'
                cStats = False
                startYear = dfRes.iloc[0]['year']
                if (startYear == 2003 and dfRes.iloc[0]['yr'] != 'FR'):
                    resStr += "(Season Stats Prior to 2002-03 N/A) \n"
                    cStats = True
                for row in range(len(dfRes)):
                    resStr += "{} {} {} {}\n".format(
                        dfRes.iloc[row]['season'],
                        dfRes.iloc[row]['yr'],
                        dfRes.iloc[row]['gp'],
                        dfRes.iloc[row]['record'])
                if(not incompleteData):
                  resStr += "----------------------\nCareer     {} {}-{}-{}".format(
                      dfRes.sum(numeric_only=True)['gp'].astype(int), wins, loss, tie)
                else:
                  resStr += "----------------------\nCareer     {} {}-{}-{}".format(
                      gStatsLine['gp'].to_string(index=False),gStatsLine['W'].to_string(index=False), gStatsLine['L'].to_string(index=False), gStatsLine['T'].to_string(index=False))

            elif ('so' in stat or 'shut' in stat):
                resStr = 'Season  Yr GP  SO\n'
                cStats = False
                startYear = dfRes.iloc[0]['year']
                if (startYear == 2003 and dfRes.iloc[0]['yr'] != 'FR'):
                    resStr += "(Season Stats Prior to 2002-03 N/A) \n"
                    cStats = True
                for row in range(len(dfRes)):
                    resStr += "{} {} {} {}\n".format(
                        dfRes.iloc[row]['season'],
                        dfRes.iloc[row]['yr'],
                        dfRes.iloc[row]['gp'],
                        dfRes.iloc[row]['SO'])
                resStr += "----------------------\nCareer     {} {}".format(
                    dfRes.sum(numeric_only=True)['gp'].astype(int), dfRes.sum(numeric_only=True)['SO'].astype(int))
        elif len(pStatsLine) >= 1:
            for row in range(len(pStatsLine)):
                if opponent != '':
                    dfRes = dfGameStats.loc[(dfGameStats['name'] == pStatsLine.iloc[row]['name']) & (
                        dfGameStats['opponent'] == opponent)].groupby('name').sum(numeric_only=True)
                    dfRes.reset_index(inplace=True)
                    if dfRes.empty:
                        return ''
                else:
                    dfRes = dfSeasSkate.loc[dfSeasSkate['name']
                                            == pStatsLine.iloc[row]['name']]
                if (dfRes.empty and opponent != ''):
                    continue
                resStr += "{} ({}): ".format(
                    pStatsLine.iloc[row]['name'].lstrip(),
                    pStatsLine.iloc[row]['career'].lstrip())
                if dfRes.empty:
                    goals = pStatsLine.iloc[row]['goals']
                    assists = pStatsLine.iloc[row]['assists']
                    pts = pStatsLine.iloc[row]['pts']
                else:
                    goals = dfRes.sum(numeric_only=True)['goals'].astype(int)
                    assists = dfRes.sum(numeric_only=True)['assists'].astype(int)
                    pts = dfRes.sum(numeric_only=True)['pts'].astype(int)
                if ('stats' in stat or 'statline' in stat.replace(' ', '')):
                    resStr += ("{}-{}--{}".format(goals, assists, pts))
                elif 'goal' in stat:
                    resStr += str(goals)
                elif 'assist' in stat:
                    resStr += str(assists)
                elif ('pts' in stat or 'point' in stat):
                    resStr += str(pts)
                resStr += "\n"
        elif len(gStatsLine) >= 1:
            for row in range(len(gStatsLine)):
                resStr += "{} ({}): ".format(
                    gStatsLine.iloc[row]['name'],
                    gStatsLine.iloc[row]['career'].lstrip())
                wins = 0
                loss = 0
                tie = 0
                mTime = 0
                dfRes = dfSeasGoalie.loc[dfSeasGoalie['name']
                                         == gStatsLine.iloc[row]['name'].lstrip()]
                for row in range(len(dfRes)):
                    rec = dfRes.iloc[row]['record'].split('-')
                    wins += int(rec[0])
                    loss += int(rec[1])
                    tie += int(rec[2])
                    mins = dfRes.iloc[row]['mins'].split(':')
                    time = "{}:{}".format(
                        *divmod(int(mins[0]), 60)) + ":" + mins[1]
                    time = pd.to_timedelta(time)
                    mTime += round(pd.Timedelta(time).total_seconds() / 60, 2)
                gaa = round(
                    (dfRes['ga'].sum(
                        numeric_only=True) /
                        mTime) * 60, 2)
                svper = round(dfRes.sum(numeric_only=True)[
                              'saves'] / (dfRes.sum(numeric_only=True)['saves'] + dfRes.sum(numeric_only=True)['ga']), 3)
                if ('stat' in stat or 'stat line' in stat or 'statline' in stat):
                    resStr += "{}/{}/{}-{}-{}".format(gaa,
                                                      svper, wins, loss, tie)
                elif 'gaa' in stat:
                    resStr += str(gaa)
                elif ('sv' in stat or 'save' in stat):
                    resStr += str(svper)
                elif 'record' in stat:
                    resStr += "{}-{}-{}".format(wins, loss, tie)
                resStr += "\n"
    return resStr.replace('nan','-')


def getBeanpotStats(dfBean, query):
    '''return Beanpot data for the requested query'''
    dfBeanpot = dfBean['results']
    dfBeanpotAwards = dfBean['awards']
    beanNumSearch = re.search(
        '(\\d{4}|\\d{1,2})(?:st|nd|rd|th)? beanpot', query)
    typeSearch = re.search(
        'beanpot (semi\\S*|cons\\S*|final|championship)?\\s?(champ|winner|runner|runner-up|1st|first|2nd|second|third|3rd|fourth|4th|last|result|finish)',
        query)
    recordSearch = re.search(
        '(bu|boston university|bc|boston college|northeastern|nu|harvard|hu) record in beanpot ?(early|late|semi\\S*|cons\\S*|final|champ|3rd|third)?(.*(\\d))?',
        query)
    head2headSearch = re.search(
        '(bu|boston university|bc|boston college|northeastern|nu|harvard|hu) record vs (bu|boston university|bc|boston college|northeastern|nu|harvard|hu) in beanpot ?(early|late|semi\\S*|cons\\S*|final|champ|3rd|third)?(\\d)?',
        query)
    finishSearch = re.search(
        '^(bu|boston university|bc|boston college|northeastern|nu|harvard|hu)? ?beanpot (1st|first|2nd|second|3rd|third|fourth|last|4th|champ\\S*|title)? ?(?:place)? ?(finish)?',
        query)
    timeSearch = re.search(
        '(?:(since|after|before) (\\d{4})|(?:between|from) (\\d{4}) (?:and|to) (\\d{4})|(in) (\\d{2,4})s)',
        query)
    teamFinishYearSearch = re.search(
        '^(bu|boston university|bc|boston college|northeastern|nu|harvard|hu)? ?beanpot finish in (\\d{4})',
        query)
    awardSearch = re.search("(eberly|mvp|most valuable|bert)", query)
    if 'semi3Winner' not in dfBeanpot.columns:
        dfBeanpot['semi3Winner'] = ''
        dfBeanpot['semi3WinnerScore'] = ''
        dfBeanpot['semi3Loser'] = ''
        dfBeanpot['semi3LoserScore'] = ''
        dfBeanpot['note'] = ''
    tQuery = ''
    if timeSearch is not None:
        timeType = timeSearch.group(1)
        if (timeType is None and timeSearch.group(5) is not None):
            timeType = 'in'
        elif timeType is None:
            timeType = 'between'
        if timeType == 'since':
            year = int(timeSearch.group(2))
            tQuery += ' & (dfBeanpot["year"]>={})'.format(year)
        if timeType == 'after':
            year = int(timeSearch.group(2))
            tQuery += ' & (dfBeanpot["year"]>{})'.format(year)
        elif timeType in ['before']:
            year = int(timeSearch.group(2))
            tQuery += ' & (dfBeanpot["year"]<{})'.format(year)
        elif timeType == 'between':
            sYear = int(timeSearch.group(3))
            eYear = int(timeSearch.group(4))
            tQuery += ' & (dfBeanpot["year"].between({},{}))'.format(sYear, eYear)
        elif timeType == 'in':
            if len(timeSearch.group(6)) == 2:
                if int(timeSearch.group(6)) > 40:
                    decadeStart = int("19" + timeSearch.group(6))
                else:
                    decadeStart = int("20" + timeSearch.group(6))
            else:
                decadeStart = int(timeSearch.group(6))
            tQuery += ' & (dfBeanpot["year"].between({},{}))'.format(
                decadeStart, decadeStart + 9)
    if (recordSearch is not None and 'vs' not in query):
        team = decodeTeam(recordSearch.group(1))
        qType = recordSearch.group(2)
        if qType is None:
            qType = ''
        if (recordSearch.group(3) is not None and recordSearch.group(3).isdigit()):
            semiNum = int(recordSearch.group(3))
        else:
            semiNum = 0
        recStr = ''
        if ((('semi' in qType or 'early' in qType) and semiNum == 0)
                or ('semi' in qType and semiNum == 1) or qType == ''):
            semi1Wins = dfBeanpot.loc[eval(
                "(dfBeanpot['semi1Winner']==\"{}\")".format(team) + tQuery)]['year'].count()
            semi1Losses = dfBeanpot.loc[eval(
                "(dfBeanpot['semi1Loser']==\"{}\")".format(team) + tQuery)]['year'].count()
            recStr += ("Semi-Final 1: {}-{}\n".format(semi1Wins, semi1Losses))
        if ((('semi' in qType or 'late' in qType) and semiNum == 0)
                or ('semi' in qType and semiNum == 2) or qType == ''):
            semi2Wins = dfBeanpot.loc[eval(
                "(dfBeanpot['semi2Winner']==\"{}\")".format(team) + tQuery)]['year'].count()
            semi2Losses = dfBeanpot.loc[eval(
                "(dfBeanpot['semi2Loser']==\"{}\")".format(team) + tQuery)]['year'].count()
            recStr += "Semi-Final 2: {}-{}\n".format(semi2Wins, semi2Losses)
        if (('semi' in qType and semiNum == 0) or qType == ''):
            semi3Wins = dfBeanpot.loc[eval(
                "(dfBeanpot['semi3Winner']==\"{}\")".format(team) + tQuery)]['year'].count()
            semi3Losses = dfBeanpot.loc[eval(
                "(dfBeanpot['semi3Loser']==\"{}\")".format(team) + tQuery)]['year'].count()
            if (semi3Wins != 0 or semi3Losses != 0):
                recStr += "Semi-Final 3: {}-{}\n".format(
                    semi3Wins, semi3Losses)
            recStr += 'Semi-Finals: {}-{}\n'.format(
                semi1Wins + semi2Wins + semi3Wins,
                semi1Losses + semi2Losses + semi3Losses)
        if ('cons' in qType or 'third' in qType or '3rd' in qType or qType == ''):
            consWins = dfBeanpot.loc[eval(
                "((dfBeanpot['consWinner']==\"{}\") & (dfBeanpot['consGD']!=0))".format(team) + tQuery)]['year'].count()
            consLosses = dfBeanpot.loc[eval(
                "((dfBeanpot['consLoser']==\"{}\") & (dfBeanpot['consGD']!=0))".format(team) + tQuery)]['year'].count()
            consTies = dfBeanpot.loc[eval("((dfBeanpot['consWinner'].str.contains(\"{}\") | (dfBeanpot['consLoser'].str.contains(\"{}\"))) & (dfBeanpot['consGD']==0))".format(
                team, team) + tQuery)]['year'].count()
            consApp = consWins + consLosses + consTies
            if consTies > 0:
                consLossesStr = str(consLosses) + '-' + str(consTies)
            else:
                consLossesStr = str(consLosses)
            recStr += "Consolation Game: {}-{} ({} Appearances)\n".format(
                consWins, consLossesStr, consApp)
        if (('final' in qType or 'champ' in qType or qType == '')
                and 'semi' not in qType):
            champWins = dfBeanpot.loc[eval(
                "(dfBeanpot['champion']==\"{}\")".format(team) + tQuery)]['year'].count()
            champLosses = dfBeanpot.loc[eval(
                "(dfBeanpot['runnerup']==\"{}\")".format(team) + tQuery)]['year'].count()
            recStr += "Championship Game: {}-{} ({} Appearances)\n".format(
                champWins, champLosses, champWins + champLosses)
        if qType == '':
            recStr += "Total: {}-{}".format(semi1Wins +
                                            semi2Wins +
                                            consWins +
                                            champWins, semi1Losses +
                                            semi2Losses +
                                            consLosses +
                                            champLosses)
            if consTies > 0:
                recStr += "-{}\n".format(consTies)
            else:
                recStr += '\n'
        return recStr
    if (typeSearch is not None and beanNumSearch is not None):
        qType = typeSearch.group(2)
        year = int(beanNumSearch.group(1))
        if year == 2021:
            return '2021 Beanpot cancelled due to the COVID-19 pandemic'
        if len(beanNumSearch.group(1)) == 4:
            dfRes = dfBeanpot.loc[dfBeanpot['year'] == year]
            numType = 'year'
        elif len(beanNumSearch.group(1)) <= 2:
            dfRes = dfBeanpot.loc[dfBeanpot['edition'] == year]
            numType = 'edition'
        finStr = ''

        if ('champ' in qType or 'winner' in qType or '1st' in qType or 'first' in qType or qType == 'finish'):
            finStr += "Champion: " + \
                dfRes['champion'].to_string(index=False).lstrip(' ') + "\n"
        if (qType in ['runner', '2nd', 'second'] or qType == 'finish'):
            finStr += "Runner-Up: " + \
                dfRes['runnerup'].to_string(index=False).lstrip(' ') + "\n"
        if ((qType in ['third', '3rd', 'fourth', '4th', 'last']
                or qType == 'finish') and (dfRes['consGD'] > 0).bool()):
            if (qType in ['third', '3rd'] or qType == 'finish'):
                finStr += "3rd Place: " + \
                    dfRes['consWinner'].to_string(
                        index=False).lstrip(' ') + "\n"
            if (qType in ['fourth', '4th', 'last'] or qType == 'finish'):
                finStr += "4th Place: " + \
                    dfRes['consLoser'].to_string(
                        index=False).lstrip(' ') + "\n"
        elif (qType in ['third', '3rd', 'fourth', '4th', 'last'] or qType == 'finish') and not (dfRes['consGD'] > 0).bool():
            if dfRes['consWinner'].to_string(index=False).lstrip() == "":
                thirds = list(set(['Boston University', 'Boston College', 'Northeastern', 'Harvard']) -
                              set([dfRes['champion'].to_string(index=False).lstrip()]) -
                              set([dfRes['runnerup'].to_string(index=False).lstrip()]))
                finStr += "No Consolation Game Held: {},{}\n".format(
                    thirds[0], thirds[1])
            else:
                if (qType in ['third', '3rd'] or qType == 'finish'):
                    finStr += "3rd Place: " + dfRes['consWinner'].to_string(index=False).lstrip(
                        ' ') + ',' + dfRes['consLoser'].to_string(index=False).lstrip(' ') + "\n"
                if (qType in ['fourth', '4th', 'last'] or qType == 'finish'):
                    finStr += "4th Place: None\n"
        if finStr != '':
            return finStr
        if 'result' in qType:
            beanStr = ''
            if (typeSearch.group(1) is None or 'semi' in typeSearch.group(1)):
                beanStr += 'Semi-Finals:\n'
                for i in [
                    'semi1Winner',
                    'semi1WinnerScore',
                    'semi1Loser',
                    'semi1LoserScore',
                        'semi1OT']:
                    beanStr += dfBeanpot.loc[dfBeanpot[numType] ==
                                             year][i].to_string(index=False).lstrip(' ') + ' '
                beanStr += '\n'
                for i in [
                    'semi2Winner',
                    'semi2WinnerScore',
                    'semi2Loser',
                    'semi2LoserScore',
                        'semi2OT']:
                    beanStr += dfBeanpot.loc[dfBeanpot[numType] ==
                                             year][i].to_string(index=False).lstrip(' ') + ' '
                if ('semi3Winner' in dfBeanpot.columns and not dfBeanpot.loc[dfBeanpot[numType] == year]['semi3Winner'].empty):
                  if(dfBeanpot.loc[dfBeanpot[numType] == year][i].to_string(index=False).lstrip(' ') != ''):
                      beanStr += '\n'
                      for i in [
                          'semi3Winner',
                          'semi3WinnerScore',
                          'semi3Loser',
                              'semi3LoserScore']:
                          beanStr += dfBeanpot.loc[dfBeanpot[numType] ==
                                                   year][i].to_string(index=False).lstrip(' ') + ' '
                      beanStr += '\n' + \
                          dfBeanpot.loc[dfBeanpot[numType] == year]['note'].to_string(
                              index=False).lstrip(' ') + ' '
                else:
                  return ''
            if ((typeSearch.group(1) is None or 'cons' in typeSearch.group(
                    1)) and dfBeanpot.loc[dfBeanpot[numType] == year]['consWinner'].to_string(index=False).strip() != ''):
                if typeSearch.group(1) is None:
                    beanStr += '\n\n'
                beanStr += 'Consolation Game:\n'
                for i in [
                    'consWinner',
                    'consWinnerScore',
                    'consLoser',
                    'consLoserScore',
                        'consOT']:
                    beanStr += dfBeanpot.loc[dfBeanpot[numType] ==
                                             year][i].to_string(index=False).lstrip(' ') + ' '
            if (typeSearch.group(1) is None or 'champ' in typeSearch.group(
                    1) or 'final' in typeSearch.group(
                    1)):
                if typeSearch.group(1) is None:
                    beanStr += '\n\n'
                beanStr += 'Championship:\n'
                for i in [
                    'champion',
                    'championScore',
                    'runnerup',
                    'runnerupScore',
                        'champOT']:
                    beanStr += dfBeanpot.loc[dfBeanpot[numType] ==
                                             year][i].to_string(index=False).lstrip(' ') + ' '
            return beanStr
    if head2headSearch is not None:
        team1 = decodeTeam(head2headSearch.group(1))
        team2 = decodeTeam(head2headSearch.group(2))
        qType = head2headSearch.group(3)
        if head2headSearch.group(4) is not None:
            semiNum = int(head2headSearch.group(4))
        else:
            semiNum = 0
        if qType is None:
            qType = ''
        h2hStr = ''
        if ((('semi' in qType or 'early' in qType) and semiNum == 0)
                or (qType in 'semi' and semiNum == 1) or qType == ''):
            semi1Team1Wins = dfBeanpot.loc[eval("(dfBeanpot['semi1Winner']==\"{}\") & (dfBeanpot['semi1Loser']==\"{}\")".format(
                team1, team2) + tQuery)]['year'].count()
            semi1Team2Wins = dfBeanpot.loc[eval("(dfBeanpot['semi1Winner']==\"{}\") & (dfBeanpot['semi1Loser']==\"{}\")".format(
                team2, team1) + tQuery)]['year'].count()
            h2hStr += "Semi-Final 1: {}-{}\n".format(
                semi1Team1Wins, semi1Team2Wins)
        if ((('semi' in qType or 'late' in qType) and semiNum == 0)
                or (qType in 'semi' and semiNum == 2) or qType == ''):
            semi2Team1Wins = dfBeanpot.loc[eval("(dfBeanpot['semi2Winner']==\"{}\") & (dfBeanpot['semi2Loser']==\"{}\")".format(
                team1, team2) + tQuery)]['year'].count()
            semi2Team2Wins = dfBeanpot.loc[eval("(dfBeanpot['semi2Winner']==\"{}\") & (dfBeanpot['semi2Loser']==\"{}\")".format(
                team2, team1) + tQuery)]['year'].count()
            h2hStr += "Semi-Final 2: {}-{}\n".format(
                semi2Team1Wins, semi2Team2Wins)
        if (('semi' in qType and semiNum == 0) or qType == ''):
            semi3Team1Wins = dfBeanpot.loc[eval("(dfBeanpot['semi3Winner']==\"{}\") & (dfBeanpot['semi3Loser']==\"{}\")".format(
                team1, team2) + tQuery)]['year'].count()
            semi3Team2Wins = dfBeanpot.loc[eval("(dfBeanpot['semi3Winner']==\"{}\") & (dfBeanpot['semi3Loser']==\"{}\")".format(
                team2, team1) + tQuery)]['year'].count()
            if (semi3Team1Wins != 0 or semi3Team2Wins != 0):
                h2hStr += "Semi-Final 3: {}-{}\n".format(
                    semi3Team1Wins, semi3Team2Wins)
            h2hStr += "Semi-Finals (Total): {}-{}\n".format(
                semi1Team1Wins + semi2Team1Wins + semi3Team1Wins,
                semi1Team2Wins + semi2Team2Wins + semi3Team2Wins)
        if ('cons' in qType or 'third' in qType or '3rd' in qType or qType == ''):
            consTeam1Wins = dfBeanpot.loc[eval("(dfBeanpot['consWinner']==\"{}\") & (dfBeanpot['consLoser']==\"{}\") & (dfBeanpot['consGD']!=0)".format(
                team1, team2) + tQuery)]['year'].count()
            consTeam2Wins = dfBeanpot.loc[eval("(dfBeanpot['consWinner']==\"{}\") & (dfBeanpot['consLoser']==\"{}\") & (dfBeanpot['consGD']!=0)".format(
                team2, team1) + tQuery)]['year'].count()
            consTies = dfBeanpot.loc[eval("(((dfBeanpot['consWinner'].str.contains(\"{}\")) & (dfBeanpot['consLoser'].str.contains(\"{}\"))) | (dfBeanpot['consWinner'].str.contains(\"{}\")) & (dfBeanpot['consLoser'].str.contains(\"{}\")))  & (dfBeanpot['consGD']==0)".format(
                team1, team2, team2, team1) + tQuery)]['year'].count()
            consApp = consTeam1Wins + consTeam2Wins + consTies
            if consTies > 0:
                consLossesStr = str(consTeam2Wins) + '-' + str(consTies)
            else:
                consLossesStr = str(consTeam2Wins)

            h2hStr += "Consolation Game: {}-{}\n".format(
                consTeam1Wins, consLossesStr)
        if (qType in ['final', 'champ', 'championship'] or qType == ''):
            champWins = dfBeanpot.loc[eval("(dfBeanpot['champion']==\"{}\") & (dfBeanpot['runnerup']==\"{}\")".format(
                team1, team2) + tQuery)]['year'].count()
            champLosses = dfBeanpot.loc[eval("(dfBeanpot['champion']==\"{}\") & (dfBeanpot['runnerup']==\"{}\")".format(
                team2, team1) + tQuery)]['year'].count()
            h2hStr += "Championship Game: {}-{}\n".format(
                champWins, champLosses)
        if qType == '':
            h2hStr += "Total: {}-{}".format(semi1Team1Wins +
                                            semi2Team1Wins +
                                            semi3Team1Wins +
                                            consTeam1Wins +
                                            champWins, semi1Team2Wins +
                                            semi2Team2Wins +
                                            semi3Team2Wins +
                                            consTeam2Wins +
                                            champLosses)
            if consTies > 0:
                h2hStr += "-{}\n".format(consTies)
            else:
                h2hStr += '\n'
        return h2hStr
    if finishSearch is not None:
        noneCheck = True
        for i in finishSearch.groups():
            if i is not None:
                noneCheck = False
        if noneCheck:
            return ""
        if finishSearch.group(1) is None:
            tQuery = tQuery.replace(' &', '')
            beans = {
                'Boston University': [0],
                'Boston College': [0],
                'Northeastern': [0],
                'Harvard': [0]}
            if 'Brown' in dfBeanpot['champion'].unique():
                beans['Brown'] = [0]
            counter = 0
            if finishSearch.group(2) is None:
                places = ['champion', 'runnerup', 'consWinner', 'consLoser']
                header = ['1st', '2nd', '3rd', '4th']
                beans = {
                    'Boston University': [
                        0, 0, 0, 0], 'Boston College': [
                        0, 0, 0, 0], 'Northeastern': [
                        0, 0, 0, 0], 'Harvard': [
                        0, 0, 0, 0]}
                if 'Brown' in dfBeanpot['champion'].unique():
                    beans['Brown'] = [0, 0, 0, 0]
            else:
                finish = finishSearch.group(2)
                places = []
                if finish is None:
                    finish = ''
                if finish in ['champ', 'title', '1st', 'first']:
                    places = ['champion']
                    header = ['Titles']
                if finish in ['2nd', 'second'] or finish == '':
                    places = ['runnerup']
                    header = ['Runner-Up']
                if finish in ['3rd', 'third'] or finish == '':
                    places = ['consWinner']
                    header = ['3rd Place Finish']
                if finish in ['4th', 'fourth', 'last'] or finish == '':
                    places = ['consLoser']
                    header = ['4th Place Finish']
            for place in places:
                if tQuery == '':
                    rows = (
                        dfBeanpot.groupby(
                            [place])[place].count().sort_values(
                            ascending=False).to_string(
                            header=False).split('\n'))
                else:
                    rows = (dfBeanpot.loc[eval(tQuery)].groupby([place])[place].count(
                    ).sort_values(ascending=False).to_string(header=False).split('\n'))
                for row in rows:
                    i = (list(filter(None, row.split('  '))))
                    if (i[0] == 'None' or len(i) == 1):
                        continue
                    beans[i[0]][counter] = int(i[1])
                if place == 'consLoser':
                    if tQuery == '':
                        tieList = dfBeanpot.loc[(dfBeanpot['consGD'] == 0) & (dfBeanpot['consWinner'] != '')].groupby(
                            ['consWinner', 'consLoser'], as_index=False).count()[['consWinner', 'consLoser', 'year']].to_csv(header=False, index=False).split('\n')
                    else:
                        tQuery = '& ({})'.format(tQuery)
                        tieList = dfBeanpot.loc[eval("(dfBeanpot['consGD']==0) & (dfBeanpot['consWinner']!='')" + tQuery)].groupby(
                            ['consWinner', 'consLoser'], as_index=False).count()[['consWinner', 'consLoser', 'year']].to_csv(header=False, index=False).split('\n')
                        if 'Empty' not in tieList[0]:
                            for r in tieList:
                                tie = list(filter(None, r.split(',')))
                                if tie:
                                    beans[tie[1].strip()][counter -
                                                          1] += int(tie[2])
                                    beans[tie[1].strip()][counter] -= int(tie[2])
                counter += 1
            if counter > 1:
                sortedFinish = dict(
                    sorted(
                        beans.items(),
                        key=lambda item: (
                            item[1][0],
                            item[1][1],
                            item[1][2],
                            item[1][3]),
                        reverse=True))
            else:
                sortedFinish = dict(
                    sorted(
                        beans.items(),
                        key=lambda item: (
                            item[1][0]),
                        reverse=True))
            finStr = ''
            for i in sortedFinish.keys():
                finStr += "{0: <18}".format(i)
                for d in sortedFinish[i]:
                    finStr += "{0: <3} ".format(d)
                finStr += '\n'
                bSearch = re.search("(Brown\\s*(?:0(?:\\s*)){1,4}\n)", finStr)
                if bSearch is not None:
                    finStr = finStr.replace(bSearch.group(1), '')
            return finStr
        if teamFinishYearSearch is not None:
            team = decodeTeam(teamFinishYearSearch.group(1))
            year = int(teamFinishYearSearch.group(2))
            if year == 2021:
                return '2021 Beanpot cancelled due to the COVID-19 pandemic'
            for i in ['champion', 'runnerup', 'consWinner', 'consLoser']:
                if (team in dfBeanpot.loc[dfBeanpot['year'] == year][i].to_string(
                        index=False).lstrip(' ')):
                    if i == 'consWinner':
                        i = '3rd Place'
                    elif i == 'consLoser':
                        i = '4th Place'
                    else:
                        i = i.title()
                    return "{} {} {}".format(year, i, team)

        else:
            team = decodeTeam(finishSearch.group(1))
            finish = finishSearch.group(2)
            if finish is None:
                finish = ''
            champWins = dfBeanpot.loc[eval(
                "(dfBeanpot['champion']==\"{}\")".format(team) + tQuery)]['year'].count()
            champLosses = dfBeanpot.loc[eval(
                "(dfBeanpot['runnerup']==\"{}\")".format(team) + tQuery)]['year'].count()
            consWins = dfBeanpot.loc[eval(
                "(dfBeanpot['consWinner']==\"{}\")".format(team) + tQuery)]['year'].count()
            consLosses = dfBeanpot.loc[eval(
                "(dfBeanpot['consLoser']==\"{}\")".format(team) + tQuery)]['year'].count()
            consTies = dfBeanpot.loc[eval(
                "((dfBeanpot['consWinner'].str.contains(team) | (dfBeanpot['consLoser'].str.contains(team))) & (dfBeanpot['consGD']==0))" + tQuery)]['year'].count()
            consApp = consWins + consLosses + consTies
            if consTies > 0:
                consLossesStr = str(consLosses) + '-' + str(consTies)
            else:
                consLossesStr = str(consLosses)

            finStr = ''
            if ('champ' in finish or 'title' in finish):
                return "{} Beanpot Titles".format(champWins)
            if ('1st' in finish or 'first' in finish or finish == ''):
                finStr += '1st {}\n'.format(champWins)
            if ('2nd' in finish or 'second' in finish or finish == ''):
                finStr += '2nd {}\n'.format(champLosses)
            if ('3rd' in finish or 'third' in finish or finish == ''):
                finStr += '3rd {}\n'.format(consWins + consTies)
            if ('4th' in finish or 'fourth' in finish or 'last' in finish or finish == ''):
                finStr += '4th {}\n'.format(consLosses)
            return finStr
    if (awardSearch is not None and beanNumSearch is not None):
        year = int(beanNumSearch.group(1))
        if len(beanNumSearch.group(1)) <= 2:
            year = int(dfBeanpot.loc[dfBeanpot['edition']
                       == year]['year'].to_string(index=False))
        if year == 2021:
            return '2021 Beanpot cancelled due to the COVID-19 pandemic'
        dfRes = dfBeanpotAwards.loc[dfBeanpotAwards['year'] == year]
        if ('ebName' in dfRes.columns and 'eberly' in awardSearch.group(1)):
            if dfRes['ebName'].any():
                return (
                    '{} ({}) {}/{}'.format(
                        dfRes['ebName'].to_string(
                            index=False).lstrip(' '), dfRes['ebSchool'].to_string(
                            index=False).lstrip(' '), dfRes['ebSV%'].to_string(
                            index=False).lstrip(' '), dfRes['ebGAA'].to_string(
                            index=False).lstrip(' ')))
        elif ('mvp' in awardSearch.group(1) or 'most val' in awardSearch.group(1)):
            if dfRes['mvpName'].any():
                if 'mvpPos' in dfRes.columns:
                    return (
                        '{} {} ({})'.format(
                            dfRes['mvpName'].to_string(
                                index=False).lstrip(' '), dfRes['mvpPos'].to_string(
                                index=False).lstrip(' '), dfRes['mvpSchool'].to_string(
                                index=False).lstrip(' ')))
                return (
                    '{} ({})'.format(
                        dfRes['mvpName'].to_string(
                            index=False).lstrip(' '), dfRes['mvpSchool'].to_string(
                            index=False).lstrip(' ')))
            return ''
        elif ('berName' in dfRes.columns and 'bert' in awardSearch.group(1)):
            if dfRes['berName'].any():
                return (
                    '{} ({})'.format(
                        dfRes['berName'].to_string(
                            index=False).lstrip(' '), dfRes['berSchool'].to_string(
                            index=False).lstrip(' ')))
            return ''
    return ''

def getMaxStreak(dfGStats,name,stat):
    dfRes=dfGStats.query(f'name == "{name}"').copy()
    dfRes['isStat']=dfRes[stat]>=1
    dfRes['SoS']=dfRes['isStat'].ne(dfRes['isStat'].shift())
    dfRes['streak_id']=dfRes.SoS.cumsum()
    dfRes['streak_counter'] = dfRes.groupby('streak_id').cumcount() + 1
    if(not dfRes.query(f"{stat}>=1").empty):
        maxStreak=dfRes.query(f'streak_counter=={dfRes.query(f"{stat}>=1")["streak_counter"].max()} and {stat}>=1')['streak_counter'].to_string(index=False,header=False)
        sId=dfRes.query(f'streak_counter=={dfRes.query(f"{stat}>=1")["streak_counter"].max()} and {stat}>=1')['streak_id'].to_string(index=False,header=False)
        maxes=maxStreak.split("\n")
        if(len(maxes)==1):
            if(len(dfRes.query(f'streak_id=={sId}'))==1):
                startDate=dfRes.query(f'streak_id=={sId}')['date'].dt.strftime("%m/%d/%Y").to_string(index=False,header=False)
                gStr="game"
            else:
                startDate=dfRes.query(f'streak_id=={sId}').iloc[0]['date'].strftime("%m/%d/%Y")
                gStr="games"
            if(len(dfRes.query(f'streak_id=={sId}'))==1):
                endDate=''
            else:
                endDate=" - "+dfRes.query(f'streak_id=={sId}').iloc[-1]['date'].strftime("%m/%d/%Y")
            return(f"{maxStreak} {gStr} ({startDate}{endDate})")
        else:
            if(int(maxes[0])==1):
                gStr='game'
            else:
                gStr='games'
            return (f"{maxes[0]} {gStr} ({len(maxes)} times)")
    return 'N/A'

def getStreaks(dfGStats,stat='pts',minStr=3,sortVal='Length',ascend=False):
    dfResTeam=pd.DataFrame()
    if(sortVal=="Length"):
      ascend^=True
    for player in dfGStats.name.unique():
        dfRes=dfGStats.query(f'name == "{player}"').copy()
        dfRes['isStat']=dfRes[stat]>=1
        dfRes['SoS']=dfRes['isStat'].ne(dfRes['isStat'].shift())
        dfRes['streak_id']=dfRes.SoS.cumsum()
        dfRes['streak_counter'] = dfRes.groupby('streak_id').cumcount() + 1
        dfResTeam=pd.concat([dfResTeam,dfRes])
    topStreaks=dfResTeam.query(f'isStat').groupby(['name','streak_id']).max('streak_counter').sort_values('streak_counter',ascending=False)
    topStreaks=topStreaks.query(f'streak_counter>={minStr}')
    dfOut=pd.DataFrame()
    for i in range(len(topStreaks)):
        startDate=dfResTeam.query(f'name=="{topStreaks.index[i][0]}" and streak_id=={topStreaks.index[i][1]}').iloc[0]['date'].strftime("%m/%d/%y")
        endDate=dfResTeam.query(f'name=="{topStreaks.index[i][0]}" and streak_id=={topStreaks.index[i][1]}').iloc[-1]['date'].strftime("%m/%d/%y")
        streakValue=dfResTeam.query(f'name=="{topStreaks.index[i][0]}" and streak_id=={topStreaks.index[i][1]}').iloc[-1]['streak_counter']
        if(streakValue<minStr):
            continue
        if(int(streakValue)==1):
            row = pd.DataFrame([{'Name':topStreaks.index[i][0], 'Length': streakValue, 'Start': pd.to_datetime(startDate),'End':''}])
        else:
            row = pd.DataFrame([{'Name':topStreaks.index[i][0], 'Length': streakValue, 'Start': pd.to_datetime(startDate),'End':pd.to_datetime(endDate)}])
        dfOut=pd.concat([dfOut,row])
        dfOut=dfOut.reset_index()[['Name','Length','Start','End']]
    return dfOut.sort_values(sortVal,ascending=ascend)

def getTopStreaks(dfGStats,season="2022-23",stat='pts',topN=5):
    dfResTeam=pd.DataFrame()
    for player in dfGStats.name.unique():
        dfRes=dfGStats.query(f'name == "{player}"').copy()
        stat='pts'
        dfRes['isStat']=dfRes[stat]>=1
        dfRes['SoS']=dfRes['isStat'].ne(dfRes['isStat'].shift())
        dfRes['streak_id']=dfRes.SoS.cumsum()
        dfRes['streak_counter'] = dfRes.groupby('streak_id').cumcount() + 1
        dfResTeam=pd.concat([dfResTeam,dfRes])
    topStreaks=dfResTeam.query(f'season=="{season}" and isStat').groupby(['name','streak_id']).max('streak_counter').sort_values('streak_counter',ascending=False).head(topN)
    dfOut=pd.DataFrame()
    for i in range(len(topStreaks)):
        startDate=dfResTeam.query(f'name=="{topStreaks.index[i][0]}" and streak_id=={topStreaks.index[i][1]}').iloc[0]['date'].strftime("%m/%d/%y")
        endDate=dfResTeam.query(f'name=="{topStreaks.index[i][0]}" and streak_id=={topStreaks.index[i][1]}').iloc[-1]['date'].strftime("%m/%d/%y")
        streakValue=dfResTeam.query(f'name=="{topStreaks.index[i][0]}" and streak_id=={topStreaks.index[i][1]}').iloc[-1]['streak_counter']
        if(int(streakValue)==1):
            row = pd.DataFrame([{'name':topStreaks.index[i][0], 'streakVal': f'{streakValue} game', 'date': f'{startDate}'}])
        else:
            row = pd.DataFrame([{'name':topStreaks.index[i][0], 'streakVal': f'{streakValue} games', 'date': f'({startDate} - {endDate})'}])
        dfOut=pd.concat([dfOut,row])
    if(dfOut.empty):
      return 'N/A'
    else:
      return dfOut.style.set_table_attributes('class="table-sm table-borderless table-responsive-md"').hide(axis='index').hide(axis='columns').to_html(index_names=False, render_links=True)

def getActiveStreaks(dfGStats,season="2022-23",stat='pts'):
    dfResTeam=pd.DataFrame()
    for player in dfGStats.name.unique():
        dfRes=dfGStats.query(f'name == "{player}"').copy()
        stat='pts'
        dfRes['isStat']=dfRes[stat]>=1
        dfRes['SoS']=dfRes['isStat'].ne(dfRes['isStat'].shift())
        dfRes['streak_id']=dfRes.SoS.cumsum()
        dfRes['streak_counter'] = dfRes.groupby('streak_id').cumcount() + 1
        dfResTeam=pd.concat([dfResTeam,dfRes])
    currPlayers=dfGStats.query(f'season=="{season}"').name.to_list()
    lastGame=dfResTeam.loc[dfResTeam['name'].isin(currPlayers)].groupby('name').last()
    lastGame.reset_index(inplace=True)
    activeStatStreak=lastGame.query('isStat').sort_values('streak_counter',ascending=False)
    activeStatStreak.reset_index(inplace=True)
    dfOut=pd.DataFrame()
    for i in activeStatStreak.iloc:
        startDate=dfResTeam.query(f'name==\"{i["name"]}\" and streak_id=={i["streak_id"]}')['date'].dt.strftime("%m/%d/%y").head(1).to_string(index=False)
        streakValue=dfResTeam.query(f'name==\"{i["name"]}\" and streak_id=={i["streak_id"]}')['streak_counter'].tail(1).to_string(index=False)
        if(int(streakValue)==1):
            row = pd.DataFrame([{'name':i["name"], 'streakVal': f'{streakValue} game', 'date': f'{startDate} - Pres.','streakNum':streakValue}])
        else:
            row = pd.DataFrame([{'name':i["name"], 'streakVal': f'{streakValue} games', 'date': f'{startDate} - Pres.','streakNum':streakValue}])
        dfOut=pd.concat([dfOut,row])
    if(dfOut.empty):
      return 'N/A'
    else:
      dfOut=dfOut[['name','streakVal','date']]
      return dfOut.style.set_table_attributes('class="table-sm table-borderless table-responsive-md"').hide(axis='index').hide(axis='columns').to_html(index_names=False, render_links=True)

def getHatTricks(dfGStats,season="2022-23"):
  if(dfGStats.query(f'season=="{season}" and goals>=3').empty):
    return 'N/A'
  return dfGStats.query(f'season=="{season}" and goals>=3')[['date','name','opponent']].assign(date=dfGStats['date'].dt.strftime('%m/%d')).style.set_table_attributes('class="table-sm table-borderless table-responsive-md"').hide(axis='index').hide(axis='columns').to_html(index_names=False, render_links=True)

def getShutouts(dfGStats,season="2022-23"):
  if(dfGStats.query(f'season=="{season}" and SO>0').empty):
    return 'N/A'
  return dfGStats.query(f'season=="{season}" and SO>0')[['date','name','opponent']].assign(date=dfGStats['date'].dt.strftime('%m/%d')).style.set_table_attributes('class="table-sm table-borderless table-responsive-md"').hide(axis='index').hide(axis='columns').to_html(index_names=False, render_links=True)


def updateCurrentSeasonStats(gender):
    '''scrape site and return updated current season stats'''
    if gender == 'Mens':
        url = "https://goterriers.com/sports/mens-ice-hockey/stats?path=mhockey"
        currSkateFileName = RECBOOK_DATA_PATH + "SeasonSkaterStats.txt"
        currGoalieFileName = RECBOOK_DATA_PATH + "SeasonGoalieStats.txt"
    elif gender == 'Womens':
        url = "https://goterriers.com/sports/womens-ice-hockey/stats/?path=whockey"
        currSkateFileName = RECBOOK_DATA_PATH + "SeasonSkaterStatsWomens.txt"
        currGoalieFileName = RECBOOK_DATA_PATH + "SeasonGoalieStatsWomens.txt"
    else:
        return

    f = urllib.request.urlopen(url)
    html = f.read()
    f.close()
    soup = BeautifulSoup(html, 'html.parser')
    head = soup.find('h1', {'class': 'no-print'})
    if currSeason not in head.get_text():
        pass
    else:
        curSkate = soup.find('section', {'id': 'individual-overall-skaters'})
        rows = curSkate.find_all('tr')
        currSkaters = []
        for i in rows:
            col = i.find_all('td')
            name = i.find('span')
            if name is not None and name.get_text() != "Team":
                lastName, firstName = name.get_text().split(', ')
                skateDict = {'number': int(col[0].get_text()),
                             'last': lastName,
                             'first': firstName,
                             'name': firstName + ' ' + lastName,
                             'gp': int(col[2].get_text()),
                             'goals': int(col[3].get_text()),
                             'assists': int(col[4].get_text()),
                             'pts': int(col[5].get_text()),
                             'pens': col[17].get_text().replace('-', '/'),
                             'season': currSeason}
                currSkaters.append(skateDict)
        dfCurSkate = pd.DataFrame(currSkaters)

        curGoals = soup.find('section',
                             {'id': 'individual-overall-goaltenders'})
        rows = curGoals.find_all('tr')
        currGoalies = []
        for i in rows:
            col = i.find_all('td')
            name = i.find('span')

            if name is not None and name.get_text() != "Team":
                lastName, firstName = name.get_text().split(',')
                goalDict = {'number': int(col[0].get_text()),
                            'last': lastName,
                            'first': firstName,
                            'name': firstName + ' ' + lastName,
                            'gp': int(col[2].get_text().split('-')[0]),
                            'mins': col[3].get_text(),
                            'ga': col[4].get_text(),
                            'gaa': col[5].get_text(),
                            'saves': col[9].get_text(),
                            'sv%': col[10].get_text(),
                            'W': col[11].get_text(),
                            'L': col[12].get_text(),
                            'T': col[13].get_text(),
                            'SO': col[14].get_text(),
                            'season': currSeason}
                currGoalies.append(goalDict)

        dfCurGoal = pd.DataFrame(currGoalies)
        dfCurSkateClean = dfCurSkate.drop(columns=['last', 'first'])
        with open(currSkateFileName, "r", encoding='utf-8') as sources:
            lines = sources.readlines()
        with open(currSkateFileName, "w", encoding='utf-8', newline='\n') as sources:
            for line in lines:
                if currSeason in line:
                    lList = line.split('\t')
                    for i in dfCurSkateClean.to_string(
                            header=False, index=False).split('\n'):
                        pStr = i.lstrip()
                        curList = (
                            list(
                                filter(
                                    None,
                                    pStr.lstrip().split(' '))))
                        if curList[0] == lList[0]:
                            lList[4] = curList[3]
                            lList[5] = curList[4]
                            lList[6] = curList[5]
                            lList[7] = curList[6]
                            lList[8] = curList[7]
                            line = '\t'.join(lList)
                sources.write(line)
        dfCurGoalClean = dfCurGoal.drop(columns=['last', 'first'])
        with open(currGoalieFileName, "r", encoding='utf-8') as sources:
            lines = sources.readlines()
        with open(currGoalieFileName, "w", encoding='utf-8', newline='\n') as sources:
            for line in lines:
                if currSeason in line:
                    lList = line.split('\t')
                    for i in dfCurGoalClean.to_string(
                            header=False, index=False).split('\n'):
                        pStr = i.lstrip()
                        curList = (
                            list(
                                filter(
                                    None,
                                    pStr.lstrip().split(' '))))
                        if curList[0] == lList[0]:
                            lList[3] = curList[3]
                            lList[4] = curList[4]
                            lList[5] = curList[5]
                            lList[6] = curList[7]
                            lList[7] = curList[8]
                            lList[8] = curList[6]
                            lList[9] = "{}-{}-{}".format(curList[9],
                                                         curList[10], curList[11])
                            lList[10] = curList[12]
                            line = '\t'.join(lList)
                sources.write(line)
        return dfCurSkate, dfCurGoal


def updateGameStats(gender):
    '''scrape site and update game stats'''
    if gender == 'Mens':
        url = 'https://goterriers.com/sports/mens-ice-hockey/stats?path=mhockey'
        pFile = RECBOOK_DATA_PATH + 'GameStatsData.txt'
        gFile = RECBOOK_DATA_PATH + 'GameStatsGoalieData.txt'
    elif gender == 'Womens':
        url = 'https://goterriers.com/sports/womens-ice-hockey/stats?path=whockey'
        pFile = RECBOOK_DATA_PATH + 'GameStatsDataWomens.txt'
        gFile = RECBOOK_DATA_PATH + 'GameStatsGoalieDataWomens.txt'
    gameStatsList = []
    with open(pFile, 'r', encoding='utf-8') as f:
        readData = f.read()
        rows = readData.split('\n')
        for i in rows:
            col = i.split(',')
            gameStatDict = {'date': col[0],
                            'opponent': col[1],
                            'name': col[2],
                            'pos': col[3],
                            'yr': col[4],
                            'gp': 1,
                            'goals': int(col[5]),
                            'assists': int(col[6]),
                            'pts': int(col[7]),
                            'season': col[8],
                            'year': int(col[8][:4]) + 1}
            gameStatsList.append(gameStatDict)
    f.close()
    dfGameStats = pd.DataFrame(gameStatsList)
    dfSeasSkate, dfSeasSkateMens, dfSeasSkateWomens = generateSeasonSkaters()
    f = urllib.request.urlopen(url)
    html = f.read()
    f.close()
    soup = BeautifulSoup(html, 'html.parser')
    refs = soup.find_all('a')
    boxscores = set()
    for i in refs:
        if 'boxscore' in str(i.get('href')):
            boxscores.add(i.get('href'))
    boxscores = sorted(list(boxscores), reverse=True)
    pList = []
    gList = []
    for box in boxscores:
        url2 = 'https://goterriers.com/'
        url2 += box
        req = urllib.request.Request(
            url2, headers={
                'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(req).read()
        soup = BeautifulSoup(html, 'html.parser')
        date = soup.find(
            'dl', {
                'class': "text-center inline"}).find('dd').get_text()
        if (pd.to_datetime(dfGameStats.iloc[-1]
                           ['date']) >= pd.to_datetime(date)):
            continue
        indBoxScore = soup.find('section', {'id': "individual-stats"})
        aTeam = indBoxScore.find_all('h4')[0].get_text()
        hTeam = indBoxScore.find_all('h4')[1].get_text()
        if 'Boston U' in aTeam:
            isBUSkate = True
            isBUGoalie = True
            teamSearch = re.search("(.*) \\d*", hTeam)
            opponent = teamSearch.group(1).strip()
        else:
            isBUSkate = False
            isBUGoalie = False
            teamSearch = re.search("(.*) \\d*", aTeam)
            opponent = teamSearch.group(1).strip()
        for i in indBoxScore.find_all('tr'):
            col = i.find_all('td')
            if (col != [] and len(col) >= 11):
                if ((len(col) >= 14 and len(col) <= 16) and 'TEAM' not in col[2].get_text(
                ) and 'Totals' not in col[2].get_text() and isBUSkate):
                    pDict = {
                        'date': date, 'opponent': decodeTeam(opponent), 'name': col[2].get_text().replace(
                            col[1].get_text().strip(), ''), 'goals': int(
                            col[3].get_text()), 'assists': int(
                            col[4].get_text()), 'pts': int(
                            col[3].get_text()) + int(
                            col[4].get_text()), 'season': currSeason}
                    name = pDict['name'].split(', ')
                    pDict['name'] = name[1] + " " + name[0]
                    if 'FitzGerald' in pDict['name']:
                        pDict['name'] = pDict['name'].title()
                    posDict = dfSeasSkate.loc[(dfSeasSkate['season'] == currSeason) & (
                        dfSeasSkate['name'].str.contains(pDict['name'],case=False))].iloc[0][['pos', 'yr']].to_dict()
                    pDict['pos'] = posDict['pos']
                    pDict['yr'] = posDict['yr']
                    pList.append(pDict)
                elif ((len(col) >= 14 and len(col) <= 16) and 'Totals' in col[2].get_text()):
                    isBUSkate = not isBUSkate
                elif ((len(col) >= 11 and len(col) <= 13) and 'TEAM' not in col[2].get_text() and 'Totals' not in col[1].get_text() and isBUGoalie):
                    gDict = {'date': date,
                             'opponent': decodeTeam(opponent),
                             'name': col[1].get_text().replace(col[0].get_text().strip(),
                                                               ''),
                             'result': col[2].get_text(),
                             'mins': col[3].get_text(),
                             'ga': int(col[4].get_text()),
                             'sv': int(col[-1].get_text()),
                             'gp': 1,
                             'season': currSeason}
                    if ((gDict['result'] == 'W' or gDict['result']
                            == 'T') and gDict['ga'] == 0):
                        gDict['so'] = 1
                    else:
                        gDict['so'] = 0
                    name = gDict['name'].split(', ')
                    gDict['name'] = name[1] + " " + name[0]
                    posDict = dfSeasSkate.loc[(dfSeasSkate['season'] == currSeason) & (
                        dfSeasSkate['name'] == pDict['name'])].iloc[0][['pos', 'yr']].to_dict()
                    gDict['yr'] = posDict['yr']
                    if gDict['mins'] != '00:00':
                        gList.append(gDict)
                    mins=gDict['mins'].split(':')
                    gDict['mins']=int(mins[0])+round(int(mins[1])/60,2)
                elif ((len(col) >= 11 and len(col) <= 13) and 'Totals' in col[1].get_text()):
                    isBUGoalie = not isBUGoalie
        dfCurrPlayStats = pd.DataFrame(pList)
        dfCurrGoalStats = pd.DataFrame(gList)
        f = open(pFile, 'a')
        for i in dfCurrPlayStats[['date',
                                  'opponent',
                                  'name',
                                  'pos',
                                  'yr',
                                  'goals',
                                  'assists',
                                  'pts',
                                  'season']].to_csv(index=False,
                                                    header=False).split('\n'):
            if i != '':
                print("\n" + i.strip(), end='', file=f)
        f.close()
        f = open(gFile, 'a')
        for i in dfCurrGoalStats[['date',
                                  'opponent',
                                  'name',
                                  'yr',
                                  'sv',
                                  'ga',
                                  'gp',
                                  'so',
                                  'mins',
                                  'result',
                                  'season']].to_csv(index=False,
                                                    header=False).split('\n'):
            if i != '':
                print("\n" + i.strip(), end='', file=f)
        f.close()


def updateCareerStats(dfSkate, dfGoalie, dfSeasSkate, dfSeasGoalie):
    ''' generate career stats for current players and return updated
    career DataFrames'''
    curSkateList = dfSeasSkate.loc[dfSeasSkate['season'].str.contains(
        currSeason)]['name'].to_list()
    curGoalieList = dfSeasGoalie.loc[dfSeasGoalie['season'].str.contains(
        currSeason)]['name'].to_list()
    for player in curSkateList:
        dfRes = dfSeasSkate.loc[dfSeasSkate['name'] == player]
        if 'Brändli' in player:
            dfRes = dfSeasSkate.loc[dfSeasSkate['name']
                                    == player.strip().title()]
        pens = dfRes.pens.str.split(
            '/',
            expand=True).astype(int).sum(
            numeric_only=True)
        pen = pens.iloc[0]
        pim = pens.iloc[1]
        pSums = dfRes.sum(numeric_only=True)
        dfSkate.loc[(dfSkate['name'].str.contains(player,case=False)) & (
            dfSkate['seasons'].str.contains(currSeason)), 'gp'] = pSums['gp']
        dfSkate.loc[(dfSkate['name'].str.contains(player,case=False)) & (
            dfSkate['seasons'].str.contains(currSeason)), 'goals'] = pSums['goals']
        dfSkate.loc[(dfSkate['name'].str.contains(player,case=False)) & (
            dfSkate['seasons'].str.contains(currSeason)), 'assists'] = pSums['assists']
        dfSkate.loc[(dfSkate['name'].str.contains(player,case=False)) & (
            dfSkate['seasons'].str.contains(currSeason)), 'pts'] = pSums['pts']
        dfSkate.loc[(dfSkate['name'].str.contains(player,case=False)) & (
            dfSkate['seasons'].str.contains(currSeason)), 'pens'] = pen
        dfSkate.loc[(dfSkate['name'].str.contains(player,case=False)) & (
            dfSkate['seasons'].str.contains(currSeason)), 'pim'] = pim

    for player in curGoalieList:
        dfRes = dfSeasGoalie.loc[dfSeasGoalie['name'] == player]
        if 'Brändli' in player:
            dfRes = dfSeasGoalie.loc[dfSeasGoalie['name']
                                     == player.strip().title()]
        pName = player.strip().title()
        dfResSeas = dfSeasGoalie.loc[(dfSeasGoalie['name'].str.contains(pName,case=False))]
        mins = dfResSeas.mins.str.split(
            ':', expand=True).astype(int).sum(
            numeric_only=True)
        time = "{}:{}".format(
            *divmod(int(mins.iloc[0]), 60)) + ":" + str(mins.iloc[1])
        time = pd.to_timedelta(time)
        record = dfResSeas.record.str.split(
            '-',
            expand=True).astype(int).sum(
            numeric_only=True)
        pSum = dfResSeas.sum(numeric_only=True)
        dfGoalie.loc[(dfGoalie['name'].str.contains(pName,case=False)) & (
            dfGoalie['seasons'].str.contains(currSeason)), 'W'] = record[0]
        dfGoalie.loc[(dfGoalie['name'].str.contains(pName,case=False)) & (
            dfGoalie['seasons'].str.contains(currSeason)), 'L'] = record[1]
        dfGoalie.loc[(dfGoalie['name'].str.contains(pName,case=False)) & (
            dfGoalie['seasons'].str.contains(currSeason)), 'T'] = record[2]
        dfGoalie.loc[(dfGoalie['name'].str.contains(pName,case=False)) & (
            dfGoalie['seasons'].str.contains(currSeason)), 'saves'] = pSum['saves']
        dfGoalie.loc[(dfGoalie['name'].str.contains(pName,case=False)) & (
            dfGoalie['seasons'].str.contains(currSeason)), 'ga'] = pSum['ga']
        dfGoalie.loc[(dfGoalie['name'].str.contains(pName,case=False)) & (
            dfGoalie['seasons'].str.contains(currSeason)), 'gp'] = pSum['gp']
        dfGoalie.loc[(dfGoalie['name'].str.contains(pName,case=False)) & (dfGoalie['seasons'].str.contains(
            currSeason)), 'mins'] += round(pd.Timedelta(time).total_seconds() / 60, 2)
        dfRes = dfGoalie.loc[(dfGoalie['name'].str.contains(pName,case=False)) & (
            dfGoalie['seasons'].str.contains(currSeason))]
        dfGoalie.loc[(dfGoalie['name'].str.contains(pName,case=False)) & (dfGoalie['seasons'].str.contains(
            currSeason)), 'sv%'] = round(dfRes['saves'] / (dfRes['ga'] + dfRes['saves']), 3)
        dfGoalie.loc[(dfGoalie['name'].str.contains(pName,case=False)) & (dfGoalie['seasons'].str.contains(
            currSeason)), 'gaa'] = round((dfRes['ga'] / dfRes['mins']) * 60, 2)

def updateResults(gender):
    ''' update results for recently completed games'''
    if gender == 'Mens':
        url = f"https://goterriers.com/sports/mens-ice-hockey/schedule/{currSeason}?grid=true"  # mens
        recBookFileName = RECBOOK_DATA_PATH + 'BURecordBook.txt'
    elif gender == 'Womens':
        url = f"https://goterriers.com/sports/womens-ice-hockey/schedule/{currSeason}?grid=true"  # womens
        recBookFileName = RECBOOK_DATA_PATH + "BUWomensRecordBook.txt"
    else:
        return
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    html = urllib.request.urlopen(req).read()
    soup = BeautifulSoup(html, 'html.parser')
    gameList=[]
    for row in soup.find('table').find_all('tr'):
      cols=row.find_all('td')
      if(cols!=[]):
          date=cols[0].get_text().strip().split(' (')[0]
          dStr=datetime.strptime(date, '%B %d, %Y').strftime("%m/%d")
          res=cols[-2].get_text().strip().replace('\n','').replace(', SOL','OT').replace(', SOW','OT').replace('(',' (').split(',')
          if(len(res)>1):
            match = re.findall(r'(\(*OT\))', res[1])
            if(match != []):
              res[1] = re.sub(r'(\(*OT\))', '', res[1]).strip()
              res[0] += ' ' + match[0].lower()
            result,scoreline=res[0],res[1]
          else:
            result='N'
            scoreline='0-0'
          gDict={'date':dStr,'result':result,'scoreline':scoreline}
          gameList.append(gDict)
    with open(recBookFileName, "r", encoding='utf-8') as sources:
        lines = sources.readlines()
    with open(recBookFileName, "w", encoding='utf-8', newline='\n') as sources:
        for line in lines:
            for game in gameList:
                if re.match(game['date'], line) is not None:
                    if (' N ' in line and ' 0-0' in line):
                        line = re.sub(
                            r' N ', ' {} '.format(
                                game['result']), line)
                    line = re.sub(r' 0-0\n', ' {}\n'.format(
                        game['scoreline']),
                        line)
            sources.write(line)
            
def updatePolls(gender):
    season=2025
    if(gender=="Mens"):
        url = "https://json-b.uscho.com/json/rankings/d-i-mens-poll"
        pollFile = RECBOOK_DATA_PATH + 'mpolls.csv'
    elif(gender=="Womens"):
        url = "https://json-b.uscho.com/json/rankings/d-i-womens-poll"
        pollFile = RECBOOK_DATA_PATH + 'wpolls.csv'
    f=urllib.request.urlopen(url)
    html = f.read()
    f.close()
    soup = BeautifulSoup(html, 'html.parser')
    tsoup=html_lib.unescape(str(soup)).replace("\/", "/")
    new_soup=BeautifulSoup(tsoup, 'html.parser')
    title=new_soup.find('h1').get_text()
    table_soup=new_soup.find('table')
    dfPoll=pd.read_csv(pollFile)
    date = title.split('-')[1].strip()
    date = datetime.strptime(date, "%B %d, %Y").strftime("%Y-%m-%d")
    if (date > dfPoll['DATE'].tail(1).values[0]):  # Ensure proper comparison
        rows = []
        for row in table_soup.find_all('tr'):
            col = row.find_all('td')
            if len(col) > 1:
                rows.append([
                    col[0].get_text(),
                    col[1].get_text(),
                    date,
                    season
                ])
    
        df_new = pd.DataFrame(rows, columns=dfPoll.columns)
        dfPoll=pd.concat([dfPoll,df_new])
        dfPoll['RK']=dfPoll['RK'].astype(int)
        dfPoll['SEASON']=dfPoll['SEASON'].astype(int)
        dfPoll.to_csv(pollFile,index=False)

def getShutoutList(gender):
  ''' returns Shutout List for given gender '''
  dfRes = pd.read_csv(RECBOOK_DATA_PATH + f"{gender[0]}Shutouts.csv")
  dfRes['date'] = pd.to_datetime(dfRes['date'])
  return dfRes

def getHatTrickList(gender):
  ''' returns Hat Trick List for given gender '''
  dfRes = pd.read_csv(RECBOOK_DATA_PATH + f"{gender[0]}Hattricks.csv")
  dfRes['date'] = pd.to_datetime(dfRes['date'])
  return dfRes

def getMissingDates():
  ''' returns Hat Trick List for given gender '''
  dfRes = pd.read_csv(RECBOOK_DATA_PATH + f"missing_dates.csv")
  dfRes['date'] = pd.to_datetime(dfRes['date'])
  return dfRes


def getBirthdays(year,month):
  ''' returns Birthdays for given month and year'''
  dfBirthday = pd.read_csv(RECBOOK_DATA_PATH + 'birthdays.csv')

  # Get birthdays for the current month
  birthdays = dfBirthday.query(f'Month == {month}').copy()
  birthdays['age'] = year - birthdays['Year']
  birthdays = birthdays.query('age>=0').copy()
  birthdays['name_age'] = birthdays['name']+ " (" + birthdays['age'].astype(str) + ")"
  return birthdays
     
     
def initializeRecordBook():
  ''' initialize all DataFrames in record book'''
  global dfGames, dfGamesWomens, dfJersey, dfJerseyMens, dfJerseyWomens, dfSkate, dfSkateMens, dfSkateWomens, dfGoalie, dfGoalieMens, dfGoalieWomens, dfLead, dfLeadWomens, dfBeanpot, dfBeanpotWomens, dfSeasSkate, dfSeasSkateMens, dfSeasSkateWomens, dfSeasGoalie, dfSeasGoalieMens, dfSeasGoalieWomens, dfGameStats, dfGameStatsMens, dfGameStatsWomens, dfGameStatsGoalie, dfGameStatsGoalieMens, dfGameStatsGoalieWomens, dfBeanpotAwards, dfBeanpotAwardsWomens, dfPollsMens, dfPollsWomens
  
  dfPollsMens, dfPollsWomens = generatePolls()
  dfGames = generateRecordBook()
  dfGamesWomens = generateWomensRecordBook()
  dfJersey, dfJerseyMens, dfJerseyWomens = generateJerseys()
  dfSkate, dfSkateMens, dfSkateWomens = generateSkaters()
  dfGoalie, dfGoalieMens, dfGoalieWomens = generateGoalies()
  dfLead, dfLeadWomens = generateSeasonLeaders()
  dfBeanpot, dfBeanpotWomens = generateBeanpotHistory()
  dfSeasSkate, dfSeasSkateMens, dfSeasSkateWomens = generateSeasonSkaters()
  dfSeasGoalie, dfSeasGoalieMens, dfSeasGoalieWomens = generateSeasonGoalies()
  dfGameStats, dfGameStatsMens, dfGameStatsWomens = generateGameSkaterStats()
  dfBeanpotAwards, dfBeanpotAwardsWomens = generateBeanpotAwards()
  dfGameStatsGoalie, dfGameStatsGoalieMens, dfGameStatsGoalieWomens = generateGameGoalieStats()
  updateCareerStats(dfSkate, dfGoalie, dfSeasSkate, dfSeasGoalie)
  updateCareerStats(dfSkateMens, dfGoalieMens, dfSeasSkateMens, dfSeasGoalieMens)
  updateCareerStats(dfSkateWomens, dfGoalieWomens, dfSeasSkateWomens, dfSeasGoalieWomens)

def refreshStats():
  print("Refreshing Stats...")
  # Update Results
  updateResults('Mens')
  updateResults('Womens')
  updateCurrentSeasonStats('Mens')
  updateCurrentSeasonStats('Womens')
  updateGameStats('Mens')
  updateGameStats('Womens')
  updatePolls('Mens')
  updatePolls('Womens')
  initializeRecordBook()
  print("Stats Refreshed")

# Awards
awardsDict={"Walter Brown Award":{1973:"Ed Walsh",
1984:"Cleon Daskalakis",
1993:"David Sacco",
1994:"Jacques Joubert",
1995:"Mike Grier",
1996:"Jay Pandolfo",
1997:"Chris Drury",
1998:"Chris Drury",
2007:"John Curry",
2009:"Matt Gilroy",
2023:"Lane Hutson"},

"First Team All-American" : {"1949-50" : ["Ralph Bevins","Walt Anderson","Jack Garrity"],
"1950-51" : ["Jack Garrity"],
"1952-53" : ["Dick Rodenhiser"],
"1957-58" : ["Don MacLeod","Bob Dupuis","Bob Marquis"],
"1958-59" : ["Bob Marquis"],
"1963-64" : ["Richie Green"],
"1964-65" : ["Jack Ferreira","Tom Ross"],
"1965-66" : ["Tom Ross","Fred Bassi"],
"1966-67" : ["Brian Gilmour"],
"1967-68" : ["Herb Wakabayashi"],
"1968-69" : ["Herb Wakabayashi"],
"1969-70" : ["Mike Hyndman"],
"1970-71" : ["Steve Stirling","Bob Brown"],
"1971-72" : ["Bob Brown","John Danby","Dan Brady"],
"1972-73" : ["Ed Walsh","Steve Dolloff"],
"1973-74" : ["Bill Burlington","Vic Stanfield"],
"1974-75" : ["Vic Stanfield","Rick Meagher"],
"1975-76" : ["Rick Meagher","Peter Brown"],
"1976-77" : ["Rick Meagher"],
"1978-79" : ["Jack O’Callahan","Jim Craig"],
"1983-84" : ["Cleon Daskalakis"],
"1990-91" : ["Shawn McEachern"],
"1991-92" : ["David Sacco"],
"1992-93" : ["David Sacco"],
"1993-94" : ["Mike Pomichter"],
"1994-95" : ["Mike Grier"],
"1995-96" : ["Jay Pandolfo"],
"1996-97" : ["Chris Drury","Jon Coleman"],
"1997-98" : ["Chris Drury","Tom Poti"],
"2002-03" : ["Freddy Meyer"],
"2005-06" : ["Dan Spang"],
"2006-07" : ["John Curry"],
"2007-08" : ["Matt Gilroy"],
"2008-09" : ["Matt Gilroy","Colin Wilson"],
"2009-10" : ["Colby Cohen"],
"2014-15" : ["Jack Eichel","Matt Grzelcyk"],
"2015-16" : ["Matt Grzelcyk"],
"2016-17" : ["Charlie McAvoy"],
"2019-20" : ["David Farrance"],
"2021-22" : ["David Farrance"],
"2022-23" : ["Lane Hutson"],
"2023-24" : ["Macklin Celebrini","Lane Hutson"]},

"Second Team All-American":{"1983-84" : ["T.J. Connolly"],
"1985-86" : ["Jay Octeau","John Cullen","Clark Donatelli"],
"1990-91" : ["Peter Ahola"],
"1991-92" : ["Tom Dion"],
"1992-93" : ["Kaj Linna"],
"1993-94" : ["J.P. McKersie","Rich Brennan","Jacques Joubert"],
"1994-95" : ["Kaj Linna","Chris O’Sullivan"],
"1995-96" : ["Jon Coleman","Chris Drury"],
"1996-97" : ["Chris Kelleher"],
"1997-98" : ["Chris Kelleher"],
"1998-99" : ["Michael Larocque"],
"1999-00" : ["Chris Dyment"],
"2000-01" : ["Carl Corazzini"],
"2001-02" : ["Chris Dyment"],
"2005-06" : ["John Curry"],
"2006-07" : ["Matt Gilroy","Sean Sullivan"],
"2007-08" : ["Bryan Ewing","Pete MacArthur"],
"2008-09" : ["Kevin Shattenkirk"],
"2015-16" : ["Danny O'Regan"],
"2022-23" : ["Matt Brown"]},

"Hockey East Rookie of the Year":{1986:"Scott Young",
1980:"Scott Cashman",
2000:"Rick DiPietro",
2006:"Brandon Yip",
2008:"Colin Wilson",
2009:"Kieran Millan",
2011:"Charlie Coyle",
2015:"Jack Eichel",
2017:"Clayton Keller",
2019:"Joel Farabee",
2023:"Lane Hutson",
2024:"Macklin Celebrini"},

"Hockey East Player of the Year" : {1996:"Jay Pandolfo",
1997:"Chris Drury",
1998:"Chris Drury",
2007:"John Curry",
2015:"Jack Eichel",
2024:"Macklin Celebrini"},

"Tim Taylor Award":{2009:"Kieran Millan",
2015:"Jack Eichel",
2017:"Clayton Keller",
2024:"Macklin Celebrini"},

"NCAA Scoring Champion":{"Jack Garrity": [1950],
"Herb Wakabayashi": [1967],
"Jack Eichel": [2015]},

"Spencer Penrose Award Winner":{"Harry Cleverly": [1958],
"Jack Parker": [1975, 1978, 2009]},

"NCAA Tournament Most Outstanding Player":{
"Ralph Bevins":[1950],
"Bob Marquis":[1960],
"Barry Urbanski":[1960],
"Dan Brady":[1971],
"Tim Regan":[1972],
"Jack O'Callahan":[1978],
"Chris O'Sullivan":[1995],
"Colby Cohen":[2009]}}
