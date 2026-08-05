import json
import random
import requests
import streamlit as st

# Configuração da página para telemóvel
st.set_page_config(page_title="DP-700 Quest", page_icon="⚡", layout="centered")

# CSS para interface estilo "App Mobile"
st.markdown(
    """
    <style>
    .stApp { max-width: 480px; margin: 0 auto; }
    div.stButton > button { width: 100%; border-radius: 12px; height: 3em; background-color: #0078D4; color: white; font-weight: bold; }
    </style>
""",
    unsafe_allow_html=True,
)

# Inicializar Estado do Jogo (Gamificação)
if "xp" not in st.session_state:
    st.session_state.xp = 0
if "streak" not in st.session_state:
    st.session_state.streak = 1
if "current_q" not in st.session_state:
    st.session_state.current_q = None
if "answered" not in st.session_state:
    st.session_state.answered = False

# Sidebar / Menu de Métricas
st.sidebar.title("🏆 Teu Progresso")
st.sidebar.metric("XP Total", st.session_state.xp)
st.sidebar.metric("Dias Seguidos", f"{st.session_state.streak} 🔥")

readiness = min(100, int((st.session_state.xp / 1000) * 100))
st.sidebar.progress(readiness / 100)
st.sidebar.caption(f"Prontidão para o Exame: {readiness}%")

st.title("⚡ DP-700 IA Quest")


def fetch_new_question_openrouter(api_key):
    try:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key.strip()}",
            "Content-Type": "application/json",
        }

        prompt = """
        Gera 1 pergunta inédita e de alta dificuldade em Português para o exame Microsoft Certified: Fabric Data Engineer Associate (DP-700).
        Responde EXCLUSIVAMENTE com um objeto JSON válido no formato:
        {
          "question": "Texto da pergunta em cenário real",
          "options": ["Opção A", "Opção B", "Opção C", "Opção D"],
          "answer": "Texto exato de uma das opções acima que está correta",
          "explanation": "Explicação detalhada baseada na documentação do Microsoft Fabric"
        }
        Não inclua marcadores de código como ```json ou texto adicional fora do JSON.
        """

        # Lista de modelos gratuitos ativos e de alta disponibilidade no OpenRouter
        free_models = [
            "deepseek/deepseek-r1:free",
            "qwen/qwen-2.5-72b-instruct:free",
            "meta-llama/llama-3.1-8b-instruct:free",
        ]

        for model_name in free_models:
            payload = {
                "model": model_name,
                "messages": [
                    {
                        "role": "system",
                        "content": "És um especialista no exame Microsoft Fabric DP-700. Respondes apenas em formato JSON estrito.",
                    },
                    {"role": "user", "content": prompt},
                ],
            }

            response = requests.post(
                url, headers=headers, json=payload, timeout=20
            )
            res_data = response.json()

            if "choices" in res_data and len(res_data["choices"]) > 0:
                content = res_data["choices"][0]["message"]["content"]

                # Limpar possíveis blocos markdown ```json ... ```
                content_clean = re.sub(
                    r"```json\s*|\s*```", "", content
                ).strip()

                # Tentar extrair o JSON do texto se houver caracteres extras
                json_match = re.search(r"\{.*\}", content_clean, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group(0))

        st.error(
            "Nenhum dos modelos gratuitos respondeu no momento. Tenta novamente em alguns segundos."
        )
        return None

    except Exception as e:
        st.error(f"Erro ao processar pergunta: {e}")
        return None

# Input da API Key do OpenRouter
api_key = st.text_input(
    "Insere a tua OpenRouter API Key (sk-or-v1-...):", type="password"
)

if api_key:
    if st.session_state.current_q is None or st.button("🔄 Próxima Pergunta"):
        with st.spinner("A IA está a gerar uma nova pergunta..."):
            st.session_state.current_q = fetch_new_question_openrouter(api_key)
            st.session_state.answered = False
            st.rerun()

    q = st.session_state.current_q
    if q:
        st.subheader("Pergunta:")
        st.write(q["question"])

        selected = st.radio("Escolhe a tua resposta:", q["options"], key="q_radio")

        if st.button("Confirmar Resposta"):
            if not st.session_state.answered:
                st.session_state.answered = True
                if selected == q["answer"]:
                    st.balloons()
                    st.success("🎉 Correto! +100 XP")
                    st.session_state.xp += 100
                else:
                    st.error(f"❌ Errado. A resposta correta era: **{q['answer']}**")

                st.info(f"**Explicação:** {q['explanation']}")
            else:
                st.warning("Clica em '🔄 Próxima Pergunta' para continuar!")
else:
    st.info(
        "Insere a tua chave do OpenRouter acima para gerar perguntas infinitas!"
    )
