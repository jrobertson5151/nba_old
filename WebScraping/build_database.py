from nba_data_player import *
from nba_data_season import *
from nba_driver import *
from time import sleep
import traceback
import sys

data_loc = '../Data/'

def build_db(dest_name='store', from_year=1950):
    driver = driver_init()
    store = get_store(dest_name)
    try:
        store_seasons(driver, store, range(from_year, 2019))
        store_player_ids(driver, store)
        recent_ids = [x.player_id for (_, x) in store['player_list'].iterrows()
                      if x.From > from_year]
        store_player_stats(driver, store, recent_ids)
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

def store_seasons(driver, store, years, force_update = False):
    if 'team_list' not in store:
        teams_df = get_teams(driver)
        store.append('team_list', teams_df)
    if 'team_name_table' not in store:
        store.append('team_name_table', process_team_table(driver))
    if type(years) is int:
        years = [years]
    for year in years:
        for f in store['team_list']['franch_id']:
            if store['team_list']['From'][f] > year:
                continue
            print('Getting ' + str(year) +  ' info for ' + f)
            stat_names = ['roster', 'season_info', 'per_game', 'totals',
                          'per_min', 'per_poss', 'advanced']
            if year >= 2000:
                stat_names += ['shooting']
            table_prefix = 'team/' + f + '/' + f + '_' + str(year) + '/'
            matched_stats = sum([table_prefix + stat in store \
                                 for stat in stat_names])
            if (matched_stats == len(stat_names)) or \
                                ((matched_stats > 3) and (force_update is False)):
                #some seasons lack some tables so skip 
                    #if it seems like they're all in the db already
                print('Already have data for ' + f + '_' + str(year))
                continue
            f_soup = get_season_soup(driver, f, year)
            for stat in stat_names:
                table_loc = table_prefix + stat
                if table_loc not in store:
                    table = globals()['get_team_' + stat](f_soup)
                    #ipdb.set_trace()
                    if table is not None:
                        print('Adding ' + table_loc)
                        store.append(table_loc, table)
                    else:
                        print(table_loc + ' not found')
            sleep(1)

def store_player_stats(driver, store, player_ids):
    for player in player_ids:
        print('Storing player stats for ' + player)
        stat_names = ['per_game', 'per_36', 'per_poss', 'advanced', 'shooting',
                      'totals', 'pbp', 'highs', 'bio', 'salaries']
        table_prefix = '/player/' + player
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
                table_loc = table_prefix + '/' + playoff_string + stat
                if table_loc not in store:
                    table = globals()['get_player_' + stat](player_soup, playoff_status)
                    if table is not None:
                        store.append(table_loc, table)
        sleep(1)
        
        
