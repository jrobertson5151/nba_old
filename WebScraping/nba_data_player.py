import time
import requests
import urllib.request
from bs4 import BeautifulSoup
import re
from datetime import datetime
import pandas as pd
from nba_driver import *
import numpy as np
import string

def get_player_soup(driver, player_id):
    soup = get_soup(driver,
                    'https://www.basketball-reference.com/players/' +
                    player_id[0] + '/' + player_id + '.html')
    for t in soup.find_all('tr', attrs={'class': 'over_header'}):
        t.decompose()
    return soup

def get_player_df(soup, id_name, playoffs = False):
    if playoffs:
        id_name = 'playoffs_' + id_name
    table = soup.find('table', id=id_name)
    if table is None:
        return None
    df = pd.read_html(str(table))
    if df is None:
        return None
    df = df[0]
    df = df[df['Season'].notna()]
    df = df[df['Season'].str.contains('-')]
    filter_empty_columns = [col for col in df if col.startswith('Unnamed')]
    df = df.drop(filter_empty_columns, axis=1)
    if id_name != 'all_salaries' and 'Tm' in df.columns:
        df = df[df['Tm'] != 'TOT']
    return df

def get_player_totals(soup, playoffs = False):
    return get_player_df(soup, 'totals', playoffs)

def get_player_per_game(soup, playoffs = False):
    return get_player_df(soup, 'per_game', playoffs)

def get_player_per_36(soup, playoffs = False):
    return get_player_df(soup, 'per_minute', playoffs)

def get_player_per_poss(soup, playoffs = False):
    return get_player_df(soup, 'per_poss', playoffs)

def get_player_advanced(soup, playoffs = False):
    return get_player_df(soup, 'advanced', playoffs)

def get_player_shooting(soup, playoffs = False):
    if playoffs:
        table = soup.find('table', id='playoffs_shooting')
    else:
        table = soup.find('table', id='shooting')
    if table is None:
        return None
    df = get_player_df(soup, 'shooting', playoffs)
    if df is None:
        return None
    cols = ['Season', 'Age', 'Tm', 'Lg', 'Pos', 'G', 'MP', 'FG%', 'Dist.',
            '% of 2PA', '% of 0-3', '% of 3-10', '% of 10-16', '% of 16-3pt', '% of 3P',
            '2P %FG', '0-3 %FG', '3-10 %FG', '10-16 %FG', '16-3pt%FG',
            '3P %FG', '2P % Assisted', '% of Dunks', 'Dunks Made',
            '3P % Assisted', '% of 3PA from Corner', 'Corner 3 %FG ',
            'Heaves Attempted', 'Heaves Made']
    df.columns = cols
    df = df[df['Tm'] != 'TOT']
    return df

def get_player_pbp(soup, playoffs = False):
    table = get_player_df(soup, 'pbp', playoffs)
    if table is None:
        return None
    table = table.fillna(value = 0)         #position% is na for unplayed positions
    for c in ['PG%', 'SG%', 'SF%', 'PF%', 'C%']:
        table[c] = [int(x[:-1]) if x != 0 else 0 for x in table[c]]
    return table
    

def get_player_highs(soup, playoffs = False):
    id_name = 'year-and-career-highs'
    if playoffs:
        id_name += '-po'
    return get_player_df(soup, id_name)

def get_player_id_list(driver):
    def by_letter(letter):
        url = 'https://www.basketball-reference.com/players/' + letter +'/'
        player_page_soup = get_soup(driver, url)
        ths = player_page_soup.find_all('th', attrs={'data-append-csv': True})
        player_pairs = pd.DataFrame([(t['data-append-csv'], t.text)
                                     for t in ths if t.parent.td is not None],
                                    columns = ['player_id', 'Player'])
        if letter == 'n':
            player_table = pd.read_html(str(player_page_soup('table')[1]), parse_dates = True)[0]
        else:
            player_table = pd.read_html(str(player_page_soup.table))[0]
        player_table = player_table[player_table.Player != 'Player']
        player_table.index = player_pairs.index
        player_table = player_table.join(player_pairs, how='inner', rsuffix='2')
        player_table.set_index('player_id', inplace = True, drop=False)
        player_table.drop('Player2', axis=1, inplace=True)
        player_table = player_table.astype({'From':'int64','To':'int64', 'Wt': 'float64'})
        return player_table
    rtn = None
    for l in string.ascii_lowercase:
        print('getting ' + l)
        if l != 'x':
            rtn = pd.concat([rtn, by_letter(l)])
        time.sleep(1)
    return rtn
                                                                                
def get_player_bio(soup, playoffs=False):
    bio = dict()
    bio_div = soup.find('div', itemtype="https://schema.org/Person")
    bio_p = bio_div.find_all('p')
    bio['Name'] = bio_div.h1.text
    for p in bio_p:
        p_text = p.text.replace(u'\xa0', u' ')
        p_text = p_text.replace('\n', '')
        p_text = p_text.strip()
        if 'lb' in p_text and 'cm' in p_text:
            c = re.compile(r'(\d)-(\d+), (\d+)lb \((\d+)cm, (\d+)kg\)')
            match = c.match(p_text)
            if match:
                bio['height_ft'] = int(match.group(1))
                bio['height_in'] = int(match.group(2))
                bio['weight_lb'] = int(match.group(3))
                bio['height_cm'] = int(match.group(4))
                bio['weight_kg'] = int(match.group(5))
        elif 'Born' in p_text:
            try:
                bio['date_of_birth'] = datetime.strptime(
                    p.span['data-birth'], "%Y-%m-%d")
            except:
                pass
        elif 'Died' in p_text:
            try:
                bio['date_of_death'] = datetime.strptime(p.span['data-death'], "%Y-%m-%d")
            except:
                pass
        elif 'Position' in p_text:
            p_split = re.split("▪|:", p_text)
            if len(p_split) > 1:
                bio['Position'] = p_split[1].strip()
            if len(p_split) > 3:
                bio['Shooting Hand'] = p_split[3].strip()
        elif '▪' in p_text:
            bio['Full Name'] = p_text.split("▪")[0].strip()
        elif "High School" in p_text:
            continue
        elif "Draft" in p_text:
            p_text = p_text[7:].strip() #remove 'draft'
            match = re.search(", (\d+) NBA", p_text)
            if match:
                bio['Draft Year'] = int(match.group(1))
            p_split = p_text.split(', ')
            bio['Drafting Team'] = p_split[0]
            if len(p_split) > 2:
                bio['Draft Round'] = int(p_split[1][0])
                match = re.match("(\d+)", p_split[2])
                if match:
                    bio['Draft Number'] = int(match.group(1))
        else:
            p_split = p_text.split(":")
            if len(p_split) == 2:
                bio[p_split[0].strip()] = p_split[1].strip()
    if 'date_of_death' in bio and 'date_of_birth' in bio:
        bio['age_at_death'] = bio['date_of_death']-bio['date_of_birth']
    elif 'date_of_birth' in bio:
        bio['age'] = datetime.now() - bio['date_of_birth']
    bio_series = pd.Series(bio)
    return pd.DataFrame(data=[list(bio_series)], columns=list(bio_series.index))

def get_player_salaries(soup, playoffs=None):
    return get_player_df(soup, 'all_salaries')
