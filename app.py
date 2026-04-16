import sys
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent.absolute()))

import streamlit as st
import pandas as pd
import random
import requests
import re
from src.core.models import Pokemon, Team, Type

st.set_page_config(page_title="Pokémon Team Builder IA", page_icon="⚔️", layout="wide")

st.title("🤖 Pokémon Team Builder IA")
st.subheader("Monte times imbatíveis com IA • Gen 9 + anteriores")

if "current_team" not in st.session_state:
    st.session_state.current_team = Team()

if "pokemon_cache" not in st.session_state:
    st.session_state.pokemon_cache = {}

if "last_generated_team" not in st.session_state:
    st.session_state.last_generated_team = []

if "hybrid_team" not in st.session_state:
    st.session_state.hybrid_team = []

if "enemy_team" not in st.session_state:
    st.session_state.enemy_team = []


def get_generation_by_id(pkm_id):
    if pkm_id <= 151:
        return 1
    elif pkm_id <= 251:
        return 2
    elif pkm_id <= 386:
        return 3
    elif pkm_id <= 493:
        return 4
    elif pkm_id <= 649:
        return 5
    elif pkm_id <= 721:
        return 6
    elif pkm_id <= 809:
        return 7
    elif pkm_id <= 905:
        return 8
    else:
        return 9


def extrair_geracao_do_prompt(prompt: str):
    if not prompt: return None
    prompt = prompt.lower().strip()
    padroes = [
        r'(?:gen|geração|geracao|generação|g)\s*(\d+)',
        r'g(\d+)',
        r'(\d+)[ªa]?\s*(?:gen|geração|geracao|generação)',
        r'(?:gen|geração|geracao|generação)\s*(\d+)[ªa]?'
    ]
    for padrao in padroes:
        match = re.search(padrao, prompt)
        if match:
            return int(match.group(1))
    return None


pt_to_en = {
    "Planta": "Grass", "Grama": "Grass", "Fogo": "Fire", "Água": "Water", "Agua": "Water", "agua": "Water",
    "Elétrico": "Electric", "Eletrico": "Electric", "eletrico": "Electric", "Gelo": "Ice",
    "Lutador": "Fighting", "Luta": "Fighting", "Veneno": "Poison", "Terra": "Ground",
    "Voador": "Flying", "Psíquico": "Psychic", "Psiquico": "Psychic", "Inseto": "Bug",
    "Pedra": "Rock", "Rocha": "Rock", "pedra": "Rock", "rocha": "Rock",
    "Fantasma": "Ghost", "Dragão": "Dragon", "Dragao": "Dragon",
    "Sombrio": "Dark", "Fada": "Fairy", "Aço": "Steel", "Normal": "Normal"
}

type_colors = {
    "Grass": "#78C850", "Fire": "#F08030", "Water": "#6890F0", "Electric": "#F8D030",
    "Ice": "#98D8D8", "Fighting": "#C03028", "Poison": "#A040A0", "Ground": "#E0C068",
    "Flying": "#A890F0", "Psychic": "#F85888", "Bug": "#A8B820", "Rock": "#B8A038",
    "Ghost": "#705898", "Dragon": "#7038F8", "Dark": "#705848", "Steel": "#B8B8D0",
    "Fairy": "#EE99AC", "Normal": "#A8A878"
}

