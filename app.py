import sys
sys.path.insert(0, ".")

import streamlit as st
import pandas as pd
import random
import requests
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

if "full_pokedex" not in st.session_state:
    try:
        df = pd.read_csv("data/pokemon_complete_2025.csv")
        st.session_state.full_pokedex = []

        for _, row in df.iterrows():
            types = []
            for col in ["type1", "Type 1", "type_1", "Type1"]:
                if col in row and pd.notna(row[col]):
                    t = str(row[col]).title().strip()
                    if t and t != "Nan":
                        types.append(Type(t))
                        break
            for col in ["type2", "Type 2", "type_2", "Type2"]:
                if col in row and pd.notna(row[col]):
                    t = str(row[col]).title().strip()
                    if t and t != "Nan" and t not in [tp.value for tp in types]:
                        types.append(Type(t))
                        break

            sprite = None
            for col in ["sprite", "Sprite", "image", "front_default", "img", "image_url", "sprite_url"]:
                if col in row and pd.notna(row[col]) and str(row[col]).strip() != "":
                    sprite = str(row[col]).strip()
                    break

            abilities = []
            for col in ["ability1", "ability2", "ability3", "abilities", "Ability"]:
                if col in row and pd.notna(row[col]):
                    abilities.extend([a.strip().title() for a in str(row[col]).split(",") if a.strip()])

            pkm = Pokemon(
                id=int(row.get("id", 0)),
                name=str(row["name"]).replace("-", " ").title(),
                types=types,
                abilities=list(dict.fromkeys(abilities)),
                base_stats={},
                sprite=sprite
            )

            generation = None
            for col_name in ["generation", "Generation", "gen", "Gen", "generation_number"]:
                if col_name in row and pd.notna(row[col_name]):
                    try:
                        generation = int(row[col_name])
                        break
                    except:
                        pass
            if generation is None:
                generation = get_generation_by_id(pkm.id)

            pkm.generation = generation
            st.session_state.full_pokedex.append(pkm)

        st.success(f"✅ {len(st.session_state.full_pokedex)} Pokémon carregados! (Gerações lidas diretamente do CSV)")
    except Exception as e:
        st.error(f"Erro ao carregar dataset: {e}")
        st.session_state.full_pokedex = []

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
                        r = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon_name.replace(' ', '-')}", timeout=10)
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
                            st.session_state.pokemon_cache[pokemon_name] = pkm
                        else:
                            st.error("❌ Pokémon não encontrado.")
                            st.stop()
                    if st.session_state.current_team.add_pokemon(pkm):
                        st.success(f"✅ {pkm.name} adicionado!")
                        st.rerun()
                    else:
                        st.error("❌ Time completo!")
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
                        st.caption(f"Tipos: {', '.join(t.value for t in pkm.types) if pkm.types else '—'}")
                    with cols[2]:
                        if st.button("🗑️", key=f"remove_{i}"):
                            team.remove_pokemon(i)
                            st.rerun()
        else:
            st.info("Time vazio.")

