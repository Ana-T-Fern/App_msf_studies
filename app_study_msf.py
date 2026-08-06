import random
import requests
import streamlit as st

# Configuração para telemóvel
st.set_page_config(
    page_title="MS Fabric Micro-Learning", page_icon="⚡", layout="centered"
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

# --- PERSISTÊNCIA DO PROGRESSO ---
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


# --- CURSOS ESPECÍFICOS E SEUS UIDS OFICIAIS ---
COURSES = {
    "🌱 Get started with Microsoft Fabric (Learning Path)": {
        "uid": "learn.wwl.get-started-fabric",
        "type": "learningPaths",
    },
    "🔥 Implement data engineering solutions using MS Fabric (DP-700)": {
        "uid": "learn.wwl.implement-data-engineering-solutions-using-microsoft-fabric",
        "type": "courses",
    },
}


# --- CARREGAR APENAS OS MÓDULOS PERTENCENTES AO PATH/CURSO ---
@st.cache_data(ttl=86400)
def fetch_strict_course_units(course_uid, course_type):
    """Passo 1: Obtém a lista estrita de módulos do curso. Passo 2: Extrai as Unidades/Lições."""
    units_list = []

    # 1. Consultar a API pelo UID do Path/Curso
    url = f"https://learn.microsoft.com/api/catalog/?uid={course_uid}&locale=pt-pt"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            data = res.json()

            # Extrair os UIDs dos módulos associados a este curso/path
            container = data.get(course_type, [])
            if not container:
                # Tentar fallback caso o objeto venha como learningPaths ou courses
                container = data.get("learningPaths", []) or data.get(
                    "courses", []
                )

            if container:
                module_uids = container[0].get("modules", [])

                if module_uids:
                    # 2. Consultar os detalhes dos módulos específicos deste curso
                    mod_uids_str = ",".join(module_uids)
                    mod_url = f"https://learn.microsoft.com/api/catalog/?uid={mod_uids_str}&locale=pt-pt"
                    mod_res = requests.get(mod_url, timeout=10)

                    if mod_res.status_code == 200:
                        modules_data = mod_res.json().get("modules", [])

                        for mod in modules_data:
                            mod_title = mod.get("title", "Módulo")
                            mod_summary = mod.get(
                                "summary", "Sem resumo disponível."
                            )
                            mod_url_link = mod.get("url", "")
                            units_uids = mod.get("units", [])

                            # Extrair as lições/unidades do módulo
                            for idx, unit_uid in enumerate(units_uids):
                                raw_name = unit_uid.split(".")[-1].replace(
                                    "-", " "
                                )
                                unit_name = raw_name.capitalize()

                                units_list.append(
                                    {
                                        "unit_title": f"Lição {idx + 1}: {unit_name}",
                                        "module_title": mod_title,
                                        "module_summary": mod_summary,
                                        "unit_index": idx + 1,
                                        "total_units": len(units_uids),
                                        "url": mod_url_link,
                                    }
                                )
    except Exception as e:
        st.error(f"Erro ao carregar os dados do MS Learn: {e}")

    return units_list


# --- INTERFACE ---
st.title("⚡ MS Fabric Hub")

selected_course_name = st.selectbox(
    "Escolhe o Caminho Oficial:", list(COURSES.keys())
)

selected_course = COURSES[selected_course_name]
units_bank = fetch_strict_course_units(
    selected_course["uid"], selected_course["type"]
)

# --- SIDEBAR ---
st.sidebar.title("🏆 Teu Progresso")
st.sidebar.metric("XP Total 🌟", st.session_state.xp)
st.sidebar.metric("Lições Lidas ⚡", st.session_state.units_read)
st.sidebar.metric("Lições do Curso", len(units_bank))

if st.sidebar.button("🗑️ Reset de Progresso"):
    st.session_state.xp = 0
    st.session_state.units_read = 0
    save_progress()
    st.rerun()

st.divider()

# --- CONTEÚDO ---
if not units_bank:
    st.warning("A carregar as lições oficiais do curso selecionado...")
else:
    if st.session_state.current_unit is None or st.button(
        "🔄 Próxima Lição do Curso"
    ):
        st.session_state.current_unit = random.choice(units_bank)
        st.rerun()

    item = st.session_state.current_unit
    if item:
        st.caption("📦 MÓDULO PERTENCENTE AO CURSO")
        st.markdown(f"**{item['module_title']}**")

        st.caption(
            f"Parte {item['unit_index']} de {item['total_units']} deste módulo"
        )
        st.subheader(item["unit_title"])

        st.info(f"💡 **Resumo do Módulo:**\n\n{item['module_summary']}")

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
