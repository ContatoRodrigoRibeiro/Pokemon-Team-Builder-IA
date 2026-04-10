import pandas as pd

def load_pokemon_data(filepath: str = "data/pokemon_complete_2025.csv") -> pd.DataFrame:
    """Carrega e faz o primeiro tratamento básico do dataset."""
    df = pd.read_csv(filepath)
    print(f"✅ Dataset carregado: {df.shape[0]} Pokémon")
    return df