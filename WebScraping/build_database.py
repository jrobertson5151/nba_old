from nba_data_player import *
from nba_data_season import *
from nba_driver import *
from time import sleep

data_loc = '../Data/'

def get_store(name):
    return pd.HDFStore(data_loc + name + '.h5')

def store_rosters(driver, store, years):
    teams_df = get_teams(driver)
    store['teams_df'] = teams_df
    for year in years:
        for f in teams_df['franch_id']:
            print('Getting ' + str(year) +  ' roster for ' + f)
            try:
                f_soup = get_roster_soup(driver, f, year)
                f_season_roster = get_roster(f_soup)
                store[f + '_roster_' + str(year)] = f_season_roster
            except:
                pass
            sleep(1)
    
