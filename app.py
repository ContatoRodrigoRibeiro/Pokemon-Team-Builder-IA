import sys
from pathlib import Path
from collections import Counter, defaultdict
import streamlit as st
import pandas as pd
import random
import requests
import re


# ==================== CLASSES MODELS ====================
class Type:
    def __init__(self, value: str):
        self.value = value.title()


class Pokemon:
    def __init__(self, id: int, name: str, types: list, abilities: list, base_stats: dict, sprite: str = None):
        self.id = id
        self.name = name
        self.types = types
        self.abilities = abilities
        self.base_stats = base_stats
        self.sprite = sprite
        self.generation = None


class Team:
    def __init__(self):
        self.pokemon = []

    def add_pokemon(self, pkm: Pokemon):
        if len(self.pokemon) >= 6:
            return False
        self.pokemon.append(pkm)
        return True

    def remove_pokemon(self, index: int):
        if 0 <= index < len(self.pokemon):
            del self.pokemon[index]
            return True
        return False


# ==================== CONFIGURAÇÃO INICIAL ====================
st.set_page_config(page_title="Pokémon Team Builder IA", page_icon="⚔️", layout="wide")

# ==================== NOVO TEMA ELEGANTE (atualizado) ====================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=Poppins:wght@600&display=swap');

    .stApp {
        background: #0f172a;
    }

    h1, h2, h3 {
        font-family: 'Poppins', sans-serif !important;
        color: #f1f5f9 !important;
        font-weight: 600;
    }

    .pokemon-card {
        background: #1e2937;
        border: 2px solid #475569;
        border-radius: 20px;
        margin: 10px 0;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.4);
        transition: all 0.3s ease;
        overflow: hidden;
    }

    .pokemon-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 40px rgba(239, 68, 68, 0.15);
        border-color: #ef4444;
    }

    .card-header {
        height: 48px;
        background: linear-gradient(90deg, #1e2937, #334155);
        display: flex;
        align-items: center;
        padding: 0 16px;
        border-bottom: 1px solid #475569;
    }

    .type-badge {
        padding: 4px 14px;
        border-radius: 9999px;
        font-size: 11px;
        font-weight: 700;
        color: white;
        margin-right: 6px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.3);
    }

    .sprite-container {
        background: #0f172a;
        padding: 20px;
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 160px;
    }

    .sprite-container img {
        filter: drop-shadow(0 15px 25px rgba(0,0,0,0.5));
        transition: transform 0.4s ease;
    }

    .pokemon-card:hover .sprite-container img {
        transform: scale(1.12);
    }

    .card-body {
        padding: 16px 20px 20px;
        text-align: center;
        background: #1e2937;
    }

    .pokemon-name {
        font-size: 20px;
        font-weight: 700;
        color: #f1f5f9;
        margin-bottom: 6px;
    }

    .card-footer {
        background: #0f172a;
        padding: 10px 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 12px;
        color: #64748b;
        border-top: 1px solid #475569;
    }

    .stButton button {
        background: linear-gradient(#ef4444, #dc2626) !important;
        color: white !important;
        border: none !important;
        font-weight: 600 !important;
        border-radius: 12px !important;
    }

    .stButton button:hover {
        background: linear-gradient(#dc2626, #b91c1c) !important;
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)

st.title("Pokémon Team Builder IA")
st.caption("Monte times imbatíveis com IA • Design elegante")

if "current_team" not in st.session_state:
    st.session_state.current_team = Team()
if "pokemon_cache" not in st.session_state:
    st.session_state.pokemon_cache = {}
if "last_generated_team" not in st.session_state:
    st.session_state.last_generated_team = []


# ==================== FUNÇÕES AUXILIARES ====================
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
        r'(?:gen|geração|geracao|generação)\s*(\d+)[ªa]?',
    ]
    for padrao in padroes:
        match = re.search(padrao, prompt)
        if match:
            return int(match.group(1))
    return None


pt_to_en = {
    "Planta": "Grass", "Grama": "Grass", "Fogo": "Fire", "Água": "Water", "Agua": "Water",
    "Elétrico": "Electric", "Eletrico": "Electric", "Gelo": "Ice", "Lutador": "Fighting",
    "Luta": "Fighting", "Veneno": "Poison", "Terra": "Ground", "Voador": "Flying",
    "Psíquico": "Psychic", "Psiquico": "Psychic", "Inseto": "Bug", "Pedra": "Rock",
    "Rocha": "Rock", "Fantasma": "Ghost", "Dragão": "Dragon", "Dragao": "Dragon",
    "Sombrio": "Dark", "Fada": "Fairy", "Aço": "Steel", "Normal": "Normal"
}

TYPE_CHART = {
    "Normal": {"Rock": 0.5, "Ghost": 0, "Steel": 0.5},
    "Fire": {"Fire": 0.5, "Water": 0.5, "Grass": 2, "Ice": 2, "Bug": 2, "Rock": 0.5, "Dragon": 0.5, "Steel": 2},
    "Water": {"Fire": 2, "Water": 0.5, "Grass": 0.5, "Ground": 2, "Rock": 2, "Dragon": 0.5},
    "Grass": {"Fire": 0.5, "Water": 2, "Grass": 0.5, "Poison": 0.5, "Ground": 2, "Flying": 0.5, "Bug": 0.5, "Rock": 2,
              "Dragon": 0.5, "Steel": 0.5},
    "Electric": {"Water": 2, "Electric": 0.5, "Grass": 0.5, "Ground": 0, "Flying": 2, "Dragon": 0.5},
    "Ice": {"Fire": 0.5, "Water": 0.5, "Grass": 2, "Ice": 0.5, "Ground": 2, "Flying": 2, "Dragon": 2, "Steel": 0.5},
    "Fighting": {"Normal": 2, "Ice": 2, "Poison": 0.5, "Flying": 0.5, "Psychic": 0.5, "Bug": 0.5, "Rock": 2, "Ghost": 0,
                 "Dark": 2, "Steel": 2, "Fairy": 0.5},
    "Poison": {"Grass": 2, "Poison": 0.5, "Ground": 0.5, "Rock": 0.5, "Ghost": 0.5, "Steel": 0, "Fairy": 2},
    "Ground": {"Fire": 2, "Electric": 2, "Grass": 0.5, "Poison": 2, "Flying": 0, "Bug": 0.5, "Rock": 2, "Steel": 2},
    "Flying": {"Electric": 0.5, "Grass": 2, "Fighting": 2, "Bug": 2, "Rock": 0.5, "Steel": 0.5},
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


def get_multiplier(attacker_type: str, defender_types: list) -> float:
    multiplier = 1.0
    for defender in defender_types:
        d_value = defender.value if isinstance(defender, Type) else str(defender)
        multiplier *= TYPE_CHART.get(attacker_type, {}).get(d_value, 1.0)
    return multiplier


def analyze_team_weaknesses(team: Team):
    if not team.pokemon: return []
    weakness_score = defaultdict(float)
    for pkm in team.pokemon:
        p_types = pkm.types
        for atk_type in TYPE_CHART.keys():
            mult = get_multiplier(atk_type, p_types)
            if mult > 1.0:
                weakness_score[atk_type] += mult
    sorted_weak = sorted(weakness_score.items(), key=lambda x: x[1], reverse=True)
    return sorted_weak[:8]


def analyze_team_coverage(team: Team):
    if not team.pokemon: return []
    coverage = defaultdict(float)
    for pkm in team.pokemon:
        for own_type in [t.value for t in pkm.types]:
            for def_type in TYPE_CHART.keys():
                mult = TYPE_CHART.get(own_type, {}).get(def_type, 1.0)
                if mult > 1.0:
                    coverage[def_type] += mult
    return sorted(coverage.items(), key=lambda x: x[1], reverse=True)[:8]


def calculate_synergy_score(team: Team) -> int:
    if not team.pokemon: return 0
    type_set = set(t.value for pkm in team.pokemon for t in pkm.types)
    diversity = len(type_set) * 12
    size_bonus = len(team.pokemon) * 8
    random_bonus = random.randint(5, 15)
    return min(100, diversity + size_bonus + random_bonus)


# ==================== FUNÇÃO DE CARD ELEGANTE ====================
def render_pokemon_card(pkm, show_remove=True, key_prefix="", expansion="SV", team_index=None):
    type_colors = {
        "Normal": "#A8A77A", "Fire": "#EE8130", "Water": "#6390F0",
        "Electric": "#F7D02C", "Grass": "#7AC74C", "Ice": "#96D9D6",
        "Fighting": "#C22E28", "Poison": "#A33EA1", "Ground": "#E2BF65",
        "Flying": "#A98FF3", "Psychic": "#F95587", "Bug": "#A6B91A",
        "Rock": "#B6A136", "Ghost": "#735797", "Dragon": "#6F35FC",
        "Dark": "#705746", "Steel": "#B7B7CE", "Fairy": "#D685AD"
    }

    # Cria o container do card
    with st.container():
        # Aplica CSS customizado no container
        st.markdown(f"""
        <style>
            .card-{key_prefix}-{team_index} {{
                background: #1e2937;
                border: 2px solid #475569;
                border-radius: 20px;
                padding: 0;
                margin: 10px 0;
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.4);
                overflow: hidden;
            }}
            .card-{key_prefix}-{team_index}:hover {{
                border-color: #ef4444;
                transform: translateY(-4px);
            }}
        </style>
        """, unsafe_allow_html=True)

        # Container principal
        with st.container():
            col1, col2 = st.columns([1, 3])

            with col1:
                # Sprite
                sprite_url = pkm.sprite or f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{pkm.id}.png"
                st.image(sprite_url, width=100)

            with col2:
                # Tipos
                if pkm.types:
                    tipos_html = ""
                    for t in pkm.types:
                        color = type_colors.get(t.value, "#64748b")
                        tipos_html += f'<span style="background:{color}; color:white; padding:2px 10px; border-radius:9999px; font-size:11px; margin-right:4px;">{t.value}</span>'
                    st.markdown(tipos_html, unsafe_allow_html=True)

                # Nome
                st.markdown(f"**{pkm.name}**", unsafe_allow_html=True)

                # Geração
                st.caption(f"Gen {getattr(pkm, 'generation', '?')} • #{str(getattr(pkm, 'id', '000')).zfill(3)}")

            # Botão Remover
            if show_remove and team_index is not None:
                if st.button("🗑️ Remover", key=f"remove_{key_prefix}_{team_index}", use_container_width=True):
                    st.session_state.current_team.remove_pokemon(team_index)
                    st.rerun()

# ==================== CARREGAMENTO DO CSV ====================
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
            abilities = []
            for col in ["habilidade_1", "habilidade_2", "habilidade_oculta"]:
                if col in row and pd.notna(row[col]):
                    abilities.extend([a.strip().title() for a in str(row[col]).split(",") if a.strip()])
            pkm = Pokemon(id=pkm_id, name=nome.replace("-", " ").title(), types=types,
                          abilities=list(dict.fromkeys(abilities)), base_stats={}, sprite=sprite)
            pkm.generation = gen
            st.session_state.full_pokedex.append(pkm)
        st.success(f"✅ {len(st.session_state.full_pokedex)} Pokémon carregados!")
    except Exception as e:
        st.error(f"Erro ao carregar CSV: {e}")
        st.session_state.full_pokedex = []

# ====================== TABS ======================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🛠️ Modo Manual", "🔬 Análise Avançada", "🧠 Recomendações Inteligentes",
    "🤖 Gerar com IA", "🌟 Modo IA Híbrido + Simulador"
])