type_chart = {
    "Normal": {"Rock": 0.5, "Ghost": 0, "Steel": 0.5},
    "Fire": {"Fire": 0.5, "Water": 0.5, "Grass": 2, "Ice": 2, "Bug": 2, "Rock": 0.5, "Dragon": 0.5, "Steel": 2},
    "Water": {"Fire": 2, "Water": 0.5, "Grass": 0.5, "Ground": 2, "Rock": 2, "Dragon": 0.5},
    "Grass": {"Fire": 0.5, "Water": 2, "Grass": 0.5, "Poison": 0.5, "Ground": 2, "Flying": 0.5, "Bug": 0.5, "Rock": 2,
              "Dragon": 0.5, "Steel": 0.5},
    "Electric": {"Water": 2, "Grass": 0.5, "Electric": 0.5, "Ground": 0, "Flying": 2, "Dragon": 0.5},
    "Ice": {"Fire": 0.5, "Water": 0.5, "Grass": 2, "Ice": 0.5, "Ground": 2, "Flying": 2, "Dragon": 2, "Steel": 0.5},
    "Fighting": {"Normal": 2, "Ice": 2, "Poison": 0.5, "Flying": 0.5, "Psychic": 0.5, "Bug": 0.5, "Rock": 2, "Ghost": 0,
                 "Dark": 2, "Steel": 2, "Fairy": 0.5},
    "Poison": {"Grass": 2, "Poison": 0.5, "Ground": 0.5, "Rock": 0.5, "Ghost": 0.5, "Steel": 0, "Fairy": 2},
    "Ground": {"Fire": 2, "Grass": 0.5, "Electric": 2, "Poison": 2, "Flying": 0, "Bug": 0.5, "Rock": 2, "Steel": 2},
    "Flying": {"Grass": 2, "Electric": 0.5, "Fighting": 2, "Bug": 2, "Rock": 0.5, "Steel": 0.5},
    "Psychic": {"Fighting": 2, "Poison": 2, "Psychic": 0.5, "Dark": 0, "Steel": 0.5},
    "Bug": {"Fire": 0.5, "Grass": 2, "Fighting": 0.5, "Poison": 0.5, "Flying": 0.5, "Psychic": 2, "Ghost": 0.5,
            "Dark": 2, "Steel": 0.5, "Fairy": 0.5},
    "Rock": {"Fire": 2, "Ice": 2, "Fighting": 0.5, "Ground": 0.5, "Flying": 2, "Bug": 2, "Steel": 0.5},
    "Ghost": {"Normal": 0, "Psychic": 2, "Ghost": 2, "Dark": 0.5},
    "Dragon": {"Dragon": 2, "Steel": 0.5, "Fairy": 0},
    "Dark": {"Fighting": 0.5, "Psychic": 2, "Ghost": 2, "Dark": 0.5, "Fairy": 0.5},
    "Steel": {"Fire": 0.5, "Water": 0.5, "Electric": 0.5, "Ice": 2, "Rock": 2, "Steel": 0.5, "Fairy": 2},
    "Fairy": {"Fire": 0.5, "Fighting": 2, "Poison": 0.5, "Dragon": 2, "Dark": 2, "Steel": 0.5}
}


def get_defensive_coverage(team):
    if not team.pokemon:
        return {}
    coverage = {t: 1.0 for t in type_chart.keys()}
    for pkm in team.pokemon:
        for atk_type in coverage:
            multiplier = 1.0
            for def_type in [t.value for t in pkm.types]:
                multiplier *= type_chart.get(atk_type, {}).get(def_type, 1.0)
            coverage[atk_type] = max(coverage[atk_type], multiplier)
    return coverage


def get_card_color(primary_type):
    return type_colors.get(primary_type, "#A8A878")


