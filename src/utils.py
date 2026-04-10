# src/utils.py
from src.type_chart import types, get_effectiveness


def calculate_team_coverage(team_df):
    """Calcula quantos tipos o time ataca com super efetividade (cobertura)."""
    covered = set()
    for _, p in team_df.iterrows():
        t1 = p['type_1']
        t2 = p['type_2']

        for t in types:
            if get_effectiveness(t1, t) == 2:
                covered.add(t)
        if t2 != 'None':
            for t in types:
                if get_effectiveness(t2, t) == 2:
                    covered.add(t)
    return len(covered), covered