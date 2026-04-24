import sys  # Importa o módulo sys, que permite manipular o caminho de busca de módulos do Python
from pathlib import \
    Path  # Importa a classe Path do módulo pathlib, que ajuda a trabalhar com caminhos de arquivos de forma moderna e segura
from collections import Counter, \
    defaultdict  # Importa Counter (para contar ocorrências) e defaultdict (dicionário com valor padrão) da biblioteca collections
import \
    streamlit as st  # Importa a biblioteca Streamlit com o apelido "st" – ela é responsável por criar a interface web interativa
import \
    pandas as pd  # Importa a biblioteca pandas com o apelido "pd" – usada para ler e manipular o arquivo CSV com os dados dos Pokémon
import random  # Importa o módulo random, que permite gerar escolhas aleatórias (usado para gerar times)
import \
    requests  # Importa a biblioteca requests, que faz requisições HTTP para APIs (aqui é usada para buscar sprites na PokeAPI)
import \
    re  # Importa o módulo re (regular expressions), usado para extrair informações como geração do texto digitado pelo usuário


# ==================== CLASSES MODELS ====================
class Type:  # Define a classe Type, que representa um tipo de Pokémon (ex: Fire, Water, Grass)
    def __init__(self, value: str):  # Método construtor da classe Type – recebe um valor (string) e inicializa o objeto
        self.value = value.title()  # Converte o nome do tipo para Title Case (primeira letra maiúscula) e armazena no atributo "value"


class Pokemon:  # Define a classe Pokemon, que representa um Pokémon individual com todas as suas informações
    def __init__(self, id: int, name: str, types: list, abilities: list, base_stats: dict,
                 sprite: str = None):  # Método construtor da classe Pokemon
        self.id = id  # Armazena o ID numérico do Pokémon (ex: 25 para Pikachu)
        self.name = name  # Armazena o nome do Pokémon (ex: "Pikachu")
        self.types = types  # Armazena a lista de objetos Type (pode ter 1 ou 2 tipos)
        self.abilities = abilities  # Armazena a lista de habilidades do Pokémon
        self.base_stats = base_stats  # Armazena o dicionário com os stats base (HP, Attack, etc.)
        self.sprite = sprite  # Armazena a URL da imagem (sprite) do Pokémon
        self.generation = None  # Inicializa o atributo generation como None (será preenchido depois com a geração do Pokémon)


class Team:  # Define a classe Team, que representa o time do jogador (máximo 6 Pokémon)
    def __init__(self):  # Método construtor da classe Team
        self.pokemon = []  # Cria uma lista vazia para guardar os Pokémon que estão no time atual

    def add_pokemon(self, pkm: Pokemon):  # Método que adiciona um Pokémon ao time
        if len(self.pokemon) >= 6:  # Verifica se o time já tem 6 Pokémon (limite máximo)
            return False  # Se estiver cheio, retorna False (não adicionou)
        self.pokemon.append(pkm)  # Adiciona o Pokémon na lista
        return True  # Retorna True indicando que foi adicionado com sucesso

    def remove_pokemon(self, index: int):  # Método que remove um Pokémon do time pela posição
        if 0 <= index < len(self.pokemon):  # Verifica se o índice está dentro dos limites da lista
            del self.pokemon[index]  # Remove o Pokémon da posição indicada
            return True  # Retorna True se removeu com sucesso
        return False  # Retorna False se o índice era inválido


# ==================== CONFIGURAÇÃO INICIAL ====================
st.set_page_config(page_title="Pokémon Team Builder IA", page_icon="⚔️",
                   layout="wide",
                   initial_sidebar_state="expanded")  # Configura a página do Streamlit: título, ícone, layout largo e sidebar expandida

# ==================== CLEAN ELEGANT POKÉMON THEME ====================
st.markdown("""
<style>
    .main .block-container {
        padding-top: 0.5rem;
        max-width: 1200px;
        margin: auto;
    }
    
    h1, h2, h3, .stHeader {
        color: #f97316 !important;
        font-weight: 800;
        letter-spacing: -0.02em;
    }
    
    .stButton > button {
        background: linear-gradient(145deg, #f97316, #ea580c);
        color: white;
        border: none;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 1rem;
        padding: 12px 28px;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 10px 15px -3px rgb(249 115 22 / 0.3), 0 4px 6px -4px rgb(249 115 22 / 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 20px 25px -5px rgb(249 115 22 / 0.4), 0 8px 10px -6px rgb(249 115 22 / 0.4);
        background: linear-gradient(145deg, #fb923c, #f97316);
    }
    
    .stContainer {
        background: #1e2937 !important;
        border: 1px solid #475569 !important;
        border-radius: 16px !important;
        box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.3);
        transition: all 0.2s ease;
    }
    
    .stContainer:hover {
        box-shadow: 0 20px 25px -5px rgb(0 0 0 / 0.3);
        border-color: #f97316 !important;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        background: #1e2937;
        border-radius: 12px;
        padding: 4px;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #94a3b8 !important;
        font-weight: 600;
        border-radius: 8px;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: #f97316 !important;
        color: white !important;
        box-shadow: 0 4px 6px -1px rgb(249 115 22 / 0.3);
    }
    
    .type-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.8rem;
        color: white;
        text-shadow: 0 1px 2px rgba(0,0,0,0.5);
        margin: 2px 4px 2px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    .stMetric {
        background: #1e2937;
        border: 1px solid #475569;
        border-radius: 12px;
        padding: 16px;
    }
    
    .stSuccess, .stInfo, .stWarning, .stError {
        border-radius: 12px !important;
        border: 1px solid #475569 !important;
    }
    
    /* Cards do time - centralização perfeita + visual premium */
    .stContainer {
        background: #1e2937 !important;
        border: 2px solid #475569 !important;
        border-radius: 20px !important;
        padding: 18px 14px 14px 14px !important;
        text-align: center !important;
        box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.35);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: space-between !important;
        min-height: 320px;
    }
    
    .stContainer:hover {
        border-color: #f97316 !important;
        box-shadow: 0 25px 50px -12px rgb(249 115 22 / 0.25);
        transform: translateY(-6px);
    }
    
    .stContainer img {
        width: 110px !important;
        height: 110px !important;
        object-fit: contain;
        border-radius: 16px;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.5);
        margin-bottom: 8px;
    }
    
    .stContainer h4 {
        margin: 4px 0 6px 0 !important;
        font-size: 1.15rem !important;
        font-weight: 800 !important;
    }
</style>
""", unsafe_allow_html=True)

