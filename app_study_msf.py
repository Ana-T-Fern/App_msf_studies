import random
import re
import requests
import streamlit as st

# Configuração da página para telemóvel
st.set_page_config(page_title="DP-700 Quest", page_icon="⚡", layout="centered")

# CSS Estilo App Mobile
st.markdown(
    """
    <style>
    .stApp { max-width: 480px; margin: 0 auto; }
    div.stButton > button { width: 100%; border-radius: 12px; height: 3.2em; background-color: #0078D4; color: white; font-weight: bold; }
    </style>
""",
    unsafe_allow_html=True,
)

# Perguntas de Fallback (Garante que a app NUNCA fica vazia)
FALLBACK_QUESTIONS = [
    {
        "question": "Precisas de armazenar dados em formato Delta Lake no Fabric para serem alterados via Spark e consultados via T-SQL pelo SQL Analytics Endpoint. Qual item deves criar?",
        "options": ["Data Warehouse", "Lakehouse", "Eventhouse", "Dataflow Gen2"],
        "answer": "Lakehouse",
        "explanation": "O Lakehouse suporta escritas em Delta Lake e expõe automaticamente um SQL Analytics Endpoint."
    },
    {
        "question": "Qual funcionalidade do Fabric otimiza a ordenação e compressão de ficheiros Parquet para carregamento ultra-rápido no Direct Lake do Power BI?",
        "options": ["SHA-256", "V-Order", "Z-Ordering", "CSV Convert"],
        "answer": "V-Order",
        "explanation": "O V-Order é uma otimização de escrita exclusiva do Fabric para o motor VertiPaq."
    },
    {
        "question": "Como podes reutilizar dados no Azure Data Lake Storage Gen2 (ADLS Gen2) dentro do OneLake sem copiar os dados fisicamente?",
        "options": ["Criar um Shortcut (Atalho)", "Usar Dataflow Gen2", "AzCopy", "Mirroring"],
        "answer": "Criar um Shortcut (Atalho)",
        "explanation": "Os Shortcuts permitem mapear armazenamento externo no OneLake sem mover dados."
    }
]

@st.cache_data(ttl=1800)
def load_questions_from_github():
    questions = []
    
    # URLs diretas dos ficheiros de estudo do repositório redonelach1
    urls = [
        "https://raw.githubusercontent.com/redonelach1/DP-700-Exam-Preparation-Content/main/README.md",
        "https://raw.githubusercontent.com/redonelach1/DP-700-Exam-Preparation-Content/main/DP-700-Study-Guide.md"
    ]
    
    for url in urls:
        try:
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                text = res.text
                
                # Procura blocos que contenham perguntas no Markdown
                blocks = re.split(r'\n(?=Question|#|###|\*\*Question)', text)
                for block in blocks:
                    lines = [l.strip() for l in block.split('\n') if l.strip()]
                    if len(lines) >= 3:
                        opts = [l for l in lines if re.match(r'^[-*A-D][\.\)]\s', l)]
                        if len(opts) >= 2:
                            questions.append({
                                "question": lines[0].replace("#", "").strip(),
                                "options": opts,
                                "answer": "Consulta a resposta oficial no repositório GitHub.",
                                "explanation": "Extraído diretamente do repositório DP-700 Exam Preparation."
                            })
        except Exception:
            continue
            
    # Se não conseguir extrair do GitHub, devolve as perguntas de reserva
    return questions if len(questions) > 0 else FALLBACK_QUESTIONS

# Inicializar Estado da Sessão
if "xp" not in st.session_state:
    st.session_state.xp = 0
if "answered_count" not in st.session_state:
    st.session_state.answered_count = 0
if "current_q" not in st.session_state:
    st.session_state.current_q = None
if "answered" not in st.session_state:
    st.session_state.answered = False

# Carregar perguntas
questions_bank = load_questions_from_github()

# Sidebar
st.sidebar.title("🏆 Teu Progresso")
st.sidebar.metric("XP Total", st.session_state.xp)
st.sidebar.metric("Respondidas", st.session_state.answered_count)
st.sidebar.metric("Perguntas na Base", len(questions_bank))

st.title("⚡ DP-700 Auto Quest")

# Sortear pergunta
if st.session_state.current_q is None or st.button("🔄 Próxima Pergunta"):
    st.session_state.current_q = random.choice(questions_bank)
    st.session_state.answered = False
    st.rerun()

q = st.session_state.current_q
if q:
    st.subheader("Pergunta:")
    st.markdown(q["question"])

    selected_option = st.radio("Escolhe a tua resposta:", q["options"], key="q_radio")

    if st.button("Confirmar Resposta"):
        if not st.session_state.answered:
            st.session_state.answered = True
            st.session_state.answered_count += 1
            st.success("🎉 +100 XP registados!")
            st.session_state.xp += 100
            st.info(f"💡 **Informação:** {q['explanation']}")
        else:
            st.warning("Clica em '🔄 Próxima Pergunta' para continuar!")