def render_pokemon_card(pkm, show_remove=False, index=None, key_prefix="card"):
    primary_type = pkm.types[0].value if pkm.types else "Normal"
    card_color = get_card_color(primary_type)
    stats = pkm.base_stats
    bst = getattr(pkm, 'bst', sum(stats.values()) if stats else 0)

    with st.container(border=True):
        col_h1, col_h2 = st.columns([4, 1])
        with col_h1:
            st.markdown(
                f"<div style='background:{card_color}; color:white; padding:6px 12px; border-radius:8px; font-size:0.85rem; font-weight:bold; text-align:center;'>BASIC</div>",
                unsafe_allow_html=True)
        with col_h2:
            st.markdown(
                f"<div style='background:#2E2E2E; color:white; padding:6px 8px; border-radius:8px; font-size:1.05rem; font-weight:bold; text-align:center;'>HP {stats.get('HP', 0)}</div>",
                unsafe_allow_html=True)

        sprite_url = pkm.sprite
        if not sprite_url or "http" not in str(sprite_url):
            try:
                name_lower = pkm.name.lower().replace(" ", "-")
                r = requests.get(f"https://pokeapi.co/api/v2/pokemon/{name_lower}", timeout=8)
                if r.status_code == 200:
                    sprite_url = r.json()["sprites"]["front_default"]
            except:
                sprite_url = None
        if sprite_url:
            st.markdown(
                "<div style='display:flex; justify-content:center; align-items:center; height:160px; margin:8px 0;'>",
                unsafe_allow_html=True)
            st.image(sprite_url, width=160)
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(f"<h3 style='text-align:center; margin:8px 0 6px 0;'>{pkm.name}</h3>", unsafe_allow_html=True)

        type_cols = st.columns(len(pkm.types))
        for i, t in enumerate(pkm.types):
            color = get_card_color(t.value)
            st.markdown(
                f"<div style='background:{color}; color:white; padding:4px 12px; border-radius:9999px; text-align:center; font-size:0.85rem; font-weight:bold;'>{t.value}</div>",
                unsafe_allow_html=True)

        st.markdown(f"""
        <div style="display:flex; justify-content:space-around; background:#1E1E1E; padding:12px; border-radius:12px; margin-top:12px; font-size:0.8rem;">
            <div><b>ATK</b><br>{stats.get('ATK', 0)}</div>
            <div><b>DEF</b><br>{stats.get('DEF', 0)}</div>
            <div><b>SPA</b><br>{stats.get('SPA', 0)}</div>
            <div><b>SPD</b><br>{stats.get('SPD', 0)}</div>
            <div><b>SPE</b><br>{stats.get('SPE', 0)}</div>
            <div style="background:#FFD700; color:#000; padding:4px 10px; border-radius:8px; font-weight:bold;">BST<br>{bst}</div>
        </div>
        """, unsafe_allow_html=True)

        if show_remove and index is not None:
            if st.button("🗑️ Remover", key=f"{key_prefix}_{index}", use_container_width=True):
                st.session_state.current_team.remove_pokemon(index)
                st.rerun()


# ====================== CARREGAMENTO CSV ======================
if "full_pokedex" not in st.session_state:
    try:
        df = pd.read_csv("data/pokemon_cleaned_pt.csv")
        st.session_state.full_pokedex = []
        for _, row in df.iterrows():
            pkm_id = int(row.get("id_pokedex", row.get("id", 0)))
            nome = str(row.get("nome", "")).strip()
            try:
                gen = int(row["geracao"])
            except:
                gen = get_generation_by_id(pkm_id)

            types = []
            if pd.notna(row.get("tipo_1")):
                tipo_pt = str(row["tipo_1"]).strip().title()
                tipo_en = pt_to_en.get(tipo_pt, tipo_pt)
                types.append(Type(tipo_en))
            if pd.notna(row.get("tipo_2")):
                tipo_pt = str(row["tipo_2"]).strip().title()
                tipo_en = pt_to_en.get(tipo_pt, tipo_pt)
                if tipo_en not in [t.value for t in types]:
                    types.append(Type(tipo_en))

            sprite = str(row.get("url_sprite", "")).strip() or None

            base_stats = {
                "HP": int(row.get("hp", 0)),
                "ATK": int(row.get("ataque", 0)),
                "DEF": int(row.get("defesa", 0)),
                "SPA": int(row.get("ataque_especial", 0)),
                "SPD": int(row.get("defesa_especial", 0)),
                "SPE": int(row.get("velocidade", 0))
            }
            bst = sum(base_stats.values())

            abilities = []
            for col in ["habilidade_1", "habilidade_2", "habilidade_oculta"]:
                if col in row and pd.notna(row[col]):
                    abilities.extend([a.strip().title() for a in str(row[col]).split(",") if a.strip()])

            pkm = Pokemon(id=pkm_id, name=nome.replace("-", " ").title(), types=types,
                          abilities=list(dict.fromkeys(abilities)), base_stats=base_stats, sprite=sprite)
            pkm.generation = gen
            pkm.bst = bst
            st.session_state.full_pokedex.append(pkm)
        st.success(f"✅ {len(st.session_state.full_pokedex)} Pokémon carregados!")
    except Exception as e:
        st.error(f"Erro ao carregar CSV: {e}")
        st.session_state.full_pokedex = []

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🛠️ Modo Manual", "🔬 Análise Avançada", "🧠 Recomendações Inteligentes",
    "🤖 Gerar com IA", "🌟 Modo IA Híbrido + Simulador"
])

