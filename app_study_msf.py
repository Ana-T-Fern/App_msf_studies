import json
import google.generativeai as genai
import streamlit as st

# Configuração da página para telemóvel
st.set_page_config(page_title="DP-700 Quest", page_icon="⚡", layout="centered")

# CSS personalizado para interface estilo "App Mobile"
st.markdown(
    """
    <style>
    .stApp { max-width: 480px; margin: 0 auto; }
    div.stButton > button { width: 100%; border-radius: 12px; height: 3em; }
    </style>
""",
    unsafe_allow_html=True,
)

# Inicializar Estados do Jogo (XP, Streak, etc.)
if "xp" not in st.session_state:
    st.session_state.xp = 0
if "streak" not in st.session_state:
    st.session_state.streak = 1
if "current_q" not in st.session_state:
    st.session_state.current_q = None
if "answered" not in st.session_state:
    st.session_state.answered = False

# Sidebar / Menu de Métricas (Gamificação)
st.sidebar.title("🏆 Teu Progresso")
st.sidebar.metric("XP Total", st.session_state.xp)
st.sidebar.metric("Dias Seguidos", f"{st.session_state.streak} 🔥")

readiness = min(100, int((st.session_state.xp / 1000) * 100))
st.sidebar.progress(readiness / 100)
st.sidebar.caption(f"Prontidão para o Exame: {readiness}%")

st.title("⚡ DP-700 Daily Quest")


# Função para gerar pergunta inédita via Gemini API

def fetch_new_question(api_key):
    try:
        clean_key = api_key.strip()
        genai.configure(api_key=clean_key)

        prompt = """
        Gera 1 pergunta inédita e de alta dificuldade para o exame Microsoft Certified: Fabric Data Engineer Associate (DP-700).
        Responde EXCLUSIVAMENTE num objeto JSON válido com a seguinte estrutura:
        {
          "question": "A pergunta contextualizada em cenário real",
          "options": ["Opção A", "Opção B", "Opção C", "Opção D"],
          "answer": "A string exata de uma das opções corretas",
          "explanation": "Explicação detalhada baseada na documentação oficial do Fabric"
        }
        """

        # Forçar o modelo 1.5-flash que tem quota gratuita ativa
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config={"response_mime_type": "application/json"},
        )

        response = model.generate_content(prompt)
        return json.loads(response.text)

    except Exception as e:
        st.error(f"Erro de Quota/API: {e}")
        return None


# Input da API Key (só pede uma vez na interface ou podes guardar em segredo)
api_key = st.text_input("Insere a tua Gemini API Key:", type="password")

if api_key:
    # Botão para gerar pergunta ou carregar a primeira
    if st.session_state.current_q is None or st.button("🔄 Próxima Pergunta"):
        with st.spinner("A IA está a criar uma pergunta nova..."):
            st.session_state.current_q = fetch_new_question(api_key)
            st.session_state.answered = False
            st.rerun()

    # Exibir Pergunta Atual
    q = st.session_state.current_q
    if q:
        st.subheader("Pergunta:")
        st.write(q["question"])

        selected = st.radio("Escolhe a tua resposta:", q["options"], key="radio_q")

        if st.button("Confirmar Resposta") and not st.session_state.answered:
            st.session_state.answered = True
            if selected == q["answer"]:
                st.balloons()
                st.success("🎉 Correto! +100 XP")
                st.session_state.xp += 100
            else:
                st.error(f"❌ Errado. A resposta correta era: **{q['answer']}**")

            st.info(f"**Explicação:** {q['explanation']}")
else:
    st.warning("Insere a tua API Key do Gemini acima para começar a jogar.")
