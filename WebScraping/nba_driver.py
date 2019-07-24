from selenium import webdriver
from bs4 import BeautifulSoup
import ipdb
import pandas as pd
import string
from time import sleep

def driver_init():
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--incognito')
    options.add_argument('--headless')
    driver = webdriver.Chrome("./chromedriver", options=options)
    return driver

def get_soup(driver, url):
    #add error checking
    driver.get(url)
    return BeautifulSoup(driver.page_source, "lxml")

def get_teams(driver):
    teams_soup = get_soup(driver, 'https://www.basketball-reference.com/teams/')
    teams_table = teams_soup.find('table', id='teams_active')
    for tags in teams_table.find_all('tr', 'partial_table'):
        tags.decompose()
    for tags in teams_table.find_all('tr', 'thread'):
        tags.decompose()
    teams_df = pd.read_html(str(teams_table))[0]
    franch_tags = teams_table.find_all(attrs={'data-stat': 'franch_name', 'scope' : 'row'})
    franch_ids = []
    for t in franch_tags:
        franch_ids.append(t.a['href'].split('/')[2])
    teams_df = teams_df[~teams_df['Franchise'].str.contains('Franchise')]
    teams_df['franch_id'] = franch_ids
    teams_df = teams_df.set_index('franch_id', drop=False)
    cols_as_series = teams_df.columns.to_series()
    int_cols = list(cols_as_series.loc['From':'L']) +\
               list(cols_as_series.loc['Plyfs':'Champ'])
    teams_df = teams_df.astype({col:'int64' for col in int_cols})
    teams_df = teams_df.astype({'W/L%':'float'})
    return teams_df

def correct_team_url(franch_id, season): #works for 1975 and on
    if franch_id == 'ATL':
        if season <= 1950:
            return 'TRI'
        if season <= 1954:
            return 'MLH'
        if season <= 1967:
            return 'STL'
        return 'ATL'
    if franch_id == 'NJN':
        if season <= 1967:
            return 'NJA'
        if season <= 1975:
            return 'NYA'
        if season == 1976:
            return 'NYN'
        if season <= 2011:
            return 'NJN'
        return 'BRK'
    if franch_id == 'CHA':
        if season <= 2001:
            return 'CHH'
        if season <= 2013:
            return 'CHA'
        return 'CHO'
    if franch_id == 'DEN':
        if season <= 1973:
            return 'DNR'
        if season <= 1975:
            return 'DNA'
        return 'DEN'
    if franch_id == 'DET' and season <= 1956:
        return 'FTW'
    if franch_id == 'GSW':
        if season <= 1961:
            return 'PHW'
        if season <= 1970:
            return 'SFW'
        return 'GSW'
    if franch_id == 'HOU' and season <= 1970:
        return 'SDR'
    if franch_id == 'IND' and season <= 1975:
        return 'INA'
    if franch_id == 'LAC':
        if season <= 1977:
            return 'BUF'
        if season <= 1983:
            return 'SDC'
        return 'LAC'
    if franch_id == 'LAL' and season <= 1959:
        return 'MNL'
    if franch_id == 'MEM' and season <= 2000:
        return 'VAN'
    if franch_id == 'NOH':
        if season <= 2004:
            return 'NOH'
        if season <= 2006:
            return 'NOK'
        if season <= 2012:
            return 'NOH'
        return 'NOP'
    if franch_id == 'OKC' and season <= 2007:
        return 'SEA'
    if franch_id == 'PHI' and season <= 1962:
        return 'SYR'
    if franch_id == 'SAC':
        if season <= 1956:
            return 'ROC'
        if season <= 1971:
            return 'CIN'
        if season <= 1974:
            return 'KCO'
        if season <= 1985:
            return 'KCK'
        return 'SAC'
    if franch_id == 'SAS':
        if season <= 1969:
            return 'DLC'
        if season == 1970:
            return 'TEX'
        if season <= 1972:
            return 'DLC'
        if season <= 1975:
            return 'SAA'
        return 'SAS'
    if franch_id == 'UTA':
        if season <= 1978:
            return 'NOJ'
        return 'UTA'
    if franch_id == 'WAS':
        if season == 1961:
            return 'CHP'
        if season == 1962:
            return 'CHZ'
        if season <= 1972:
            return 'BAL'
        if season == 1973:
            return 'CAP'
        if season <= 1996:
            return 'WSB'
        return 'WAS'
    return franch_id

def get_correct_franch_id(other_id):
    if other_id == 'BRK':
        return 'NJN'
    elif other_id == 'SEA':
        return 'OKC'
    elif other_id in ['CHO', 'CHH']:
        return 'CHA'
    elif other_id == 'VAN':
        return 'MEM'
    elif other_id in ['NOK', 'NOP']:
        return 'NOH'
    elif other_id == 'KCK':
        return 'SAC'
    elif other_id == 'WSB':
        return 'WAS'
    else:
        return other_id

def process_team_table(driver):
    soup = get_soup(driver, 'https://www.basketball-reference.com/teams/')
    soup = soup.tbody
    for tag in soup.find_all('tr', attrs={'class': 'thead'}):
        tag.decompose()
    franch_dict = dict()
    for row in soup.find_all('tr'):
        if row['class'] == ['full_table']:
            last_team = row.th.a['href'].split('/')[2]
        year_min = int(row.find('td', attrs={'data-stat': 'year_min'}).text)
        year_max = int(row.find('td', attrs={'data-stat': 'year_max'}).text)
        franch_dict[row.th.text] = (last_team, year_min, year_max)
    return pd.DataFrame.from_dict(franch_dict, orient = 'index',
                                  columns = ['franch_id', 'From', 'To'])
    
def get_franch_id(team_name):
    pass
