from nba_driver import *

def get_games(driver, game_ids):
    base_url = 'https://www.basketball-reference.com/boxscores/'
    def single_game(game_id):
        tables = dict()
        game_soup = get_soup(driver, base_url+game_id+'.html')
        line_score_html = game_soup.find('table', id='line_score')
        if line_score_html is not None:
            line_score = pd.read_html(str(line_score_html))[0]
            correct_cols = ['Team'] + list(line_score.iloc[0][1:])
            line_score.columns = correct_cols
            line_score.drop(0, inplace=True)
            away = str.lower(line_score.iloc[0,0])
            home = str.lower(line_score.iloc[1,0])
            tables['line_score'] = line_score

        ff_html = game_soup.find('table', id='four_factors')
        if ff_html is not None:
            ff_corrected = '<table>' + str(ff_html.tbody) + '</table>'
            ff = pd.read_html(ff_corrected)[0]
            ff.rename(columns={'Unnamed: 0': 'Team'}, inplace=True)
            tables['ff'] = ff

        for tag in game_soup.find_all('th', attrs={'class': 'over_header'}):
            tag.decompose()

        table_ids = ['box_' + away + '_basic', 'box_' + away + '_advanced',
                     'box_' + home + '_basic', 'box_' + home + '_advanced']
        table_names = ['away_basic', 'away_advanced', 'home_basic', 'home_advanced']
        ipdb.set_trace()
        for (table_id, table_name) in zip(table_ids, table_names):
            html = game_soup.find('table', id=table_id)
            if html is not None:
                [t.decompose() for t in html('tr', attrs={'class':'thead'})]
                table = pd.read_html(str(html))[0]
                table.rename(columns={'Starters':'Player'})
                table = table[:-1]
                tables[table_name] = table

        return tables

    rtn = []
    for g in game_ids:
        rtn.append(single_game(g))
        sleep(1)
    return rtn
        
            
            
        
