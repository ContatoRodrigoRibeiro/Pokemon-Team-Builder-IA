# src/team_optimizer.py
import pulp
import pandas as pd
from src.utils import calculate_team_coverage


def build_optimal_team(df: pd.DataFrame, no_legendary: bool = True, max_gen: int = None, style: str = 'balanced'):
    """
    Monta o melhor time de 6 Pokémon.
    Agora com pré-filtragem (mais confiável).
    """
    # ====================== PRÉ-FILTRAGEM (mais confiável) ======================
    pool = df.copy()

    if no_legendary:
        pool = pool[~pool['is_legendary_or_mythical']]

    if max_gen is not None:
        pool = pool[pool['generation'] <= max_gen]

    if len(pool) < 6:
        st.error("Não há Pokémon suficientes com esses filtros!")
        return pd.DataFrame(), 0

    # ====================== OTIMIZAÇÃO ======================
    prob = pulp.LpProblem("Pokemon_Team_Builder", pulp.LpMaximize)

    vars_list = [pulp.LpVariable(f"p_{i}", cat="Binary") for i in pool.index]

    # Score conforme o estilo
    if style == 'aggressive':
        score = pulp.lpSum(
            [vars_list[i] * (pool.iloc[i]['attack'] + pool.iloc[i]['sp_attack'] + pool.iloc[i]['speed']) for i in
             range(len(pool))])
    elif style == 'defensive':
        score = pulp.lpSum(
            [vars_list[i] * (pool.iloc[i]['defense'] + pool.iloc[i]['sp_defense'] + pool.iloc[i]['hp']) for i in
             range(len(pool))])
    else:
        score = pulp.lpSum([vars_list[i] * pool.iloc[i]['base_stat_total'] for i in range(len(pool))])

    prob += score
    prob += pulp.lpSum(vars_list) == 6

    prob.solve(pulp.PULP_CBC_CMD(msg=0))

    # Extrair time
    selected_idx = [i for i in range(len(pool)) if vars_list[i].value() == 1]
    team = pool.iloc[selected_idx].copy()

    coverage, _ = calculate_team_coverage(team)

    print(f"🚀 Time otimizado gerado! Cobertura: {coverage}/18 | Estilo: {style}")
    return team, coverage