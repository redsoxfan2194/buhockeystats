'''Boots and Runs BU Hockey Stats Website Via Flask'''
import re
import numpy as np
import pandas as pd
from flask import Flask, render_template, request, jsonify
from querystatsbot import querystatsbot,generaterandomstat
from burecordbook import initializeRecordBook
from formatstatsdata import formatResults, formatStats, convertToHtmlTable
import burecordbook as burb

dayNames = {
    0: 'Monday',
    1: 'Tuesday',
    2: 'Wednesday',
    3: 'Thursday',
    4: 'Friday',
    5: 'Saturday',
    6: 'Sunday'}

print('Initializing Record Book...')
initializeRecordBook()
print('Record Book Initialized')

app = Flask(__name__)

@app.route('/')
def homepage():
    ''' Renders "Home" Page
    
    Returns:
      Flask Template : flask template containing home.html
    '''
    query,result=generaterandomstat()
    return render_template('home.html',result=convertToHtmlTable(result),query=query.upper())



@app.route('/about')
def about():
    ''' Renders "About" Page
    
    Returns:
      Flask Template : flask template containing about.html
    '''
    return render_template('about.html')


def getOpponentList(dfRes):
    ''' Generates Opponent List
    
    Parameters:
      dfRes (DataFrame) : DataFrame containing Game Results
    
    Returns:
      list : list of Opponents for given DataFrame
    '''
    dfRes.loc[dfRes['tourney'].isnull(), 'tourney'] = ''
    nonCollOpps = sorted(
        list(dfRes[dfRes['tourney'].str.contains("Non-Collegiate")].opponent.unique()))
    exOpps = sorted(list(set(dfRes.query('result=="E"').opponent.unique(
    )) - set(dfRes.query('result!="E"').opponent.unique())))
    opps = sorted(list(set(dfRes.opponent.unique()) -
                  set(nonCollOpps) - set(exOpps)))
    retList = opps
    if nonCollOpps != []:
        retList += ['Non-Collegiate:'] + nonCollOpps
    if exOpps != []:
        retList += ['Exhibition:'] + exOpps
    return retList


def getTourneyList(dfRes):
    ''' Generates Tournament List
    
    Parameters:
      dfRes (DataFrame) : DataFrame containing Game Results
    
    Returns:
      list : list of Tournaments for given DataFrame
    
    '''
    dfRes = dfRes.copy()
    dfRes.loc[dfRes['tourney'].isnull(), 'tourney'] = ''
    dfRes = dfRes.query('tourney != ""').loc[~dfRes['tourney'].str.contains('1932')]
    retList = ['Tournament'] + \
        sorted(dfRes.query('tourney != ""').tourney.unique())
    return retList


