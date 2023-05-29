COLUMNS = {
    'date': 'Date',
    'opponent': 'Opponent',
    'result': 'Result',
    'scoreline': 'Score',
    'arena': 'Location',
    'tourney': 'Tournament',
    'note': 'Note'
}
TABLE_STYLES = [
    {
        'selector': 'th:not(.index_name)',
        'props': 'color: #FFFFFF;'
    }, {
        'selector': 'table',
        'props': [('class', 'sortable')]
    }
]

BU_COLOR = "#FFFFFF"
BU_BG_COLOR = '#CC0000'

DEFAULT_COLOR = '#000000'
DEFAULT_BG_COLOR = '#FFFFFF'

TIE_COLOR = '#000000'
TIE_BG_COLOR = '#808080'

TEAM_COLORS ={"Air Force":("#003594","#B2B4B2"),
  "Alaska Anchorage":("#00583D","#FFC425"),
  "Alaska":("#1E59AE","#FCD006"),
  "American International":("#000000","#FFB60F"),
  "Arizona State":("#7D2248","#FFC72C"),
  "Army":("#2C2A29","#D3BC8D"),
  "Augustana":("#002D62","#FFDD00"),
  "Bemidji State":("#004D44","#FFFFFF"),
  "Bentley":("#1B5FAA","#FFFFFF"),
  "Boston College":("#8C2232","#DBCCA6"),
  "Boston University":("#CC0000","#FFFFFF"),
  "Bowling Green":("#4F2C1D","#FF7300"),
  "Brown":("#4E3629","#C00404"),
  "Canisius":("#0E2756","#FFBA00"),
  "Clarkson":("#03522B","#FFD204"),
  "Colby":("#254893","#FFFFFF"),
  "Colgate":("#821019","#FFFFFF"),
  "Colorado College":("#000000","#EFAB1E"),
  "Connecticut":("#000E2F","#FFFFFF"),
  "Cornell":("#B31B1B","#FFFFFF"),
  "Dalhousie":("#242424","#FFD400"),
  "Dartmouth":("#00693E","#FFFFFF"),
  "Denver":("#BA0C2F","#A89968"),
  "Ferris State":("#BA0C2F","#FFD043"),
  "Hamilton College":("#002F86","#D6BA8B"),
  "Harvard":("#A31F36","#FFFFFF"),
  "Holy Cross":("#602D89","#FFFFFF"),
  "Lake Superior State":("#003F87","#FFC61E"),
  "Lindenwood":("#000000","#B5A36A"),
  "Long Island":("#69B3E7","#FFC72C"),
  "MIT":("#231F20","#B20D35"),
  "Maine":("#003263","#B0D7FF"),
  "Massachusetts":("#881C1C","#FFFFFF"),
  "Mercyhurst":("#0F4F44","#FFFFFF"),
  "Merrimack":("#003768","#F1C400"),
  "Miami":("#B61E2E","#FFFFFF"),
  "Michigan State":("#173F35","#FFFFFF"),
  "Michigan Tech":("#000000","#FFCD00"),
  "Michigan":("#00274C","#FFCB05"),
  "Middlebury":("#37538C","#FFFFFF"),
  "Minnesota Duluth":("#7A0019","#FFCC33"),
  "Minnesota State":("#480059","#F7E400"),
  "Minnesota":("#5B0013","#FFB71E"),
  "Nebraska Omaha":("#000000","#D71920"),
  "New Hampshire":("#041E42","#BBBCBC"),
  "Niagara":("#582C83","#FFFFFF"),
  "North Dakota":("#009A44","#FFFFFF"),
  "Northeastern":("#000000","#D41B2C"), #flipped
  "Northern Michigan":("#095339","#FFC425"),
  "Norwich":("#9C0A2E","#B99457"),
  "Notre Dame":("#0C2340","#C99700"),
  "Ohio State":("#BA0C2F","#A1B1B7"),
  "Penn State":("#001E44","#FFFFFF"),
  "Pennsylvania":("#990000","#011F5B"),
  "Princeton":("#000000","#FF6000"),
  "Providence":("#000000","#FFFFFF"),
  "Queen's":("#B90E31","#FABD0F"),
  "Quinnipiac":("#0A2240","#FFB819"),
  "RIT":("#F76902","#FFFFFF"),
  "Rensselaer":("#E2231B","#FFFFFF"),
  "Robert Morris":("#001E41","#AA182C"),
  "Sacred Heart":("#CD1041","#FFFFFF"),
  "St. Cloud State":("#A10209","#FFFFFF"),
  "St. Francis Xavier":("#0C2340","#FFFFFF"),
  "St. Lawrence":("#AF1E2D","#4B2B23"),
  "St. Louis": ("#003DA5","#C8C9C7"),
  "St. Thomas":("#500878","#97999B"),
  "Stonehill":("#2F2975","#FFFFFF"),
  "Syracuse":("#F76900","#FFFFFF"),
  "Toronto":("#002A5C","#FFFFFF"),
  "Tufts":("#3E8EDE","#512C1D"),
  "UMass Lowell":("#0067B1","#C8102E"),
  "Union":("#822433","#FFFFFF"),
  "Vermont":("#005710","#FFC20E"),
  "Wayne State":("#0C5449","#FFCC33"),
  "Western Michigan":("#532E1F","#F1C500"),
  "Williams":("#362061","#FECC06"),
  "Wisconsin":("#C5050C","#FFFFFF"),
  "Yale":("#0A2240","#FFFFFF")}

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

