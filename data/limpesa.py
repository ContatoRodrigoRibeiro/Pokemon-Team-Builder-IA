import pandas as pd

# ==================== CARREGAR DADOS ====================
df = pd.read_csv('pokemon_complete_2025.csv')

# ==================== LIMPEZA ====================
# Preencher valores vazios corretamente
df['type_2'] = df['type_2'].fillna('')
df['ability_2'] = df['ability_2'].fillna('')
df['hidden_ability'] = df['hidden_ability'].fillna('')
df['habitat'] = df['habitat'].fillna('')
df['egg_groups'] = df['egg_groups'].fillna('')

# Converter booleanos
bool_cols = ['is_legendary', 'is_mythical', 'is_baby', 'is_dual_type']
for col in bool_cols:
    df[col] = df[col].astype(bool)

# ==================== RENOMEAR COLUNAS (PT-BR) ====================
column_mapping = {
    'pokedex_id': 'id_pokedex', 'name': 'nome', 'genus': 'genero',
    'generation': 'geracao', 'type_1': 'tipo_1', 'type_2': 'tipo_2',
    'num_types': 'num_tipos', 'hp': 'hp', 'attack': 'ataque',
    'defense': 'defesa', 'sp_attack': 'ataque_especial',
    'sp_defense': 'defesa_especial', 'speed': 'velocidade',
    'base_stat_total': 'total_estatisticas_base', 'height_m': 'altura_m',
    'weight_kg': 'peso_kg', 'base_experience': 'experiencia_base',
    'ability_1': 'habilidade_1', 'ability_2': 'habilidade_2',
    'hidden_ability': 'habilidade_oculta', 'color': 'cor',
    'shape': 'forma', 'habitat': 'habitat',
    'growth_rate': 'taxa_crescimento', 'egg_groups': 'grupos_ovos',
    'is_legendary': 'e_lendario', 'is_mythical': 'e_mitico',
    'is_baby': 'e_baby', 'capture_rate': 'taxa_captura',
    'base_happiness': 'felicidade_base', 'hatch_counter': 'contador_chocagem',
    'gender_rate': 'taxa_genero', 'description': 'descricao',
    'sprite_url': 'url_sprite', 'is_dual_type': 'e_dual_tipo',
    'bmi': 'imc', 'attack_defense_ratio': 'razao_ataque_defesa',
    'physical_total': 'total_fisico', 'special_total': 'total_especial',
    'offensive_total': 'total_ofensivo', 'defensive_total': 'total_defensivo',
    'gender_distribution': 'distribuicao_genero', 'stat_tier': 'nivel_estatisticas'
}
df = df.rename(columns=column_mapping)

# ==================== TRADUÇÕES OFICIAIS PT-BR ====================
type_map = {'grass':'planta','fire':'fogo','water':'água','bug':'inseto','flying':'voador',
            'poison':'veneno','electric':'elétrico','ground':'terra','rock':'pedra',
            'psychic':'psíquico','ice':'gelo','dragon':'dragão','dark':'sombrio',
            'steel':'aço','fairy':'fada','fighting':'lutador','ghost':'fantasma','normal':'normal'}

color_map = {'green':'verde','red':'vermelho','blue':'azul','yellow':'amarelo','brown':'marrom',
             'purple':'roxo','pink':'rosa','gray':'cinza','white':'branco','black':'preto'}

shape_map = {'quadruped':'quadrúpede','upright':'bípede','wings':'asas','squiggle':'serpentina',
             'armor':'armadura','bug-wings':'asas de inseto','legs':'pernas','tentacles':'tentáculos',
             'heads':'cabeças','ball':'bola','fish':'peixe','humanoid':'humanóide','blob':'gota','arms':'braços'}

habitat_map = {'grassland':'pradaria','mountain':'montanha','forest':'floresta','waters-edge':'beira d\'água',
               'sea':'mar','cave':'caverna','rough-terrain':'terreno acidentado','urban':'urbano','rare':'raro'}

growth_map = {'medium-slow':'médio-lento','medium':'médio','fast':'rápido','slow':'lento',
              'slow-then-very-fast':'lento-então-muito-rápido'}

egg_map = {'monster':'monstro','plant':'planta','dragon':'dragão','water1':'água1','water2':'água2',
           'water3':'água3','bug':'inseto','flying':'voador','ground':'terra','fairy':'fada',
           'humanshape':'forma humana','mineral':'mineral','indeterminate':'indeterminado',
           'no-eggs':'sem ovos','ditto':'ditto'}

# Aplicar traduções
df['tipo_1'] = df['tipo_1'].map(type_map).fillna(df['tipo_1'])
df['tipo_2'] = df['tipo_2'].map(type_map).fillna(df['tipo_2'])
df['cor'] = df['cor'].map(color_map).fillna(df['cor'])
df['forma'] = df['forma'].map(shape_map).fillna(df['forma'])
df['habitat'] = df['habitat'].map(habitat_map).fillna(df['habitat'])
df['taxa_crescimento'] = df['taxa_crescimento'].map(growth_map).fillna(df['taxa_crescimento'])

def traduzir_grupos_ovos(grupo):
    if pd.isna(grupo) or grupo == '': return ''
    grupos = [g.strip() for g in str(grupo).split(',')]
    return ', '.join([egg_map.get(g, g) for g in grupos])

df['grupos_ovos'] = df['grupos_ovos'].apply(traduzir_grupos_ovos)

# Booleanos como Sim/Não (mais fácil de ler)
for col in ['e_lendario', 'e_mitico', 'e_baby', 'e_dual_tipo']:
    df[col] = df[col].map({True: 'Sim', False: 'Não'})

# ==================== SALVAR ARQUIVO LIMPO ====================
df.to_csv('pokemon_cleaned_pt.csv', index=False, encoding='utf-8-sig')

print("✅ Arquivo gerado com sucesso: pokemon_cleaned_pt.csv")
print(f"Total de Pokémon: {len(df)}")
print(f"Colunas: {list(df.columns)}")
print("\nPrimeiras 5 linhas:")
print(df[['id_pokedex', 'nome', 'geracao', 'tipo_1', 'tipo_2', 'e_lendario']].head())