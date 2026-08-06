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

# Índice da lição atual (começa na 0 = primeira lição)
if "lesson_index" not in st.session_state:
    st.session_state.lesson_index = 0


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


# --- CARREGAR UNIDADES E MÓDULOS DE FORMA SEQUENCIAL ---
@st.cache_data(ttl=86400)
def fetch_strict_course_units(course_uid, course_type):
    """Busca a lista de módulos do curso e extrai as lições mantendo a ordem exata."""
    units_list = []

    url = f"https://learn.microsoft.com/api/catalog/?uid={course_uid}&locale=pt-pt"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            data = res.json()
            container = data.get(course_type, []) or data.get(
                "learningPaths", []
            ) or data.get("courses", [])

            if container:
                module_uids = container[0].get("modules", [])

                if module_uids:
                    mod_uids_str = ",".join(module_uids)
                    mod_url = f"https://learn.microsoft.com/api/catalog/?uid={mod_uids_str}&locale=pt-pt"
                    mod_res = requests.get(mod_url, timeout=10)

                    if mod_res.status_code == 200:
                        modules_data = mod_res.json().get("modules", [])

                        # Manter a ordem original dos módulos definida no curso
                        mod_map = {m.get("uid"): m for m in modules_data}
                        ordered_modules = [
                            mod_map[uid] for uid in module_uids if uid in mod_map
                        ]

                        for mod_idx, mod in enumerate(ordered_modules):
                            mod_title = mod.get("title", "Módulo")
                            mod_summary = mod.get(
                                "summary", "Sem resumo disponível."
                            )
                            mod_url_link = mod.get("url", "")
                            units_uids = mod.get("units", [])

                            for idx, unit_uid in enumerate(units_uids):
                                raw_name = unit_uid.split(".")[-1].replace(
                                    "-", " "
                                )
                                unit_name = raw_name.capitalize()

                                units_list.append(
                                    {
                                        "unit_title": f"Lição: {unit_name}",
                                        "module_title": f"Módulo {mod_idx + 1}: {mod_title}",
                                        "module_summary": mod_summary,
                                        "unit_index": idx + 1,
                                        "total_units_in_mod": len(units_uids),
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

# Se mudar de curso, volta à primeira lição (índice 0)
if "last_selected_course" not in st.session_state or st.session_state.last_selected_course != selected_course_name:
    st.session_state.lesson_index = 0
    st.session_state.last_selected_course = selected_course_name

selected_course = COURSES[selected_course_name]
units_bank = fetch_strict_course_units(
    selected_course["uid"], selected_course["type"]
)

# --- SIDEBAR (PROGRESSO) ---
st.sidebar.title("🏆 Teu Progresso")
st.sidebar.metric("XP Total 🌟", st.session_state.xp)
st.sidebar.metric("Lições Concluídas ⚡", st.session_state.units_read)
st.sidebar.metric("Total de Lições no Curso", len(units_bank))

if st.sidebar.button("🗑️ Reset de Progresso"):
    st.session_state.xp = 0
    st.session_state.units_read = 0
    st.session_state.lesson_index = 0
    save_progress()
    st.rerun()

st.divider()

# --- EXIBIÇÃO DA LIÇÃO ORDENADA ---
if not units_bank:
    st.warning("A carregar as lições oficiais do curso selecionado...")
else:
    # Garantir que o índice não sai dos limites da lista
    total_lessons = len(units_bank)
    current_idx = min(st.session_state.lesson_index, total_lessons - 1)
    item = units_bank[current_idx]

    # Indicador visual de progresso na sequência (Ex: Lição 3 de 24)
    st.progress((current_idx + 1) / total_lessons)
    st.caption(f"📍 **Progresso no Curso:** Lição {current_idx + 1} de {total_lessons}")

    # Cabeçalho do Módulo e da Lição
    st.caption("📦 MÓDULO OFICIAL")
    st.markdown(f"**{item['module_title']}**")
    st.caption(f"Parte {item['unit_index']} de {item['total_units_in_mod']} do módulo")

    st.subheader(item["unit_title"])
    st.info(f"💡 **Resumo do Módulo:**\n\n{item['module_summary']}")

    # Botões de Ação
    col_conclude, col_link = st.columns(2)
    with col_conclude:
        if st.button("✅ Concluir (+25 XP)"):
            st.session_state.xp += 25
            st.session_state.units_read += 1
            save_progress()
            st.success("+25 XP!")
            st.rerun()

    with col_link:
        st.link_button("📖 Estudar no MS Learn", item["url"])

    st.divider()

    # --- CONTROLO DE NAVEGAÇÃO SEQUENCIAL (ANTERIOR / PRÓXIMA) ---
    nav_col1, nav_col2 = st.columns(2)

    with nav_col1:
        if current_idx > 0:
            if st.button("⬅️ Lição Anterior"):
                st.session_state.lesson_index -= 1
                st.rerun()

    with nav_col2:
        if current_idx < total_lessons - 1:
            if st.button("➡️ Próxima Lição"):
                st.session_state.lesson_index += 1
                st.rerun()
