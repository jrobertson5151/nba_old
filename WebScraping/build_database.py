from nba_data_player import *
from nba_data_season import *
from nba_driver import *
from time import sleep
import traceback
import sys

data_loc = '../Data/'

def build_db():
    driver = driver_init()
    store = get_store('store')
    try:
        store_seasons(driver, store, [2018])
        store_player_ids(driver, store)
        store_player_stats(driver, store, list(store['player_list'].player_id[0:2]))
    except:
        traceback.print_exc(file=sys.stdout)
    finally:
        driver.quit()
        store.close()

def get_store(name):
    return pd.HDFStore(data_loc + name + '.h5')

def store_player_ids(driver, store):
    print('Storing player list')
    if 'player_list' not in store:
        store.append('player_list', get_player_id_list(driver))

def store_rosters(driver, store, years):
    if 'team_list' not in store:
        print('Getting team_list')
        teams_df = get_teams(driver)
        store.append('team_list', teams_df)
    if type(years) is int:
        years = [years]
    for year in years:
        for f in teams_df['franch_id']:
            print('Getting ' + str(year) +  ' roster for ' + f)
            try:
                f_soup = get_season_soup(driver, f, year)
                f_season_roster = get_roster(f_soup)
                if f + '_roster_' + str(year) not in store:
                    store.append('team/' + f + '/' + f+'_' + str(year)+'/' + 'roster'
                                 , f_season_roster)
            except:
                pass
            sleep(1)

def store_seasons(driver, store, years):
    if 'team_list' not in store:
        teams_df = get_teams(driver)
        store.append('team_list', teams_df)
    if type(years) is int:
        years = [years]
    for year in years:
        for f in store['team_list']['franch_id']:
            print('Getting ' + str(year) +  ' info for ' + f)
            stat_names = ['roster', 'season_info', 'per_game', 'totals',
                          'per_min', 'per_poss', 'advanced', 'shooting']
            table_prefix = 'team/' + f + '/' + f + '_' + str(year) + '/'
            if sum([table_prefix + stat in store for stat in stat_names]) == len(stat_names):
                print('Already have data for ' + f + '_' + str(year))
                continue
            f_soup = get_season_soup(driver, f, year)
            for stat in stat_names:
                table_loc = table_prefix + stat
                print('storing ' + table_loc)
                if table_loc not in store:
                    table = globals()['get_team_' + stat](f_soup)
                    #ipdb.set_trace()
                    if table is not None:
                        store.append(table_loc, table)
            sleep(1)

def store_player_stats(driver, store, player_ids):
    for player in player_ids:
        print('Storing player stats for ' + player)
        stat_names = ['per_game', 'per_36', 'per_poss', 'advanced', 'shooting',
                      'totals', 'pbp', 'highs', 'bio']
        table_prefix = 'player/' + player+ '/'
        if table_prefix in store:
            print('Have data for ' + player)
            continue
        player_soup = get_player_soup(driver, player)
        for stat in stat_names:
            for playoff_status in [False, True]:
                playoff_string = ''
                if playoff_status:
                    playoff_string = 'playoff_'
                print('Getting ' + player + ': ' + playoff_string + stat)
                table_loc = table_prefix + playoff_string + stat
                if table_loc not in store:
                    table = globals()['get_player_' + stat](player_soup, playoff_status)
                    if table is not None:
                        store.append(table_loc, table)
        sleep(1)
        
        
