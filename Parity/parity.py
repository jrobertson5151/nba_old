import sys
sys.path.append("..")
from math import log

from Data.helper import *

def win_loss_summary(db, years):
    def win_loss_single_season(year):
        summary = season_summary(db, year)
        summary = summary['W %'].describe().loc['std':'max']
        summary['Season'] = str(int(year)) + '-' + str(int(year+1))
        return summary
    total_summary = pd.DataFrame([win_loss_single_season(y) for y in years])
    total_summary.set_index('Season', inplace = True)
    return total_summary

def norm_probs(probs):
    return [x/sum(probs) for x in probs]

#compute perceived probability from odds
def entropy(probs):
    #probs is a list of probabilities that add up to 1 or greater
    probs = norm_probs(probs)
    return sum([-p*log(p) for p in probs if p > 0])

def eff_num_teams(probs):
    probs = norm_probs(probs)
    return 1/sum([p*p for p in probs])

db = get_db()
try:
    s = win_loss_summary(db, range(2010, 2019))
    e = [entropy([odds_to_prob(x) for x in odds(db, y)['Odds']]) for y in range(1984, 2019)]
    print(e)
    eff = [eff_num_teams([odds_to_prob(x) for x in odds(db, y)['Odds']])
           for y in range(1984, 2019)]
except:
    traceback.print_exc(file=sys.stdout)
finally:
    db.close()
