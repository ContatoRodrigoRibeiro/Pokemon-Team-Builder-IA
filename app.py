# app.py
import streamlit as st
import pandas as pd
from src.data_loader import load_pokemon_data
from src.preprocessor import preprocess_data
from src.team_optimizer import build_optimal_team

# ====================== CORES POR TIPO ======================
type_colors = {
    'Normal': '#A8A878', 'Fire': '#F08030', 'Water': '#6890F0', 'Grass': '#78C850',
    'Electric': '#F8D030', 'Ice': '#98D8D8', 'Fighting': '#C03028', 'Poison': '#A040A0',
    'Ground': '#E0C068', 'Flying': '#A890F0', 'Psychic': '#F85888', 'Bug': '#A8B820',
    'Rock': '#B8A038', 'Ghost': '#705898', 'Dragon': '#7038F8', 'Dark': '#705848',
    'Steel': '#B8B8D0', 'Fairy': '#EE99AC'
}

# ====================== CSS - CARDS COM DIMENSÕES FIXAS (TCG STYLE) ======================
st.markdown("""
<style>
    .main { background: linear-gradient(180deg, #1a1a2e 0%, #0f0f1e 100%); color: #fff; }

    .pokemon-card {
        background: #ffffff;
        border: 8px solid #FFCB05;
        border-radius: 16px;
        padding: 12px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.4);
        text-align: center;
        transition: all 0.3s ease;
        width: 100%;
        max-width: 205px;
        height: 320px;           /* altura fixa */
        margin: 0 auto;
        display: flex;
        flex-direction: column;
        align-items: center;
    }

    .pokemon-card:hover {
        transform: scale(1.05);
        box-shadow: 0 20px 40px rgba(255, 203, 5, 0.5);
    }

    .pokemon-card img {
        width: 155px;
        height: 155px;
        object-fit: contain;
        margin-top: 8px;
        margin-bottom: 12px;
    }

    .pokemon-name {
        font-size: 1.28rem;
        font-weight: bold;
        color: #222222;
        margin: 0 0 10px 0;
        min-height: 58px;
        line-height: 1.2;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .type-badge {
        display: inline-block;
        padding: 5px 18px;
        border-radius: 30px;
        font-size: 0.82rem;
        font-weight: bold;
        color: white;
        margin: 4px 3px;
        box-shadow: 0 3px 8px rgba(0,0,0,0.3);
    }

    h1 { 
        color: #EE1515; 
        text-shadow: 3px 3px 0 #FFCB05; 
        font-size: 2.7rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("⚔️ Pokémon Team Builder IA")
st.markdown("**Monte o time perfeito automaticamente** usando o Ultimate Pokémon Dataset 2025")


# Carregar dados
@st.cache_data
def get_data():
    df = load_pokemon_data()
    return preprocess_data(df)


pokemon = get_data()

# Sidebar
st.sidebar.header("⚙️ Configurações do Time")
no_legendary = st.sidebar.checkbox("Sem lendários/míticos", value=True)
max_gen = st.sidebar.slider("Máximo de geração", 1, 9, 9)
style = st.sidebar.selectbox("Estilo do time", ["balanced", "aggressive", "defensive"])

if st.sidebar.button("🚀 Gerar Time Otimizado", type="primary", use_container_width=True):
    with st.spinner("Otimizando seu time..."):
        team, coverage = build_optimal_team(pokemon, no_legendary, max_gen, style)

        st.success(f"✅ **Time gerado!** Cobertura: **{coverage}/18** tipos")

        st.subheader("Seu Time")
        cols = st.columns(6)

        for idx, (_, row) in enumerate(team.iterrows()):
            color = type_colors.get(row['type_1'], '#FFCB05')

            badges = f'<span class="type-badge" style="background: {color};">{row["type_1"]}</span>'
            if row['type_2'] != 'None':
                color2 = type_colors.get(row['type_2'], '#666')
                badges += f' <span class="type-badge" style="background: {color2};">{row["type_2"]}</span>'

            with cols[idx]:
                st.markdown(f"""
                <div class="pokemon-card">
                    <img src="{row['sprite_url']}" alt="{row['name']}">
                    <div class="pokemon-name">{row['name']}</div>
                    <div style="margin-bottom: 12px;">
                        {badges}
                    </div>
                    <p style="margin: 0; font-size: 1.05rem; color: #333;">
                        BST: <strong>{row['base_stat_total']}</strong>
                    </p>
                </div>
                """, unsafe_allow_html=True)

        csv = team[['name', 'type_1', 'type_2', 'base_stat_total']].to_csv(index=False)
        st.download_button("📥 Baixar time como CSV", csv, "meu_time_pokemon.csv", "text/csv", use_container_width=True)

st.caption("Projeto Pokémon Team Builder IA • Rodrigo Ribeiro")