import csv
import collections
import scipy.stats as s
from equipos import clubes


combinaciones = [(i, j) for i in clubes for j in clubes if i != j]

def refresh_odds(results, match, local_goals = None, away_goals = None):
    if (local_goals and away_goals) is not None:
        results[match].append([local_goals, away_goals])
    s_1 = 0
    s_2 = 0
    for result in results[match]:
        s_1 += result[0]
        s_2 += result[1]
    prob = (s_1 / len(results[match]), s_2 / len(results[match]))
    return results, prob


def get_matrix(match, odds):
    m = []
    S = 0
    for i in range(5):
        line = []
        for k in range(5):
            p = s.poisson.pmf(i, odds[match][0]) * s.poisson.pmf(k, odds[match][1])
            line.append(p)  # revisar
            S += p
        m.append(line)
    for i in range(5):
        for j in range(5):
            m[i][j] = m[i][j] / S
    return m


def load_database():
    resultados = collections.defaultdict(list)
    prob = {}
    with open('chilean_db.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['LOCAL'] in clubes and row['VISITA'] in clubes:
                resultados[(row['LOCAL'], row['VISITA'])].append(
                    (int(row["GOLESLOCAL"]), int(row["GOLESVISITA"])))
    """
    for i in resultados:
        if len(resultados[i]) <= 2: #tienen menos de 3 partidos
            #print i, resultados[i]
            pass
    
    for i in combinaciones:
        if i not in resultados:
            print i
    """
    for partido in resultados:
        prob[partido] = refresh_odds(resultados, partido)[1]

    l = [[0], [1], [2], [3], [4]]
    matrix = [l, l, l, l, l]
    matrices = {}

    for partido in prob:
        matrices[partido] = get_matrix(partido, prob)

    return matrices


def draw_odds(match, odds):
    p = 0
    for i in range(5):
        print(i)
        #p += odds[match][i][i]
    #return p


def win_odds(match, odds, winner):
    matches = match.split(",")
    print(match)
    p = 0
    if winner in matches[0]: #local
        for i in range(5):
            for j in range(5):
                if j > i:
                    try :
                        p += odds[match][i][j]
                    except KeyError as err :
                        print(err)
        return p
    else:
        return 1 - draw_odds(match, odds) - p


ODDS = load_database()








