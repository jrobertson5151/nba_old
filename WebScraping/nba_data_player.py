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

def get_player_df(soup, id_name):
    table = soup.find('table', id=id_name)
    df = pd.read_html(str(table))[0]
    df = df[df['Season'].notna()]
    df = df[df['Season'].str.contains('-')]
    return df
    
def get_player_per_game(soup):
    return get_player_df(soup, 'per_game')

def get_player_per_36(soup):
    return get_player_df(soup, 'per_minute')

def get_player_per_poss(soup):
    return get_player_df(soup, 'per_poss')

def get_player_advanced(soup):
    return get_player_df(soup, 'advanced')

def get_player_shooting(soup):
    table = soup.find('table', id='shooting')
    fixed_table_string = '<table>' + str(table.tbody) + '</table>'
    cols = ['Season', 'Age', 'Tm', 'Lg', 'Pos', 'G', 'MP', 'FG%', 'Dist.',
            '% of 2PA', '% of 0-3', '% of 3-10', '% of 10-16', '% of 16-3pt', '% of 3P',
            '2P %FG', '0-3 %FG', '3-10 %FG', '10-16 %FG', '16-3pt%FG',
            '3P %FG', '2P % Assisted', '% of Dunks', 'Dunks Made',
            '3P % Assisted', '% of 3PA from Corner', 'Corner 3 %FG ',
            'Heaves Attempted', 'Heaves Made']
    df = pd.read_html(fixed_table_string)[0]
    df.columns = cols
    return df

def get_player_id_list(driver):
    def by_letter(letter):
        url = 'https://www.basketball-reference.com/players/' + letter +'/'
        player_page_soup = get_soup(driver, url)
        ths = player_page_soup.find_all('th', attrs={'data-append-csv': True})
        return [(t['data-append-csv'], int(t.parent.td.text))
                for t in ths if t.parent.td is not None]
    rtn = []
    for l in string.ascii_lowercase:
        rtn.append(by_letter(l))
        print('getting ' + l)
        time.sleep(1)
    return rtn
                                                                            
    
def get_bio(soup):
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
            bio['date_of_birth'] = datetime.strptime(p.span['data-birth'], "%Y-%m-%d")
        elif 'Died' in p_text:
            bio['date_of_death'] = datetime.strptime(p.span['data-death'], "%Y-%m-%d")
        elif 'Position' in p_text:
            p_split = re.split("▪|:", p_text)
            bio['Position'] = p_split[1].strip()
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
    if 'date_of_death' in bio:
        bio['age_at_death'] = bio['date_of_death']-bio['date_of_birth']
    else:
        bio['age'] = datetime.now() - bio['date_of_birth']
    return bio
    


