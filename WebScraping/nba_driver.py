from selenium import webdriver
from bs4 import BeautifulSoup
import ipdb
import pandas as pd

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

def correct_team_url(franch_id, season):
    if franch_id == 'NJN' and season > 2012:
        return 'BRK'
    elif franch_id == 'OKC' and season <= 2007:
        return 'SEA'
    elif franch_id == 'CHA' and season >= 2014:
        return 'CHO'
    elif franch_id == 'CHA' and season <= 2003:
        return 'CHH'
    elif franch_id == 'MEM' and season <= 2000:
        return 'VAN'
    elif franch_id == 'NOH' and season in [2005, 2006]:
        return 'NOK'
    elif franch_id == 'NOH' and season >= 2013:
        return 'NOP'
    elif franch_id == 'SAC' and season <= 1984:
        return 'KCK'
    elif franch_id == 'WAS' and season <= 1996:
        return 'WSB'
    else:
        return franch_id

def get_start_date(franch_id):
    pass
