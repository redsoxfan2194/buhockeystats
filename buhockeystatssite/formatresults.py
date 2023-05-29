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

TIE_COLOR = '#808080'
TIE_BG_COLOR = '#000000'

TEAM_COLORS = {
    "Yale": ("#0A2240", "#FFFFFF"),
    "Harvard": ("#A31F36", "#FFFFFF"),
    "Princeton": ("#000000", "#FF6000"),
    "Army": ("#2C2A29", "#D3BC8D"),
    "Dartmouth": ("#00693E", "#FFFFFF"),
    "Cornell": ("#B31B1B", "#FFFFFF"),
    "Rensselaer": ("#E2231B", "#FFFFFF"),
    "Michigan Tech": ("#000000", "#FFCD00"),
    "Minnesota": ("#5B0013", "#FFB71E"),
    "Clarkson": ("#03522B", "#FFD204"),
    "Michigan": ("#00274C", "#FFCB05"),
    "Boston College": ("#8C2232", "#DBCCA6"),
    "St. Thomas": ("#500878", "#97999B"),
    "New Hampshire": ("#041E42", "#BBBCBC"),
    "Brown": ("#4E3629", "#C00404"),
    "Boston University": ("#CC0000", "#FFFFFF"),
    "Colgate": ("#821019", "#FFFFFF"),
    "Massachusetts": ("#881C1C", "#FFFFFF"),
    "Northeastern": ("#000000", "#D41B2C"),  # flipped
    "St. Cloud State": ("#A10209", "#FFFFFF"),
    "St. Lawrence": ("#AF1E2D", "#4B2B23"),
    "Colorado College": ("#000000", "#EFAB1E"),
    "Union": ("#822433", "#FFFFFF"),
    "Michigan State": ("#173F35", "#FFFFFF"),
    "North Dakota": ("#009A44", "#FFFFFF"),
    "Minnesota Duluth": ("#7A0019", "#FFCC33"),
    "American International": ("#000000", "#FFB60F"),
    "Wisconsin": ("#C5050C", "#FFFFFF"),
    "Denver": ("#BA0C2F", "#A89968"),
    "Alaska": ("#1E59AE", "#FCD006"),
    "Providence": ("#000000", "#FFFFFF"),
    "Bemidji State": ("#004D44", "#FFFFFF"),
    "Merrimack": ("#003768", "#F1C400"),
    "Notre Dame": ("#0C2340", "#C99700"),
    "Connecticut": ("#000E2F", "#FFFFFF"),
    "Ohio State": ("#BA0C2F", "#A1B1B7"),
    "Vermont": ("#005710", "#FFC20E"),
    "RIT": ("#F76902", "#FFFFFF"),
    "Holy Cross": ("#602D89", "#FFFFFF"),
    "Lake Superior State": ("#003F87", "#FFC61E"),
    "UMass Lowell": ("#0067B1", "#C8102E"),
    "Air Force": ("#003594", "#B2B4B2"),
    "Bowling Green": ("#4F2C1D", "#FF7300"),
    "Minnesota State": ("#480059", "#F7E400"),
    "Western Michigan": ("#532E1F", "#F1C500"),
    "Maine": ("#003263", "#B0D7FF"),
    "Ferris State": ("#BA0C2F", "#FFD043"),
    "Quinnipiac": ("#0A2240", "#FFB819"),
    "Northern Michigan": ("#095339", "#FFC425"),
    "Bentley": ("#1B5FAA", "#FFFFFF"),
    "Miami": ("#B61E2E", "#FFFFFF"),
    "Stonehill": ("#2F2975", "#FFFFFF"),
    "Canisius": ("#0E2756", "#FFBA00"),
    "Alaska Anchorage": ("#00583D", "#FFC425"),
    "Mercyhurst": ("#0F4F44", "#FFFFFF"),
    "Sacred Heart": ("#CD1041", "#FFFFFF"),
    "Niagara": ("#582C83", "#FFFFFF"),
    "Nebraska Omaha": ("#000000", "#D71920"),
    "Penn State": ("#001E44", "#FFFFFF"),
    "Robert Morris": ("#001E41", "#AA182C"),
    "Arizona State": ("#7D2248", "#FFC72C"),
    "Long Island": ("#69B3E7", "#FFC72C"),
    "Lindenwood": ("#000000", "#B5A36A"),
    "Augustana": ("#002D62", "#FFDD00"),
    "Tufts": ("#3E8EDE", "#512C1D"),
    "MIT": ("#231F20", "#B20D35"),
    "Toronto": ("#002A5C", "#FFFFFF"),
    "Colby": ("#254893", "#FFFFFF"),
    "Dalhousie": ("#242424", "#FFD400"),
    "Pennsylvania": ("#990000", "#011F5B"),
    "St. Louis": ("#003DA5", "#C8C9C7"),
    "Norwich": ("#9C0A2E", "#B99457"),
    "Queen's": ("#B90E31", "#FABD0F"),
    "Middlebury": ("#37538C", "#FFFFFF"),
    "Williams": ("#362061", "#FECC06"),
    "Hamilton College": ("#002F86", "#D6BA8B"),
    "St. Francis Xavier": ("#0C2340", "#FFFFFF"),
    "Syracuse": ("#F76900", "#FFFFFF"),
    "Wayne State": ("#0C5449", "#FFCC33")
}


def formatResults(df_results):
    table_data = df_results[['date', 'opponent', 'result', 'scoreline', 'ot', 'arena', 'tourney', 'note']].copy()

    table_data['date'] = table_data['date'].dt.strftime('%m/%d/%Y')

    table_data.loc[table_data['ot'].notnull(), 'scoreline'] = table_data['scoreline'] + " (" + table_data.loc[table_data['ot'].notnull(), 'ot'] + ")"
    table_data.drop(['ot'], axis=1, inplace=True)

    if len(list(table_data['note'].unique())) < 1:
        table_data.drop(['note'], axis=1, inplace=True)

    table_data.fillna('', inplace=True)
    table_data.rename(columns=COLUMNS, inplace=True)
    return table_data.style.apply(styleRow, axis=1).hide(axis='index').set_table_styles(TABLE_STYLES).to_html(index_names=False, render_links=True)


def styleRow(row):
    background, font = winnerColors(row['Result'], row['Opponent'])
    return [f'background-color: {background}; color: {font}; text-align:center'] * len(row)


def winnerColors(result, opponent):
    if result == "W":
        return BU_BG_COLOR, BU_COLOR
    elif result == "L":
        return opponentColors(opponent)
    elif result == "T":
        return TIE_BG_COLOR, TIE_COLOR
    else:
        return DEFAULT_BG_COLOR, DEFAULT_COLOR


def opponentColors(opponent):
    if opponent not in TEAM_COLORS.keys():
        return DEFAULT_BG_COLOR, DEFAULT_COLOR
    else:
        return TEAM_COLORS[opponent][0], TEAM_COLORS[opponent][1]