with tab2:
    st.header("🔬 Análise Avançada do Time")
    team = st.session_state.current_team
    if not team.pokemon:
        st.warning("Adicione Pokémon ao time para ver a análise completa.")
    else:
        all_types = set(t for p in team.pokemon for t in p.types)
        st.write("**Tipos no time:**", ", ".join(t.value for t in all_types))

        st.subheader("Fraquezas do time (defensivo)")

        type_chart = {
            "Fire": {"Water": 2, "Ground": 2, "Rock": 2, "Fire": 0.5, "Grass": 0.5, "Ice": 0.5, "Bug": 0.5, "Steel": 0.5},
            "Water": {"Electric": 2, "Grass": 2, "Water": 0.5, "Fire": 0.5, "Ice": 0.5, "Steel": 0.5},
            "Grass": {"Fire": 2, "Ice": 2, "Poison": 2, "Flying": 2, "Bug": 2, "Grass": 0.5, "Water": 0.5, "Ground": 0.5, "Electric": 0.5},
            "Electric": {"Ground": 2, "Electric": 0.5, "Flying": 0.5, "Steel": 0.5},
            "Ice": {"Fire": 2, "Fighting": 2, "Rock": 2, "Steel": 2, "Ice": 0.5},
            "Fighting": {"Flying": 2, "Psychic": 2, "Fairy": 2, "Bug": 0.5, "Rock": 0.5, "Dark": 0.5},
            "Poison": {"Ground": 2, "Psychic": 2, "Grass": 0.5, "Fighting": 0.5, "Poison": 0.5, "Bug": 0.5, "Fairy": 0.5},
            "Ground": {"Water": 2, "Grass": 2, "Ice": 2, "Electric": 0, "Poison": 0.5, "Rock": 0.5},
            "Flying": {"Electric": 2, "Ice": 2, "Rock": 2, "Grass": 0.5, "Fighting": 0.5, "Bug": 0.5},
            "Psychic": {"Bug": 2, "Ghost": 2, "Dark": 2, "Fighting": 0.5, "Psychic": 0.5},
            "Bug": {"Fire": 2, "Flying": 2, "Rock": 2, "Grass": 0.5, "Fighting": 0.5, "Ground": 0.5},
            "Rock": {"Water": 2, "Grass": 2, "Fighting": 2, "Ground": 2, "Steel": 2, "Fire": 0.5, "Flying": 0.5, "Normal": 0.5, "Poison": 0.5},
            "Ghost": {"Ghost": 2, "Dark": 2, "Psychic": 0, "Normal": 0, "Poison": 0.5, "Bug": 0.5},
            "Dragon": {"Ice": 2, "Dragon": 2, "Fairy": 2, "Fire": 0.5, "Water": 0.5, "Grass": 0.5, "Electric": 0.5},
            "Dark": {"Fighting": 2, "Bug": 2, "Fairy": 2, "Ghost": 0.5, "Dark": 0.5, "Psychic": 0},
            "Steel": {"Fire": 2, "Fighting": 2, "Ground": 2, "Normal": 0.5, "Grass": 0.5, "Ice": 0.5, "Flying": 0.5, "Psychic": 0.5, "Bug": 0.5, "Rock": 0.5, "Dragon": 0.5, "Steel": 0.5, "Fairy": 0.5},
            "Fairy": {"Poison": 2, "Steel": 2, "Dragon": 2, "Fighting": 0.5, "Bug": 0.5, "Dark": 0.5},
            "Normal": {"Fighting": 2, "Ghost": 0}
        }

        weaknesses = []
        resistances = []
        immunities = []

        for attack_type in Type:
            multiplier = 1.0
            for pkm in team.pokemon:
                for def_type in pkm.types:
                    mult = type_chart.get(attack_type.value, {}).get(def_type.value, 1.0)
                    multiplier = max(multiplier, mult)
            if multiplier >= 2:
                weaknesses.append(f"{attack_type.value} (x{multiplier})")
            elif multiplier == 0:
                immunities.append(f"{attack_type.value}")
            elif multiplier <= 0.5:
                resistances.append(f"{attack_type.value} (x{multiplier})")

        col_w, col_r, col_i = st.columns(3)
        with col_w:
            st.error("**Fraquezas**")
            st.write("\n".join(weaknesses[:8]) if weaknesses else "Nenhuma fraqueza grave")
        with col_r:
            st.success("**Resistências**")
            st.write("\n".join(resistances[:8]) if resistances else "Poucas resistências")
        with col_i:
            st.info("**Imunidades**")
            st.write("\n".join(immunities) if immunities else "Nenhuma imunidade")

        if len(weaknesses) >= 3:
            top_weak = weaknesses[0].split()[0]
            st.warning(f"⚠️ Seu time tem **várias fraquezas graves** (principalmente {top_weak}).\n**Solução recomendada:** Adicione Pokémon resistentes ou imunes a {top_weak}.")
        else:
            st.success("✅ Ótima cobertura defensiva!")