@app.route('/players', methods=['POST', 'GET'])
def players():
    ''' Loads BU Hockey Stats Players page
    
    Returns: 
      json : json structure of Player stats table
    '''
    if request.method == 'POST':
        formData = request.form
        dfStat = pd.DataFrame()
        seasVals = []
        sortVal = ''
        if formData['gender'] == 'Mens':
            mergeGames = burb.dfGames.copy()
            if formData['type'] == 'career':
                if formData['position'] == 'skater':
                    dfStat = burb.dfSkateMens
                elif formData['position'] == 'goalie':
                    dfStat = burb.dfGoalieMens
                seasVals = sorted(set(dfStat['seasons'].to_string(
                    index=False).replace(' ', '').replace('\n', ',').split(',')))
            elif formData['type'] == 'season':
                if formData['position'] == 'skater':
                    dfStat = burb.dfSeasSkateMens
                    pens = dfStat['pens'].str.split('/', expand=True)
                    dfStat.loc[:, 'pen'] = pens[0].replace('—', np.nan).astype('Int64')
                    dfStat.loc[:, 'pim'] = pens[1].replace('—', np.nan).astype('Int64')
                elif formData['position'] == 'goalie':
                    dfStat = burb.dfSeasGoalieMens
                    rec = dfStat.record.str.split('-', expand=True)
                    dfStat['W'] = rec[0].replace('', -1).astype(int)
                    dfStat['L'] = rec[1].replace('', -1).astype(int)
                    dfStat['T'] = rec[2].replace('', -1).astype(int)
            elif formData['type'] == 'game':
                if formData['position'] == 'skater':
                    dfStat = burb.dfGameStatsMens
                elif formData['position'] == 'goalie':
                    dfStat = burb.dfGameStatsGoalieMens
        elif formData['gender'] == 'Womens':
            mergeGames = burb.dfGamesWomens.copy()
            if formData['type'] == 'career':
                if formData['position'] == 'skater':
                    dfStat = burb.dfSkateWomens
                elif formData['position'] == 'goalie':
                    dfStat = burb.dfGoalieWomens
                seasVals = sorted(set(dfStat['seasons'].to_string(index=False).
                replace(' ', '').replace('\n', ',').split(',')))
            elif formData['type'] == 'season':
                if formData['position'] == 'skater':
                    dfStat = burb.dfSeasSkateWomens
                    pens = dfStat['pens'].str.split('/', expand=True)
                    dfStat.loc[:, 'pen'] = pens[0].replace('—', np.nan).astype('Int64')
                    dfStat.loc[:, 'pim'] = pens[1].replace('—', np.nan).astype('Int64')
                elif formData['position'] == 'goalie':
                    dfStat = burb.dfSeasGoalieWomens
                    rec = dfStat.record.str.split('-', expand=True)
                    dfStat['W'] = rec[0].astype(int)
                    dfStat['L'] = rec[1].astype(int)
                    dfStat['T'] = rec[2].astype(int)
            elif formData['type'] == 'game':
                if formData['position'] == 'skater':
                    dfStat = burb.dfGameStatsWomens
                elif formData['position'] == 'goalie':
                    dfStat = burb.dfGameStatsGoalieWomens
        if seasVals == []:
            seasVals = list(dfStat.season.unique())
        sSeas = formData['seasonStart']
        eSeas = formData['seasonEnd']
        if sSeas not in seasVals:
                sIdx = 0
                sSeas = seasVals[0]
        else:
            sIdx = seasVals.index(sSeas)
        eIdx = seasVals.index(eSeas) + 1
        if sIdx > eIdx:
            sIdx, eIdx = eIdx, sIdx
            sSeas = seasVals[sIdx]
            eSeas = seasVals[eIdx]
        valSeas = seasVals[sIdx:eIdx]
        if formData['type'] == 'career':
          idx = []
          for seas in valSeas:
              idx += (list(dfStat.loc[dfStat['seasons'].str.contains(seas)].index))
          idx = list(set(idx))
          dfStat = dfStat.loc[idx]
          dfStat.reset_index(inplace=True)
          
        if formData['season'] != 'all':
            if formData['type'] == 'career':
                dfStat = dfStat.loc[dfStat['seasons'].str.contains(
                    formData['season'])]
            else:
                dfStat = dfStat.loc[(dfStat['season'].isin(valSeas)) & (dfStat['season']==formData['season'])]
        else:
            if formData['type'] != 'career':
                dfStat = dfStat.loc[dfStat['season'].isin(valSeas)]
                
        if formData['type'] != 'career':
            if (formData['pos'] !=
                    'all' and formData['position'] != 'goalie'):
                dfStat = dfStat.query(f"pos=='{formData['pos']}'")
            if formData['yr'] != 'all':
                dfStat = dfStat.query(f"yr=='{formData['yr']}'")
        if formData['type'] == 'game':
            oppList = sorted(list(dfStat.opponent.unique()))
            if formData['opponent'] != 'all':
                dfStat = dfStat.query(f"opponent==\"{formData['opponent']}\"")
            if formData['date'] != 'Date':
                dfStat = dfStat.query(f"date==\"{formData['date']}\"")
        else:
            oppList = []
        if formData['name'] != 'Name':
            dfStat = dfStat.loc[dfStat['name'].str.contains(
                formData['name'].strip(), case=False)]
        if formData['number'] != '':
            dfStat = dfStat.query(f"number == {formData['number']}")
        if (formData['group'] not in ['', 'splits', 'records']
                and formData['position'] == 'skater'):
            dfStat = dfStat.groupby(
                ['name', 'opponent']).sum(numeric_only=True)
            dfStat = dfStat.reset_index()
            dfStat = dfStat[['name', 'opponent',
                             'gp', 'goals', 'assists', 'pts']]
        if (formData['group'] not in ['', 'splits', 'records']
                and formData['position'] == 'goalie'):
            dfStat = determineRecord(dfStat)
            dfStat = dfStat.groupby(
                ['name', 'opponent']).sum(numeric_only=True)
            dfStat = dfStat.reset_index()
            dfStat['sv%'] = dfStat['sv'] / (dfStat['sv'] + dfStat['ga'])
            dfStat['gaa'] = (dfStat['ga'] / dfStat['mins']) * 60
            dfStat = dfStat[['name', 'opponent', 'gp', 'ga',
                             'gaa', 'sv', 'sv%', 'SO', 'W', 'L', 'T']]
        if (formData['group'] in ['splits', 'records']
                and formData['name'] in ['', 'Name']):
            dfStat = pd.DataFrame([{"": 'Please Enter a Player Name'}])
        if (formData['group'] == 'splits' and formData['name'] not in [
                '', 'Name'] and formData['position'] == 'skater'):
            if (len(dfStat.loc[dfStat['name'].str.contains(
                    formData['name'], case=False)].name.unique()) > 1):
                dfStat = pd.DataFrame({"": ['Please Enter One of the Following Player Names:'] +
                [i for i in dfStat.loc[dfStat['name'].str.contains(
                formData['name'], case='False')].name.unique()]})
            elif not dfStat.empty:
                mergeGames.drop(
                    axis=1,
                    labels=[
                        'opponent',
                        'season',
                        'year'],
                    inplace=True)
                dfMerged = dfStat.merge(mergeGames, on='date', how='left')
                dfStat = pd.DataFrame(dfMerged.loc[dfMerged['name'].str.contains(
                formData['name'], case=False)].sum(numeric_only=True)[[
                'gp', 'goals', 'assists', 'pts']]).transpose()
                dfStat.insert(0, 'value', 'Total')
                dfStat.insert(0, 'Split', '')
                for col in [
                    'location',
                    'result',
                    'month',
                    'dow',
                    'opponent',
                    'oppconference',
                    'arena',
                    'tourney']:
                    vals = dfMerged.loc[(dfMerged['name'].str.contains(
                    formData['name'], case=False)) & (dfMerged[col] != '')].groupby(col).sum(
                    numeric_only=True)[['gp', 'goals', 'assists', 'pts']]
                    vals.reset_index(inplace=True)
                    vals.rename(columns={col: 'value'}, inplace=True)
                    if col == 'month':
                        vals.loc[:, 'value'] = pd.to_datetime(
                            vals['value'], format='%m').dt.strftime('%B')
                    if col == 'dow':
                        vals.loc[:, 'value'] = vals['value'].map(dayNames)
                        col = 'Day'
                    if col == 'oppconference':
                        col = 'Conference'
                    row = pd.DataFrame([col.capitalize() if i == 0 else np.nan for i in range(
                        len(dfStat.columns))]).transpose()
                    row.columns = dfStat.columns
                    vals.insert(0, 'Split', ['' for i in range(len(vals))])
                    vals = pd.concat([row, vals])
                    dfStat = pd.concat([dfStat, vals]).reset_index(drop=True)
            else:
                dfStat = pd.DataFrame([{"": 'No Data Available'}])
        if (formData['group'] == 'splits' and formData['name'] not in
                ['', 'Name'] and formData['position'] == 'goalie'):
            if (len(dfStat.loc[dfStat['name'].str.contains(
                    formData['name'], case=False)].name.unique()) > 1):
                dfStat = pd.DataFrame({"": ['Please Enter One of the Following Player Names:'] + [
                          i for i in dfStat.loc[dfStat['name'].str.contains(
                          formData['name'], case='False')].name.unique()]})
            elif not dfStat.empty:
                dfStat = dfStat.copy()
                dfStat.drop(axis=1, labels=['result'], inplace=True)
                mergeGames.drop(
                    axis=1,
                    labels=[
                        'opponent',
                        'season',
                        'year'],
                    inplace=True)
                dfMerged = dfStat.merge(mergeGames, on='date', how='left')
                dfStat = pd.DataFrame(dfMerged.loc[dfMerged['name'].str.contains(
                formData['name'], case=False)].sum(numeric_only=True)[[
                'gp', 'sv', 'ga', 'mins', 'SO']]).transpose()
                dfStat['sv'] = int(dfStat['sv'])
                dfStat['sv%'] = round(
                    dfStat['sv'] / (dfStat['sv'] + dfStat['ga']), 3)
                dfStat['gaa'] = round((dfStat['ga'] / dfStat['mins']) * 60, 2)
                dfStat.insert(0, 'value', 'Total')
                dfStat.insert(0, 'Split', '')
                for col in [
                    'location',
                    'result',
                    'month',
                    'dow',
                    'opponent',
                    'oppconference',
                    'arena',
                        'tourney']:
                    vals = dfMerged.loc[(dfMerged['name'].str.contains(
                      formData['name'], case=False)) & (dfMerged[col] != '')].groupby(col).sum(
                      numeric_only=True)[['gp', 'sv', 'ga', 'mins', 'SO']]
                    vals['sv%'] = round(
                        vals['sv'] / (vals['sv'] + vals['ga']), 3)
                    vals['gaa'] = round((vals['ga'] / vals['mins']) * 60, 2)
                    vals.reset_index(inplace=True)
                    vals.rename(columns={col: 'value'}, inplace=True)
                    if col == 'month':
                        vals.loc[:, 'value'] = pd.to_datetime(
                            vals['value'], format='%m').dt.strftime('%B')
                    if col == 'dow':
                        vals.loc[:, 'value'] = vals['value'].map(dayNames)
                        col = 'Day'
                    row = pd.DataFrame([col.capitalize() if i == 0 else np.nan for i in range(
                        len(dfStat.columns))]).transpose()
                    row.columns = dfStat.columns
                    vals.insert(0, 'Split', ['' for i in range(len(vals))])
                    vals = pd.concat([row, vals])
                    dfStat = pd.concat([dfStat, vals]).reset_index(drop=True)
                dfStat = dfStat[['Split', 'value', 'gp',
                                 'ga', 'gaa', 'sv', 'sv%', 'SO', 'mins']]
            else:
                dfStat = pd.DataFrame([{"": 'No Data Available'}])
        if (formData['group'] ==
                'records' and formData['name'] not in ['', 'Name']):
            if (len(dfStat.loc[dfStat['name'].str.contains(
                    formData['name'], case=False)].name.unique()) > 1):
                dfStat = pd.DataFrame({"": ['Please Enter One of the Following Player Names:'] +
                                      [i for i in dfStat.loc[dfStat['name'].str.contains(
                                      formData['name'], case='False')].name.unique()]})
            elif not dfStat.empty:
                if formData['position'] == 'skater':
                    queries = [
                        'goals>0',
                        'goals==0',
                        'goals==1',
                        'goals>1',
                        'goals==2',
                        'goals>=3',
                        'assists==0',
                        'assists>0',
                        'assists==1',
                        'assists>1',
                        'assists==2',
                        'assists>=3',
                        'pts==0',
                        'pts>0',
                        'pts==1',
                        'pts>1',
                        'pts==2',
                        'pts==3',
                        'pts>=3',
                    ]
                    qText = [
                        "Scores",
                        "Doesn't Score",
                        "Scores Exactly 1 Goal",
                        "Has a Multi-Goal Game",
                        "Scores Exactly 2 Goals",
                        "Scores 3+ Goals",
                        'Gets 0 Assists',
                        'Gets At Least 1 Assist',
                        'Gets 1 Assist',
                        'Has A Multi-Assist Game',
                        'Gets 2 Assists',
                        'Gets 3+ Assists',
                        'Gets 0 Points',
                        'Gets At Least 1 Point',
                        'Gets Exactly 1 Point',
                        'Has A Multi-Point Game',
                        'Gets Exactly 2 Points',
                        'Gets Exactly 3 Points',
                        'Gets 3+ Points']
                else:
                    dfStat = dfStat.copy()
                    dfStat.drop(axis=1, labels=['result'], inplace=True)
                    queries = [
                        'ga==0',
                        'ga>0',
                        'ga==1',
                        'ga>1',
                        'ga==2',
                        'ga>=3',
                        'sv>0 and sv<20',
                        'sv>=20 and sv<30',
                        'sv>=30 and sv<40',
                        'sv>=40 and sv<50',
                        'sv>=50']
                    qText = [
                        "Allows 0 Goals",
                        "Allows at least 1 Goal",
                        "Allows exactly 1 Goal",
                        "Allows 1+ Goals",
                        "Allows Exactly 2 Goals",
                        "Allows 3+ Goals",
                        'Makes 0-19 Saves',
                        'Makes 20-29 Saves',
                        'Makes 30-39 Saves',
                        'Makes 40-49 Saves',
                        'Makes 50+ Saves']
                mergeGames.drop(
                    axis=1,
                    labels=[
                        'opponent',
                        'season',
                        'year'],
                    inplace=True)
                dfMerged = dfStat.merge(mergeGames, on='date', how='left')
                if len(dfMerged.loc[dfMerged['name'].str.contains(
                        formData['name'], case=False)].name.unique() > 0):
                    name = dfMerged.loc[dfMerged['name'].str.contains(
                        formData['name'], case=False)].name.unique()[0]
                else:
                    name = ''
                qList = []
                for quer in range(len(queries)):
                    rec = dfMerged.query(f'name == "{name}" and {queries[quer]}').groupby(
                        'result').count()['date'].to_dict()
                    for res in ['W', 'L', 'T']:
                        if res not in rec:
                            rec[res] = 0
                    rec['GP'] = rec['W'] + rec['L'] + rec['T']
                    if rec['GP'] != 0:
                        rec['Win%'] = round(
                            (rec['W'] + rec['T'] * .5) / (rec['GP']), 3)
                    else:
                        rec['Win%'] = 0
                    rec[f'BU\'s Record when {name}...'] = qText[quer]
                    qList.append(rec)
                dfStat = pd.DataFrame(
                    qList)[[f'BU\'s Record when {name}...', 'GP', 'W', 'L', 'T', 'Win%']]
            else:
                dfStat = pd.DataFrame([{"": 'No Data Available'}])
        if formData['isAscending'] != '':
            if (formData['sortval'] != '' and formData['sortval'].lower()
             in dfStat.columns or formData['sortval'] in ['W', 'L', 'T', 'SO']):
                sortType = eval(formData['isAscending'].capitalize())
                if (formData['sortval'].lower() != 'date' and sortType != ''
                and formData['sortval'].lower() != 'career'
                and formData['sortval'].lower() != 'season'):
                    sortType = not sortType
                if (formData['sortval'].lower() == 'name' and
                         'last' in dfStat.columns):
                    sortVal = 'last'
                else:
                    if (formData['sortval'] not in ['W', 'L', 'T', 'SO']):
                        sortVal = formData['sortval'].lower()
                    else:
                        sortVal = formData['sortval']
                if sortVal in dfStat.columns:
                    dfStat = dfStat.sort_values(sortVal, ascending=sortType)
                sortVal = formData['sortval']
        else:
            sortVal = ''
            sortType = ''
        if formData['type'] == 'game':
            dfStat = dfStat[:1000]
        return jsonify(statTable=formatStats(dfStat),
                       season_values=seasVals,
                       opponents_values=oppList,
                       sortval=sortVal,
                       isAscending=formData['isAscending'])
    dfStat = burb.dfSkateMens
    seasVals = sorted(set(dfStat['seasons'].to_string(
        index=False).replace(' ', '').replace('\n', ',').split(',')))
    return render_template('players.html',
                           statTable=formatStats(dfStat),
                           season_values=seasVals,
                           selected_startSeas=seasVals[0],
                           selected_endSeas=seasVals[-1],
                           name="Name",
                           number="Number",
                           date="Date")


