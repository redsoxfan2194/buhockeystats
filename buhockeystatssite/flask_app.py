'''Boots and Runs BU Hockey Stats Website Via Flask'''
import re
import random
import datetime
import calendar as cal
import numpy as np
import pandas as pd
import pytz
from flask import Flask, render_template, request, jsonify, Response, redirect
from werkzeug.middleware.proxy_fix import ProxyFix
from querystatsbot import querystatsbot, generaterandomstat
from formatstatsdata import formatResults, formatStats, convertToHtmlTable,formatTable
import burecordbook as burb

dayNames = {
    0: 'Monday',
    1: 'Tuesday',
    2: 'Wednesday',
    3: 'Thursday',
    4: 'Friday',
    5: 'Saturday',
    6: 'Sunday'}

numOptions = 5

easternTZ = pytz.timezone('US/Eastern')

app = Flask(__name__)

app.wsgi_app = ProxyFix(app.wsgi_app)  # If behind a proxy, to handle HTTPS detection correctly

@app.before_request
def redirect_to_https():
    if("127.0.0.1" in request.headers['Host']):
        return
    if not request.is_secure and request.headers.get('X-Forwarded-Proto', 'http') == 'http':
        # Redirect to the same URL but with HTTPS scheme
        url = request.url.replace('http://', 'https://', 1)
        return redirect(url, code=301)


@app.route('/sitemap.xml', methods=['GET'])
def generate_sitemap():
    pages = ['', 'about', 'players', 'statsbot', 'records', 'trivia', 'triviagame', 'notables', 'tidbits', 'trio', 'olympians','worldjuniors', 'bloodlines', 'birthdays','shutouts','hattricks']

    xml_sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_sitemap += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

    for page in pages:
        xml_sitemap += '    <url>\n'
        xml_sitemap += f'        <loc>https://www.buhockeystats.com/{page}</loc>\n'
        xml_sitemap += '    </url>\n'

    xml_sitemap += '</urlset>'
    return Response(xml_sitemap, mimetype='text/xml')

@app.route('/robots.txt')
def static_from_root():
    return app.send_static_file('robots.txt')

@app.route('/favicon.ico')
def static_favicon():
    return app.send_static_file('images/favicon.ico')

if(datetime.datetime.now(easternTZ).month>=10 or datetime.datetime.now(easternTZ).month<5):
  try:
    burb.refreshStats()
  except:
    print('Failed to Refresh Stats...Initializing')
  burb.initializeRecordBook()

else:
  print('Initializing Record Book...')
  burb.initializeRecordBook()
  print('Record Book Initialized')

burb.dfGameStatsMens = burb.dfGameStatsMens.query('name!="Unknown"')

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404

@app.route('/', methods=['POST', 'GET'])
def homepage():
    ''' Renders "Home" Page

    Returns:
      Flask Template : flask template containing home.html
    '''
    result = generaterandomstat()
    if (request.method == 'POST'):
        return jsonify(result=result)
    return render_template('home.html', result=result)


@app.route('/about')
def about():
    ''' Renders "About" Page

    Returns:
      Flask Template : flask template containing about.html
    '''
    return render_template('about.html',titletag=' - About')

@app.route('/feedback')
def feedback():
    ''' Renders "Feedback" Page

    Returns:
      Flask Template : flask template containing feedback.html
    '''
    return render_template('feedback.html',titletag=' - Feedback')

