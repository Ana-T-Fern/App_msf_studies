import random
import requests
import streamlit as st

# Configuração para ecrã de telemóvel
st.set_page_config(
    page_title="MS Fabric Micro-Learning", page_icon="⚡", layout="centered"
)

st.markdown(
    """
    <style>
    .stApp { max-width: 480px; margin: 0 auto; }
    div.stButton > button { width: 100%; border-radius: 12px; height: 3.2em; background-color: #0078D4; color: white; font-weight: bold; }
    .mod-badge { background-color: #e1dfdd; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 0.85em; }
    </style>
""",
    unsafe_allow_html=True,
)

# --- PERSISTÊNCIA DE PROGRESSO (GUARDA NO NAVEGADOR) ---
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


# --- DICIONÁRIO DOS DOIS CURSOS ESPECÍFICOS DA MICROSOFT ---
COURSES = {
    "🌱 Get started with Microsoft Fabric (Learning Path)": {
        "uid": "learn.wwl.get-started-fabric",
        "search": "get-started-fabric",
    },
    "🔥 Implement data engineering solutions using MS Fabric (Course DP-700)": {
        "uid": "learn.wwl.implement-data-engineering-solutions-using-microsoft-fabric",
        "search": "implement-data-engineering-solutions-using-microsoft-fabric",
    },
}


# --- CARREGAR UNIDADES E MÓDULOS DOS CURSOS ESPECÍFICOS ---
@st.cache_data(ttl=86400)
def fetch_exact_course_units(course_search):
    """Busca o catálogo da MS filtrado exclusivamente pelo curso selecionado."""
    url = f"https://learn.microsoft.com/api/catalog/?search={course_search}&locale=pt-pt"
    units_list = []

    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            data = res.json()
            modules = data.get("modules", [])

            for mod in modules:
                mod_title = mod.get("title", "Módulo sem título")
                mod_url = mod.get("url", "")
                mod_summary = mod.get(
                    "summary", "Sem resumo disponível."
                )
                units_uids = mod.get("units", [])

                if units_uids:
                    for idx, unit_uid in enumerate(units_uids):
                        # Limpa o identificador para criar um nome amigável para a lição
                        raw_name = unit_uid.split(".")[-1].replace("-", " ")
                        unit_name = raw_name.capitalize()

                        units_list.append(
                            {
                                "unit_title": f"Lição {idx + 1}: {unit_name}",
                                "module_title": mod_title,
                                "module_summary": mod_summary,
                                "unit_index": idx + 1,
                                "total_units": len(units_uids),
                                "url": mod_url,
                            }
                        )
    except Exception as e:
        st.error(f"Erro ao ligar à API do MS Learn: {e}")

    return units_list


# --- INTERFACE ---
st.title("⚡ MS Fabric Hub")

selected_course_name = st.selectbox(
    "Escolhe o Caminho Oficial:", list(COURSES.keys())
)

selected_course = COURSES[selected_course_name]
units_bank = fetch_exact_course_units(selected_course["search"])

# --- SIDEBAR (PROGRESSO) ---
st.sidebar.title("🏆 Teu Progresso")
st.sidebar.metric("XP Total 🌟", st.session_state.xp)
st.sidebar.metric("Lições Lidas ⚡", st.session_state.units_read)
st.sidebar.metric("Total de Lições no Curso", len(units_bank))

if st.sidebar.button("🗑️ Reset de Progresso"):
    st.session_state.xp = 0
    st.session_state.units_read = 0
    save_progress()
    st.rerun()

st.divider()

# --- EXIBIÇÃO DO CONTEÚDO ---
if not units_bank:
    st.warning(
        "Não foi possível carregar as lições deste curso no momento. Tenta recarregar."
    )
else:
    # Botão para sortear ou passar à próxima lição do curso selecionado
    if st.session_state.current_unit is None or st.button(
        "🔄 Próxima Lição do Curso"
    ):
        st.session_state.current_unit = random.choice(units_bank)
        st.rerun()

    item = st.session_state.current_unit
    if item:
        # Exibe o Módulo Pai
        st.caption("📦 MÓDULO OFICIAL")
        st.markdown(f"**{item['module_title']}**")

        st.caption(
            f"Parte {item['unit_index']} de {item['total_units']} deste módulo"
        )
        st.subheader(item["unit_title"])

        # Breve contexto/resumo do módulo
        st.info(f"💡 **Sobre este Módulo:**\n\n{item['module_summary']}")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("✅ Concluir (+25 XP)"):
                st.session_state.xp += 25
                st.session_state.units_read += 1
                save_progress()
                st.success("+25 XP!")
                st.rerun()

        with col2:
            st.link_button("📖 Estudar no MS Learn", item["url"])
