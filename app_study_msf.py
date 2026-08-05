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


# Função para procurar e parsear ficheiros Markdown (.md) do repositório GitHub
@st.cache_data(
    ttl=3600
)  # Atualiza automaticamente a base a cada 1 hora sem lentidão
def load_questions_from_github():
    questions = []

    # API do GitHub para listar ficheiros do repositório redonelach1/DP-700-Exam-Preparation-Content
    api_url = "https://api.github.com/repos/redonelach1/DP-700-Exam-Preparation-Content/contents"

    try:
        res = requests.get(api_url, timeout=10)
        if res.status_code == 200:
            files = res.json()
            # Filtrar apenas ficheiros .md
            md_files = [
                f
                for f in files
                if f["name"].endswith(".md")
                and f["name"].lower() != "readme.md"
            ]

            for file_info in md_files:
                raw_url = file_info["download_url"]
                content_res = requests.get(raw_url, timeout=10)
                if content_res.status_code == 200:
                    text = content_res.text

                    # Regex para identificar blocos de perguntas no Markdown
                    # Procura padrões comuns de perguntas/opções em dumps do GitHub
                    blocks = re.split(r"\n(?=Question|Question \d+|### Question|\*\*Question)", text, flags=re.IGNORECASE)

                    for block in blocks:
                        if len(block.strip()) < 20:
                            continue

                        # Tentar extrair a Pergunta, Opções e Resposta
                        lines = [
                            l.strip() for l in block.split("\n") if l.strip()
                        ]
                        if not lines:
                            continue

                        q_text = lines[0]
                        options = []
                        answer = "Ver documentação no repositório"
                        explanation = ""

                        for line in lines[1:]:
                            if re.match(r"^[-*A-D]\.\s|^[A-D]\)", line):
                                options.append(line)
                            elif "Correct Answer" in line or "Answer:" in line:
                                answer = line
                            elif "Explanation" in line or "Rationale" in line:
                                explanation += line + " "

                        # Se encontrou uma pergunta válida com pelo menos 2 opções
                        if len(options) >= 2:
                            questions.append(
                                {
                                    "question": q_text,
                                    "options": options,
                                    "answer": answer,
                                    "explanation": (
                                        explanation
                                        if explanation
                                        else "Baseado no repositório DP-700 Exam Preparation."
                                    ),
                                }
                            )
    except Exception as e:
        st.error(f"Erro ao ligar ao GitHub: {e}")

    return questions


# Inicializar Estado da Sessão
if "xp" not in st.session_state:
    st.session_state.xp = 0
if "answered_count" not in st.session_state:
    st.session_state.answered_count = 0
if "current_q" not in st.session_state:
    st.session_state.current_q = None
if "answered" not in st.session_state:
    st.session_state.answered = False

# Carregar perguntas do GitHub
with st.spinner("A carregar base de conhecimento do GitHub..."):
    questions_bank = load_questions_from_github()

# Sidebar com Métricas
st.sidebar.title("🏆 Teu Progresso")
st.sidebar.metric("XP Total", st.session_state.xp)
st.sidebar.metric("Perguntas Respondidas", st.session_state.answered_count)
st.sidebar.metric("Total Disponível no Repo", len(questions_bank))

st.title("⚡ DP-700 Auto Quest")

if not questions_bank:
    st.warning(
        "Não foi possível carregar as perguntas do GitHub neste momento. Verifica a ligação ou tenta novamente."
    )
else:
    # Sortear primeira pergunta se não houver
    if st.session_state.current_q is None or st.button("🔄 Próxima Pergunta"):
        st.session_state.current_q = random.choice(questions_bank)
        st.session_state.answered = False
        st.rerun()

    q = st.session_state.current_q
    if q:
        st.subheader("Pergunta:")
        st.markdown(q["question"])

        selected_option = st.radio(
            "Escolhe a tua resposta:", q["options"], key="q_radio"
        )

        if st.button("Confirmar Resposta"):
            if not st.session_state.answered:
                st.session_state.answered = True
                st.session_state.answered_count += 1

                # Verifica se a opção escolhida contém a letra/texto da resposta
                st.info(f"📌 **Resposta / Gabarito:** {q['answer']}")
                st.success("🎉 +100 XP por concluir a questão!")
                st.session_state.xp += 100

                st.markdown(f"💡 **Explicação:** {q['explanation']}")
            else:
                st.warning("Clica em '🔄 Próxima Pergunta' para continuar!")