# HERO HEADER LIMPO E ELEGANTE
st.markdown("""
<div style="
    background: linear-gradient(135deg, #1e2937 0%, #334155 100%);
    padding: 32px 48px;
    border-radius: 24px;
    text-align: center;
    margin-bottom: 32px;
    border: 1px solid #475569;
    box-shadow: 0 25px 50px -12px rgb(0 0 0 / 0.4);
">
    <div style="display: flex; align-items: center; justify-content: center; gap: 16px; margin-bottom: 12px;">
        <span style="font-size: 48px;">⚔️</span>
        <h1 style="margin: 0; font-size: 2.8rem; color: #f97316; font-weight: 800;">Pokémon Team Builder IA</h1>
        <span style="font-size: 48px;">⚔️</span>
    </div>
    <p style="color: #94a3b8; font-size: 1.25rem; margin: 0; font-weight: 500;">Monte times imbatíveis com IA • Gerações 1 a 9</p>
    <div style="margin-top: 16px;">
        <span style="background: #f97316; color: white; padding: 6px 20px; border-radius: 9999px; font-size: 0.875rem; font-weight: 700;">✨ Feito com paixão Pokémon</span>
    </div>
</div>
""", unsafe_allow_html=True)

if "current_team" not in st.session_state:  # Verifica se a variável "current_team" ainda não existe no session_state
    st.session_state.current_team = Team()  # Cria um novo objeto Team e guarda no session_state (para manter o time entre recarregamentos)
if "pokemon_cache" not in st.session_state:  # Verifica se o cache de Pokémon ainda não existe
    st.session_state.pokemon_cache = {}  # Cria um dicionário vazio para cachear Pokémon buscados via PokeAPI
if "last_generated_team" not in st.session_state:  # Verifica se o time gerado pela IA ainda não existe
    st.session_state.last_generated_team = []  # Cria uma lista vazia para guardar o último time gerado pela IA


def get_generation_by_id(pkm_id):  # Define uma função que calcula a geração de um Pokémon pelo ID
    if pkm_id <= 151:
        return 1  # Geração 1 (Kanto) – primeiros 151 Pokémon
    elif pkm_id <= 251:
        return 2  # Geração 2 (Johto)
    elif pkm_id <= 386:
        return 3  # Geração 3 (Hoenn)
    elif pkm_id <= 493:
        return 4  # Geração 4 (Sinnoh)
    elif pkm_id <= 649:
        return 5  # Geração 5 (Unova)
    elif pkm_id <= 721:
        return 6  # Geração 6 (Kalos)
    elif pkm_id <= 809:
        return 7  # Geração 7 (Alola)
    elif pkm_id <= 905:
        return 8  # Geração 8 (Galar)
    else:
        return 9  # Qualquer ID maior é considerado Geração 9 (Paldea)


def extrair_geracao_do_prompt(
        prompt: str):  # Função que analisa o texto digitado pelo usuário e tenta extrair a geração (ex: "gen 9")
    if not prompt:  # Se o prompt estiver vazio
        return None  # Retorna None (não tem geração)
    prompt = prompt.lower().strip()  # Converte o texto para minúsculo e remove espaços das pontas
    padroes = [  # Lista de padrões de expressões regulares para identificar a geração
        r'(?:gen|geração|geracao|generação|g)\s*(\d+)',  # Ex: "gen 9", "geração 9", "g 9"
        r'g(\d+)',  # Ex: "g9"
        r'(\d+)[ªa]?\s*(?:gen|geração|geracao|generação)',  # Ex: "9 gen"
        r'(?:gen|geração|geracao|generação)\s*(\d+)[ªa]?',  # Ex: "gen 9ª"
    ]
    for padrao in padroes:  # Percorre cada padrão
        match = re.search(padrao, prompt)  # Tenta encontrar o padrão no texto
        if match:  # Se encontrou
            return int(match.group(1))  # Retorna o número da geração encontrado
    return None  # Se nenhum padrão bateu, retorna None


# ==================== MAPA DE TIPOS ====================
pt_to_en = {  # Dicionário que traduz nomes de tipos do português para o inglês (usado pela PokeAPI)
    "Planta": "Grass", "Grama": "Grass",
    "Fogo": "Fire",
    "Água": "Water", "Agua": "Water", "agua": "Water",
    "Elétrico": "Electric", "Eletrico": "Electric", "eletrico": "Electric",
    "Gelo": "Ice",
    "Lutador": "Fighting", "Luta": "Fighting",
    "Veneno": "Poison",
    "Terra": "Ground",
    "Voador": "Flying",
    "Psíquico": "Psychic", "Psiquico": "Psychic",
    "Inseto": "Bug",
    "Pedra": "Rock", "Rocha": "Rock", "pedra": "Rock", "rocha": "Rock",
    "Fantasma": "Ghost",
    "Dragão": "Dragon", "Dragao": "Dragon",
    "Sombrio": "Dark",
    "Fada": "Fairy",
    "Aço": "Steel",
    "Normal": "Normal"
}

