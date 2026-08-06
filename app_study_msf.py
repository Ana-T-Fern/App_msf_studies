import json
import random
import requests
import streamlit as st

# Configuração da página para estilo Mobile
st.set_page_config(page_title="DP-700 Hub", page_icon="⚡", layout="centered")

# Estilo CSS para botões e layout de telemóvel
st.markdown(
    """
    <style>
    .stApp { max-width: 480px; margin: 0 auto; }
    div.stButton > button { width: 100%; border-radius: 12px; height: 3.2em; background-color: #0078D4; color: white; font-weight: bold; }
    </style>
""",
    unsafe_allow_html=True,
)


# --- FUNÇÕES DE CARREGAMENTO DE DADOS ---


# 1. Carregar Conteúdos do MS Learn via API Oficial
@st.cache_data(ttl=86400)
def fetch_ms_learn_modules(query="fabric dp-700"):
    url = f"https://learn.microsoft.com/api/catalog/?search={query}&locale=pt-pt"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            modules = []
            for item in data.get("modules", []):
                modules.append(
                    {
                        "title": item.get("title"),
                        "summary": item.get("summary"),
                        "duration": item.get("duration_in_minutes", "5"),
                        "url": item.get("url"),
                        "levels": ", ".join(item.get("levels", ["Geral"])),
                    }
                )
            return modules
    except Exception:
        pass
    return []


# 2. Carregar Perguntas do Ficheiro JSON Local
@st.cache_data(ttl=60)
def load_quiz_questions():
    try:
        with open("questions.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


# --- INICIALIZAÇÃO DO ESTADO DA SESSÃO ---

if "xp" not in st.session_state:
    st.session_state.xp = 0
if "cards_read" not in st.session_state:
    st.session_state.cards_read = 0
if "quiz_answered" not in st.session_state:
    st.session_state.quiz_answered = 0
if "current_flashcard" not in st.session_state:
    st.session_state.current_flashcard = None
if "current_question" not in st.session_state:
    st.session_state.current_question = None
if "answered_status" not in st.session_state:
    st.session_state.answered_status = False

# Carregar dados
flashcards_bank = fetch_ms_learn_modules()
quiz_bank = load_quiz_questions()

# --- SIDEBAR / PAINEL DE PROGRESSO ---

st.sidebar.title("🏆 Teu Progresso")
st.sidebar.metric("XP Total", st.session_state.xp)
st.sidebar.metric("Tópicos Lidos 📚", st.session_state.cards_read)
st.sidebar.metric("Questões Respondidas 📝", st.session_state.quiz_answered)

total_items = len(flashcards_bank) + len(quiz_bank)
progress_val = min(
    1.0,
    (st.session_state.cards_read + st.session_state.quiz_answered)
    / max(1, total_items),
)
st.sidebar.progress(progress_val)

# --- NAVEGAÇÃO ENTRE MODOS ---

st.title("⚡ DP-700 Master Hub")
mode = st.radio(
    "Escolhe o teu modo de estudo:",
    ["📚 Teoria (MS Learn Flashcards)", "📝 Prática (Quiz de Perguntas)"],
    horizontal=True,
)

st.divider()

# --- MODO 1: FLASHCARDS MS LEARN ---

if mode == "📚 Teoria (MS Learn Flashcards)":
    st.caption("Conceitos Oficiais da Documentação Microsoft Learn")

    if not flashcards_bank:
        st.warning(
            "Não foi possível carregar os módulos da Microsoft neste momento."
        )
    else:
        if st.session_state.current_flashcard is None or st.button(
            "🔄 Sortear Novo Flashcard"
        ):
            st.session_state.current_flashcard = random.choice(flashcards_bank)
            st.rerun()

        card = st.session_state.current_flashcard
        if card:
            st.caption(
                f"⏱️ Duração: ~{card['duration']} min | Nível: {card['levels']}"
            )
            st.subheader(card["title"])
            st.info(f"💡 **Resumo do Conceito:**\n\n{card['summary']}")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Marcar como Lido (+50 XP)"):
                    st.session_state.xp += 50
                    st.session_state.cards_read += 1
                    st.success("+50 XP!")
            with col2:
                st.link_button("📖 Ler Artigo Completo", card["url"])

# --- MODO 2: QUIZ DE PERGUNTAS ---

elif mode == "📝 Prática (Quiz de Perguntas)":
    st.caption("Testa os teus conhecimentos para o Exame DP-700")

    if not quiz_bank:
        st.warning(
            "O ficheiro questions.json não foi encontrado ou está vazio."
        )
    else:
        if st.session_state.current_question is None or st.button(
            "🔄 Próxima Pergunta"
        ):
            st.session_state.current_question = random.choice(quiz_bank)
            st.session_state.answered_status = False
            st.rerun()

        q = st.session_state.current_question
        if q:
            st.caption(f"Tópico: {q.get('topic', 'DP-700 / Fabric')}")
            st.subheader("Pergunta:")
            st.write(q["question"])

            selected = st.radio(
                "Escolhe a opção correta:",
                q["options"],
                key=f"quiz_opt_{q.get('id', random.randint(1, 1000))}",
            )

            if st.button("Confirmar Resposta"):
                if not st.session_state.answered_status:
                    st.session_state.answered_status = True
                    st.session_state.quiz_answered += 1

                    if selected == q["answer"]:
                        st.balloons()
                        st.success("🎉 Correto! +100 XP")
                        st.session_state.xp += 100
                    else:
                        st.error(
                            f"❌ Errado. A resposta correta era: **{q['answer']}**"
                        )

                    st.info(f"💡 **Explicação:** {q['explanation']}")
                else:
                    st.warning(
                        "Clica em '🔄 Próxima Pergunta' para continuar!"
                    )