@app.route('/statsbot', methods=['POST', 'GET'])
def statsbot():
    ''' Loads BU Hockey Stats StatsBot page
    
    Returns: 
      Flask Template : Flask Template containing statbot.html
    '''
    if request.method == 'POST':
        formData = request.form
        if 'query' in formData.keys():
            query = formData['query']
            result = convertToHtmlTable(querystatsbot(query))

            return render_template(
                'statsbot.html',
                result=result,
                query=query.upper()
            )

    return render_template('statsbot.html', result='', query='')

@app.route('/records', methods=['POST', 'GET'])
def records():
    ''' Loads BU Hockey Stats Record page
    
    Returns: 
      json : json structure of Records table
    '''
    buscore = 'BU Score'
    oppscore = 'Opp Score'
    dfRes = burb.dfGames
    dfOrig = burb.dfGames
    minYear = dfRes.year.min()
    maxYear = dfRes.year.max()
    result = ''
    for i in ['W', 'L', 'T']:
        if (dfRes['result'] == i).any():
            res = dfRes.groupby('result').count()['date'][i]
        else:
            res = 0
        result += str(res) + '-'
    result = result.rstrip('-')

    if request.method == 'POST':
        formData = request.form
        if formData['gender'] == 'Mens':
            dfRes = burb.dfGames
            dfOrig = burb.dfGames
        else:
            dfRes = burb.dfGamesWomens
            dfOrig = burb.dfGamesWomens
        minYear = dfRes.year.min()
        maxYear = dfRes.year.max()
        if 'startYear' in formData:
            if formData['startYear'] == '':
                sYear = dfRes.year.min()
            else:
                sYear = formData['startYear']
                if formData['gender'] == 'Womens':
                    sYear = max(2005, int(sYear))
            if formData['endYear'] == '':
                eYear = dfRes.year.max()
            else:
                eYear = formData['endYear']
            dfRes = dfRes.query(f"year>={sYear} and year<={eYear}")
        else:

            sSearch = re.search('(\\d{4})-(\\d{2})', formData['seasonStart'])
            if sSearch is not None:
                sDate = f'9/1/{sSearch.group(1)}'
            else:
                sDate = f'9/1/{dfRes.year.min()}'
            eSearch = re.search('(\\d{4})-(\\d{2})', formData['seasonEnd'])
            if eSearch is not None:
                eDate = f'5/1/{int(eSearch.group(1)) + 1}'
            else:
                eDate = f'5/1/{dfRes.year.max()}'

            dfRes = dfRes.query(f"date>='{sDate}' and date<='{eDate}'")
            sYear = dfRes.year.min()
            eYear = dfRes.year.max()

        if formData['DOW'] != '-1':
            dfRes = dfRes.query(f"dow == {formData['DOW']}")
        if formData['month'] != '0':
            dfRes = dfRes.query(f"month == {formData['month']}")
        if ('day' in formData and formData['day'] != '0'):
            dfRes = dfRes.query(f"day == {formData['day']}")
        if formData['opponent'] != 'all':
            if formData['opponent'] == 'Exhibition:':
                dfRes = dfRes.query("result=='E'")
            elif formData['opponent'] == 'Non-Collegiate:':
                dfRes = dfRes.query('tourney=="Non-Collegiate"')
            else:
                dfRes = dfRes.query(f'opponent==\"{formData["opponent"]}\"')
        result = ''
        if formData['conference'] != 'all':
            if formData['conference'] == 'conf':
                dfRes = dfRes.query("gameType==\'Conference\'")
            elif formData['conference'] == 'nc':
                dfRes = dfRes.query("gameType==\'Non-Conference\'")
            else:
                dfRes = dfRes.query(
                    f"oppconference==\'{formData['conference']}\'")
        if formData['season'] != 'all':
            dfRes = dfRes.query(f"season==\'{formData['season']}\'")
        if formData['tourney'] != 'Tournament':
            dfRes = dfRes.query(f"tourney==\"{formData['tourney']}\"")
        if formData['location'] != 'all':
            dfRes = dfRes.query(f"location==\'{formData['location']}\'")
        if formData['coach'] != 'all':
            dfRes = dfRes.query(f"coach==\"{formData['coach']}\"")
        if formData['arena'] != 'all':
            dfRes = dfRes.query(f"arena==\'{formData['arena']}\'")
        if formData['buscore'] != '':
            buscore = formData['buscore']
            buscore = buscore.split(' ')[0]
            dfRes = dfRes.query(f"BUScore {formData['buscoreop']} {buscore}")
            buscore = formData['buscore']
        else:
            buscore = "BU Score"
        if formData['oppscore'] != '':
            oppscore = formData['oppscore']
            oppscore = oppscore.split(' ')[0]
            dfRes = dfRes.query(
                f"OppoScore {formData['oppscoreop']} {oppscore}")
            oppscore = formData['oppscore']
        else:
            oppscore = "Opp Score"

        for i in ['W', 'L', 'T']:
            if (dfRes['result'] == i).any():
                res = dfRes.groupby('result').count()['date'][i]
            else:
                res = 0
            result += str(res) + '-'
        result = result.rstrip('-')
        sortType = eval(formData['isAscending'].capitalize())
        if formData['sortval'] != 'date':
            sortType = not sortType
        if 'hideEx' in formData:
            dfRes = dfRes.query("result !='E'")
        if ('grouping' in formData and formData['grouping'] != ''):
            if formData['grouping'] == 'Month':
                dfRes = dfRes.copy()
                dfRes.loc[:, 'month'] = pd.to_datetime(
                    dfRes['month'], format='%m').dt.strftime('%B')
            elif formData['grouping'] == 'DOW':
                dfRes = dfRes.copy()
                dfRes.loc[:, 'dow'] = dfRes['dow'].map(dayNames)
            if formData['tabletype'] == 'record':
                groupedData = dfRes.groupby(
                    [formData['grouping'].lower(), 'result']).count()['date']
                gameRecords = groupedData.unstack().fillna(0).astype(int).to_dict(orient='index')
                recsList = []
                for team in gameRecords.keys():
                    recDict = {formData['grouping']: team}
                    for res in ['W', 'L', 'T']:
                        if res not in gameRecords[team]:
                            recDict[res] = 0
                        else:
                            recDict[res] = gameRecords[team][res]

                    if (recDict['W'] + recDict['L'] + recDict['T']) != 0:
                        recDict['Win%'] = round(
                            (recDict['W'] + recDict['T'] * .5) /
                            (recDict['W'] + recDict['L'] + recDict['T']), 3)
                        recsList.append(recDict)
                dfRes = pd.DataFrame(recsList)
            elif formData['tabletype'] == 'first':
                dfRes = dfRes.copy()
                dfRes.fillna('', inplace=True)
                dfRes = dfRes.groupby(formData['grouping'].lower()).first()
                dfRes.reset_index(inplace=True)
            elif formData['tabletype'] == 'last':
                dfRes = dfRes.copy()
                dfRes.fillna('', inplace=True)
                dfRes = dfRes.groupby(formData['grouping'].lower()).last()
                dfRes.reset_index(inplace=True)
        if (formData['sortval'] in ["date", "GD", "BUScore","OppoScore"]
                                     and 'date' not in dfRes.columns):
            if formData['sortval'] != 'date':
                sortType = not sortType
            dfRes = dfRes.sort_values(
                formData['grouping'], ascending=sortType)
        elif (formData['sortval'] in ['Win%', 'W', 'L', 'T', 'sort']
              and 'Win%' not in dfRes.columns):
            sortType = not sortType
            dfRes = dfRes.sort_values('date', ascending=sortType)
        elif formData['sortval'] == 'sort':
            sortType = not sortType
            dfRes = dfRes.sort_values(
                formData['grouping'], ascending=sortType)
        else:
            dfRes = dfRes.sort_values(formData['sortval'], ascending=sortType)

        return jsonify(
            resTable=formatResults(dfRes),
            result=result,
            opponents_values=getOpponentList(dfOrig),
            season_values=list(
                dfOrig.season.unique()),
            conference_values=sorted(
                list(
                    dfOrig.query('oppconference!=""').oppconference.unique())),
            arena_values=sorted(
                list(
                    dfOrig.arena.unique())),
            tourney_values=getTourneyList(dfOrig),
            coach_values=list(
                dfOrig.coach.unique()),
            minYear=int(minYear))

    return render_template(
        'records.html',
        result=result,
        query='',
        resTable=formatResults(dfRes),
        opponents_values=getOpponentList(dfOrig),
        conference_values=sorted(
            list(
                dfOrig.query('oppconference!=""').oppconference.unique())),
        season_values=list(
            dfOrig.season.unique()),
        arena_values=sorted(
            list(
                dfOrig.arena.unique())),
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
        coach_values=list(
            dfOrig.coach.unique()),
        selected_day=0)

