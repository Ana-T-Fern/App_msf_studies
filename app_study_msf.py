import requests
import streamlit as st

# Mobile layout configuration
st.set_page_config(
    page_title="MS Fabric Micro-Learning", page_icon="⚡", layout="centered"
)

st.markdown(
    """
    <style>
    .stApp { max-width: 480px; margin: 0 auto; }
    div.stButton > button { width: 100%; border-radius: 12px; height: 3.2em; background-color: #0078D4; color: white; font-weight: bold; }
    .badge-completed { background-color: #107C41; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 0.85em; }
    </style>
""",
    unsafe_allow_html=True,
)

# --- PERSIST PROGRESS IN BROWSER URL ---
params = st.query_params

if "xp" not in st.session_state:
    st.session_state.xp = int(params.get("xp", 0))
if "completed_units" not in st.session_state:
    # Save completed lesson indexes as a set of string integers
    raw_completed = params.get("completed", "")
    st.session_state.completed_units = (
        set(raw_completed.split(",")) if raw_completed else set()
    )
if "lesson_index" not in st.session_state:
    st.session_state.lesson_index = int(params.get("idx", 0))


def save_progress():
    st.query_params["xp"] = str(st.session_state.xp)
    st.query_params["completed"] = ",".join(
        map(str, st.session_state.completed_units)
    )
    st.query_params["idx"] = str(st.session_state.lesson_index)


# --- SPECIFIC OFFICIAL COURSES (EN-US) ---
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


# --- FETCH UNITS & MODULES IN EN-US ---
@st.cache_data(ttl=86400)
def fetch_strict_course_units(course_uid, course_type):
    """Fetch strict modules and lessons in en-us preserving order."""
    units_list = []

    url = f"https://learn.microsoft.com/api/catalog/?uid={course_uid}&locale=en-us"
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
                    mod_url = f"https://learn.microsoft.com/api/catalog/?uid={mod_uids_str}&locale=en-us"
                    mod_res = requests.get(mod_url, timeout=10)

                    if mod_res.status_code == 200:
                        modules_data = mod_res.json().get("modules", [])

                        mod_map = {m.get("uid"): m for m in modules_data}
                        ordered_modules = [
                            mod_map[uid] for uid in module_uids if uid in mod_map
                        ]

                        for mod_idx, mod in enumerate(ordered_modules):
                            mod_title = mod.get("title", "Module")
                            mod_summary = mod.get(
                                "summary", "No summary available."
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
                                        "unit_title": f"Lesson: {unit_name}",
                                        "module_title": f"Module {mod_idx + 1}: {mod_title}",
                                        "module_summary": mod_summary,
                                        "unit_index": idx + 1,
                                        "total_units_in_mod": len(units_uids),
                                        "url": mod_url_link,
                                    }
                                )
    except Exception as e:
        st.error(f"Error fetching data from MS Learn API: {e}")

    return units_list


# --- UI HEADER ---
st.title("⚡ MS Fabric Hub")

selected_course_name = st.selectbox(
    "Choose Official Path:", list(COURSES.keys())
)

# Reset or maintain index when switching courses
if "last_selected_course" not in st.session_state or st.session_state.last_selected_course != selected_course_name:
    st.session_state.lesson_index = 0
    st.session_state.last_selected_course = selected_course_name

selected_course = COURSES[selected_course_name]
units_bank = fetch_strict_course_units(
    selected_course["uid"], selected_course["type"]
)

# --- SIDEBAR PROGRESS TRACKER ---
st.sidebar.title("🏆 Your Progress")
st.sidebar.metric("Total XP 🌟", st.session_state.xp)
st.sidebar.metric(
    "Lessons Completed ⚡", len(st.session_state.completed_units)
)
st.sidebar.metric("Total Course Lessons", len(units_bank))

if st.sidebar.button("🗑️ Reset All Progress"):
    st.session_state.xp = 0
    st.session_state.completed_units = set()
    st.session_state.lesson_index = 0
    save_progress()
    st.rerun()

st.divider()

# --- CONTENT DISPLAY & TRACKING ---
if not units_bank:
    st.warning("Loading official course lessons...")
else:
    total_lessons = len(units_bank)
    current_idx = min(st.session_state.lesson_index, total_lessons - 1)
    item = units_bank[current_idx]

    # Progress Bar & Current Position
    st.progress((current_idx + 1) / total_lessons)
    
    is_completed = str(current_idx) in st.session_state.completed_units
    
    status_tag = "✅ COMPLETED" if is_completed else "📖 IN PROGRESS"
    st.caption(
        f"📍 **Course Progress:** Lesson {current_idx + 1} of {total_lessons} | **Status:** {status_tag}"
    )

    # Module & Lesson Hierarchy
    st.caption("📦 OFFICIAL MODULE")
    st.markdown(f"**{item['module_title']}**")
    st.caption(
        f"Part {item['unit_index']} of {item['total_units_in_mod']} in this module"
    )

    st.subheader(item["unit_title"])
    st.info(f"💡 **Module Overview:**\n\n{item['module_summary']}")

    # Actions
    col_conclude, col_link = st.columns(2)

    with col_conclude:
        if is_completed:
            st.success("✅ Already Completed")
        else:
            if st.button("Mark as Complete (+25 XP)"):
                st.session_state.xp += 25
                st.session_state.completed_units.add(str(current_idx))
                save_progress()
                st.rerun()

    with col_link:
        st.link_button("📖 Study on MS Learn", item["url"])

    st.divider()

    # --- SEQUENTIAL NAVIGATION ---
    nav_col1, nav_col2 = st.columns(2)

    with nav_col1:
        if current_idx > 0:
            if st.button("⬅️ Previous Lesson"):
                st.session_state.lesson_index -= 1
                save_progress()
                st.rerun()

    with nav_col2:
        if current_idx < total_lessons - 1:
            if st.button("Next Lesson ➡️"):
                st.session_state.lesson_index += 1
                save_progress()
                st.rerun()