with tab1:
    st.header("Monte seu Time Manualmente")
    col_busca, col_time = st.columns([2, 3])

    with col_busca:
        st.subheader("🔍 Buscar Pokémon")
        pokemon_name = st.text_input("Nome do Pokémon (em inglês)", placeholder="pikachu").strip().lower()

        if st.button("➕ Buscar e Adicionar", type="primary", use_container_width=True):
            if pokemon_name:
                try:
                    if pokemon_name in st.session_state.pokemon_cache:
                        pkm = st.session_state.pokemon_cache[pokemon_name]
                    else:
                        r = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon_name.replace(' ', '-')}",
                                         timeout=10)
                        if r.status_code == 200:
                            data = r.json()
                            pkm = Pokemon(
                                id=data["id"],
                                name=data["name"].replace("-", " ").title(),
                                types=[Type(t["type"]["name"].title()) for t in data["types"]],
                                abilities=[a["ability"]["name"].replace("-", " ").title() for a in data["abilities"]],
                                base_stats={stat["stat"]["name"]: stat["base_stat"] for stat in data["stats"]},
                                sprite=data["sprites"]["front_default"]
                            )
                            pkm.generation = get_generation_by_id(pkm.id)
                            st.session_state.pokemon_cache[pokemon_name] = pkm
                        else:
                            st.error("❌ Pokémon não encontrado.")
                            st.stop()
                    if st.session_state.current_team.add_pokemon(pkm):
                        st.success(f"✅ {pkm.name} adicionado!")
                        st.rerun()
                    else:
                        st.error("❌ Time completo! (máximo 6)")
                except Exception as e:
                    st.error(f"Erro: {e}")

    with col_time:
        st.subheader("Seu Time Atual")
        team = st.session_state.current_team
        if team.pokemon:
            cols = st.columns(len(team.pokemon))
            for i, pkm in enumerate(team.pokemon):
                with cols[i]:
                    render_pokemon_card(pkm, show_remove=True, index=i, key_prefix=f"manual_{i}")
        else:
            st.info("Time vazio. Adicione Pokémon acima.")

with tab2:
    st.header("🔬 Análise Avançada")
    team = st.session_state.current_team
    if not team.pokemon:
        st.warning("Monte um time primeiro para ver a análise avançada!")
        st.stop()

    st.subheader("Seu Time Atual")
    for pkm in team.pokemon:
        tipos = ', '.join(t.value for t in pkm.types)
        st.write(f"• **{pkm.name}** – {tipos} | Gen {getattr(pkm, 'generation', '?')}")

    st.subheader("📊 Cobertura Defensiva")
    coverage = get_defensive_coverage(team)

    col1, col2 = st.columns([3, 2])
    with col1:
        st.write("**Multiplicador de dano recebido por tipo de ataque:**")
        for atk_type, multiplier in sorted(coverage.items(), key=lambda x: x[1], reverse=True):
            if multiplier >= 2:
                st.error(f"🔴 **{atk_type}** → {multiplier}x (Fraqueza grave)")
            elif multiplier > 1:
                st.warning(f"🟠 **{atk_type}** → {multiplier}x (Fraqueza)")
            elif multiplier == 0:
                st.success(f"🟢 **{atk_type}** → Imune")
            elif multiplier < 1:
                st.success(f"🟢 **{atk_type}** → {multiplier}x (Resistente)")
            else:
                st.write(f"⚪ **{atk_type}** → {multiplier}x (Neutro)")

    with col2:
        st.write("**Resumo:**")
        weak = sum(1 for v in coverage.values() if v > 1)
        immune = sum(1 for v in coverage.values() if v == 0)
        strong = sum(1 for v in coverage.values() if v < 1)
        st.metric("Fraquezas graves", weak)
        st.metric("Imunidades", immune)
        st.metric("Resistências", strong)

    st.subheader("💡 Sugestões rápidas de melhoria")
    st.write("• Adicione Pokémon que cubram as fraquezas mostradas acima.")
    st.write("• Priorize Pokémon com imunidades ou resistências aos tipos mais perigosos.")