def determineRecord(dfRes):
    ''' Generate Record for given DataFrame

    Parameters:
      dfRes (DataFrame) : DataFrame containing results
      
    Returns:
      DataFrame: DataFrame containg W-L-T

    '''
    dfStat = dfRes.groupby(['name', 'opponent']).sum(numeric_only=True)
    dfStat.reset_index(inplace=True)
    dfStat['W'] = 0
    dfStat['L'] = 0
    dfStat['T'] = 0
    dfRec = dfRes.groupby(['name', 'opponent', 'result']).count()
    dfRec.reset_index(inplace=True)
    for res in ['W', 'L', 'T']:
        dfRec[res] = dfRec.query(f'result=="{res}"')['date']
        dfRec[res] = dfRec[res].fillna(0).astype(int)
    dfRec = dfRec.groupby(['name', 'opponent']).sum(numeric_only=True)
    dfRec.reset_index(inplace=True)
    # Merge dfStat and dfRec based on name and opponent columns
    mergedDf = pd.merge(dfStat, dfRec[['name', 'opponent', 'W', 'L', 'T']], on=[
                         'name', 'opponent'], how='left')

    # Sum the 'W', 'L', 'T' columns from dfRec and assign the values to
    # corresponding columns in dfStat
    dfStat['W'] = mergedDf.groupby(['name', 'opponent'])['W_y'].transform(sum, numeric_only=True)
    dfStat['L'] = mergedDf.groupby(['name', 'opponent'])['L_y'].transform(sum, numeric_only=True)
    dfStat['T'] = mergedDf.groupby(['name', 'opponent'])['T_y'].transform(sum, numeric_only=True)

    return dfStat


if __name__ == '__main__':
    app.run(host='localhost', port=5000)
