# src/preprocessor.py
import pandas as pd


def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """Limpeza + conversão correta de geração (Romanos → números)."""
    df = df.copy()

    # Tratamento básico
    df['type_2'] = df['type_2'].fillna('None')
    df['is_legendary_or_mythical'] = df['is_legendary'] | df['is_mythical']

    # Conversão de geração romana para número
    roman_to_int = {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'VI': 6, 'VII': 7, 'VIII': 8, 'IX': 9}
    df['generation'] = df['generation'].map(roman_to_int)

    # Colunas numéricas
    numeric_cols = ['hp', 'attack', 'defense', 'sp_attack', 'sp_defense', 'speed', 'base_stat_total']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Colunas finais
    cols = [
        'pokedex_id', 'name', 'type_1', 'type_2', 'generation',
        'hp', 'attack', 'defense', 'sp_attack', 'sp_defense', 'speed', 'base_stat_total',
        'is_legendary_or_mythical', 'is_baby', 'sprite_url', 'description'
    ]

    return df[cols].dropna(subset=['name', 'type_1'])