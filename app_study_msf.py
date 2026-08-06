import datetime
import requests
import streamlit as st

st.set_page_config(
    page_title="MS Fabric Micro-Learning", page_icon="⚡", layout="centered"
)

st.markdown(
    """
    <style>
    .stApp { max-width: 480px; margin: 0 auto; }
    div.stButton > button { width: 100%; border-radius: 12px; height: 3.2em; background-color: #0078D4; color: white; font-weight: bold; }
    .boss-card { background: linear-gradient(135deg, #ff4b4b, #6b0000); color: white; padding: 12px; border-radius: 10px; margin-bottom: 10px; }
    </style>
""",
    unsafe_allow_html=True,
)

# --- PERSIST PROGRESS & GAMIFICATION DATA ---
params = st.query_params

if "xp" not in st.session_state:
    st.session_state.xp = int(params.get("xp", 0))
if "streak" not in st.session_state:
    st.session_state.streak = int(params.get("streak", 0))
if "last_date" not in st.session_state:
    st.session_state.last_date = params.get("last_date", "")
if "completed_units" not in st.session_state:
    raw_completed = params.get("completed", "")
    st.session_state.completed_units = (
        set(raw_completed.split(",")) if raw_completed else set()
    )
if "lesson_index" not in st.session_state:
    st.session_state.lesson_index = int(params.get("idx", 0))


def save_progress():
    st.query_params["xp"] = str(st.session_state.xp)
    st.query_params["streak"] = str(st.session_state.streak)
    st.query_params["last_date"] = st.session_state.last_date
    st.query_params["completed"] = ",".join(
        map(str, st.session_state.completed_units)
    )
    st.query_params["idx"] = str(st.session_state.lesson_index)


def get_rank(xp):
    if xp < 100:
        return "🐣 Fabric Novice"
    if xp < 250:
        return "💾 OneLake Explorer"
    if xp < 500:
        return "🧹 Data Wrangler"
    if xp < 1000:
        return "🛠️ Pipeline Architect"
    return "🏆 Fabric Master"


def update_streak():
    today_str = str(datetime.date.today())
    if st.session_state.last_date != today_str:
        yesterday_str = str(datetime.date.today() - datetime.timedelta(days=1))
        if st.session_state.last_date == yesterday_str:
            st.session_state.streak += 1
        else:
            st.session_state.streak = 1
        st.session_state.last_date = today_str


COURSES = {
    "🌱 Get started with Microsoft Fabric": {
        "uid": "learn.wwl.get-started-fabric",
        "type": "learningPaths",
    },
    "🔥 Implement Data Engineering (DP-700)": {
        "uid": "learn.wwl.implement-data-engineering-solutions-using-microsoft-fabric",
        "type": "courses",
    },
}


@st.cache_data(ttl=86400)
def fetch_strict_course_units(course_uid, course_type):
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
                    mod_res = requests.get(
                        f"https://learn.microsoft.com/api/catalog/?uid={mod_uids_str}&locale=en-us",
                        timeout=10,
                    )
                    if mod_res.status_code == 200:
                        modules_data = mod_res.json().get("modules", [])
                        mod_map = {m.get("uid"): m for m in modules_data}
                        ordered_modules = [
                            mod_map[uid] for uid in module_uids if uid in mod_map
                        ]

                        for mod_idx, mod in enumerate(ordered_modules):
                            units_uids = mod.get("units", [])
                            for idx, unit_uid in enumerate(units_uids):
                                raw_name = unit_uid.split(".")[-1].replace(
                                    "-", " "
                                )
                                is_boss = idx == len(units_uids) - 1
                                units_list.append(
                                    {
                                        "unit_title": f"Lesson: {raw_name.capitalize()}",
                                        "module_title": f"Module {mod_idx + 1}: {mod.get('title')}",
                                        "module_summary": mod.get(
                                            "summary", ""
                                        ),
                                        "unit_index": idx + 1,
                                        "total_units_in_mod": len(units_uids),
                                        "url": mod.get("url", ""),
                                        "is_boss": is_boss,
                                    }
                                )
    except Exception as e:
        st.error(f"Error: {e}")
    return units_list


# --- HEADER & GAMIFICATION STATS ---
st.title("⚡ MS Fabric Quest")

# Streak Banner
col_s1, col_s2 = st.columns(2)
with col_s1:
    st.subheader(f"🔥 {st.session_state.streak} Day Streak")
with col_s2:
    st.subheader(f"{get_rank(st.session_state.xp)}")

selected_course_name = st.selectbox(
    "Select Quest Path:", list(COURSES.keys())
)
selected_course = COURSES[selected_course_name]
units_bank = fetch_strict_course_units(
    selected_course["uid"], selected_course["type"]
)

# Sidebar Stats
st.sidebar.title("🎮 Player Profile")
st.sidebar.metric("Current Rank", get_rank(st.session_state.xp))
st.sidebar.metric("Total XP 🌟", st.session_state.xp)
st.sidebar.metric("Daily Streak 🔥", f"{st.session_state.streak} Days")
st.sidebar.metric("Quests Cleared ⚡", len(st.session_state.completed_units))

if st.sidebar.button("🗑️ Reset Character"):
    st.session_state.xp = 0
    st.session_state.streak = 0
    st.session_state.completed_units = set()
    st.session_state.lesson_index = 0
    save_progress()
    st.rerun()

st.divider()

if units_bank:
    total_lessons = len(units_bank)
    current_idx = min(st.session_state.lesson_index, total_lessons - 1)
    item = units_bank[current_idx]

    st.progress((current_idx + 1) / total_lessons)

    is_completed = str(current_idx) in st.session_state.completed_units

    # Boss Fight Banner
    if item["is_boss"]:
        st.markdown(
            """
            <div class="boss-card">
                🚨 <b>BOSS BATTLE LESSON!</b><br>
                Complete the final lesson of this module to earn a <b>+100 XP Boss Bonus</b>!
            </div>
        """,
            unsafe_allow_html=True,
        )

    st.caption(f"📦 {item['module_title']}")
    st.subheader(item["unit_title"])
    st.info(f"💡 **Quest Briefing:**\n\n{item['module_summary']}")

    col_conclude, col_link = st.columns(2)

    with col_conclude:
        if is_completed:
            st.success("✅ Quest Cleared")
        else:
            reward_xp = 100 if item["is_boss"] else 25
            if st.button(f"⚔️ Complete Quest (+{reward_xp} XP)"):
                st.session_state.xp += reward_xp
                st.session_state.completed_units.add(str(current_idx))
                update_streak()
                save_progress()
                st.balloons() if item["is_boss"] else None
                st.rerun()

    with col_link:
        st.link_button("📖 Read Briefing", item["url"])

    st.divider()

    nav_col1, nav_col2 = st.columns(2)
    with nav_col1:
        if current_idx > 0:
            if st.button("⬅️ Prev Quest"):
                st.session_state.lesson_index -= 1
                save_progress()
                st.rerun()
    with nav_col2:
        if current_idx < total_lessons - 1:
            if st.button("Next Quest ➡️"):
                st.session_state.lesson_index += 1
                save_progress()
                st.rerun()
