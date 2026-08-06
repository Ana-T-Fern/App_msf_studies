import random
import requests
import streamlit as st

# Configuração para ecrã de telemóvel
st.set_page_config(
    page_title="Fabric & DP-700 Hub", page_icon="⚡", layout="centered"
)

st.markdown(
    """
    <style>
    .stApp { max-width: 480px; margin: 0 auto; }
    div.stButton > button { width: 100%; border-radius: 12px; height: 3.2em; background-color: #0078D4; color: white; font-weight: bold; }
    </style>
""",
    unsafe_allow_html=True,
)

# --- SISTEMA DE PERSISTÊNCIA DE PROGRESSO (GUARDA NO NAVEGADOR) ---
# Lê os valores guardados nos parâmetros do URL
params = st.query_params

if "xp" not in st.session_state:
    st.session_state.xp = int(params.get("xp", 0))
if "cards_read" not in st.session_state:
    st.session_state.cards_read = int(params.get("read", 0))
if "current_card" not in st.session_state:
    st.session_state.current_card = None


def save_progress():
    """Atualiza o URL do navegador para não perder o progresso ao fechar a app."""
    st.query_params["xp"] = str(st.session_state.xp)
    st.query_params["read"] = str(st.session_state.cards_read)


# --- FUNÇÃO DE BUSCA NA API DO MICROSOFT LEARN ---
@st.cache_data(ttl=86400)
def fetch_course_modules(search_query):
    """Busca os módulos oficiais associados ao curso selecionado."""
    url = f"https://learn.microsoft.com/api/catalog/?search={search_query}&locale=pt-pt"
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
                        "duration": item.get("duration_in_minutes", "10"),
                        "url": item.get("url"),
                        "levels": ", ".join(item.get("levels", ["Geral"])),
                    }
                )
            return modules
    except Exception as e:
        st.error(f"Erro ao carregar o catálogo: {e}")
    return []


# --- SELEÇÃO DE CURSOS ---
st.title("⚡ Microsoft Data Hub")

course_choice = st.selectbox(
    "Escolhe o Caminho de Estudo:",
    [
        "🟢 Starter: Primeiros passos com Fabric",
        "🔥 Advanced: DP-700 (Data Engineer Fabric)",
    ],
)

# Define a query de pesquisa da API consoante a escolha
if "Starter" in course_choice:
    search_term = "get-started-fabric"
    course_tag = "Getting Started"
else:
    search_term = "dp-700"
    course_tag = "DP-700 Advanced"

modules_bank = fetch_course_modules(search_term)

# --- SIDEBAR (PROGRESSO PERSISTENTE) ---
st.sidebar.title("🏆 Teu Progresso")
st.sidebar.metric("XP Total 🌟", st.session_state.xp)
st.sidebar.metric("Módulos Concluídos 📚", st.session_state.cards_read)
st.sidebar.metric("Módulos Encontrados 🧩", len(modules_bank))

if st.sidebar.button("🗑️ Reset de Progresso"):
    st.session_state.xp = 0
    st.session_state.cards_read = 0
    save_progress()
    st.rerun()

st.divider()

# --- EXIBIÇÃO DO CONTEÚDO ---
if not modules_bank:
    st.warning("Não foi possível carregar os módulos deste curso no momento.")
else:
    # Botão para trocar de tópico dentro do curso selecionado
    if st.session_state.current_card is None or st.button(
        "🔄 Próximo Tópico do Curso"
    ):
        st.session_state.current_card = random.choice(modules_bank)
        st.rerun()

    card = st.session_state.current_card
    if card:
        st.caption(
            f"🎯 Curso: {course_tag} | ⏱️ Duração: ~{card['duration']} min"
        )
        st.subheader(card["title"])
        st.info(f"💡 **Resumo do Módulo:**\n\n{card['summary']}")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("✅ Concluir (+100 XP)"):
                st.session_state.xp += 100
                st.session_state.cards_read += 1
                save_progress()  # <--- Guarda o progresso no URL
                st.success("Guardado! +100 XP")
                st.rerun()

        with col2:
            st.link_button("📖 Abrir no MS Learn", card["url"])