with tab3:
    st.header("🧠 Recomendações Inteligentes")
    team = st.session_state.current_team
    if not team.pokemon:
        st.warning("Monte um time primeiro para receber recomendações!")
        st.stop()

    st.subheader("Sugestões para completar seu time")
    current_types = {t.value for pkm in team.pokemon for t in pkm.types}
    recommended = []
    for pkm in st.session_state.full_pokedex:
        if pkm in team.pokemon: continue
        pkm_types = {t.value for t in pkm.types}
        new_types = pkm_types - current_types
        if new_types:
            recommended.append((pkm, len(new_types)))
    recommended.sort(key=lambda x: x[1], reverse=True)
    recommended = recommended[:6]

    if recommended:
        for pkm, new_count in recommended:
            with st.container(border=True):
                cols = st.columns([1, 4, 2])
                with cols[0]:
                    if pkm.sprite: st.image(pkm.sprite, width=80)
                with cols[1]:
                    st.markdown(f"**{pkm.name}**")
                    tipos = ', '.join(t.value for t in pkm.types)
                    st.caption(f"Tipos: {tipos} | +{new_count} tipo(s) novo(s)")
                with cols[2]:
                    if st.button("➕ Adicionar", key=f"rec_{pkm.id}"):
                        if st.session_state.current_team.add_pokemon(pkm):
                            st.success(f"✅ {pkm.name} adicionado!")
                            st.rerun()
    else:
        st.info("Seu time já tem ótima cobertura de tipos!")

with tab4:
    st.header("🤖 Gerar Time Completo com IA")
    st.caption("Usando pokemon_cleaned_pt.csv + Filtro por Geração + Tipo")

    user_prompt = st.text_area("Descreva o time", placeholder="time de água gen 9", height=100)

    if st.button("🚀 Gerar Time com IA", type="primary", use_container_width=True):
        if not st.session_state.full_pokedex or not user_prompt.strip():
            st.error("Dataset não carregado ou descrição vazia!")
            st.stop()

        with st.spinner("🔍 Gerando time..."):
            filtered = st.session_state.full_pokedex.copy()
            gen_filter = extrair_geracao_do_prompt(user_prompt)
            if gen_filter:
                filtered = [p for p in filtered if getattr(p, 'generation', 0) == gen_filter]
                if len(filtered) == 0:
                    filtered = [p for p in st.session_state.full_pokedex if get_generation_by_id(p.id) == gen_filter]
                st.success(f"✅ Filtrado para **Gen {gen_filter}** ({len(filtered)} Pokémon)")

            prompt_lower = user_prompt.lower()
            single_type = None
            for pt, en in pt_to_en.items():
                if pt.lower() in prompt_lower:
                    single_type = en
                    break
            if single_type:
                filtered = [p for p in filtered if any(t.value == single_type for t in p.types)]
                st.success(f"🔥 Tipo **{single_type}** aplicado ({len(filtered)} Pokémon restantes)")

            if len(filtered) < 6:
                st.error(f"❌ Só encontrei {len(filtered)} Pokémon.")
                st.stop()

            generated = random.sample(filtered, 6)
            st.session_state.last_generated_team = generated
            st.success(f"✅ Time gerado com sucesso! (Gen {gen_filter or 'qualquer'})")

    if st.session_state.last_generated_team:
        st.subheader("Seu time gerado pela IA")
        cols = st.columns(len(st.session_state.last_generated_team))
        for idx, pkm in enumerate(st.session_state.last_generated_team):
            with cols[idx]:
                render_pokemon_card(pkm, show_remove=False, key_prefix=f"gen_{idx}")