# ==================== TABELA DE EFETIVIDADE DE TIPOS ====================
TYPE_CHART = {
    "Normal": {"Rock": 0.5, "Ghost": 0, "Steel": 0.5},
    "Fire": {"Fire": 0.5, "Water": 0.5, "Grass": 2, "Ice": 2, "Bug": 2, "Rock": 0.5, "Dragon": 0.5, "Steel": 2},
    "Water": {"Fire": 2, "Water": 0.5, "Grass": 0.5, "Ground": 2, "Rock": 2, "Dragon": 0.5},
    "Grass": {"Fire": 0.5, "Water": 2, "Grass": 0.5, "Poison": 0.5, "Ground": 2, "Flying": 0.5, "Bug": 0.5, "Rock": 2, "Dragon": 0.5, "Steel": 0.5},
    "Electric": {"Water": 2, "Electric": 0.5, "Grass": 0.5, "Ground": 0, "Flying": 2, "Dragon": 0.5},
    "Ice": {"Fire": 0.5, "Water": 0.5, "Grass": 2, "Ice": 0.5, "Ground": 2, "Flying": 2, "Dragon": 2, "Steel": 0.5},
    "Fighting": {"Normal": 2, "Ice": 2, "Poison": 0.5, "Flying": 0.5, "Psychic": 0.5, "Bug": 0.5, "Rock": 2, "Ghost": 0, "Dark": 2, "Steel": 2, "Fairy": 0.5},
    "Poison": {"Grass": 2, "Poison": 0.5, "Ground": 0.5, "Rock": 0.5, "Ghost": 0.5, "Steel": 0, "Fairy": 2},
    "Ground": {"Fire": 2, "Electric": 2, "Grass": 0.5, "Poison": 2, "Flying": 0, "Bug": 0.5, "Rock": 2, "Steel": 2},
    "Flying": {"Electric": 0.5, "Grass": 2, "Fighting": 2, "Bug": 2, "Rock": 0.5, "Steel": 0.5},
    "Psychic": {"Fighting": 2, "Poison": 2, "Psychic": 0.5, "Dark": 0, "Steel": 0.5},
    "Bug": {"Fire": 0.5, "Grass": 2, "Fighting": 0.5, "Poison": 0.5, "Flying": 0.5, "Psychic": 2, "Ghost": 0.5, "Dark": 2, "Steel": 0.5, "Fairy": 0.5},
    "Rock": {"Fire": 2, "Ice": 2, "Fighting": 0.5, "Ground": 0.5, "Flying": 2, "Bug": 2, "Steel": 0.5},
    "Ghost": {"Normal": 0, "Psychic": 2, "Ghost": 2, "Dark": 0.5},
    "Dragon": {"Dragon": 2, "Steel": 0.5, "Fairy": 0},
    "Dark": {"Fighting": 0.5, "Psychic": 2, "Ghost": 2, "Dark": 0.5, "Fairy": 0.5},
    "Steel": {"Fire": 0.5, "Water": 0.5, "Electric": 0.5, "Ice": 2, "Rock": 2, "Steel": 0.5, "Fairy": 2},
    "Fairy": {"Fire": 0.5, "Fighting": 2, "Poison": 0.5, "Dragon": 2, "Dark": 2, "Steel": 0.5}
}

# ==================== CORES OFICIAIS DOS TIPOS POKÉMON (UI) ====================
TYPE_COLORS = {
    "Normal": "#A8A878", "Fire": "#F08030", "Water": "#6890F0",
    "Grass": "#78C850", "Electric": "#F8D030", "Ice": "#98D8D8",
    "Fighting": "#C03028", "Poison": "#A040A0", "Ground": "#E0C068",
    "Flying": "#A890F0", "Psychic": "#F85888", "Bug": "#A8B820",
    "Rock": "#B8A038", "Ghost": "#705898", "Dragon": "#7038F8",
    "Dark": "#705848", "Steel": "#B8B8D0", "Fairy": "#EE99AC"
}

def get_type_badge(type_name: str) -> str:
    """Gera HTML elegante para badge de tipo Pokémon (somente UI, não altera lógica)"""
    color = TYPE_COLORS.get(type_name, "#A8A878")
    return f'<span class="type-badge" style="background-color: {color};">{type_name}</span>'

def get_multiplier(attacker_type: str,
                   defender_types: list) -> float:  # Função que calcula o multiplicador de dano de um tipo atacante contra os tipos do defensor
    multiplier = 1.0  # Começa com multiplicador neutro (1x)
    for defender in defender_types:  # Percorre cada tipo do Pokémon defensor
        d_value = defender.value if isinstance(defender, Type) else str(
            defender)  # Pega o nome do tipo (tratando se for objeto Type ou string)
        multiplier *= TYPE_CHART.get(attacker_type, {}).get(d_value,
                                                            1.0)  # Multiplica pelo valor da tabela (ou 1.0 se não existir)
    return multiplier  # Retorna o multiplicador final (ex: 4.0 = super efetivo em dual-type)