def formatResults(dfRes):
    table_data = dfRes[['date', 'opponent', 'result', 'scoreline', 'ot', 'arena', 'tourney', 'note']].copy()
    table_data.fillna('', inplace=True)

    table_data['date'] = table_data['date'].dt.strftime('%m/%d/%Y')

    table_data.loc[table_data['ot']!='', 'scoreline'] = table_data['scoreline'] + " (" + table_data.loc[table_data['ot']!='', 'ot'] + ")"
    table_data.drop(['ot'], axis=1, inplace=True)

    if len(list(table_data['note'].unique())) < 1:
        table_data.drop(['note'], axis=1, inplace=True)

    table_data.rename(columns=COLUMNS, inplace=True)
    return table_data.style.apply(stylerow, axis=1).hide(axis='index').set_table_styles(TABLE_STYLES).to_html(index_names=False, render_links=True)
    
def formatStats(dfRes):
    dfRes=dfRes.copy()
    if('career' in dfRes.columns and 'pts' in dfRes.columns):
      dfRes=dfRes[['name','career','gp','goals','assists','pts','pen','pim']]
    elif('career' in dfRes.columns and 'gaa' in dfRes.columns):
      dfRes=dfRes[['name','career','gp','mins','ga','gaa','saves','sv%','W','L','T']]
    elif('number' in dfRes.columns and 'gaa' in dfRes.columns):
      dfRes=dfRes[['number','name','yr','season','gp','mins','ga','gaa','saves','sv%','W','L','T','SO']]
    elif('date' in dfRes.columns and 'ga' in dfRes.columns):
      dfRes['date']=dfRes['date'].dt.strftime('%m/%d/%Y')
      dfRes=dfRes[['date','name','opponent','yr','season','sv','ga','mins','result']]
    elif('number' in dfRes.columns and 'pts' in dfRes.columns):
      dfRes['number']=dfRes['number'].astype(int)
      dfRes=dfRes[['number','name','pos','yr','season','gp','goals','assists','pts','pens']]
    elif('date' in dfRes.columns and 'pts' in dfRes.columns):
      dfRes['date']=dfRes['date'].dt.strftime('%m/%d/%Y')
      dfRes=dfRes[['date','name','opponent','yr','pos','season','goals','assists','pts']]
    if('season' in dfRes.columns):
      style= dfRes.style.apply(lambda x: ['background-color: white; color:#cc0000; text-align:center' if i % 2 == 0 else 'background-color: #cc0000; color:white; text-align:center' for i in range(len(x))]).hide(axis='index').format({'gaa':'{:.2f}','sv%':'{:.3f}'})
    else:
      style= dfRes.style.apply(lambda x: ['background-color: white; color:#cc0000; text-align:center' if i % 2 == 0 else 'background-color: #cc0000; color:white; text-align:center' for i in range(len(x))]).hide(axis='index').format({'gaa':'{:.2f}','mins':'{:.2f}','sv%':'{:.3f}'})
    for stat in ['gp','goals','assists','pts','pen','pim','ga','W','L','T','saves']:
      if(stat not in dfRes.columns):
        continue
      dfRes[stat] = dfRes[stat].fillna(-1)
      dfRes[stat] = dfRes[stat].astype(int)
      dfRes[stat] = dfRes[stat].astype(str)
      dfRes[stat] = dfRes[stat].replace('-1', '-')
      
    headers = {
        'selector': 'th:not(.index_name)',
        'props': 'color: white;'
    }
    table={
        'selector': 'table',
        'props': [('class', 'sortable')]
    }
    dfRes.columns=dfRes.columns.str.capitalize()
    dfRes.rename(columns={'Yr':'YR','Gp':'GP','Ga':'GA','Gaa':'GAA','Sv%':'SV%','So':'SO','Sv':'SV','Pim':'PIM'},inplace=True)
    style.set_table_styles([headers,table])
    dfRes=style.to_html(index_names=False,render_links=True).replace(">nan<",">-<").replace('<th','<th onclick=setSort(this)')
    return dfRes
    
  
def stylerow(row):
    background, font = winnercolors(row['Result'], row['Opponent'])
    return [f'background-color: {background}; color: {font}; text-align:center'] * len(row)


def winnercolors(result, opponent):
    if result == "W":
        return BU_BG_COLOR, BU_COLOR
    elif result == "L":
        return opponentcolors(opponent)
    elif result == "T":
        return TIE_BG_COLOR, TIE_COLOR
    else:
        return DEFAULT_BG_COLOR, DEFAULT_COLOR
        
def opponentcolors(opponent):
    if opponent not in TEAM_COLORS.keys():
        return DEFAULT_BG_COLOR, DEFAULT_COLOR
    else:
        return TEAM_COLORS[opponent][0], TEAM_COLORS[opponent][1]