@app.route('/missingdates')
def missingdates():
    ''' Renders "Missing Dates" Page

    Returns:
      Flask Template : flask template containing missing_dates.html
    '''
    return render_template('missing_dates.html',missingDates=formatTable(burb.getMissingDates()),titletag=' - Missing Dates')


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
                    dfStat.loc[:, 'pen'] = pens[0].replace(
                        '—', np.nan).astype('Int64')
                    dfStat.loc[:, 'pim'] = pens[1].replace(
                        '—', np.nan).astype('Int64')
                elif formData['position'] == 'goalie':
                    dfStat = burb.dfSeasGoalieMens
                    rec = dfStat.record.str.split('-', expand=True)
                    dfStat['W'] = rec[0].replace('', -1).astype(int)
                    dfStat['L'] = rec[1].replace('', -1).astype(int)
                    dfStat['T'] = rec[2].replace('', -1).astype(int)
            elif formData['type'] == 'game' or formData['type']=='streak':
                if formData['position'] == 'skater':
                    dfStat = pd.merge(burb.dfGameStatsMens,burb.dfGames[['date','location','arena']],on='date')
                elif formData['position'] == 'goalie':
                    dfStat = pd.merge(burb.dfGameStatsGoalieMens,burb.dfGames[['date','location','arena']],on='date')
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
                    dfStat.loc[:, 'pen'] = pens[0].replace(
                        '—', np.nan).astype('Int64')
                    dfStat.loc[:, 'pim'] = pens[1].replace(
                        '—', np.nan).astype('Int64')
                elif formData['position'] == 'goalie':
                    dfStat = burb.dfSeasGoalieWomens
                    rec = dfStat.record.str.split('-', expand=True)
                    dfStat['W'] = rec[0].astype(int)
                    dfStat['L'] = rec[1].astype(int)
                    dfStat['T'] = rec[2].astype(int)
            elif formData['type'] == 'game' or formData['type']=='streak':
                if formData['position'] == 'skater':
                    dfStat = pd.merge(burb.dfGameStatsWomens,burb.dfGamesWomens[['date','location','arena']],on='date')
                elif formData['position'] == 'goalie':
                    dfStat = pd.merge(burb.dfGameStatsGoalieWomens,burb.dfGamesWomens[['date','location','arena']],on='date')
        if seasVals == []:
            seasVals = list(dfStat.season.unique())
        sSeas = formData['seasonStart']
        eSeas = formData['seasonEnd']
        if sSeas not in seasVals:
            sIdx = 0
            sSeas = seasVals[0]
        else:
            sIdx = seasVals.index(sSeas)
        if(eSeas not in seasVals):
            eIdx = len(seasVals)-1
            seasVals=list(dfStat.season.unique())
        else:
          eIdx = seasVals.index(eSeas) + 1
        if sIdx > eIdx:
            sIdx, eIdx = eIdx, sIdx
            sSeas = seasVals[sIdx]
            eSeas = seasVals[eIdx]
        valSeas = seasVals[sIdx:eIdx]
        dfStat = filterStats(formData,dfStat)
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
                dfStat = dfStat.loc[(dfStat['season'].isin(valSeas)) & (
                    dfStat['season'] == formData['season'])]
        else:
            if formData['type'] != 'career':
                dfStat = dfStat.loc[dfStat['season'].isin(valSeas)]

        if formData['type'] != 'career':
            if (formData['pos'] !=
                    'all' and formData['position'] != 'goalie'):
                dfStat = dfStat.loc[dfStat['pos'].str.contains(formData['pos'])]
            if formData['yr'] != 'all':
                dfStat = dfStat.query(f"yr=='{formData['yr']}'")
        if formData['type'] == 'game':
            oppList = sorted(list(dfStat.opponent.unique()))
            arenaList = sorted(list(dfStat.arena.unique()))
            if formData['opponent'] != 'all':
                dfStat = dfStat.query(f"opponent==\"{formData['opponent']}\"")
            if formData['date'] != '':
                dfStat = dfStat.query(f"date==\"{formData['date']}\"")
            if formData['arena'] != 'all':
                dfStat = dfStat.query(f"arena==\"{formData['arena']}\"")
            if formData['location'] != 'all':
                dfStat = dfStat.query(f"location==\"{formData['location']}\"")
        else:
            oppList = []
            arenaList = []
        if formData['name'] != '':
            dfStat = dfStat.loc[dfStat['name'].str.contains(
                formData['name'].strip(), case=False)]
        if formData['number'] != '':
            dfStat = dfStat.query(f"number == {formData['number']}")
        if (formData['group'] not in ['', 'splits', 'records']
                and formData['position'] == 'skater'):
            dfStat = dfStat.groupby(
                ['name', formData['group']]).sum(numeric_only=True)
            dfStat = dfStat.reset_index()
            dfStat = dfStat[['name', formData['group'],
                             'gp', 'goals', 'assists', 'pts']]
        if (formData['group'] not in ['', 'splits', 'records']
                and formData['position'] == 'goalie'):
            dfStat = determineRecord(dfStat,formData['group'])
            dfStat = dfStat.groupby(
                ['name', formData['group']]).sum(numeric_only=True)
            dfStat = dfStat.reset_index()
            dfStat['sv%'] = dfStat['sv'] / (dfStat['sv'] + dfStat['ga'])
            dfStat['gaa'] = (dfStat['ga'] / dfStat['mins']) * 60
            dfStat = dfStat[['name', formData['group'], 'gp', 'ga',
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
                                           formData['name'], case=False)].name.unique()]})
            elif not dfStat.empty:
                mergeGames.drop(
                    axis=1,
                    labels=[
                        'opponent',
                        'season',
                        'year',
                        'location',
                        'arena'],
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
                # add blank row
                row = pd.DataFrame(["" if i == 0 else np.nan for i in range(
                    len(dfStat.columns))]).transpose()
                row.columns = dfStat.columns
                dfStat = pd.concat([dfStat, row]).reset_index(drop=True)

                name = (dfMerged.loc[(dfMerged['name'].str.contains(
                        formData['name'], case=False))]['name'].unique()[0])
                row = pd.DataFrame(["Longest Point Streak" if i == 0 else np.nan for i in range(
                    len(dfStat.columns))]).transpose()
                row.columns = dfStat.columns
                row['value']=burb.getMaxStreak(dfMerged,name,'pts')
                dfStat = pd.concat([dfStat, row]).reset_index(drop=True)

            else:
                dfStat = pd.DataFrame([{"": 'No Data Available'}])
        if (formData['group'] == 'splits' and formData['name'] not in
                ['', 'Name'] and formData['position'] == 'goalie'):
            if (len(dfStat.loc[dfStat['name'].str.contains(
                    formData['name'], case=False)].name.unique()) > 1):
                dfStat = pd.DataFrame({"": ['Please Enter One of the Following Player Names:'] + [
                    i for i in dfStat.loc[dfStat['name'].str.contains(
                        formData['name'], case=False)].name.unique()]})
            elif not dfStat.empty:
                dfStat = dfStat.copy()
                dfStat.drop(axis=1, labels=['result'], inplace=True)
                mergeGames.drop(
                    axis=1,
                    labels=[
                        'opponent',
                        'season',
                        'year',
                        'location',
                        'arena'],
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
                                          formData['name'], case=False)].name.unique()]})
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
                        'ga<=1',
                        'ga==1',
                        'ga>1',
                        'ga==2',
                        'ga<=2',
                        'ga>=3',
                        'sv>0 and sv<20',
                        'sv>=20 and sv<30',
                        'sv>=30 and sv<40',
                        'sv>=40 and sv<50',
                        'sv>=50']
                    qText = [
                        "Allows 0 Goals",
                        "Allows at least 1 Goal",
                        "Allows 1 Goal or fewer",
                        "Allows exactly 1 Goal",
                        "Allows 1+ Goals",
                        "Allows Exactly 2 Goals",
                        "Allows 2 Goals or fewer",
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
                        formData['name'], case=False)].name.unique()) > 0:
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
        if(formData['type'] == 'streak'):
            streakMin=3
            if(formData['streakmin']!=''):
              streakMin=max(int(formData['streakmin']),3)
            if(formData['sortval']!=''):
              sortVal=formData['sortval']
              if(formData['isAscending']==''):
                isAsc=True
              else:
                isAsc=eval(formData['isAscending'].capitalize())
            else:
              sortVal="Length"
              isAsc=True
            dfStat = burb.getStreaks(dfStat,formData['streak'],streakMin,sortVal,isAsc)
        return jsonify(statTable=formatStats(dfStat),
                       season_values=seasVals,
                       opponents_values=oppList,
                       arena_values=arenaList,
                       sortval=sortVal,
                       isAscending=formData['isAscending'])
    dfStat = burb.dfSkateMens
    seasVals = sorted(set(dfStat['seasons'].to_string(
        index=False).replace(' ', '').replace('\n', ',').split(',')))
    return render_template('players.html',titletag=" - Players",
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
            qStr=querystatsbot(query)
            oppsList=list(set(list(burb.dfGames.loc[burb.dfGames['opponent'].str.contains(' ')].opponent.unique())+\
              list(burb.dfGamesWomens.loc[burb.dfGamesWomens['opponent'].str.contains(' ')].opponent.unique())))+['Boston University']
            for q in range(len(qStr)):
              for team in oppsList:
                if(team.strip() in qStr[q]):
                  qStr[q]=qStr[q].replace(team,team.replace(' ','!!'))
            result = convertToHtmlTable(qStr)

            return render_template(
                'statsbot.html',titletag=' - Stats Bot',
                result=result,
                query=query.upper()
            )

    return render_template('statsbot.html', titletag=' - Stats Bot', result='', query='')


@app.route('/records', methods=['POST', 'GET'])
def records():
    ''' Loads BU Hockey Stats Record page

    Returns:
      json : json structure of Records table
    '''
    buscore = 'BU Score'
    oppscore = 'Opp Score'
    burank = 'BU Rank'
    opprank = 'Opp Rank'
    totalgoals = 'Total Goals'
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
        if formData['result'] != 'all':
            dfRes = dfRes.query(f"result == \"{formData['result']}\"")
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
        if formData['tourney'] != 'All':
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
        if formData['totalgoals'] != '':
            totalgoals = formData['totalgoals']
            totalgoals = totalgoals.split(' ')[0]
            dfRes = dfRes.query(f"TG {formData['tgop']} {totalgoals}")
            totalgoals = formData['totalgoals']
        else:
            totalgoals = "Total Goals"
        if formData['oppscore'] != '':
            oppscore = formData['oppscore']
            oppscore = oppscore.split(' ')[0]
            dfRes = dfRes.query(
                f"OppoScore {formData['oppscoreop']} {oppscore}")
            oppscore = formData['oppscore']
        else:
            oppscore = "Opp Score"

        if formData['burank'] != '':
            burank = formData['burank']
            burank = burank.split(' ')[0]
            dfRes = dfRes.query(f"BURank {formData['burankop']} {burank}")
            burank = formData['burank']
        else:
            burank = "BU Rank"
        if formData['opprank'] != '':
            opprank = formData['opprank']
            opprank = opprank.split(' ')[0]
            dfRes = dfRes.query(
                f"OppRank {formData['opprankop']} {opprank}")
            opprank = formData['opprank']
        else:
            opprank = "Opp Rank"

        for i in ['W', 'L', 'T']:
            if (dfRes['result'] == i).any():
                res = dfRes.groupby('result').count()['date'][i]
            else:
                res = 0
            result += str(res) + '-'
        result = result.rstrip('-')
        if(formData['isAscending']!=''):
          sortType = eval(formData['isAscending'].capitalize())
        else:
          sortType=True
        if formData['sortval'] != 'date':
            sortType = not sortType
        if 'hideEx' in formData:
            dfRes = dfRes.query("result !='E'")
        if ('grouping' in formData and formData['grouping'] != ''):
            if formData['tabletype'] == 'record':
                groupedData = dfRes.groupby(
                    [formData['grouping'].lower(), 'result']).count()['date']
                gameRecords = groupedData.unstack().fillna(
                    0).astype(int).to_dict(orient='index')
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
                        recDict['GP']=recDict['W'] + recDict['L'] + recDict['T']
                        recsList.append(recDict)

                dfRes = pd.DataFrame(recsList)
                recCols = dfRes.columns.tolist()
                recCols.insert(1, recCols.pop())
                dfRes = dfRes[recCols]

                if formData['grouping'] == 'Month':
                  dfRes = dfRes.copy()
                  dfRes.loc[:, 'Month'] = pd.to_datetime(
                  dfRes['Month'], format='%m').dt.strftime('%B')
                elif formData['grouping'] == 'DOW':
                  dfRes = dfRes.copy()
                  dfRes.loc[:, 'DOW'] = dfRes['DOW'].map(dayNames)
            elif formData['tabletype'] == 'first':
                dfRes = dfRes.copy()
                dfRes.fillna('', inplace=True)
                dfRes = dfRes.query('result != "N"').groupby(formData['grouping'].lower()).first()
                dfRes.reset_index(inplace=True)
                if formData['grouping'] == 'Month':
                  dfRes = dfRes.copy()
                  dfRes.loc[:, 'month'] = pd.to_datetime(
                  dfRes['month'], format='%m').dt.strftime('%B')
                elif formData['grouping'] == 'DOW':
                  dfRes = dfRes.copy()
                  dfRes.loc[:, 'dow'] = dfRes['dow'].map(dayNames)
            elif formData['tabletype'] == 'last':
                dfRes = dfRes.copy()
                dfRes.fillna('', inplace=True)
                dfRes = dfRes.query('result != "N"').groupby(formData['grouping'].lower()).last()
                dfRes.reset_index(inplace=True)
                if formData['grouping'] == 'Month':
                  dfRes = dfRes.copy()
                  dfRes.loc[:, 'month'] = pd.to_datetime(
                  dfRes['month'], format='%m').dt.strftime('%B')
                elif formData['grouping'] == 'DOW':
                  dfRes = dfRes.copy()
                  dfRes.loc[:, 'dow'] = dfRes['dow'].map(dayNames)
            elif formData['tabletype'] ==  'streaks':
                dfRes = generateStreaks(dfRes.copy())

        if (formData['sortval'] in ["date", "GD", "BUScore", "OppoScore", "BURank", "OppRank","TG"]
                and 'date' not in dfRes.columns):
            if formData['sortval'] != 'date':
                sortType = not sortType
            if(not dfRes.empty and "Longest Streak" not in dfRes.columns):
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
            if formData['grouping'] == 'Month':
                dfRes = dfRes.copy()
                dfRes.loc[:, 'Month'] = pd.to_datetime(
                    dfRes['Month'], format='%m').dt.strftime('%B')
            elif formData['grouping'] == 'DOW':
                dfRes = dfRes.copy()
                dfRes.loc[:, 'DOW'] = dfRes['DOW'].map(dayNames)
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
        'records.html',titletag=' - Records',
        result=result,
        query='',
        resTable=formatResults(dfRes.query('result != "E"')),
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
        totalgoals=totalgoals,
        burank=burank,
        opprank=opprank,
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


@app.route('/notables')
def noteables():
    ''' Renders "Season Notables" Page

    Returns:
      Flask Template : flask template containing season_notables.html
    '''
    #currSeasonM=burb.dfGameStatsMens.season.tail(1).to_string(index=False,header=False)
    #currSeasonW=burb.dfGameStatsWomens.season.tail(1).to_string(index=False,header=False)
    currSeasonM=burb.dfSeasSkateMens.season.tail(1).to_string(index=False,header=False)
    currSeasonW=burb.dfSeasSkateWomens.season.tail(1).to_string(index=False,header=False)
    return render_template(
    'season_notables.html',titletag=' - Notables',
    mHatTricksCurr=burb.getHatTricks(burb.dfGameStatsMens,currSeasonM),
    mShutoutsCurr=burb.getShutouts(burb.dfGameStatsGoalieMens,currSeasonM),
    mLongPtStreak=burb.getTopStreaks(burb.dfGameStatsMens,currSeasonM),
    mActivePtStreak=burb.getActiveStreaks(burb.dfGameStatsMens,currSeasonM),
    wHatTricksCurr=burb.getHatTricks(burb.dfGameStatsWomens,currSeasonW),
    wShutoutsCurr=burb.getShutouts(burb.dfGameStatsGoalieWomens,currSeasonW),
    wLongPtStreak=burb.getTopStreaks(burb.dfGameStatsWomens,currSeasonW),
    wActivePtStreak=burb.getActiveStreaks(burb.dfGameStatsWomens,currSeasonW),
    currSeasonM=currSeasonM,
    currSeasonW=currSeasonW)

@app.route('/trio')
def trio():
    ''' Renders "Terrier Trio" Page

    Returns:
      Flask Template : flask template containing trio.html
    '''
    return render_template(
    'trio.html',titletag=' - T. Anthony Trio Terrier Tallies"')

@app.route('/tidbits')
def tidbits():
    ''' Renders "Tidbits" Page

    Returns:
      Flask Template : flask template containing tidbits.html
    '''
    return render_template(
    'tidbits.html',titletag=' - Tidbits')
    
@app.route('/bloodlines')
def bloodlines():
    ''' Renders "Bloodlines" Page

    Returns:
      Flask Template : flask template containing bloodlines.html
    '''
    return render_template(
    'bloodlines.html',siblings=formatTable(burb.getSiblings()),family=formatTable(burb.getFamily()),titletag=' - Bloodlines')

@app.route('/worldjuniors')
def worldjuniors():
    ''' Renders "worldjuniors" Page

    Returns:
      Flask Template : flask template containing worldjuniors.html
    '''
    return render_template(
    'worldjuniors.html',worldjuniors=formatTable(burb.getWJC()),titletag=' - World Junior Championship')

@app.route('/olympians')
def olympians():
    ''' Renders "Olympians" Page

    Returns:
      Flask Template : flask template containing worldjuniors.html
    '''
    return render_template(
    'olympians.html',molympians=formatTable(burb.getOlympians('Mens')),wolympians=formatTable(burb.getOlympians('Womens')),titletag=' - Olympians')


@app.route('/shutouts')
def shutouts():
    ''' Renders "Shutouts" Page

    Returns:
      Flask Template : flask template containing shutouts.html
    '''
    return render_template(
    'shutouts.html',
    mShutouts=formatTable(burb.getShutoutList('Mens')),
    wShutouts=formatTable(burb.getShutoutList('Womens')),titletag=' - Shutouts')

@app.route('/hattricks')
def hattricks():
    ''' Renders "Hat Tricks" Page

    Returns:
      Flask Template : flask template containing hattricks.html
    '''
    return render_template(
    'hattricks.html',
    mHattricks=formatTable(burb.getHatTrickList('Mens')),
    wHattricks=formatTable(burb.getHatTrickList('Womens')),titletag=' - Hat Tricks')

@app.route('/birthday')
@app.route('/birthdays',methods=['GET'])
def birthdays():
    d_str = request.args.get('date')  # Get the 'year' parameter from the request
        # You can now use the 'year' variable to perform any logic you need
    if(d_str is None):
      today = datetime.datetime.now()
      # Get month and year
      year = request.args.get('year', today.year, type=int)
      month = request.args.get('month', today.month, type=int)
      day = request.args.get('day', today.day, type=int)
    else:
      today = d_str.split('-')
      year = int(today[0])
      month = int(today[1])
      day = 1

    # Create a date for the first day of the month
    first_day = datetime.datetime(year, month, 1)

    # Calculate the number of days in the month
    num_days = (first_day + datetime.timedelta(days=32)).replace(day=1) - datetime.timedelta(days=1)

    birthdays = burb.getBirthdays(year,month)

    # Create a calendar grid
    calendar = [
        [None] * 7 for _ in range((num_days.day + first_day.weekday() + 7) // 7)
    ]

    # Fill in the calendar with the days of the month
    for day in range(1, num_days.day + 1):
        row = (day + first_day.weekday()) // 7
        col = (day + first_day.weekday()) % 7
        calendar[row][col] = {
            'day': day,
            'birthdays': birthdays[birthdays['Day'] == day]['name_age'].tolist()
        }

    if(not any(calendar[0])):
      calendar.pop(0)

    return render_template(
        'birthdays.html',
        titletag='- Birthdays',
        year=year,
        month=cal.month_name[month],
        calendar=calendar,
        birthdays=birthdays,
        prev_month=(first_day - datetime.timedelta(days=1)).strftime('%Y-%m'),
        next_month=(first_day + datetime.timedelta(days=num_days.day)).strftime('%Y-%m')
    )


@app.route('/trivia', methods=['POST', 'GET'])
def dailyTrivia():
    ''' Renders "Trivia Challenge" Page

    Returns:
      Flask Template : flask template containing daily_trivia.html
    '''
    DOW = dayNames[datetime.datetime.now(easternTZ).weekday()]
    titles={'Monday':"Beanpot Monday",
      'Tuesday':"Terrific Terrier Tuesday",  # Awards Related Questions
      'Wednesday':"Womens Hockey Wednesday",
      'Thursday':"Jersday Thursday",
      'Friday': "Foe Friday",  # Questions About Opponents
      'Saturday':"Staturday", # Player Stat Questions
      'Sunday':"Sunday Scores"} # score related questions

    # seed is Day of Year + Year
    launchSeed=2267
    seedVal=int(datetime.datetime.now(easternTZ).strftime('%j'))+int(datetime.datetime.now(easternTZ).strftime('%Y'))
    random.seed(seedVal)
    np.random.seed(seedVal)

    if (request.method == 'POST'):
        quiz = []
        for q in range(5):

            if DOW == "Monday":
                question, choices, answer = generateBeanpotQuestion()

            elif DOW == "Tuesday":
                question, choices, answer = generateAwardQuestion()

            elif DOW == "Wednesday":
                qChoice = random.choice(['jersey', 'season', 'result'])
                if (qChoice == 'jersey'):
                    question, choices, answer = generateJerseyQuestion(
                        "Womens")
                elif (qChoice == 'season'):
                    question, choices, answer = generateSeasonStatQuestion(
                        "Womens")
                elif (qChoice == 'result'):
                    question, choices, answer = generateResultsQuestion(
                        "Womens")

            elif DOW == "Thursday":
                question, choices, answer = generateJerseyQuestion()

            elif DOW == "Friday":
                question, choices, answer = generateResultsQuestion()

            elif DOW == "Saturday":
                question, choices, answer = generateSeasonStatQuestion()

            elif DOW == "Sunday":
                question, choices, answer = generateScoreQuestion()

            random.shuffle(choices)
            ques = {'question': question, 'choices': choices,
                    'correctAnswer': choices.index(answer)}

            quiz.append(ques)
            random.shuffle(quiz)
        return jsonify(quiz=quiz,triviaNum=(seedVal-launchSeed)+1)
    return render_template('daily_trivia.html',titletag=' - Daily Trivia', topic=titles[DOW])


@app.route('/triviagame', methods=['POST', 'GET'])
def triviagame():
    ''' Renders "Trivia Free Play" Page

    Returns:
      Flask Template : flask template containing trivia_game.html
    '''
    random.seed(None)
    np.random.seed(None)
    if (request.method == 'POST'):
        quiz = []
        qType = []
        formData = request.form
        if ('gender' not in formData):
            gender = 'Mens'
        else:
            gender = formData['gender']
        for type in ['jersey', 'season', 'result', 'beanpot']:
            if (type in formData):
                qType.append(type)
        if (qType == []):
            qType = ['jersey', 'season', 'result', 'beanpot']
        numQuestions = int(formData['numQuestions'])
        distQ = distributeQuestions(len(qType), numQuestions)
        qDict = {}
        qNum = 0
        for q in range(len(qType)):
            qDict[qType[q]] = distQ[q]
        while (qNum < numQuestions):
            sYear = formData['seasonStart'][:4]
            eYear = formData['seasonEnd'][:4]
            if (sYear == eYear):
                eYear = str(int(eYear)+1)
            seasList = burb.dfGames.query(
                f'year>{sYear} and year<={eYear}').season.unique()
            random.shuffle(qType)
            qChoice = random.choice(qType)

            if (qDict[qChoice] == 0):
                continue
            if (qChoice == 'jersey'):
                question, choices, answer = generateJerseyQuestion(gender, seasList)
            elif (qChoice == 'season'):
                question, choices, answer = generateSeasonStatQuestion(gender, seasList)
            elif (qChoice == 'result'):
                question, choices, answer = generateResultsQuestion(gender, seasList)
            elif (qChoice == 'beanpot'):
                question, choices, answer = generateBeanpotQuestion(gender, seasList)
            random.shuffle(choices)
            qDict[qChoice] -= 1
            qNum += 1
            ques = {'question': question, 'choices': choices,
                    'correctAnswer': choices.index(answer)}
            quiz.append(ques)
            random.shuffle(quiz)
        return jsonify(quiz=quiz)

    return render_template('trivia_game.html',titletag=' - Trivia Game',
                           season_values=burb.dfGames.season.unique(),
                           selected_startSeas=burb.dfGames.season.min(),
                           selected_endSeas=burb.dfGames.season.max())


def distributeQuestions(numCategories, numQuestions):

    # Calculate the number of questions per category.
    quesPerCat = numQuestions // numCategories

    # Calculate the remainder questions.
    remQs = numQuestions % numCategories

    # Create a list to hold the distribution of questions per category.
    distribution = [quesPerCat] * numCategories

    # Randomly assign the remainder questions to the categories.
    for i in range(remQs):
        randCat = random.randint(0, numCategories - 1)
        distribution[randCat] += 1

    return distribution


def generateJerseyQuestion(gender="Mens", seasList=burb.dfGames.season.unique()):
    quesType = random.choice(['number', 'name'])
    dfJerSeas = pd.DataFrame()
    if (gender == 'Mens'):
        dfJers = burb.dfJerseyMens.copy()
    elif (gender == 'Womens'):
        dfJers = burb.dfJerseyWomens.copy()
    validQuestion = False
    while (not validQuestion):
        season = random.choice(seasList)
        dfJerSeas = dfJers.loc[dfJers['season'].str.contains(season)]
        if (len(dfJerSeas) < numOptions):
            continue
        correctAnswer = dfJerSeas.sample()
        validChoices = False
        while (not validChoices):
            wrongAnswers = dfJerSeas.sample(n=numOptions-1)
            if (correctAnswer['name'].unique()[0] not in wrongAnswers['name'].unique()):
                validChoices = True
        validQuestion = True
        choices = pd.concat([wrongAnswers, correctAnswer])
    if quesType == 'number':
        question = f'What number did {correctAnswer["name"].to_string(index=False,header=False)} wear in {season}?'
        options = choices['number'].to_list()
        answer = int(correctAnswer["number"].to_string(
            index=False, header=False))

    elif quesType == 'name':
        question = f'Who wore #{correctAnswer["number"].to_string(index=False,header=False)} in {season}?'
        options = choices['name'].to_list()
        answer = correctAnswer["name"].to_string(index=False, header=False)
    return question, options, answer


def generateSeasonStatQuestion(gender="Mens", seasList=burb.dfGames.season.unique()):
    dfStatSeas = pd.DataFrame()
    if (gender == 'Mens'):
        dfSeas = burb.dfSeasSkateMens.copy()
    elif (gender == 'Womens'):
        dfSeas = burb.dfSeasSkateWomens.copy()
    validQuestion = False
    while (not validQuestion):
        season = random.choice(seasList)
        dfStatSeas = dfSeas.loc[dfSeas['season'] == season]
        quesType = random.choice(['', 'FR', 'SO', 'JR', 'SR'])
        posType = random.choice(['', 'F', 'D'])
        stat = random.choice(['goals', 'assists', 'pts'])
        nameVal = random.choice(['name','value'])
        qStr = ''
        if (quesType != '' and posType != ''):
            qStr = f' yr == "{quesType}" and pos == "{posType}"'
            quesStr = f"all {quesType} {posType}"
        elif (quesType != ''):
            qStr = f' yr == "{quesType}"'
            quesStr = f"all {quesType}"
        elif (posType != ''):
            qStr = f' pos == "{posType}"'
            quesStr = f"all {posType}"
        else:
            quesStr = "all Terriers"
        if (qStr != ''):
            correctAnswer = dfStatSeas.query(qStr).sort_values(
                stat, ascending=False).head(1)
        else:
            correctAnswer = dfStatSeas.sort_values(
                stat, ascending=False).head(1)
        if(nameVal=='name'):
          question = f'Who lead {quesStr} in {stat} in {season}?'
          validChoices = False
          vChoiceCounter = 0
          broken = False
          while (not validChoices):
              if (len(dfStatSeas.query('pos != "G"')) < numOptions or vChoiceCounter > 10):
                  broken = True
                  break
              wrongAnswers = dfStatSeas.query('pos != "G"').sample(n=numOptions-1)
              if ((len(correctAnswer['name'].unique()) > 0) and correctAnswer['name'].unique()[0] not in wrongAnswers['name'].unique()):
                  validChoices = True
              vChoiceCounter += 1
          if (broken):
              continue
          choices = pd.concat([wrongAnswers, correctAnswer])
          options = choices['name'].to_list()
          answer = correctAnswer["name"].to_string(index=False, header=False)
          if (qStr != ''):
              if ((dfStatSeas.query(qStr).sort_values(stat, ascending=False).head(1)[stat] != 0).bool()):
                  validQuestion = True
          else:
              if ((dfStatSeas.sort_values(stat, ascending=False).head(1)[stat] != 0).bool()):
                  validQuestion = True
          if (validQuestion):
              break
        elif(nameVal=='value'):
          question = f'{correctAnswer["name"].to_string(index=False, header=False)} lead {quesStr} with ____ {stat} in {season}.'
          if(correctAnswer[stat].empty or correctAnswer[stat].isnull().bool()):
            continue
          answer = int(correctAnswer[stat].astype(int).to_string(index=False, header=False))
          if (qStr != ''):
              if ((dfStatSeas.query(qStr).sort_values(stat, ascending=False).head(1)[stat] != 0).bool()):
                  validQuestion = True
          else:
              if ((dfStatSeas.sort_values(stat, ascending=False).head(1)[stat] != 0).bool()):
                  validQuestion = True
          options = []
          while (len(set(options)) < numOptions-1 or answer in options):
              if(answer-5<0):
                low=1
              else:
                low=answer-5
              high=answer+10
              options = random.sample(range(low, high), numOptions-1)
          options.append(answer)
    return question, options, answer


def generateResultsQuestion(gender="Mens", seasList=burb.dfGames.season.unique()):
    if (gender == "Mens"):
        dfG = burb.dfGames.copy()
    elif (gender == "Womens"):
        dfG = burb.dfGamesWomens.copy()
    qOps = ['first', 'last', 'road']
    qChoice = random.choice(qOps)
    teamsList = dfG.loc[dfG['season'].isin(seasList)].opponent.unique()
    if (qChoice in ['first', 'last']):
        if (qChoice == 'last'):
            lastGame = dfG.loc[(dfG['result'] != "E") & (dfG['result'] != "N") & (~dfG['tourney'].isin(['Non-Collegiate', 'Non-Collegiate', '1932 NEAAU Olympic tryouts',
                                                                              '1932 NEAAU Olympic tryouts-Non-Collegiate', 'NEIHL Tournament', 'ECAC Tournament', 'Hockey East Tournament'])) & (dfG['opponent'].isin(teamsList))].groupby('opponent').last()
            ans = lastGame.sample()

        elif (qChoice == 'first'):
            firstGame = dfG.loc[(dfG['result'] != "E") & (dfG['result'] != "N") & (~dfG['tourney'].isin(['Non-Collegiate', 'Non-Collegiate', '1932 NEAAU Olympic tryouts',
                                                                               '1932 NEAAU Olympic tryouts-Non-Collegiate', 'NEIHL Tournament', 'ECAC Tournament', 'Hockey East Tournament'])) & (dfG['opponent'].isin(teamsList))].groupby('opponent').first()
            ans = firstGame.sample()

        ans.reset_index(inplace=True)
        oppName = ans['opponent'].to_string(index=False)
        season = ans['season'].to_string(index=False)
        coach = ans['coach'].to_string(index=False)
        seasons = list(dfG.season.unique())
        seasIdx = seasons.index(season)
        eIdx = seasIdx+10
        sIdx = seasIdx-5
        if ((seasIdx-5) < 0):
            sIdx = 0
            eIdx += abs(int(seasIdx)-10)
        if (eIdx > len(seasons)):
            eIdx = len(seasons)
            sIdx -= (seasIdx+5)-len(seasons)
        ops = []
        while (len(set(ops)) < numOptions-1 or seasIdx in ops):
            ops = random.sample(range(sIdx, eIdx), numOptions-1)

        options = [seasons[i] for i in ops]
        options.append(season)
        question = f"BU's {qChoice} game vs {oppName} occurred during which season?"
        answer = season
    elif (qChoice == 'road'):
        ans = dfG.loc[dfG['opponent'].isin(teamsList)].query(
            'location=="Away"').groupby(['opponent', 'arena']).count()['date'].sample()
        arenaName = ans.index[0][1]
        numGames = ans.values[0]
        answer = ans.index[0][0]
        if (numGames == 1):
            numGames = str(numGames) + " game"
        else:
            numGames = str(numGames) + " games"
        options = []
        while (len(set(options)) < numOptions-1 or answer in options):
            options = dfG.loc[dfG['opponent'].isin(teamsList)].query(
                'location=="Away"').opponent.sample(numOptions-1).to_list()
        options.append(answer)
        question = f"BU has played {numGames} at {arenaName} vs:"
    return question, options, answer


def generateBeanpotQuestion(gender="Mens", seasList=burb.dfGames.season.unique()):
    if (gender == "Mens"):
        dfBean = burb.dfBeanpot.copy()
    elif (gender == "Womens"):
        dfBean = burb.dfBeanpotWomens.copy()
    ops = ['finish', 'championship']
    opChoice = random.choice(ops)
    validQuestion = False
    while (not validQuestion):
        ans = dfBean.sample()
        if (opChoice == 'finish'):
            place = ['champion', 'runnerup', 'consWinner', 'consLoser']
            pChoice = random.choices(place, weights=[5, 2, 1, 1])[0]
            answer = ans[pChoice].to_string(index=False)
            pQues = {'champion': "Who won the", 'runnerup': "Who was the runner-up of the",
                     'consWinner': "Who finished 3rd in the", 'consLoser': "Who finished last in the"}
            question = f"{pQues[pChoice]} {ans['year'].to_string(index=False)} Beanpot?"
            if (answer == "Brown"):
                options = ['Brown', 'Boston College',
                           'Northeastern', 'Harvard']
            else:
                options = ['Boston University',
                           'Boston College', 'Northeastern', 'Harvard']
        if (opChoice == 'championship'):
            champCombo = tuple(ans[['champion', 'runnerup']].to_csv(
                index=False, header=False).strip('\r\n').split(','))
            combos = [('Boston University', 'Boston College'),
                      ('Boston University', 'Northeastern'),
                      ('Boston University', 'Harvard'),
                      ('Boston College', 'Northeastern'),
                      ('Boston College', 'Harvard'),
                      ('Harvard','Northeastern')]
            invCombo=champCombo[1],champCombo[0]
            options=[]
            for op in combos:
                op = list(op)
                options.append(f"{op[0]} vs {op[1]}")
            if(tuple(champCombo) in combos):
              answer = f"{champCombo[0]} vs {champCombo[1]}"
            else:
              answer = f"{invCombo[0]} vs {invCombo[1]}"
            question = f"Which of the following was the championship matchup for the {ans['year'].to_string(index=False)} Beanpot?"
        if (answer == ''):
            continue
        validQuestion = True
    return question, options, answer


def generateAwardQuestion():
    validQuestion = False
    while (not validQuestion):
        broken = False
        qType = random.choice(list(burb.awardsDict.keys()))
        kName = random.choice(list(burb.awardsDict[qType].keys()))
        if (qType in ['Spencer Penrose Award Winner', 'NCAA Scoring Champion','NCAA Tournament Most Outstanding Player']):
            question = f"{kName} was the {qType} in what year?"
            answer = random.choice(burb.awardsDict[qType][kName])
            options = []
            while (answer in options or len(set(options)) < numOptions-1):
                options = random.sample(range(answer-2, answer+7), k=numOptions-1)
            options.append(answer)
            validQuestion = True

        elif ("All-American" in qType):
            question = f"Who was named a {qType} in {kName}?"
            aList = burb.awardsDict[qType][kName]
            if (len(aList) > 1):
                answer = random.choice(burb.awardsDict[qType][kName])
            else:
                answer = aList[0]
            options = []
            while (len(set(options)-set(aList)) < numOptions-1):
                if (len(burb.dfSkateMens.loc[burb.dfSkateMens['seasons'].str.contains(kName)]) < numOptions):
                    broken = True
                    break
                options = burb.dfSkateMens.loc[burb.dfSkateMens['seasons'].str.contains(kName)].sample(numOptions-1)[
                    'name'].to_list()
            options.append(answer)
            validQuestion = True
        else:
            question = f"Who won the {qType} in {kName}?"
            answer = burb.awardsDict[qType][kName]
            options = []
            while (answer in options or len(set(options)) < numOptions-1):
                if (len(burb.dfSeasSkateMens.query(f'year=={kName}')) < numOptions):
                    broken = True
                    break
                options = burb.dfSeasSkateMens.query(f'year=={kName}').sample(numOptions-1)[
                    'name'].to_list()
            if (not broken):
                validQuestion = True
                options.append(answer)
    return question, options, answer


def generateScoreQuestion():
    validQuestion = False
    while (not validQuestion):
        broken = False
        game = burb.dfGames.query('result=="W"').sample()
        dateStr = pd.to_datetime(game['date']).dt.strftime(
            '%B %d, %Y').to_string(index=False)
        oppStr = game['opponent'].to_string(index=False)
        arenaStr = game['arena'].to_string(index=False)
        answer = game['scoreline'].to_string(index=False)
        question = f"On {dateStr}, BU beat {oppStr} at {arenaStr} with a score of:"
        options = []
        failCount = 0
        while (answer in options or len(set(options)) < numOptions-1):
            if (len(burb.dfGames.loc[burb.dfGames['GD'].isin(game['GD'])]) < numOptions or failCount > 10):
                broken = True
                break
            options = burb.dfGames.loc[burb.dfGames['GD'].isin(game['GD'])].sample(numOptions-1)[
                'scoreline'].to_list()
            failCount += 1
        options.append(answer)
        if (not broken):
            validQuestion = True
    return question, options, answer


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
    dfRes = dfRes.query(
        'tourney != ""').loc[~dfRes['tourney'].str.contains('1932')]
    retList = ['All'] + \
        sorted(dfRes.query('tourney != ""').tourney.unique())
    return retList


def determineRecord(dfRes,grpCol):
    ''' Generate Record for given DataFrame

    Parameters:
      dfRes (DataFrame) : DataFrame containing results

    Returns:
      DataFrame: DataFrame containing W-L-T

    '''
    dfStat = dfRes.groupby(['name', grpCol]).sum(numeric_only=True)
    dfStat.reset_index(inplace=True)
    dfStat['W'] = 0
    dfStat['L'] = 0
    dfStat['T'] = 0
    dfRec = dfRes.groupby(['name', grpCol, 'result']).count()
    dfRec.reset_index(inplace=True)
    for res in ['W', 'L', 'T']:
        dfRec[res] = dfRec.query(f'result=="{res}"')['date']
        dfRec[res] = dfRec[res].fillna(0).astype(int)
    dfRec = dfRec.groupby(['name', grpCol]).sum(numeric_only=True)
    dfRec.reset_index(inplace=True)
    # Merge dfStat and dfRec based on name and opponent columns
    mergedDf = pd.merge(dfStat, dfRec[['name', grpCol, 'W', 'L', 'T']], on=[
        'name', grpCol], how='left')

    # Sum the 'W', 'L', 'T' columns from dfRec and assign the values to
    # corresponding columns in dfStat
    dfStat['W'] = mergedDf.groupby(['name', grpCol])['W_y'].transform(sum, numeric_only=True)
    dfStat['L'] = mergedDf.groupby(['name', grpCol])['L_y'].transform(sum, numeric_only=True)
    dfStat['T'] = mergedDf.groupby(['name', grpCol])['T_y'].transform(sum, numeric_only=True)

    return dfStat

def generateStreaks(dfRes):
  streakList=[]
  streakType={'Winning':['W'],'Unbeaten':['W','T'],'Winless':['L','T'],'Losing':['L']}
  for sType in streakType.keys():
      dfRes=dfRes.query('result != "N" and result != "E"').copy()
      dfRes['resBool']=dfRes['result'].isin(streakType[sType])
      dfRes['SoS']=dfRes['resBool'].ne(dfRes['resBool'].shift())
      dfRes['streak_id']=dfRes.SoS.cumsum()
      dfRes['streak_counter'] = dfRes.groupby('streak_id').cumcount() + 1
      streakId=dfRes.query(f'resBool').sort_values('streak_counter')[-1:]['streak_id'].to_string(index=False,header=False)
      if(dfRes.query(f'resBool').sort_values('streak_counter')[-1:]['streak_id'].empty):
        continue
      if(len(dfRes.loc[dfRes['streak_id']==int(streakId)])>1):
          startDate=dfRes.query(f'streak_id=={streakId}').iloc[0]['date'].strftime('%m/%d/%y')
          endDate=dfRes.query(f'streak_id=={streakId}').iloc[-1]['date'].strftime('%m/%d/%y')
          if((endDate==dfRes['date'].tail(1)).bool()):
              endDate='Active'
          streakLength=dfRes.query(f'streak_id=={streakId}').iloc[-1]['streak_counter']
      else:
          if(dfRes.query(f'resBool').empty):
              continue
          startDate=dfRes[dfRes['streak_id']==int(streakId)]['date'].dt.strftime('%m/%d/%y').to_string(index=False,header=False)
          endDate=''
          streakLength=1
      recVal=''
      record=dfRes.query(f'streak_id=={streakId}').groupby('result')['date'].count().to_dict()
      for i in ['W','L','T']:
          if(i not in record):
              val='0'
          else:
              val=str(record[i])
          recVal+=val+'-'
      recVal=recVal[:-1]
      streakList.append({'Longest Streak':sType,'Length':streakLength,'Record':recVal,'Start Date':startDate,'End Date':endDate})
  dfOut = pd.DataFrame(streakList)
  if(dfOut.empty):
    return ''
  return dfOut

def filterStats(formData,dfStat):
    dfRes=dfStat.copy()
    if(formData['gpmin']!=''):
      dfRes=dfRes.query(f"gp{formData['gpop']} {int(formData['gpmin'])}")
    if(formData['position']=='skater'):
      if(formData['goalmin'] != ''):
        dfRes=dfRes.query(f"goals{formData['goalop']} {int(formData['goalmin'])}")
      if(formData['assistmin'] != ''):
        dfRes=dfRes.query(f"assists{formData['assistop']} {int(formData['assistmin'])}")
      if(formData['ptsmin'] != ''):
        dfRes=dfRes.query(f"pts{formData['ptsop']} {int(formData['ptsmin'])}")
      if(formData['type']!='game'):
        if(formData['pensmin'] != ''):
          dfRes=dfRes.query(f"pen{formData['pensop']} {int(formData['pensmin'])}")
        if(formData['pimmin'] != ''):
          dfRes=dfRes.query(f"pim{formData['pimop']} {int(formData['pimmin'])}")
    elif(formData['position']=='goalie'):
      if(formData['minsmin'] != ''):
        dfRes=dfRes.query(f"mins{formData['minsop']} {float(formData['minsmin'])}")
      if(formData['gamin'] != ''):
        dfRes=dfRes.query(f"ga{formData['gaop']} {int(formData['gamin'])}")
      if(formData['savesmin'] != ''):
        if('sv' in dfRes.columns):
          dfRes=dfRes.query(f"sv{formData['savesop']} {int(formData['savesmin'])}")
        else:
          dfRes=dfRes.query(f"saves{formData['savesop']} {int(formData['savesmin'])}")
    return dfRes

if __name__ == '__main__':
    app.run(host='localhost', port=5000)