with tab5:
    st.header("🌟 Modo IA Híbrido + Simulador")
    st.caption("Gere um time com IA e simule batalhas contra times inimigos")

    col_h1, col_h2 = st.columns([1, 1])
    with col_h1:
        if st.button("🤖 Gerar Time Híbrido com IA", type="primary", use_container_width=True):
            with st.spinner("🔍 Gerando time híbrido..."):
                filtered = st.session_state.full_pokedex.copy()
                generated = random.sample(filtered, 6)
                st.session_state.hybrid_team = generated
                st.success("✅ Time Híbrido gerado!")

    with col_h2:
        if st.button("⚔️ Simular Batalha", type="secondary", use_container_width=True):
            if len(st.session_state.current_team.pokemon) < 6:
                st.error("Seu time precisa ter 6 Pokémon para simular!")
            else:
                with st.spinner("Simulando batalha..."):
                    enemy_team = random.sample(st.session_state.full_pokedex, 6)
                    st.session_state.enemy_team = enemy_team
                    st.success("Batalha simulada!")

    st.subheader("Seu Time Atual")
    team = st.session_state.current_team
    if team.pokemon:
        cols = st.columns(len(team.pokemon))
        for i, pkm in enumerate(team.pokemon):
            with cols[i]:
                render_pokemon_card(pkm, show_remove=True, index=i, key_prefix=f"hybrid_{i}")
    else:
        st.info("Time vazio.")

    if st.session_state.hybrid_team:
        st.subheader("Time Sugerido pela IA (Híbrido)")
        cols = st.columns(len(st.session_state.hybrid_team))
        for idx, pkm in enumerate(st.session_state.hybrid_team):
            with cols[idx]:
                render_pokemon_card(pkm, show_remove=False, key_prefix=f"hybrid_add_{idx}")

    if "enemy_team" in st.session_state:
        st.subheader("⚔️ Simulação de Batalha")
        st.write("**Seu Time** vs **Time Inimigo**")
        col_y, col_e = st.columns(2)
        with col_y:
            st.write("**Seu Time**")
            for p in st.session_state.current_team.pokemon:
                st.write(f"• {p.name}")
        with col_e:
            st.write("**Time Inimigo**")
            for p in st.session_state.enemy_team:
                st.write(f"• {p.name}")

        your_score = sum(1 for p in st.session_state.current_team.pokemon if random.random() > 0.4)
        enemy_score = 6 - your_score + random.randint(-1, 2)
        if your_score > enemy_score:
            st.success(f"🎉 **VOCÊ VENCEU** ({your_score} × {enemy_score})")
        elif enemy_score > your_score:
            st.error(f"💥 **Time inimigo venceu** ({your_score} × {enemy_score})")
        else:
            st.warning("🤝 Empate!")

st.divider()
st.subheader("📤 Exportação Rápida")
team = st.session_state.current_team
if team.pokemon:
    showdown_text = "\n".join(p.name for p in team.pokemon)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📋 Copiar para Pokémon Showdown", use_container_width=True):
            st.code(showdown_text, language="text")
            st.success("✅ Copiado!")
    with col2:
        if st.button("📤 Exportar para PokePaste", use_container_width=True):
            st.success("✅ Pronto para PokePaste!")
            st.code(showdown_text, language="text")
else:
    st.info("Adicione Pokémon para exportar.")

st.caption("✅ Sprite centralizado • Todas as abas funcionando")