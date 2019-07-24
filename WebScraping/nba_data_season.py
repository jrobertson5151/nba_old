import pandas as pd
from nba_driver import *

teams_url = 'https://www.basketball-reference.com/teams/'

def get_season_soup(driver, team, season):
    return get_soup(driver, teams_url + correct_team_url(team, season) +
                    '/' + str(season+1) + '.html')

def get_player_ids(table):
    player_ids = []
    for td in table.find_all('td', attrs={'data-stat': 'player'}):
        player_ids.append(td['data-append-csv'])
    return player_ids

def get_season_table(season_soup, id_name):
    table = season_soup.find('table', id =id_name)
    try:
        df = pd.read_html(str(table))[0]
    except:
        return None
    df['player_id'] = get_player_ids(table)
    df = df.set_index('player_id', drop = False)
    return df    
    
def get_team_roster(season_soup):
    table = season_soup.find('table', id='roster')
    try:
        df = pd.read_html(str(table))[0]
    except:
        return None
        '''player_ids = []
    for td in table.find_all('td', attrs={'data-stat': 'player'}):
        player_ids.append(td['data-append-csv'])'''
    df['player_id'] = get_player_ids(table)
    df = df[['player_id', 'Player', 'No.', 'Pos']]
    df = df.set_index('player_id')
    return df

def get_team_season_info(season_soup):
    try:
        table = season_soup.find('table', id='team_misc')
        table.find('tr', attrs={'class': 'over_header'}).decompose()
        rtn = pd.read_html(str(table))[0]
        rtn.name = None
        return rtn
    except:
        return None

def get_team_per_game(season_soup):
    try:
        df = get_season_table(season_soup, 'per_game')
        return df
    except:
        return None

def get_team_totals(season_soup):
    try:
        for tag in season_soup.find_all('tr', attrs={'class':'stat_average'}):
            tag.decompose()
        df = get_season_table(season_soup, 'totals')
        return df
    except:
        return None

def get_team_per_min(season_soup):
    df = get_season_table(season_soup, 'per_minute')
    return df

def get_team_per_poss(season_soup):
    df = get_season_table(season_soup, 'per_poss')
    return df

def get_team_advanced(season_soup):
    df = get_season_table(season_soup, 'advanced')
    return df

def get_team_shooting(season_soup):
    df = get_season_table(season_soup, 'shooting')
    return df

def get_team_schedule(driver, franch_id, season):
    correct_id = correct_team_url(franch_id, season)
    sched_soup = get_soup(driver,
                          'https://www.basketball-reference.com/teams/' +
                          correct_id + '/' + str(season+1) + '_games.html')
    [t.decompose() for t in sched_soup.find_all('tr', attrs={'class':'thead'})]
    game_ids = [str.split(td.a['href'], '/')[2][:-5] for td in
                sched_soup.find_all('td', attrs={'data-stat': 'box_score_text'})]
    sched_df = pd.read_html(str(sched_soup))[0]
    sched_df = sched_df.set_index('G', drop=False)
    sched_df['Win'] = [True if x == 'W' else False for x in sched_df['Unnamed: 7']]
    sched_df['Home'] = [False if x == '@' else False for x in sched_df['Unnamed: 5']]
    sched_df['Overtimes'] = [0 if pd.isnull(x) else 1 if x == 'OT' else int(x[0])
                             for x in sched_df['Unnamed: 8']]
    filter_empty_columns = [col for col in sched_df if
                            col.startswith('Unnamed') or col == 'Notes']
    sched_df = sched_df.drop(filter_empty_columns, axis=1)
    sched_df['game_id'] = game_ids
    #get franch_id for opponent
    #box scores
    #playoffs
    return sched_df

    