def analyze_team_weaknesses(team: Team):  # Função que analisa as fraquezas defensivas do time inteiro
    if not team.pokemon:  # Se o time estiver vazio
        return []  # Retorna lista vazia
    weakness_score = defaultdict(float)  # Cria um dicionário que começa com valor 0.0 para qualquer chave nova
    for pkm in team.pokemon:  # Para cada Pokémon no time
        p_types = pkm.types  # Pega os tipos dele
        for atk_type in TYPE_CHART.keys():  # Para cada tipo possível de ataque
            mult = get_multiplier(atk_type, p_types)  # Calcula o multiplicador
            if mult > 1.0:  # Se for super efetivo (maior que 1x)
                weakness_score[atk_type] += mult  # Soma o multiplicador na pontuação de fraqueza
    sorted_weak = sorted(weakness_score.items(), key=lambda x: x[1],
                         reverse=True)  # Ordena do mais fraco para o menos fraco
    return sorted_weak[:8]  # Retorna as 8 fraquezas mais graves


def analyze_team_coverage(team: Team):  # Função que analisa a cobertura ofensiva do time
    if not team.pokemon:  # Se o time estiver vazio
        return []  # Retorna lista vazia
    coverage = defaultdict(float)  # Dicionário para somar cobertura ofensiva
    for pkm in team.pokemon:  # Para cada Pokémon no time
        for own_type in [t.value for t in pkm.types]:  # Para cada tipo do Pokémon
            for def_type in TYPE_CHART.keys():  # Para cada tipo possível de defesa
                mult = TYPE_CHART.get(own_type, {}).get(def_type, 1.0)  # Pega o multiplicador de ataque
                if mult > 1.0:  # Se for super efetivo
                    coverage[def_type] += mult  # Soma na cobertura
    return sorted(coverage.items(), key=lambda x: x[1], reverse=True)[:8]  # Retorna os 8 tipos mais bem cobertos


def calculate_synergy_score(team: Team) -> int:  # Função que calcula uma pontuação de sinergia do time (0 a 100)
    if not team.pokemon:  # Se o time estiver vazio
        return 0  # Retorna 0
    type_set = set(
        t.value for pkm in team.pokemon for t in pkm.types)  # Cria um conjunto com todos os tipos únicos do time
    diversity = len(type_set) * 12  # Quanto mais tipos diferentes, maior a diversidade (máximo 18 tipos × 12)
    size_bonus = len(team.pokemon) * 8  # Bônus por ter mais Pokémon no time
    random_bonus = random.randint(5, 15)  # Pequeno bônus aleatório para dar variação
    return min(100, diversity + size_bonus + random_bonus)  # Retorna a pontuação, limitando em 100


# ==================== CARREGAMENTO DO CSV ====================
if "full_pokedex" not in st.session_state:  # Verifica se o pokedex completo ainda não foi carregado
    try:  # Tenta executar o bloco de carregamento
        df = pd.read_csv("data/pokemon_cleaned_pt.csv")  # Lê o arquivo CSV com todos os Pokémon em português
        st.session_state.full_pokedex = []  # Cria lista vazia para guardar os objetos Pokemon
        for _, row in df.iterrows():  # Percorre cada linha do DataFrame
            pkm_id = int(row.get("id_pokedex", row.get("id", 0)))  # Pega o ID do Pokémon (usa id_pokedex ou id)
            nome = str(row.get("nome", "")).strip()  # Pega o nome e remove espaços
            try:  # Tenta pegar a geração do CSV
                gen = int(row["geracao"])  # Se existir, usa o valor da coluna "geracao"
            except:  # Se der erro
                gen = get_generation_by_id(pkm_id)  # Calcula a geração pelo ID
            types = []  # Lista vazia para os tipos
            if pd.notna(row.get("tipo_1")):  # Se existe tipo 1
                tipo_pt = str(row["tipo_1"]).strip().title()  # Pega e formata o tipo em português
                tipo_en = pt_to_en.get(tipo_pt, tipo_pt)  # Traduz para inglês
                types.append(Type(tipo_en))  # Cria objeto Type e adiciona
            if pd.notna(row.get("tipo_2")):  # Se existe tipo 2
                tipo_pt = str(row["tipo_2"]).strip().title()  # Mesma coisa para o segundo tipo
                tipo_en = pt_to_en.get(tipo_pt, tipo_pt)
                if tipo_en not in [t.value for t in types]:  # Evita duplicar tipo
                    types.append(Type(tipo_en))
            sprite = str(row.get("url_sprite", "")).strip() or None  # Pega a URL da sprite ou None
            abilities = []  # Lista de habilidades
            for col in ["habilidade_1", "habilidade_2", "habilidade_oculta"]:  # Percorre as colunas de habilidades
                if col in row and pd.notna(row[col]):  # Se a coluna existe e não é nula
                    abilities.extend([a.strip().title() for a in str(row[col]).split(",") if
                                      a.strip()])  # Adiciona as habilidades separadas por vírgula
            pkm = Pokemon(  # Cria o objeto Pokemon
                id=pkm_id,
                name=nome.replace("-", " ").title(),
                types=types,
                abilities=list(dict.fromkeys(abilities)),  # Remove duplicatas mantendo ordem
                base_stats={},
                sprite=sprite
            )
            pkm.generation = gen  # Define a geração
            st.session_state.full_pokedex.append(pkm)  # Adiciona na pokedex completa
        gen_count = Counter(p.generation for p in st.session_state.full_pokedex)  # Conta quantos Pokémon por geração
        st.success(f"✅ {len(st.session_state.full_pokedex)} Pokémon carregados!")  # Mostra mensagem de sucesso
        st.info(f"📊 Gerações: {dict(sorted(gen_count.items()))}")  # Mostra quantos Pokémon por geração
    except Exception as e:  # Se der qualquer erro no carregamento
        st.error(f"Erro ao carregar CSV: {e}")  # Mostra erro na tela
        st.session_state.full_pokedex = []  # Deixa a pokedex vazia

