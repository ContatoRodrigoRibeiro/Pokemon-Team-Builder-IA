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
    """Detecta qualquer menção de geração no prompt."""
    if not prompt:
        return None
    prompt = prompt.lower().strip()

    padroes = [
        r'(?:gen|geração|geracao|generação|g)\s*(\d+)',
        r'g(\d+)',
        r'(\d+)[ªa]?\s*(?:gen|geração|geracao|generação)',
        r'(?:gen|geração|geracao|generação)\s*(\d+)[ªa]?',
    ]

    for padrao in padroes:
        match = re.search(padrao, prompt)
        if match:
            return int(match.group(1))
    return None


# Tradução de tipos PT → EN
pt_to_en = {
    "Planta": "Grass", "Fogo": "Fire", "Água": "Water", "Agua": "Water",
    "Elétrico": "Electric", "Eletrico": "Electric", "Gelo": "Ice",
    "Lutador": "Fighting", "Luta": "Fighting", "Veneno": "Poison",
    "Terra": "Ground", "Voador": "Flying", "Psíquico": "Psychic",
    "Psiquico": "Psychic", "Inseto": "Bug", "Rocha": "Rock",
    "Fantasma": "Ghost", "Dragão": "Dragon", "Dragao": "Dragon",
    "Sombrio": "Dark", "Fada": "Fairy", "Aço": "Steel", "Normal": "Normal"
}

if "full_pokedex" not in st.session_state:
    try:
        df = pd.read_csv("data/pokemon_cleaned_pt.csv")
        st.session_state.full_pokedex = []

        for _, row in df.iterrows():
            # === TIPOS ===
            types = []
            for col in ["type1", "tipo1", "Type 1", "Tipo 1"]:
                if col in row and pd.notna(row[col]):
                    tipo_pt = str(row[col]).strip().title()
                    tipo_en = pt_to_en.get(tipo_pt, tipo_pt)
                    types.append(Type(tipo_en))
                    break
            for col in ["type2", "tipo2", "Type 2", "Tipo 2"]:
                if col in row and pd.notna(row[col]):
                    tipo_pt = str(row[col]).strip().title()
                    tipo_en = pt_to_en.get(tipo_pt, tipo_pt)
                    if tipo_en not in [t.value for t in types]:
                        types.append(Type(tipo_en))
                    break

            sprite = str(row.get("sprite", row.get("image", ""))).strip() or None

            abilities = []
            for col in ["ability1", "ability2", "ability3", "abilities"]:
                if col in row and pd.notna(row[col]):
                    abilities.extend([a.strip().title() for a in str(row[col]).split(",") if a.strip()])

            nome = str(row.get("name", row.get("nome", row.get("pokemon", "")))).strip()

            pkm = Pokemon(
                id=int(row.get("id", row.get("ID", row.get("#", 0)))),
                name=nome.replace("-", " ").title(),
                types=types,
                abilities=list(dict.fromkeys(abilities)),
                base_stats={},
                sprite=sprite
            )

            # ===================== MELHORIA FORTE NA CARGA DE GERAÇÃO =====================
            gen = None
            gen_columns = ["Generation", "generation", "Gen", "gen",
                           "Geração", "geração", "Geracao", "geracao", "Generacao"]

            for col in gen_columns:
                if col in row and pd.notna(row[col]):
                    try:
                        gen = int(row[col])
                        break
                    except (ValueError, TypeError):
                        pass

            # Fallback por ID (muito mais confiável quando a coluna falha)
            if gen is None or gen == 0:
                gen = get_generation_by_id(pkm.id)

            pkm.generation = gen
            # ================================================================================

            st.session_state.full_pokedex.append(pkm)

        # === DEBUG DE GERAÇÕES (aparece só uma vez) ===
        gen_count = Counter(p.generation for p in st.session_state.full_pokedex)
        st.success(f"✅ {len(st.session_state.full_pokedex)} Pokémon carregados!")
        st.info(f"📊 Gerações carregadas: {dict(sorted(gen_count.items()))}")

    except Exception as e:
        st.error(f"Erro ao carregar pokemon_cleaned_pt.csv: {e}")
        st.session_state.full_pokedex = []

# ====================== TABS ======================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🛠️ Modo Manual",
    "🔬 Análise Avançada",
    "🧠 Recomendações Inteligentes",
    "🤖 Gerar com IA",
    "🌟 Modo IA Híbrido + Simulador"
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
            for i, pkm in enumerate(team.pokemon):
                with st.container(border=True):
                    cols = st.columns([1, 4, 1])
                    with cols[0]:
                        if pkm.sprite: st.image(pkm.sprite, width=90)
                    with cols[1]:
                        st.markdown(f"**{pkm.name}**")
                        tipos = ', '.join(t.value for t in pkm.types) if pkm.types else '—'
                        gen = getattr(pkm, 'generation', '?')
                        st.caption(f"Tipos: {tipos} | Gen {gen}")
                    with cols[2]:
                        if st.button("🗑️", key=f"remove_{i}"):
                            team.remove_pokemon(i)
                            st.rerun()
        else:
            st.info("Time vazio. Adicione Pokémon acima.")