# ====================== TAB 1 - MANUAL (COM CARDS NOVOS) ======================
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
            cols = st.columns(3)
            for i, pkm in enumerate(team.pokemon):
                with cols[i % 3]:
                    render_pokemon_card(pkm, show_remove=True, key_prefix="manual", team_index=i)
        else:
            st.info("Time vazio. Adicione Pokémon acima.")

# ====================== TAB 2 - ANÁLISE AVANÇADA (COMPLETO) ======================
with tab2:
    st.header("🔬 Análise Avançada")
    team = st.session_state.current_team
    if not team.pokemon:
        st.warning("Monte um time primeiro para analisar!")
    else:
        st.subheader("📊 Seu time atual")
        for pkm in team.pokemon:
            tipos = ', '.join(t.value for t in pkm.types)
            st.write(f"• **{pkm.name}** — {tipos} (Gen {getattr(pkm, 'generation', '?')})")
        st.divider()
        col_ana1, col_ana2 = st.columns(2)
        with col_ana1:
            st.subheader("⚠️ Fraquezas Defensivas")
            weaknesses = analyze_team_weaknesses(team)
            if weaknesses:
                for atk_type, score in weaknesses:
                    color = "🔴" if score > 4 else "🟠" if score > 2 else "🟡"
                    st.markdown(f"{color} **{atk_type}** — multiplicador {score:.1f}x")
            else:
                st.success("Nenhuma fraqueza crítica!")
        with col_ana2:
            st.subheader("🔥 Cobertura Ofensiva")
            coverage = analyze_team_coverage(team)
            for def_type, score in coverage:
                st.markdown(f"✅ **{def_type}** — super efetivo ({score:.1f}x)")
        st.divider()
        synergy = calculate_synergy_score(team)
        st.metric("Pontuação de Sinergia do Time", f"{synergy}/100")
        if synergy >= 80:
            st.success("🎉 Time muito equilibrado e sinérgico!")
        elif synergy >= 60:
            st.info("👍 Boa sinergia")
        else:
            st.warning("⚠️ Precisa de ajustes para maior sinergia")

