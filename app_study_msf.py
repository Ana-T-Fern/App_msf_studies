import random
import requests
import streamlit as st

# Configuração para ecrã de telemóvel
st.set_page_config(
    page_title="Fabric Micro-Learning", page_icon="⚡", layout="centered"
)

st.markdown(
    """
    <style>
    .stApp { max-width: 480px; margin: 0 auto; }
    div.stButton > button { width: 100%; border-radius: 12px; height: 3.2em; background-color: #0078D4; color: white; font-weight: bold; }
    .micro-card { background-color: #f0f4f8; border-left: 4px solid #0078D4; padding: 15px; border-radius: 8px; margin-bottom: 15px; }
    </style>
""",
    unsafe_allow_html=True,
)

# --- PERSISTÊNCIA DE PROGRESSO ---
params = st.query_params

if "xp" not in st.session_state:
    st.session_state.xp = int(params.get("xp", 0))
if "units_read" not in st.session_state:
    st.session_state.units_read = int(params.get("read", 0))
if "current_unit" not in st.session_state:
    st.session_state.current_unit = None


def save_progress():
    st.query_params["xp"] = str(st.session_state.xp)
    st.query_params["read"] = str(st.session_state.units_read)


# --- BUSCA DE UNIDADES/LIÇÕES INDIVIDUAIS (MICRO-LEARNING) ---
@st.cache_data(ttl=86400)
def fetch_micro_lessons(search_query):
    """Busca módulos e extrai as lições/unidades individuais de 2 minutos."""
    url = f"https://learn.microsoft.com/api/catalog/?search={search_query}&locale=pt-pt"
    micro_units = []
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            modules = data.get("modules", [])

            for mod in modules:
                mod_title = mod.get("title", "Módulo")
                icon_url = mod.get("icon_url", "")
                units = mod.get("units", [])

                for idx, unit_uid in enumerate(units):
                    # Criar um objeto leve para cada lição interna
                    micro_units.append(
                        {
                            "module_title": mod_title,
                            "unit_number": idx + 1,
                            "total_units": len(units),
                            "unit_uid": unit_uid,
                            "icon": icon_url,
                            "url": f"https://learn.microsoft.com/pt-pt/training/modules/{mod.get('uid', '')}/{unit_uid}",
                        }
                    )
    except Exception as e:
        st.error(f"Erro ao carregar micro-lições: {e}")

    return micro_units


# --- INTERFACE E SELEÇÃO DE CURSO ---
st.title("⚡ Fabric Micro-Learning")
st.caption("Lições Rápidas de 2 Minutos")

course_choice = st.selectbox(
    "Escolhe o Curso:",
    [
        "🟢 Starter: Primeiros passos com Fabric",
        "🔥 Advanced: DP-700 (Data Engineer)",
    ],
)

search_term = (
    "get-started-fabric" if "Starter" in course_choice else "dp-700"
)
lessons_bank = fetch_micro_lessons(search_term)

# --- SIDEBAR (PROGRESSO) ---
st.sidebar.title("🏆 Teu Progresso")
st.sidebar.metric("XP Total 🌟", st.session_state.xp)
st.sidebar.metric("Micro-Lições Lidas ⚡", st.session_state.units_read)
st.sidebar.metric("Lições Disponíveis 🧩", len(lessons_bank))

if st.sidebar.button("🗑️ Reset de Progresso"):
    st.session_state.xp = 0
    st.session_state.units_read = 0
    save_progress()
    st.rerun()

st.divider()

# --- EXIBIÇÃO DA MICRO-LIÇÃO ---
if not lessons_bank:
    st.warning("Não foi possível carregar as lições de micro-learning.")
else:
    if st.session_state.current_unit is None or st.button(
        "⚡ Próxima Lição Rápida"
    ):
        st.session_state.current_unit = random.choice(lessons_bank)
        st.rerun()

    unit = st.session_state.current_unit
    if unit:
        # Mostra o ícone da Microsoft se existir
        if unit["icon"]:
            st.image(unit["icon"], width=48)

        st.caption(
            f"📦 {unit['module_title']} (Parte {unit['unit_number']} de {unit['total_units']})"
        )
        st.subheader(f"Lição #{unit['unit_number']}")

        st.info(
            f"🎯 **Objetivo de Micro-Learning:**\n\nEstuda esta unidade curta para avançares no módulo **{unit['module_title']}**."
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button("✅ Concluir (+25 XP)"):
                st.session_state.xp += 25
                st.session_state.units_read += 1
                save_progress()
                st.success("+25 XP!")
                st.rerun()

        with col2:
            st.link_button("📖 Ler Lição (2 min)", unit["url"])