with tab3:
    st.header("🧠 Recomendações Inteligentes")
    st.caption("Baseado no meta Gen 9 VGC • Abril 2026")
    team = st.session_state.current_team

    if not team.pokemon:
        st.warning("Adicione Pokémon para ver recomendações.")
    else:
        st.subheader("🔥 Sugestões para cobrir fraquezas do time")

        weaknesses_list = []
        for attack_type in Type:
            multiplier = 1.0
            for pkm in team.pokemon:
                for def_type in pkm.types:
                    mult = type_chart.get(attack_type.value, {}).get(def_type.value, 1.0)
                    multiplier = max(multiplier, mult)
            if multiplier >= 2:
                weaknesses_list.append(attack_type.value)

        if weaknesses_list:
            st.info(f"Fraquezas principais detectadas: {', '.join(weaknesses_list[:4])}")

            recommended_counters = []
            for weak_type in weaknesses_list[:3]:
                for pkm in st.session_state.full_pokedex:
                    if len(recommended_counters) >= 6:
                        break
                    resists = any(t.value in type_chart.get(weak_type, {}) and type_chart[weak_type][t.value] <= 0.5 for t in pkm.types)
                    if resists and pkm not in recommended_counters:
                        recommended_counters.append(pkm)

            if recommended_counters:
                for pkm in recommended_counters[:4]:
                    with st.container(border=True):
                        col_img, col_info = st.columns([1, 4])
                        with col_img:
                            if pkm.sprite:
                                st.image(pkm.sprite, width=80)
                        with col_info:
                            st.markdown(f"**{pkm.name}** (Gen {pkm.generation})")
                            st.caption(f"Tipos: {', '.join(t.value for t in pkm.types)}")
                            st.write("✅ Excelente counter")
                            if st.button("➕ Adicionar ao time", key=f"counter_{pkm.name}"):
                                if st.session_state.current_team.add_pokemon(pkm):
                                    st.success(f"{pkm.name} adicionado!")
                                    st.rerun()
        else:
            st.success("Seu time já tem ótima cobertura de tipos!")

        st.subheader("📋 Recomendações por Pokémon do seu time")
        suggestions_db = {
            "Ponyta": {"ability": "Flame Body", "item": "Choice Scarf", "nature": "Timid", "evs": "252 SpA / 4 SpD / 252 Spe", "moves": ["Flamethrower", "Morning Sun", "Wild Charge", "Will-O-Wisp"]},
            "Rapidash": {"ability": "Flame Body", "item": "Heavy-Duty Boots", "nature": "Jolly", "evs": "252 Atk / 4 Def / 252 Spe", "moves": ["Flare Blitz", "High Horsepower", "Wild Charge", "Swords Dance"]},
            "Charizard": {"ability": "Blaze", "item": "Heavy-Duty Boots", "nature": "Modest", "evs": "252 SpA / 4 SpD / 252 Spe", "moves": ["Flamethrower", "Air Slash", "Solar Beam", "Roost"]},
            "Moltres": {"ability": "Pressure", "item": "Choice Specs", "nature": "Timid", "evs": "252 SpA / 4 SpD / 252 Spe", "moves": ["Flamethrower", "Hurricane", "U-turn", "Roost"]},
            "Lapras": {"ability": "Water Absorb", "item": "Assault Vest", "nature": "Calm", "evs": "252 HP / 4 Def / 252 SpD", "moves": ["Surf", "Ice Beam", "Freeze-Dry", "Thunderbolt"]},
        }

        for pkm in team.pokemon:
            with st.container(border=True):
                col_img, col_rec = st.columns([1, 4])
                with col_img:
                    if pkm.sprite:
                        st.image(pkm.sprite, width=110)
                with col_rec:
                    sug = suggestions_db.get(pkm.name, {
                        "ability": pkm.abilities[0] if pkm.abilities else "Hidden Ability",
                        "item": "Leftovers" if any(t.value in ["Water", "Grass"] for t in pkm.types) else "Life Orb",
                        "nature": "Adamant" if any(t.value in ["Fighting", "Ground"] for t in pkm.types) else "Modest",
                        "evs": "252 HP / 252 Atk / 4 Spe" if any(t.value in ["Fire", "Fighting"] for t in pkm.types) else "252 HP / 252 SpA / 4 Spe",
                        "moves": ["Signature Move 1", "Signature Move 2", "Coverage", "Utility"]
                    })
                    st.write(f"**Ability:** {sug['ability']}")
                    st.write(f"**Item:** {sug['item']}")
                    st.write(f"**Nature:** {sug['nature']}")
                    st.write(f"**EVs:** {sug['evs']}")
                    st.write(f"**Moveset:** {', '.join(sug['moves'])}")
                    if st.button("📋 Copiar moveset", key=f"copy_{pkm.name}"):
                        st.code(f"{pkm.name} @ {sug['item']}\nAbility: {sug['ability']}\nEVs: {sug['evs']}\n{sug['nature']} Nature\n- {sug['moves'][0]}\n- {sug['moves'][1]}\n- {sug['moves'][2]}\n- {sug['moves'][3]}", language="text")
                        st.success("Moveset copiado!")

