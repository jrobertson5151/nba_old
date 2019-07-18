import pandas as pd
from nba_driver import *

teams_url = 'https://www.basketball-reference.com/teams/'

def get_roster_soup(driver, team, season):
    return get_soup(driver, teams_url + correct_team_url(team, season) +
                    '/' + str(season+1) + '.html')

def get_player_ids(table):
    player_ids = []
    for td in table.find_all('td', attrs={'data-stat': 'player'}):
        player_ids.append(td['data-append-csv'])
    return player_ids

def get_season_table(roster_soup, id_name):
    table = roster_soup.find('table', id =id_name)
    df = pd.read_html(str(table))[0]
    df['player_id'] = get_player_ids(table)
    df = df.set_index('player_id', drop = False)
    return df    
    
def get_roster(roster_soup):
    table = roster_soup.find('table', id='roster')
    df = pd.read_html(str(table))[0]
    '''player_ids = []
    for td in table.find_all('td', attrs={'data-stat': 'player'}):
        player_ids.append(td['data-append-csv'])'''
    df['player_id'] = get_player_ids(table)
    df = df[['player_id', 'Player', 'No.', 'Pos']]
    df = df.set_index('player_id')
    return df

def get_season_info(roster_soup):
    table = roster_soup.find('table', id='team_misc')
    table.find('tr', attrs={'class': 'over_header'}).decompose()
    rtn = pd.read_html(str(table))[0].iloc[0, :][1:]
    rtn.name = None
    return rtn

def get_team_per_game(roster_soup):
    df = get_season_table(roster_soup, 'per_game')
    return df

def get_team_totals(roster_soup):
    df = get_season_table(roster_soup, 'totals')
    return df

def get_team_per_min(roster_soup):
    df = get_season_table(roster_soup, 'per_minute')
    return df

def get_team_per_poss(roster_soup):
    df = get_season_table(roster_soup, 'per_poss')
    return df

def get_team_advanced(roster_soup):
    df = get_season_table(roster_soup, 'advanced')
    return df

def get_team_shooting(roster_soup):
    df = get_season_table(roster_soup, 'shooting')
    return df

def get_team_season(roster_soup):
    df = get_season_table(roster_soup, 'totals')
    return df


    