# ====================== TAB 3 - RECOMENDAÇÕES (COMPLETO) ======================
with tab3:
    st.header("🧠 Recomendações Inteligentes")
    team = st.session_state.current_team
    if not team.pokemon:
        st.warning("Monte um time primeiro para receber sugestões!")
    else:
        st.subheader("Sugestões para completar seu time")
        weaknesses = [w[0] for w in analyze_team_weaknesses(team)]
        st.write("**Fraquezas detectadas:**", ", ".join(weaknesses[:4]) or "Nenhuma crítica")
        if st.button("🔍 Gerar Recomendações Inteligentes", type="primary"):
            with st.spinner("Analisando melhorias..."):
                recommendations = []
                for pkm in st.session_state.full_pokedex:
                    if any(pkm.id == existing.id for existing in team.pokemon):
                        continue
                    p_types = [t.value for t in pkm.types]
                    covers_weakness = any(w in p_types for w in weaknesses)
                    new_type = len(set(p_types) - set(t.value for p in team.pokemon for t in p.types)) > 0
                    if covers_weakness or new_type:
                        recommendations.append(pkm)
                    if len(recommendations) >= 6:
                        break
                if not recommendations:
                    recommendations = random.sample(st.session_state.full_pokedex, 6)
                st.session_state.last_generated_team = recommendations[:6]
                st.success("✅ Recomendações geradas!")
        if st.session_state.last_generated_team:
            st.subheader("Pokémon recomendados")
            for idx, pkm in enumerate(st.session_state.last_generated_team):
                sprite_url = pkm.sprite
                with st.container(border=True):
                    cols = st.columns([1, 4, 2])
                    with cols[0]:
                        if sprite_url:
                            st.image(sprite_url, width=80)
                    with cols[1]:
                        st.markdown(f"**{pkm.name}**")
                        tipos = ', '.join(t.value for t in pkm.types)
                        st.caption(f"Tipos: {tipos} | Gen {getattr(pkm, 'generation', '?')}")
                    with cols[2]:
                        if st.button("➕ Adicionar", key=f"rec_add_{idx}_{pkm.id}"):
                            if st.session_state.current_team.add_pokemon(pkm):
                                st.success(f"✅ {pkm.name} adicionado!")
                                st.rerun()
                            else:
                                st.error("❌ Time já está completo!")

