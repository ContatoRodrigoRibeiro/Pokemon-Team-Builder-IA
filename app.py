# app.py
import streamlit as st
import pandas as pd
from src.data_loader import load_pokemon_data
from src.preprocessor import preprocess_data
from src.team_optimizer import build_optimal_team

# 1. ATIVAR MODO WIDE PARA CABEREM OS 6 CARDS
st.set_page_config(page_title="Pokémon Team Builder IA", layout="wide")

# ====================== CORES POR TIPO ======================
type_colors = {
    'Normal': '#A8A878', 'Fire': '#F08030', 'Water': '#6890F0', 'Grass': '#78C850',
    'Electric': '#F8D030', 'Ice': '#98D8D8', 'Fighting': '#C03028', 'Poison': '#A040A0',
    'Ground': '#E0C068', 'Flying': '#A890F0', 'Psychic': '#F85888', 'Bug': '#A8B820',
    'Rock': '#B8A038', 'Ghost': '#705898', 'Dragon': '#7038F8', 'Dark': '#705848',
    'Steel': '#B8B8D0', 'Fairy': '#EE99AC'
}

# ====================== CSS - TCG STYLE ======================
st.markdown("""
<style>
    .main { background: linear-gradient(180deg, #121212 0%, #1a1a2e 100%); color: #fff; }

    .tcg-card {
        width: 100%;
        max-width: 280px; /* Aumentado para permitir cartas maiores */
        aspect-ratio: 44 / 88;
        border-radius: 4.5% / 3.5%;
        margin: 0 auto;
        position: relative;
        overflow: hidden;
        background: radial-gradient(circle at 50% 30%, rgba(255,255,255,0.2) 0%, transparent 60%),
                    linear-gradient(135deg, var(--type-color) 0%, #1a1a1a 100%);
        box-shadow: 0 10px 20px rgba(0,0,0,0.5), inset 0 0 0 8px #7a7a7a, inset 0 0 0 10px #333;
        transition: transform 0.4s ease, box-shadow 0.4s ease;
        display: flex;
        flex-direction: column;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        cursor: pointer;
    }

    .tcg-card:hover {
        transform: translateY(-15px) scale(1.05);
        box-shadow: 0 20px 40px rgba(0,0,0,0.6), inset 0 0 0 8px #b5b5b5, inset 0 0 0 10px #333;
    }

    .tcg-card::after {
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: linear-gradient(
            115deg, transparent 20%, rgba(255, 255, 255, 0.5) 30%,
            rgba(255, 255, 255, 0.6) 40%, transparent 50%,
            rgba(255, 255, 255, 0.3) 60%, transparent 80%
        );
        background-size: 200% 200%;
        mix-blend-mode: color-dodge;
        opacity: 0;
        transition: opacity 0.4s ease, background-position 0.5s ease;
        pointer-events: none;
        z-index: 10;
    }

    .tcg-card:hover::after {
        opacity: 1;
        background-position: 100% 100%;
    }

    .tcg-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
        padding: 8px 12px 0 12px;
        color: white;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.8), 0 0 5px var(--type-color);
        z-index: 2;
        flex: 0 0 auto;
    }

    .tcg-name {
        font-size: 1.15rem; /* Fonte um pouco maior */
        font-weight: 900;
        font-style: italic;
        flex-grow: 1;
        margin-left: 6px;
        letter-spacing: 0.5px;
        text-transform: capitalize;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .tcg-hp { font-size: 1.05rem; font-weight: bold; }

    .tcg-image {
        flex: 1 1 auto; /* Permite que a imagem preencha o espaço sem vazar */
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 2;
        padding: 5px;
        min-height: 0; /* Crucial para o flexbox funcionar no aspect-ratio */
    }

    .tcg-image img {
        width: 100%;
        height: 100%;
        max-height: 140px; /* Ajuste no tamanho da imagem */
        object-fit: contain;
        filter: drop-shadow(0px 8px 8px rgba(0,0,0,0.7));
        transition: transform 0.4s ease;
    }

    .tcg-card:hover .tcg-image img {
        transform: scale(1.15) translateY(-5px);
    }

    .tcg-body {
        background: linear-gradient(to bottom, rgba(255,255,255,0.92), rgba(240,240,240,0.98));
        margin: 0 8px 8px 8px; /* Margem inferior reduzida */
        border-radius: 4px;
        padding: 6px;
        box-shadow: inset 0 0 0 2px #d4d4d4, 0 4px 6px rgba(0,0,0,0.3);
        z-index: 2;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        flex: 0 0 auto;
    }

    .type-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: bold;
        color: white;
        margin: 2px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        text-shadow: 1px 1px 1px rgba(0,0,0,0.5);
    }

    .tcg-badges { display: flex; justify-content: center; margin-bottom: 4px; }

    .tcg-stats {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 3px;
        font-size: 0.7rem; /* Fonte um pouco maior para leitura */
        color: #222;
        text-align: left;
        border-top: 1px solid #ccc;
        padding-top: 4px;
    }

    .tcg-stats div {
        background: rgba(0,0,0,0.05);
        padding: 2px 4px;
        border-radius: 3px;
        font-weight: 700;
        display: flex;
        justify-content: space-between;
    }

    h1 { color: #EE1515; text-shadow: 3px 3px 0 #FFCB05; font-size: 2.7rem; }
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

        # Uso de gap="small" para dar mais largura disponível para cada carta
        cols = st.columns(6, gap="small")

        for idx, (_, row) in enumerate(team.iterrows()):
            color1 = type_colors.get(row['type_1'], '#FFCB05')

            badges = f'<span class="type-badge" style="background: {color1};">{row["type_1"]}</span>'
            if row['type_2'] != 'None':
                color2 = type_colors.get(row['type_2'], '#666')
                badges += f'<span class="type-badge" style="background: {color2};">{row["type_2"]}</span>'

            hp = row.get('hp', '-')
            atk = row.get('attack', '-')
            def_stat = row.get('defense', '-')
            spa = row.get('sp_attack', '-')
            spd = row.get('sp_defense', '-')
            spe = row.get('speed', '-')
            bst = row.get('base_stat_total', '-')

            # HTML do card
            card_html = f"""
<div class="tcg-card" style="--type-color: {color1};">
<div class="tcg-header">
<span style="font-size: 0.65rem; font-style: italic; opacity: 0.8; margin-bottom: 3px;">BASIC</span>
<div class="tcg-name">{row['name']}</div>
<div class="tcg-hp">HP {hp}</div>
</div>
<div class="tcg-image">
<img src="{row['sprite_url']}" alt="{row['name']}">
</div>
<div class="tcg-body">
<div class="tcg-badges">
{badges}
</div>
<div class="tcg-stats">
<div><span>ATK</span> <span>{atk}</span></div>
<div><span>DEF</span> <span>{def_stat}</span></div>
<div><span>SPA</span> <span>{spa}</span></div>
<div><span>SPD</span> <span>{spd}</span></div>
<div><span>SPE</span> <span>{spe}</span></div>
<div style="background: #FFCB05; color: #000;"><span>BST</span> <span>{bst}</span></div>
</div>
</div>
</div>
"""
            with cols[idx]:
                st.markdown(card_html, unsafe_allow_html=True)

        st.markdown("<br><br>", unsafe_allow_html=True)
        csv = team[['name', 'type_1', 'type_2', 'base_stat_total']].to_csv(index=False)
        st.download_button("📥 Baixar time como CSV", csv, "meu_time_pokemon.csv", "text/csv", use_container_width=True)

st.caption("Projeto Pokémon Team Builder IA • Deeline Design")