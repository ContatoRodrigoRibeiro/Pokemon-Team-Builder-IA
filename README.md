# 🤖 Pokémon Team Builder IA

**Monte times imbatíveis com IA • Gen 9 + anteriores**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://iageradoradetimepokemon.streamlit.app/)

**🎮 App Online (já rodando):**  
[https://iageradoradetimepokemon.streamlit.app/](https://iageradoradetimepokemon.streamlit.app/)

---

Uma aplicação web completa e moderna para construir times de Pokémon (Gen 1 a Gen 9) de forma **manual ou assistida por IA**. Feita **100% em um único arquivo** (`app.py`).

---

## ✨ Funcionalidades Completas

| Módulo                              | Status     | O que faz |
|-------------------------------------|------------|-----------|
| **🛠️ Modo Manual**                 | ✅ Completo | Busca Pokémon pela PokeAPI e monta time manualmente |
| **🔬 Análise Avançada**             | ✅ Completo | Fraquezas defensivas, cobertura ofensiva e pontuação de sinergia |
| **🧠 Recomendações Inteligentes**   | ✅ Completo | Sugestões automáticas baseadas nas fraquezas do seu time |
| **🤖 Gerar com IA**                 | ✅ Completo | Gera time completo por prompt (ex: "time de água geração 9") |
| **🌟 Modo IA Híbrido + Simulador**  | ✅ Completo | Geração híbrida + simulador de batalha contra time rival |
| **📤 Exportação**                   | ✅ Completo | Exporta direto para Pokémon Showdown e PokePaste |

**Destaques técnicos:**
- Análise completa de tipos (tabela de efetividade Gen 6+)
- Suporte total a dual-types
- Cache de Pokémon para melhor performance
- Interface totalmente em português
- Design moderno e responsivo (Streamlit)

---
<img width="1868" height="884" alt="image" src="https://github.com/user-attachments/assets/8b8703a9-872e-4684-95b0-300f9279fc9b" />


## 🚀 Como Usar

### ✅ Versão Online (Recomendada)
Acesse diretamente:  
**[https://iageradoradetimepokemon.streamlit.app/](https://iageradoradetimepokemon.streamlit.app/)**

### 🖥️ Rodar Localmente


# 1. Clone o repositório
git clone https://github.com/ContatoRodrigoRibeiro/Pokemon-Team-Builder-IA.git
cd Pokemon-Team-Builder-IA

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Rode a aplicação
streamlit run app.py
A aplicação abrirá automaticamente no navegador em http://localhost:8501


🛠️ Tecnologias Utilizadas

Streamlit – Interface web interativa
Pandas – Leitura do CSV da Pokédex
PokeAPI – Busca de sprites e dados em tempo real
Python 3.10+
Single-file architecture (tudo em um único arquivo app.py)


📁 Estrutura do Projeto
textPokemon-Team-Builder-IA/
├── app.py                    # ← Arquivo principal (tudo em um único arquivo)
├── data/
│   └── pokemon_cleaned_pt.csv # Pokédex em português
├── requirements.txt
├── README.md
└── preview.png               # Imagem de demonstração

📸 Demonstração

Modo Manual com busca em tempo real
Análise Avançada com cores de gravidade
Geração com IA (filtro por geração e tipo)
Simulador de batalhas com pontuação de sinergia
Exportação para Showdown e PokePaste

(Imagens de demonstração serão atualizadas em breve no repositório)

📌 Próximas Melhorias (Opcionais)

Integração com modelo de IA real (Groq / OpenAI) para prompts mais inteligentes
Salvamento de times (JSON / localStorage)
Modo competitivo com EVs, IVs e nature
Tema dark/light automático
Suporte a movesets e abilities na análise


👨‍💻 Autor
Rodrigo Ribeiro
Desenvolvido com ❤️ para a comunidade Pokémon brasileira

Projeto finalizado e estável ✅
Versão atual: 1.0.0 (todos os módulos "Em breve" foram implementados)

Quer contribuir?
Fork → Faça suas melhorias → Pull Request
Qualquer dúvida ou sugestão, é só abrir uma Issue!

Feito com Streamlit • Pokémon © Nintendo, Game Freak, Creatures