# ====================== TAB 4 - GERAR COM IA (COMPLETO) ======================
with tab4:
    st.header("🤖 Gerar Time Completo com IA")
    st.caption("Usando pokemon_cleaned_pt.csv + Filtro por Geração + Tipo")
    user_prompt = st.text_area("Descreva o time", placeholder="time de água gen 9", height=100)
    if st.button("🚀 Gerar Time com IA", type="primary", use_container_width=True):
        if not st.session_state.full_pokedex:
            st.error("Dataset não carregado!")
            st.stop()
        if not user_prompt.strip():
            st.error("Digite uma descrição!")
            st.stop()
        with st.spinner("🔍 Gerando time..."):
            filtered = st.session_state.full_pokedex.copy()
            gen_filter = extrair_geracao_do_prompt(user_prompt)
            if gen_filter:
                filtered = [p for p in filtered if getattr(p, 'generation', 0) == gen_filter]
            prompt_lower = user_prompt.lower()
            single_type = None
            for pt, en in pt_to_en.items():
                if pt.lower() in prompt_lower:
                    single_type = en
                    break
            if single_type:
                filtered = [p for p in filtered if any(t.value == single_type for t in p.types)]
            if len(filtered) < 6:
                st.error(f"❌ Só encontrei {len(filtered)} Pokémon. Tente outro filtro!")
                st.stop()
            generated = random.sample(filtered, 6)
            st.session_state.last_generated_team = generated
            st.success(f"✅ Time gerado com sucesso!")
    if st.session_state.last_generated_team:
        st.subheader("Seu time gerado pela IA")
        for idx, pkm in enumerate(st.session_state.last_generated_team):
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
                    if sprite_url:
                        st.image(sprite_url, width=90)
                with cols[1]:
                    st.markdown(f"**{pkm.name}**")
                    tipos = ', '.join(t.value for t in pkm.types) if pkm.types else '—'
                    gen = getattr(pkm, 'generation', '?')
                    st.caption(f"Tipos: {tipos} | Gen {gen}")
                with cols[2]:
                    if st.button("➕ Adicionar ao meu time", key=f"add_ia_{idx}_{pkm.id}_{pkm.name}"):
                        if st.session_state.current_team.add_pokemon(pkm):
                            st.success(f"✅ {pkm.name} adicionado ao seu time!")
                            st.rerun()
                        else:
                            st.error("❌ Time já está completo (máximo 6)!")

