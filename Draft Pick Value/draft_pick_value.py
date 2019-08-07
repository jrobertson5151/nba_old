import sys
sys.path.append("..")

from Data.helper import *

def win_shares_for_drafting_team(db, player_id):
    try:
        bio = player_bio(db, player_id)
        adv_string = '/player/' + player_id + '/advanced'
        draft_year = bio['Draft Year']
        draft_number = bio['Draft Number']
            
        adv = db[adv_string]
        draft_team = adv.iloc[0]['Tm']
        #actually the first team the player played for to account for trades
        team_win_shares = adv[adv['Tm'] == draft_team]['WS'].sum()
        career_win_shares = adv['WS'].sum()
        
        return (draft_year, draft_number, team_win_shares, career_win_shares)
    except:
        return None

def all_win_shares(db):
    pl = player_list(db)
    list_of_ws = []
    for pid in pl['player_id']:
        rtn = win_shares_for_drafting_team(db, pid)
        if rtn is not None:
            (dy, dn, tws, cws) = rtn
            name = pl.loc[pid]['Player']
            list_of_ws.append((name, dy, dn, tws, cws))
    return pd.DataFrame(list_of_ws, columns=
                        ['Name', 'Draft Year', 'Draft Number', 'Team WS', 'Career WS'])

