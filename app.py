# app.py
import streamlit as st
import pandas as pd
from src.data_loader import load_pokemon_data
from src.preprocessor import preprocess_data
from src.team_optimizer import build_optimal_team

# 1. ATIVAR MODO WIDE PARA CABEREM OS 6 CARDS
st.set_page_config(page_title="Pokémon Team Builder IA", layout="wide")

# ====================== CORES POR TIPO (DEFINIÇÃO GLOBAL) ======================
type_colors = {
    'Normal': '#A8A878', 'Fire': '#F08030', 'Water': '#6890F0', 'Grass': '#78C850',
    'Electric': '#F8D030', 'Ice': '#98D8D8', 'Fighting': '#C03028', 'Poison': '#A040A0',
    'Ground': '#E0C068', 'Flying': '#A890F0', 'Psychic': '#F85888', 'Bug': '#A8B820',
    'Rock': '#B8A038', 'Ghost': '#705898', 'Dragon': '#7038F8', 'Dark': '#705848',
    'Steel': '#B8B8D0', 'Fairy': '#EE99AC'
}

# ====================== CSS - TCG STYLE COM MELHORIAS DE NOME ======================
st.markdown("""
<style>
    .main { 
        background: linear-gradient(180deg, #121212 0%, #1a1a2e 100%); 
        color: #fff; 
    }

    .tcg-card {
        width: 100%;
        max-width: 260px;
        aspect-ratio: 42 / 94;
        border-radius: 4.5% / 3.5%;
        margin: 0 auto;
        overflow: hidden;
        background: radial-gradient(circle at 50% 30%, rgba(255,255,255,0.2) 0%, transparent 60%),
                    linear-gradient(135deg, var(--type-color) 0%, #1a1a1a 100%);
        box-shadow: 0 10px 20px rgba(0,0,0,0.5), 
                    inset 0 0 0 8px #7a7a7a, 
                    inset 0 0 0 10px #333;
        display: flex;
        flex-direction: column;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }

   .tcg-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 11px 14px 5px 14px;
        color: #fff;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.8);
        font-weight: 900;
        border-radius: 8px 8px 0 0;
    }

    .basic {
        font-size: 0.68rem;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        opacity: 0.95;
    }

    .tcg-hp {
        font-size: 1.12rem;
        font-weight: 900;
        background: rgba(0, 0, 0, 0.45);
        padding: 2px 12px;
        border-radius: 4px;
        white-space: nowrap;
    }

    .basic {
        font-size: 0.65rem;
        font-weight: 900;
        letter-spacing: 1px;
        text-transform: uppercase;
        opacity: 0.9;
    }

    .tcg-hp {
        font-size: 1.05rem;
        font-weight: bold;
        background: rgba(0, 0, 0, 0.55);
        padding: 4px 12px;
        border-radius: 6px;
        white-space: nowrap;
    }

    .tcg-name {
        font-size: 1.22rem;
        font-weight: 900;
        font-style: italic;
        text-align: center;
        color: white;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.9);
        padding: 0 12px 6px;
        min-height: 58px;
        display: flex;
        align-items: center;
        justify-content: center;
        line-height: 1.1;
        text-transform: capitalize;
    }

    .tcg-image {
        flex: 1 1 auto;
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 4px 0;
    }

    .tcg-image img {
        width: 88%;
        max-height: 128px;
        object-fit: contain;
        filter: drop-shadow(0px 8px 10px rgba(0,0,0,0.7));
    }

    .tcg-body {
        background: linear-gradient(to bottom, rgba(255,255,255,0.92), rgba(240,240,240,0.98));
        margin: 0 8px 10px 8px;
        border-radius: 4px;
        padding: 10px;
        box-shadow: inset 0 0 0 2px #040404;
    }

    .type-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: bold;
        color: white;
        margin: 1px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }

    .tcg-stats {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 3px;
        font-size: 0.7rem;
        color: #222;
        border-top: 1px solid #ccc;
        padding-top: 4px;
        margin-top: 4px;
    }

    .tcg-stats div {
        background: rgba(0,0,0,0.04);
        padding: 1px 4px;
        border-radius: 3px;
        display: flex;
        justify-content: space-between;
    }

    h1 { 
        color: #EE1515; 
        text-shadow: 3px 3px 0 #FFCB05; 
        font-size: 2.8rem;
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
style = st.sidebar.selectbox("Estilo do time", ["Balanciado", "Agressivo", "Defensivo"])

if st.sidebar.button("🚀 Gerar Time Otimizado", type="primary", use_container_width=True):
    with st.spinner("Otimizando seu time..."):
        team, coverage = build_optimal_team(pokemon, no_legendary, max_gen, style)

        st.success(f"✅ **Time gerado!** Cobertura: **{coverage}/18** tipos")

        st.subheader("Seu Time")
        cols = st.columns(6, gap="small")

        for idx, (_, row) in enumerate(team.iterrows()):
            color1 = type_colors.get(row.get('type_1'), '#FFCB05')

            # Badges dos tipos
            badges = f'<span class="type-badge" style="background: {color1};">{row.get("type_1", "")}</span>'
            if row.get('type_2') and str(row['type_2']).lower() not in ['none', 'nan', '']:
                color2 = type_colors.get(row['type_2'], '#666666')
                badges += f'<span class="type-badge" style="background: {color2};">{row["type_2"]}</span>'

            hp = row.get('hp', '-')
            atk = row.get('attack', '-')
            def_stat = row.get('defense', '-')
            spa = row.get('sp_attack', '-')
            spd = row.get('sp_defense', '-')
            spe = row.get('speed', '-')
            bst = row.get('base_stat_total', '-')

            # ====================== CARD HTML ======================
            color1 = type_colors.get(str(row.get('type_1', '')).capitalize(), '#FFCB05')

            badges = f'<span class="type-badge" style="background: {color1};">{row.get("type_1", "")}</span>'
            if row.get('type_2') and str(row.get('type_2', '')).lower() not in ['none', 'nan', '']:
                color2 = type_colors.get(str(row.get('type_2', '')).capitalize(), '#666666')
                badges += f'<span class="type-badge" style="background: {color2};">{row.get("type_2", "")}</span>'

            hp = row.get('hp', '-')
            atk = row.get('attack', '-')
            def_stat = row.get('defense', '-')
            spa = row.get('sp_attack', '-')
            spd = row.get('sp_defense', '-')
            spe = row.get('speed', '-')
            bst = row.get('base_stat_total', '-')

            card_html = f"""
                        <div class="tcg-card" style="--type-color: {color1};">
                            <div class="tcg-header" style="background-color: {color1} !important;">
                                <div class="basic">BASIC</div>
                                <div class="tcg-hp">HP {hp}</div>
                            </div>
                            <div class="tcg-name">{row['name']}</div>
                            <div class="tcg-image">
                                <img src="{row['sprite_url']}" alt="{row['name']}">
                            </div>
                            <div class="tcg-body">
                                <div class="tcg-badges">{badges}</div>
                                <div class="tcg-stats">
                                    <div><span>ATK</span><span>{atk}</span></div>
                                    <div><span>DEF</span><span>{def_stat}</span></div>
                                    <div><span>SPA</span><span>{spa}</span></div>
                                    <div><span>SPD</span><span>{spd}</span></div>
                                    <div><span>SPE</span><span>{spe}</span></div>
                                    <div style="background:#FFCB05;color:#000;font-weight:bold;">
                                        <span>BST</span><span>{bst}</span>
                                    </div>
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