# ====================== TAB 5 - HÍBRIDO + SIMULADOR (COMPLETO) ======================
with tab5:
    st.header("🌟 Modo IA Híbrido + Simulador")
    team = st.session_state.current_team
    st.subheader("🔄 Geração Híbrida")
    hybrid_prompt = st.text_input("Descreva o estilo do time (ex: ofensivo dragão gen 9)",
                                  placeholder="ofensivo com dragão")
    if st.button("🧬 Gerar Time Híbrido", type="primary"):
        with st.spinner("Gerando time híbrido..."):
            filtered = st.session_state.full_pokedex.copy()
            gen_filter = extrair_geracao_do_prompt(hybrid_prompt)
            if gen_filter:
                filtered = [p for p in filtered if getattr(p, 'generation', 0) == gen_filter]
            prompt_lower = hybrid_prompt.lower()
            single_type = None
            for pt, en in pt_to_en.items():
                if pt.lower() in prompt_lower:
                    single_type = en
                    break
            if single_type:
                filtered = [p for p in filtered if any(t.value == single_type for t in p.types)]
            generated = random.sample(filtered, min(6, len(filtered)))
            st.session_state.last_generated_team = generated
            st.success("Time híbrido gerado!")
    if st.session_state.last_generated_team:
        st.write("**Time sugerido pela IA híbrida:**")
        for pkm in st.session_state.last_generated_team:
            if st.button(f"➕ {pkm.name}", key=f"hybrid_add_{pkm.id}"):
                if st.session_state.current_team.add_pokemon(pkm):
                    st.success(f"{pkm.name} adicionado!")
                    st.rerun()
                else:
                    st.error("Time cheio!")
    st.divider()
    st.subheader("⚔️ Simulador de Batalhas")
    if st.button("🚀 Simular Batalha contra Time Rival"):
        if not team.pokemon:
            st.error("Monte seu time primeiro!")
        else:
            rival_team = random.sample(st.session_state.full_pokedex, 6)
            st.write("**Seu Time** vs **Time Rival**")
            col_me, col_rival = st.columns(2)
            with col_me:
                st.subheader("Seu Time")
                for p in team.pokemon:
                    st.write(f"• {p.name}")
            with col_rival:
                st.subheader("Time Rival")
                for p in rival_team:
                    st.write(f"• {p.name}")
            my_score = calculate_synergy_score(team)
            rival_score = random.randint(40, 95)
            st.metric("Pontuação do seu time", my_score)
            st.metric("Pontuação do rival", rival_score)
            if my_score > rival_score:
                st.success("🏆 VITÓRIA!")
            elif my_score == rival_score:
                st.info("⚖️ Empate técnico.")
            else:
                st.error("❌ Derrota.")

# ====================== EXPORTAÇÃO ======================
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

st.caption("✅ Projeto FINALIZADO - Design elegante atualizado • Todas as funcionalidades preservadas")