with tab4:
    st.header("🤖 Gerar Time Completo com IA")
    st.caption("Usando pokemon_cleaned_pt.csv + Detecção inteligente de geração (Gen 1 a Gen 9)")

    user_prompt = st.text_area(
        "Descreva o time",
        placeholder="time de água gen 9",
        height=100
    )

    if st.button("🚀 Gerar Time com IA", type="primary", use_container_width=True):
        if not st.session_state.full_pokedex:
            st.error("Dataset não carregado!")
            st.stop()
        if not user_prompt.strip():
            st.error("Digite uma descrição!")
            st.stop()

        with st.spinner("🔍 IA analisando..."):
            filtered = st.session_state.full_pokedex.copy()

            # ===================== FILTRAGEM POR GERAÇÃO =====================
            gen_filter = extrair_geracao_do_prompt(user_prompt)

            if gen_filter:
                original_len = len(filtered)
                filtered = [p for p in filtered if getattr(p, 'generation', 0) == gen_filter]

                if len(filtered) == 0:
                    # FALLBACK POR ID (caso a coluna de geração esteja com problema)
                    filtered = [p for p in st.session_state.full_pokedex
                                if get_generation_by_id(p.id) == gen_filter]
                    st.warning(f"⚠️ Usando fallback por ID para Gen {gen_filter}")
                else:
                    st.success(f"✅ Filtrado para **Gen {gen_filter}** ({len(filtered)} Pokémon)")
            else:
                st.info("🔄 Nenhuma geração específica detectada → usando todos os Pokémon")
            # ============================================================

            # Filtro por tipo (mantido igual)
            type_map = {
                "fogo": "Fire", "água": "Water", "grama": "Grass", "eletrico": "Electric",
                "gelo": "Ice", "lutador": "Fighting", "veneno": "Poison", "terra": "Ground",
                "voador": "Flying", "psiquico": "Psychic", "inseto": "Bug", "rocha": "Rock",
                "fantasma": "Ghost", "dragão": "Dragon", "sombrio": "Dark", "fada": "Fairy",
                "aço": "Steel", "normal": "Normal"
            }
            prompt_lower = user_prompt.lower()
            single_type = None
            for pt, en in type_map.items():
                if pt in prompt_lower:
                    single_type = en
                    break
            if single_type:
                filtered = [p for p in filtered if any(t.value == single_type for t in p.types)]

            if len(filtered) < 6:
                st.error(f"❌ Só encontrei {len(filtered)} Pokémon com esses filtros.")
                gen_count = Counter(p.generation for p in st.session_state.full_pokedex)
                st.info(f"ℹ️ Gerações no dataset: {dict(sorted(gen_count.items()))}")
                st.stop()

            generated = random.sample(filtered, 6)
            st.session_state.last_generated_team = generated
            st.success(f"✅ Time gerado com sucesso! (Gen {gen_filter or 'qualquer'})")

            st.subheader("Seu time gerado pela IA")
            for idx, pkm in enumerate(generated):
                sprite_url = pkm.sprite
                if not sprite_url or "http" not in str(sprite_url):
                    try:
                        name_lower = pkm.name.lower().replace(" ", "-")
                        r = requests.get(f"https://pokeapi.co/api/v2/pokemon/{name_lower}", timeout=8)
                        if r.status_code == 200:
                            sprite_url = r.json()["sprites"]["front_default"]
                    except:
                        sprite_url = None

                with st.container(border=True):
                    cols = st.columns([1, 4, 2])
                    with cols[0]:
                        if sprite_url: st.image(sprite_url, width=90)
                    with cols[1]:
                        st.markdown(f"**{pkm.name}**")
                        tipos = ', '.join(t.value for t in pkm.types) if pkm.types else '—'
                        gen = getattr(pkm, 'generation', '?')
                        st.caption(f"Tipos: {tipos} | Gen {gen}")
                    with cols[2]:
                        if st.button("➕ Adicionar ao meu time", key=f"add_ia_{idx}_{pkm.name}"):
                            if st.session_state.current_team.add_pokemon(pkm):
                                st.success(f"✅ {pkm.name} adicionado!")
                                st.rerun()

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

st.caption("✅ Versão corrigida - Coluna Generation detectada + fallback por ID + debug completo")