# ====================== SIDEBAR ELEGANTE ======================
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:16px; background: linear-gradient(145deg, #1e2937, #334155); border-radius:16px; margin-bottom:20px; border:1px solid #475569;">
        <div style="font-size:32px; margin-bottom:8px;">⚔️</div>
        <h3 style="color:#f97316; margin:0; font-weight:800;">Professor Oak's Lab</h3>
        <p style="color:#64748b; font-size:0.75rem; margin:4px 0 0 0;">Dicas para treinadores</p>
    </div>
    """, unsafe_allow_html=True)
    
    tips = [
        "💧 Água é super efetivo contra Fogo, Terra e Pedra!",
        "⚡ Elétrico não afeta Ground — use Ground contra Electric!",
        "🌿 Grass cobre bem Water, Ground e Rock.",
        "Use tipos diversificados para máxima sinergia!",
        "🐉 Dragão é forte, mas Fairy é sua fraqueza principal.",
        "🛡️ Steel resiste a quase tudo — ótimo para tanques!",
        "🌟 Geração 9 (Paldea) tem Terastal incrível!"
    ]
    st.info(random.choice(tips))
    
    st.divider()
    st.markdown("**Atalhos Rápidos**")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Recarregar", use_container_width=True):
            st.rerun()
    with col2:
        if st.button("📖 Tipos", use_container_width=True):
            st.success("Análise já usa a tabela completa!")
    
    st.divider()
    st.caption("Feito com ❤️ por fãs de Pokémon • Streamlit + PokeAPI")
    st.caption("© Nintendo / Game Freak — Apenas para diversão!")

# ====================== TABS ======================
tab1, tab2, tab3, tab4, tab5 = st.tabs([  # Cria as 5 abas (tabs) da interface
    "🛠️ Modo Manual",
    "🔬 Análise Avançada",
    "🧠 Recomendações Inteligentes",
    "🤖 Gerar com IA",
    "🌟 Modo IA Híbrido + Simulador"
])

# ====================== TAB 1 - MANUAL ======================
with tab1:  # Tudo dentro deste bloco aparece na aba "Modo Manual"
    st.header("Monte seu Time Manualmente")  # Título da aba
    col_busca, col_time = st.columns([2, 3])  # Divide a tela em duas colunas (2/5 e 3/5)
    with col_busca:  # Dentro da coluna de busca
        st.subheader("🔍 Buscar Pokémon")  # Subtítulo
        pokemon_name = st.text_input("Nome do Pokémon (em inglês)",
                                     placeholder="pikachu").strip().lower()  # Campo de texto para digitar nome
        if st.button("➕ Buscar e Adicionar", type="primary", use_container_width=True):  # Botão de busca
            if pokemon_name:  # Se digitou algo
                try:  # Tenta buscar
                    if pokemon_name in st.session_state.pokemon_cache:  # Se já está no cache
                        pkm = st.session_state.pokemon_cache[pokemon_name]  # Usa o cache (mais rápido)
                    else:  # Se não está no cache
                        r = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon_name.replace(' ', '-')}",
                                         timeout=10)  # Faz requisição na PokeAPI
                        if r.status_code == 200:  # Se encontrou
                            data = r.json()  # Converte resposta para dicionário
                            pkm = Pokemon(  # Cria objeto Pokemon com dados da API
                                id=data["id"],
                                name=data["name"].replace("-", " ").title(),
                                types=[Type(t["type"]["name"].title()) for t in data["types"]],
                                abilities=[a["ability"]["name"].replace("-", " ").title() for a in data["abilities"]],
                                base_stats={stat["stat"]["name"]: stat["base_stat"] for stat in data["stats"]},
                                sprite=data["sprites"]["front_default"]
                            )
                            pkm.generation = get_generation_by_id(pkm.id)  # Define geração
                            st.session_state.pokemon_cache[pokemon_name] = pkm  # Salva no cache
                        else:  # Se não encontrou
                            st.error("❌ Pokémon não encontrado.")  # Mostra erro
                            st.stop()  # Para a execução
                    if st.session_state.current_team.add_pokemon(pkm):  # Tenta adicionar ao time
                        st.success(f"✅ {pkm.name} adicionado!")  # Sucesso
                        st.rerun()  # Recarrega a página
                    else:  # Se time cheio
                        st.error("❌ Time completo! (máximo 6)")  # Erro
                except Exception as e:  # Qualquer erro
                    st.error(f"Erro: {e}")  # Mostra erro
    with col_time:  # Coluna do time atual
        st.subheader("Seu Time Atual")  # Subtítulo
        
        team = st.session_state.current_team
        
        # Botão limpar time
        if team.pokemon:
            if st.button("🗑️ LIMPAR TIME COMPLETO", type="secondary", use_container_width=True, key="clear_team_btn"):
                st.session_state.current_team = Team()
                st.success("✅ Time limpo com sucesso!")
                st.rerun()
        
        if team.pokemon:
            # Grid de 3 colunas
            cols_grid = st.columns(3)
            
            for idx, pkm in enumerate(team.pokemon):
                col = cols_grid[idx % 3]
                
                with col:
                    first_type = pkm.types[0].value if pkm.types else "Normal"
                    type_color = TYPE_COLORS.get(first_type, "#64748b")
                    
                    # Card bonito usando container + CSS global
                    with st.container(border=True):
                        # Barra de cor no topo (usando markdown pequeno)
                        st.markdown(f"""
                        <div style="height: 8px; background: linear-gradient(90deg, {type_color}, #f97316); margin: -12px -12px 12px -12px; border-radius: 14px 14px 0 0;"></div>
                        """, unsafe_allow_html=True)
                        
                        # Sprite centralizado
                        if pkm.sprite:
                            st.image(pkm.sprite, width=100)
                        
                        # Nome
                        st.markdown(f"<h4 style='text-align:center; margin:8px 0 4px 0; color:white;'>{pkm.name}</h4>", unsafe_allow_html=True)
                        
                        # Tipos
                        tipos_html = ' '.join(get_type_badge(t.value) for t in pkm.types) if pkm.types else '—'
                        st.markdown(f"<div style='text-align:center; margin-bottom:6px;'>{tipos_html}</div>", unsafe_allow_html=True)
                        
                        # Geração + ID
                        st.markdown(f"<div style='text-align:center; color:#94a3b8; font-size:0.8rem; margin-bottom:8px;'>Gen {getattr(pkm, 'generation', '?')} • #{pkm.id:04d}</div>", unsafe_allow_html=True)
                        
                        # Stats (Attack / Defense / Speed) - mais bonito e útil
                        if hasattr(pkm, 'base_stats') and pkm.base_stats:
                            atk = pkm.base_stats.get('attack', 0)
                            defense = pkm.base_stats.get('defense', 0)
                            speed = pkm.base_stats.get('speed', 0)
                            st.markdown(f"""
                            <div style="display: flex; justify-content: center; gap: 12px; margin-bottom: 12px; font-size: 0.75rem;">
                                <div><span style="color:#f97316;">⚔️</span> {atk}</div>
                                <div><span style="color:#3b82f6;">🛡️</span> {defense}</div>
                                <div><span style="color:#22c55e;">⚡</span> {speed}</div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Botão Remover
                        if st.button("🗑️ Remover", key=f"remove_{idx}", use_container_width=True):
                            team.remove_pokemon(idx)
                            st.rerun()
        else:
            st.info("Seu time está vazio. Busque e adicione Pokémon acima!")

# ====================== TAB 2 - ANÁLISE AVANÇADA ======================
with tab2:  # Aba de análise
    st.header("🔬 Análise Avançada")  # Título
    team = st.session_state.current_team  # Pega o time
    if not team.pokemon:  # Se vazio
        st.warning("Monte um time primeiro para analisar!")  # Aviso
    else:  # Se tem time
        st.subheader("📊 Seu time atual")  # Subtítulo
        for pkm in team.pokemon:  # Mostra cada Pokémon
            tipos_html = ' '.join(get_type_badge(t.value) for t in pkm.types) if pkm.types else '—'
            gen = getattr(pkm, 'generation', '?')
            st.markdown(f"• **{pkm.name}** — {tipos_html} <span style='color:#FFDE00'>(Gen {gen})</span>", unsafe_allow_html=True)  # Tipos com badges Pokémon

        st.divider()  # Linha divisória
        col_ana1, col_ana2 = st.columns(2)  # Duas colunas

        with col_ana1:  # Coluna de fraquezas
            st.subheader("⚠️ Fraquezas Defensivas")  # Título
            weaknesses = analyze_team_weaknesses(team)  # Chama função de análise
            if weaknesses:  # Se tem fraquezas
                for atk_type, score in weaknesses:  # Para cada fraqueza
                    color = "🔴" if score > 4 else "🟠" if score > 2 else "🟡"  # Define cor conforme gravidade
                    st.markdown(f"{color} **{atk_type}** — multiplicador {score:.1f}x")  # Mostra
            else:  # Se nenhuma fraqueza
                st.success("Nenhuma fraqueza crítica!")  # Mensagem positiva

        with col_ana2:  # Coluna de cobertura
            st.subheader("🔥 Cobertura Ofensiva")  # Título
            coverage = analyze_team_coverage(team)  # Chama função
            for def_type, score in coverage:  # Para cada tipo coberto
                st.markdown(f"✅ **{def_type}** — super efetivo ({score:.1f}x)")  # Mostra

        st.divider()  # Outra linha divisória
        synergy = calculate_synergy_score(team)  # Calcula pontuação de sinergia
        col_syn, col_feed = st.columns([2, 3])
        with col_syn:
            st.markdown(f'<div class="metric-container"><h3 style="color:#FFDE00; margin:0;">SINERGIA</h3><p style="font-size:2.8em; font-weight:900; color:white; margin:5px 0;">{synergy}<span style="font-size:0.5em;">/100</span></p></div>', unsafe_allow_html=True)
            st.progress(synergy / 100)
        with col_feed:
            if synergy >= 80:
                st.success("🎉 **EXCELENTE!** Time lendário, pronto para a Elite Four!")
            elif synergy >= 60:
                st.info("👍 **BOA!** Sinergia sólida — adicione mais cobertura.")
            else:
                st.warning("⚠️ **ATENÇÃO!** Adicione tipos que cubram as fraquezas detectadas.")
            st.caption("Quanto mais tipos únicos e cobertura, maior a pontuação!")

# ====================== TAB 3 - RECOMENDAÇÕES INTELIGENTES ======================
with tab3:  # Aba de recomendações
    st.header("🧠 Recomendações Inteligentes")  # Título
    team = st.session_state.current_team  # Time atual
    if not team.pokemon:  # Se vazio
        st.warning("Monte um time primeiro para receber sugestões!")  # Aviso
    else:  # Se tem time
        st.subheader("Sugestões para completar seu time")  # Subtítulo
        weaknesses = [w[0] for w in analyze_team_weaknesses(team)]  # Lista só dos tipos fracos
        st.write("**Fraquezas detectadas:**", ", ".join(weaknesses[:4]) or "Nenhuma crítica")  # Mostra fraquezas

        if st.button("🔍 Gerar Recomendações Inteligentes", type="primary"):  # Botão para gerar sugestões
            with st.spinner("Analisando melhorias..."):  # Mostra loading
                recommendations = []  # Lista de recomendações
                for pkm in st.session_state.full_pokedex:  # Percorre toda a pokedex
                    if any(pkm.id == existing.id for existing in team.pokemon):  # Se já está no time, pula
                        continue
                    p_types = [t.value for t in pkm.types]  # Tipos do Pokémon
                    covers_weakness = any(w in p_types for w in weaknesses)  # Verifica se cobre fraqueza
                    new_type = len(set(p_types) - set(
                        t.value for p in team.pokemon for t in p.types)) > 0  # Verifica se traz tipo novo
                    if covers_weakness or new_type:  # Se atende algum critério
                        recommendations.append(pkm)  # Adiciona
                    if len(recommendations) >= 6:  # Limita em 6
                        break
                if not recommendations:  # Se não encontrou nenhuma
                    recommendations = random.sample(st.session_state.full_pokedex, 6)  # Pega 6 aleatórios
                st.session_state.last_generated_team = recommendations[:6]  # Salva no session_state
                st.success("✅ Recomendações geradas!")  # Mensagem

        if st.session_state.last_generated_team:  # Se tem recomendações
            st.subheader("Pokémon recomendados")  # Título
            for idx, pkm in enumerate(st.session_state.last_generated_team):  # Para cada recomendação
                sprite_url = pkm.sprite  # Pega sprite
                with st.container(border=True):  # Card
                    cols = st.columns([1, 4, 2])  # Colunas
                    with cols[0]:  # Imagem
                        if sprite_url: st.image(sprite_url, width=80)
                    with cols[1]:  # Info
                        st.markdown(f"**{pkm.name}**")
                        tipos = ', '.join(t.value for t in pkm.types)
                        st.caption(f"Tipos: {tipos} | Gen {getattr(pkm, 'generation', '?')}")
                    with cols[2]:  # Botão adicionar
                        if st.button("➕ Adicionar", key=f"rec_add_{idx}_{pkm.id}"):  # Botão único
                            if st.session_state.current_team.add_pokemon(pkm):  # Adiciona
                                st.success(f"✅ {pkm.name} adicionado!")
                                st.rerun()  # Recarrega
                            else:
                                st.error("❌ Time já está completo!")

# ====================== TAB 4 - GERAR COM IA ======================
with tab4:  # Aba de geração com IA (filtro simples)
    st.header("🤖 Gerar Time Completo com IA")  # Título
    st.caption("Usando pokemon_cleaned_pt.csv + Filtro por Geração + Tipo")  # Legenda
    user_prompt = st.text_area(  # Campo grande de texto
        "Descreva o time",
        placeholder="time de água gen 9",
        height=100
    )

    if st.button("🚀 Gerar Time com IA", type="primary", use_container_width=True):  # Botão principal de gerar
        if not st.session_state.full_pokedex:  # Se pokedex não carregou
            st.error("Dataset não carregado!")
            st.stop()
        if not user_prompt.strip():  # Se não digitou nada
            st.error("Digite uma descrição!")
            st.stop()
        with st.spinner("🔍 Gerando time..."):  # Loading
            filtered = st.session_state.full_pokedex.copy()  # Copia toda a pokedex
            gen_filter = extrair_geracao_do_prompt(user_prompt)  # Extrai geração do prompt
            if gen_filter:  # Se encontrou geração
                filtered = [p for p in filtered if getattr(p, 'generation', 0) == gen_filter]  # Filtra
                if len(filtered) == 0:  # Se nada sobrou
                    filtered = [p for p in st.session_state.full_pokedex if
                                get_generation_by_id(p.id) == gen_filter]  # Tenta de novo
                st.success(f"✅ Filtrado para **Gen {gen_filter}** ({len(filtered)} Pokémon)")  # Mensagem
            prompt_lower = user_prompt.lower()  # Prompt em minúsculo
            single_type = None  # Variável para tipo
            for pt, en in pt_to_en.items():  # Procura tipo mencionado
                if pt.lower() in prompt_lower:
                    single_type = en
                    break
            if single_type:  # Se encontrou tipo
                filtered = [p for p in filtered if any(t.value == single_type for t in p.types)]  # Filtra
                st.success(f"🔥 Tipo **{single_type}** aplicado ({len(filtered)} Pokémon restantes)")  # Mensagem
            if len(filtered) < 6:  # Se não tem 6 Pokémon
                st.error(f"❌ Só encontrei {len(filtered)} Pokémon. Tente outro filtro!")
                st.stop()
            generated = random.sample(filtered, 6)  # Escolhe 6 aleatórios
            st.session_state.last_generated_team = generated  # Salva
            st.success(f"✅ Time gerado com sucesso! (Gen {gen_filter or 'qualquer'})")  # Mensagem

    if st.session_state.last_generated_team:  # Exibe o time gerado (fora do if do botão – isso faz o botão funcionar)
        st.subheader("Seu time gerado pela IA")  # Título
        for idx, pkm in enumerate(st.session_state.last_generated_team):  # Para cada Pokémon gerado
            sprite_url = pkm.sprite  # Sprite
            if not sprite_url or "http" not in str(sprite_url):  # Se sprite não existe ou não é URL
                try:  # Tenta pegar da PokeAPI
                    name_lower = pkm.name.lower().replace(" ", "-")
                    r = requests.get(f"https://pokeapi.co/api/v2/pokemon/{name_lower}", timeout=8)
                    if r.status_code == 200:
                        sprite_url = r.json()["sprites"]["front_default"]
                except:
                    sprite_url = None
            with st.container(border=True):  # Card
                cols = st.columns([1, 4, 2])
                with cols[0]:
                    if sprite_url: st.image(sprite_url, width=90)
                with cols[1]:
                    st.markdown(f"**{pkm.name}**")
                    tipos = ', '.join(t.value for t in pkm.types) if pkm.types else '—'
                    gen = getattr(pkm, 'generation', '?')
                    st.caption(f"Tipos: {tipos} | Gen {gen}")
                with cols[2]:
                    if st.button("➕ Adicionar ao meu time", key=f"add_ia_{idx}_{pkm.id}_{pkm.name}"):  # Botão único
                        if st.session_state.current_team.add_pokemon(pkm):  # Adiciona
                            st.success(f"✅ {pkm.name} adicionado ao seu time!")
                            st.rerun()
                        else:
                            st.error("❌ Time já está completo (máximo 6)!")

# ====================== TAB 5 - MODO IA HÍBRIDO + SIMULADOR ======================
with tab5:  # Aba híbrida + simulador
    st.header("🌟 Modo IA Híbrido + Simulador")  # Título
    team = st.session_state.current_team  # Time atual

    st.subheader("🔄 Geração Híbrida")  # Subtítulo
    hybrid_prompt = st.text_input("Descreva o estilo do time (ex: ofensivo dragão gen 9)",
                                  placeholder="ofensivo com dragão")  # Campo de texto
    if st.button("🧬 Gerar Time Híbrido", type="primary"):  # Botão híbrido
        with st.spinner("Gerando time híbrido..."):  # Loading
            filtered = st.session_state.full_pokedex.copy()  # Copia pokedex
            gen_filter = extrair_geracao_do_prompt(hybrid_prompt)  # Filtra geração
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
            generated = random.sample(filtered, min(6, len(filtered)))  # Gera time
            st.session_state.last_generated_team = generated  # Salva
            st.success("Time híbrido gerado!")  # Mensagem

    if st.session_state.last_generated_team:  # Exibe sugestão híbrida
        st.write("**Time sugerido pela IA híbrida:**")
        for pkm in st.session_state.last_generated_team:
            if st.button(f"➕ {pkm.name}", key=f"hybrid_add_{pkm.id}"):  # Botão adicionar
                if st.session_state.current_team.add_pokemon(pkm):
                    st.success(f"{pkm.name} adicionado!")
                    st.rerun()
                else:
                    st.error("Time cheio!")

    st.divider()  # Divisória
    st.subheader("⚔️ Simulador de Batalhas")  # Subtítulo simulador
    if st.button("🚀 Simular Batalha contra Time Rival"):  # Botão de simulação
        if not team.pokemon:  # Se time vazio
            st.error("Monte seu time primeiro!")
        else:
            rival_team = random.sample(st.session_state.full_pokedex, 6)  # Gera time rival aleatório
            st.write("**Seu Time** vs **Time Rival**")  # Título
            col_me, col_rival = st.columns(2)  # Duas colunas
            with col_me:
                st.subheader("Seu Time")
                for p in team.pokemon:
                    st.write(f"• {p.name}")
            with col_rival:
                st.subheader("Time Rival")
                for p in rival_team:
                    st.write(f"• {p.name}")
            my_score = calculate_synergy_score(team)  # Pontuação do jogador
            rival_score = random.randint(40, 95)  # Pontuação rival aleatória
            st.metric("Pontuação do seu time", my_score)  # Mostra métrica
            st.metric("Pontuação do rival", rival_score)
            if my_score > rival_score:  # Resultado
                st.success("🏆 VITÓRIA!")
            elif my_score == rival_score:
                st.info("⚖️ Empate técnico.")
            else:
                st.error("❌ Derrota.")

# ====================== EXPORTAÇÃO ======================
st.divider()  # Linha divisória final
st.subheader("📤 Exportação Rápida")  # Título de exportação
team = st.session_state.current_team  # Time atual
if team.pokemon:  # Se tem Pokémon
    showdown_text = "\n".join(p.name for p in team.pokemon)  # Texto para Showdown (um nome por linha)
    col1, col2 = st.columns(2)  # Duas colunas
    with col1:  # Botão Showdown
        if st.button("📋 Copiar para Pokémon Showdown", use_container_width=True):
            st.code(showdown_text, language="text")  # Mostra o texto
            st.success("✅ Copiado!")
    with col2:  # Botão PokePaste
        if st.button("📤 Exportar para PokePaste", use_container_width=True):
            st.success("✅ Pronto para PokePaste!")
            st.code(showdown_text, language="text")
else:  # Se time vazio
    st.info("Adicione Pokémon para exportar.")  # Mensagem

st.markdown("""
<div style="text-align: center; padding: 20px; background: linear-gradient(90deg, #0a1428, #1a2a4a); border-radius: 15px; margin-top: 30px; border: 2px solid #FFDE00;">
    <p style="color: #FFDE00; font-size: 1.1em; margin: 0;"><strong>⚔️ FEITO COM PAIXÃO POKÉMON POR TREINADORES PARA TREINADORES ⚔️</strong></p>
    <p style="color: #A8A878; font-size: 0.9em; margin: 8px 0 0 0;">Gotta Catch 'Em All • Streamlit + PokeAPI • Gen 1-9</p>
    <p style="color: #E3350D; font-size: 0.85em; margin: 5px 0 0 0;">© 2026 — Projeto open-source inspirado no universo Pokémon</p>
</div>
""", unsafe_allow_html=True)