with tab4:
    st.header("🤖 Gerar Time Completo com IA")
    st.caption("Filtro FORTE: usa exatamente a coluna 'generation' do CSV")

    user_prompt = st.text_area(
        "Descreva o estilo do time",
        placeholder="time defensivo gen 1",
        height=100
    )

    if st.button("🚀 Gerar Time com IA", type="primary", use_container_width=True):
        if not st.session_state.full_pokedex:
            st.error("Dataset não carregado!")
            st.stop()
        if not user_prompt.strip():
            st.error("Digite uma descrição!")
            st.stop()

        with st.spinner("🔍 IA analisando geração e tipo do CSV..."):
            prompt = user_prompt.lower()
            filtered = st.session_state.full_pokedex.copy()

            gen_filter = None
            if any(x in prompt for x in ["gen 1", "gen1", "kanto", "primeira", "1ª"]):
                gen_filter = 1
            elif any(x in prompt for x in ["gen 2", "gen2", "johto", "segunda", "2ª"]):
                gen_filter = 2
            elif any(x in prompt for x in ["gen 3", "gen3", "hoenn", "terceira", "3ª"]):
                gen_filter = 3
            elif any(x in prompt for x in ["gen 4", "gen4", "sinnoh", "quarta", "4ª"]):
                gen_filter = 4
            elif any(x in prompt for x in ["gen 5", "gen5", "unova", "quinta", "5ª"]):
                gen_filter = 5
            elif any(x in prompt for x in ["gen 6", "gen6", "kalos", "sexta", "6ª"]):
                gen_filter = 6
            elif any(x in prompt for x in ["gen 7", "gen7", "alola", "sétima", "7ª"]):
                gen_filter = 7
            elif any(x in prompt for x in ["gen 8", "gen8", "galar", "oitava", "8ª"]):
                gen_filter = 8
            elif any(x in prompt for x in ["gen 9", "gen9", "paldea", "nona", "9ª"]):
                gen_filter = 9

            if gen_filter:
                filtered = [p for p in filtered if p.generation == gen_filter]

            type_map = {
                "fogo": "Fire", "agua": "Water", "água": "Water", "grama": "Grass",
                "eletrico": "Electric", "elétrico": "Electric", "gelo": "Ice",
                "lutador": "Fighting", "luta": "Fighting", "veneno": "Poison",
                "terra": "Ground", "voador": "Flying", "psiquico": "Psychic",
                "psíquico": "Psychic", "inseto": "Bug", "rocha": "Rock",
                "fantasma": "Ghost", "dragão": "Dragon", "sombrio": "Dark",
                "fada": "Fairy", "aço": "Steel", "normal": "Normal"
            }
            single_type = None
            for pt, en in type_map.items():
                if pt in prompt:
                    single_type = en
                    break
            if single_type:
                filtered = [p for p in filtered if any(t.value == single_type for t in p.types)]

            if len(filtered) < 6:
                st.error(f"❌ Só encontrei {len(filtered)} Pokémon com esses filtros. Tente outro prompt.")
                st.stop()

            generated = random.sample(filtered, 6)
            st.session_state.last_generated_team = generated
            st.success(f"✅ Time gerado! (Geração {gen_filter} + filtros do CSV)")

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
                        if sprite_url:
                            st.image(sprite_url, width=90)
                        else:
                            st.write("🖼️")
                    with cols[1]:
                        st.markdown(f"**{pkm.name}**")
                        st.caption(f"Tipos: {', '.join(t.value for t in pkm.types) if pkm.types else '—'} | Gen {pkm.generation}")
                    with cols[2]:
                        if st.button("➕ Adicionar ao meu time", key=f"add_ia_{idx}_{pkm.name}"):
                            if st.session_state.current_team.add_pokemon(pkm):
                                st.success(f"✅ {pkm.name} adicionado ao time!")
                                st.rerun()

with tab5:
    st.header("🌟 Modo IA Híbrido + Simulador de Batalhas")
    st.info("🔧 Em breve: montar time com IA + simular batalhas contra o meta Gen 9.")
    st.caption("Funcionalidade em desenvolvimento - volta na próxima atualização!")
    st.write("Quando estiver pronto, você poderá:")
    st.write("• Gerar time com IA + escolher moves/ability/item")
    st.write("• Simular batalhas 6x6 contra times famosos")
    st.button("🚀 Testar simulador (em breve)", disabled=True)

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

st.caption("✅ IA agora usa a coluna 'generation' diretamente do CSV")