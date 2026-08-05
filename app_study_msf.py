import random
import streamlit as st

# Configuração da página para telemóvel
st.set_page_config(page_title="DP-700 Quest", page_icon="⚡", layout="centered")

# CSS para interface estilo "App Mobile"
st.markdown(
    """
    <style>
    .stApp { max-width: 480px; margin: 0 auto; }
    div.stButton > button { width: 100%; border-radius: 12px; height: 3.2em; background-color: #0078D4; color: white; font-weight: bold; }
    </style>
""",
    unsafe_allow_html=True,
)

# Banco de 25 Perguntas Base (DP-700 Microsoft Fabric)
QUESTION_BANK = [
    {
        "question": "Precisas de armazenar dados semi-estruturados em formato Delta Lake no Fabric para serem alterados via Apache Spark e consultados via T-SQL pelo SQL Analytics Endpoint. Qual item deves criar?",
        "options": [
            "Data Warehouse",
            "Lakehouse",
            "Eventhouse",
            "Dataflow Gen2",
        ],
        "answer": "Lakehouse",
        "explanation": "O Lakehouse suporta nativamente escritas via Spark em tabelas Delta e expõe automaticamente um SQL Analytics Endpoint para consultas T-SQL.",
    },
    {
        "question": "Uma tabela no Lakehouse com 400 milhões de linhas está a causar lentidão nos relatórios do Power BI em modo Direct Lake devido ao fallback para DirectQuery. Que funcionalidade deves aplicar para otimizar o VertiPaq?",
        "options": [
            "SHA-256 Hashing",
            "V-Order",
            "Z-Ordering clássico",
            "Converter para CSV",
        ],
        "answer": "V-Order",
        "explanation": "O V-Order é uma otimização de escrita do Fabric que ordena e comprime ficheiros Parquet para carregamento ultra-rápido no motor VertiPaq do Direct Lake.",
    },
    {
        "question": "Precisas de extrair dados de uma base de dados SQL Server on-premises para um Fabric Data Warehouse com o mínimo de código e suporte a On-Premises Data Gateway. Qual ferramenta deves usar?",
        "options": [
            "Data Pipeline",
            "Notebook PySpark",
            "KQL Queryset",
            "Dataflow Gen1",
        ],
        "answer": "Data Pipeline",
        "explanation": "Os Data Pipelines são otimizados para movimentação de dados em grande escala e integram-se nativamente com o On-Premises Data Gateway.",
    },
    {
        "question": "Qual é a estrutura de diretórios local recomendada no PySpark do Fabric para aceder diretamente aos ficheiros na secção Files do Lakehouse anexado?",
        "options": [
            "abfss://workspace@onelake.dfs.fabric.microsoft.com/...",
            "mssparkutils.fs.head()",
            "files/path/to/file",
            "/lakehouse/default/Files/",
        ],
        "answer": "/lakehouse/default/Files/",
        "explanation": "A pasta local '/lakehouse/default/Files/' está automaticamente mapeada no ambiente do Notebook para a secção Files do Lakehouse.",
    },
    {
        "question": "Queres conceder a analistas acesso de leitura a tabelas específicas do Gold Layer no Lakehouse, sem expor os ficheiros brutos nas camadas Bronze/Silver. Qual a melhor abordagem?",
        "options": [
            "Atribuir a função de Viewer no Workspace",
            "Conceder permissões GRANT SELECT no SQL Analytics Endpoint ou OneLake Data Access Roles",
            "Dar permissão de Read All Apache Spark",
            "Criar um workspace duplicado e copiar os ficheiros",
        ],
        "answer": "Conceder permissões GRANT SELECT no SQL Analytics Endpoint ou OneLake Data Access Roles",
        "explanation": "Permite aplicar o princípio do menor privilégio, controlando o acesso ao nível da tabela/coluna sem expor a camada de ficheiros brutos.",
    },
    {
        "question": "Qual é a principal diferença entre um Data Warehouse e um Lakehouse no Microsoft Fabric no que respeita ao suporte a transações ACID e linguagem de escrita primária?",
        "options": [
            "O Warehouse suporta T-SQL e DML completo; o Lakehouse foca-se em Spark/Delta Lake e leitura via SQL Analytics Endpoint.",
            "O Lakehouse não suporta transações ACID; o Warehouse suporta.",
            "O Warehouse guarda dados em formato parquet proprietário; o Lakehouse guarda em CSV.",
            "Não existe diferença, são exatamente o mesmo motor.",
        ],
        "answer": "O Warehouse suporta T-SQL e DML completo; o Lakehouse foca-se em Spark/Delta Lake e leitura via SQL Analytics Endpoint.",
        "explanation": "O Data Warehouse permite comandos T-SQL de alteração (INSERT, UPDATE, DELETE) nativos, enquanto o Lakehouse é focado no ecossistema Spark sobre o OneLake.",
    },
    {
        "question": "Precisas de ingerir dados de streaming com baixíssima latência (segundos) vindos de sensores IoT. Qual o item do Fabric mais indicado para este cenário Real-Time Intelligence?",
        "options": [
            "Eventhouse (KQL Database)",
            "Data Warehouse",
            "Dataflow Gen2",
            "Semantic Model",
        ],
        "answer": "Eventhouse (KQL Database)",
        "explanation": "O Eventhouse e o motor KQL são desenhados especificamente para ingestão e consulta de dados temporais e de streaming em tempo real.",
    },
    {
        "question": "O que acontece quando ativas o 'Fast Copy' num Dataflow Gen2?",
        "options": [
            "Utiliza o motor do Data Pipeline no fundo para mover grandes volumes de dados sem processamento pesado em memória.",
            "Converte automaticamente o código Power Query para Python.",
            "Duplica a capacidade de CPU do workspace.",
            "Aumenta a velocidade reduzindo a precisão decimal dos dados.",
        ],
        "answer": "Utiliza o motor do Data Pipeline no fundo para mover grandes volumes de dados sem processamento pesado em memória.",
        "explanation": "O Fast Copy permite ao Dataflow Gen2 delegar o carregamento de grandes volumes para a infraestrutura de pipeline altamente escalável.",
    },
    {
        "question": "Em que situação o Power BI em modo Direct Lake faz 'fallback' automático para DirectQuery?",
        "options": [
            "Quando a consulta requer uma funcionalidade DAX não suportada ou os limites de memória da capacidade (CU) são excedidos.",
            "Sempre que o relatório tem mais de 5 utilizadores concorrentes.",
            "Quando as tabelas Delta estão otimizadas com V-Order.",
            "O Direct Lake nunca faz fallback para DirectQuery.",
        ],
        "answer": "Quando a consulta requer uma funcionalidade DAX não suportada ou os limites de memória da capacidade (CU) são excedidos.",
        "explanation": "Se o limite de memória da capacidade for atingido ou a query usar funções não mapeadas, o motor transita para DirectQuery para garantir a resposta.",
    },
    {
        "question": "Como podes reutilizar dados armazenados no Azure Data Lake Storage Gen2 (ADLS Gen2) dentro do OneLake do Fabric sem copiar os dados fisicamente?",
        "options": [
            "Criar um Shortcut (Atalho) no OneLake",
            "Usar um Dataflow Gen2 em modo de sincronização",
            "Exportar os dados via AzCopy",
            "Criar uma cópia espelho (Mirroring)",
        ],
        "answer": "Criar um Shortcut (Atalho) no OneLake",
        "explanation": "Os Shortcuts permitem mapear dados externos (ADLS Gen2, Amazon S3, Dataverse) no OneLake sem mover nem duplicar dados.",
    },
    {
        "question": "Num Notebook PySpark no Fabric, qual a biblioteca recomendada para gerir credenciais e segredos armazenados num Azure Key Vault?",
        "options": [
            "mssparkutils.credentials",
            "azure.identity.DefaultAzureCredential",
            "os.environ['SECRET']",
            "spark.conf.get('keyvault')",
        ],
        "answer": "mssparkutils.credentials",
        "explanation": "A utilidade `mssparkutils.credentials.getSecret()` é a forma nativa e segura de recuperar segredos de um Key Vault no Fabric.",
    },
    {
        "question": "O que é o conceito de 'Medallion Architecture' recomendado pela Microsoft para desenhar Lakehouses no Fabric?",
        "options": [
            "Estrutura em camadas: Bronze (Dados brutos), Silver (Dados limpos/validados) e Gold (Dados agregados para negócio).",
            "Divisão de dados por categorias de preço: Grátis, Standard e Premium.",
            "Um modelo de segurança baseado em medalhas de acesso.",
            "A separação geográfica de datacenters no OneLake.",
        ],
        "answer": "Estrutura em camadas: Bronze (Dados brutos), Silver (Dados limpos/validados) e Gold (Dados agregados para negócio).",
        "explanation": "A arquitetura Medallion organiza os dados incrementalmente para garantir qualidade, rastreabilidade e performance.",
    },
    {
        "question": "Qual das seguintes opções descreve corretamente o funcionalidade de 'Mirroring' (Espelhamento) no Fabric?",
        "options": [
            "Replicação contínua e em tempo real de bases de dados externas (ex: Snowflake, Cosmos DB, Azure SQL) para tabelas Delta no OneLake sem ETL complexo.",
            "Criar uma cópia de segurança diária do workspace.",
            "Espelhar o ecrã do Power BI para outros utilizadores.",
            "Sincronizar dois modelos semânticos entre ambientes de Dev e Prod.",
        ],
        "answer": "Replicação contínua e em tempo real de bases de dados externas (ex: Snowflake, Cosmos DB, Azure SQL) para tabelas Delta no OneLake sem ETL complexo.",
        "explanation": "O Mirroring lê o log de alterações das fontes e replica os dados continuamente no formato Delta Parquet no OneLake.",
    },
    {
        "question": "Se precisares de orquestrar a execução sequencial de um Dataflow Gen2, seguido de dois Notebooks em paralelo e um envio de e-mail no final, que item do Fabric deves utilizar?",
        "options": [
            "Data Pipeline",
            "Environment",
            "KQL Queryset",
            "Power BI App",
        ],
        "answer": "Data Pipeline",
        "explanation": "Os Data Pipelines são o motor de orquestração no Fabric, permitindo gerir fluxos de trabalho, dependências, paralelismo e notificações.",
    },
    {
        "question": "O que é um 'Environment' (Ambiente) num workspace de Engenharia de Dados no Fabric?",
        "options": [
            "Um item reutilizável que define as bibliotecas Python/R, configurações Spark e computação para os Notebooks e Spark Jobs.",
            "A cor do tema da interface do utilizador.",
            "A região do Azure onde os dados estão armazenados.",
            "Uma máquina virtual isolada para cada utilizador.",
        ],
        "answer": "Um item reutilizável que define as bibliotecas Python/R, configurações Spark e computação para os Notebooks e Spark Jobs.",
        "explanation": "Os Environments permitem padronizar bibliotecas (custom de pypi ou whl) e definições do Spark para todo o grupo de trabalho.",
    },
    {
        "question": "Como podes otimizar o desempenho de uma tabela Delta no Lakehouse que sofreu milhares de operações de UPDATE e DELETE recentes?",
        "options": [
            "Executar os comandos OPTIMIZE e VACUUM na tabela Delta via Spark.",
            "Reiniciar o workspace do Fabric.",
            "Converter a tabela para JSON e voltar a importar.",
            "Apagar os logs do OneLake manualmente.",
        ],
        "answer": "Executar os comandos OPTIMIZE e VACUUM na tabela Delta via Spark.",
        "explanation": "O OPTIMIZE compacta ficheiros pequenos e o VACUUM remove ficheiros antigos não utilizados retidos pelos logs de Time Travel.",
    },
    {
        "question": "Qual é a unidade de medida utilizada pela Microsoft para cobrar a capacidade e o consumo no Microsoft Fabric?",
        "options": [
            "Capacity Units (CUs)",
            "Virtual Cores (vCores)",
            "Database Transaction Units (DTUs)",
            "Gigabytes por Hora (GB/h)",
        ],
        "answer": "Capacity Units (CUs)",
        "explanation": "Todas as cargas de trabalho no Fabric (Spark, SQL, Dataflows, Power BI) consomem uma reserva unificada de Capacity Units (CUs).",
    },
    {
        "question": "Precisas de implementar Row-Level Security (RLS) para restringir o acesso a linhas específicas de dados de vendas consoante a região do utilizador. Onde podes configurar isto?",
        "options": [
            "No SQL Analytics Endpoint / Data Warehouse usando T-SQL ou no Semantic Model do Power BI.",
            "Apenas no ficheiro Parquet no OneLake.",
            "No pipeline de cópia de dados.",
            "O Fabric não suporta Row-Level Security.",
        ],
        "answer": "No SQL Analytics Endpoint / Data Warehouse usando T-SQL ou no Semantic Model do Power BI.",
        "explanation": "O RLS pode ser aplicado nativamente no motor SQL (T-SQL) ou na camada do Modelo Semântico usando DAX.",
    },
    {
        "question": "O que permite a funcionalidade 'Time Travel' nas tabelas Delta Lake do Fabric?",
        "options": [
            "Consultar versões anteriores da tabela usando registos de histórico mantidos nos Delta Logs.",
            "Agendar pipelines para correrem no futuro.",
            "Restaurar o workspace para o estado de há 30 dias.",
            "Prever dados futuros utilizando inteligência artificial.",
        ],
        "answer": "Consultar versões anteriores da tabela usando registos de histórico mantidos nos Delta Logs.",
        "explanation": "O Time Travel permite fazer queries a dados exatamente como estavam num momento específico do passado usando carimbos de data/hora ou números de versão.",
    },
    {
        "question": "Para garantir que o código dos teus Notebooks e Pipelines está versionado e sincronizado com um repositório empresarial, qual a integração nativa do Fabric?",
        "options": [
            "Integração com Git (Azure DevOps / GitHub)",
            "Exportação manual de ficheiros .zip",
            "OneDrive Sync",
            "Azure Blob Storage Backup",
        ],
        "answer": "Integração com Git (Azure DevOps / GitHub)",
        "explanation": "O Fabric possui integração nativa com Git para controlo de versões, ALM e sincronização de itens do workspace.",
    },
    {
        "question": "Qual é o comportamento por defeito do OneLake em relação ao armazenamento de dados nos workspaces de uma organização?",
        "options": [
            "É um único SaaS Data Lake unificado e lógico para toda a organização, eliminando silos de dados.",
            "Cada workspace requer uma conta de armazenamento Azure isolada e configurada manualmente.",
            "Guarda os dados apenas em memória temporária RAM.",
            "Exige o uso de SQL Server Management Studio para criar tabelas.",
        ],
        "answer": "É um único SaaS Data Lake unificado e lógico para toda a organização, eliminando silos de dados.",
        "explanation": "O OneLake é apelidado de 'OneDrive para dados': um único repositório lógico central para toda a empresa.",
    },
    {
        "question": "O que é o 'Deployment Pipeline' (Pipelines de Implantação) no Fabric?",
        "options": [
            "Uma ferramenta do ciclo de vida do desenvolvimento (ALM) para mover conteúdos entre ambientes de Desenvolvimento, Teste e Produção.",
            "Um pipeline para mover dados entre diferentes clouds.",
            "Um script PySpark para instalar pacotes.",
            "Um assistente de instalação do Power BI Desktop.",
        ],
        "answer": "Uma ferramenta do ciclo de vida do desenvolvimento (ALM) para mover conteúdos entre ambientes de Desenvolvimento, Teste e Produção.",
        "explanation": "Permite gerir a transição de relatórios, modelos, lakehouses e pipelines através dos estágios de dev, test e prod.",
    },
    {
        "question": "Qual é a melhor linguagem para fazer consultas analíticas e exploração de dados no KQL Queryset dentro do Real-Time Intelligence?",
        "options": [
            "KQL (Kusto Query Language)",
            "PL/SQL",
            "DAX",
            "VBScript",
        ],
        "answer": "KQL (Kusto Query Language)",
        "explanation": "O KQL é a linguagem otimizada para pesquisa e análise rápida em grandes volumes de dados de logs, métricas e eventos em tempo real.",
    },
    {
        "question": "Num Data Warehouse do Fabric, qual é o método recomendado para carregar grandes volumes de dados a partir de ficheiros Parquet localizados no OneLake com máxima performance T-SQL?",
        "options": [
            "Comando COPY INTO",
            "INSERT INTO linha a linha",
            "Power Query Gen1",
            "Exportar para Excel e importar",
        ],
        "answer": "Comando COPY INTO",
        "explanation": "O comando `COPY INTO` do T-SQL é altamente paralelizado e otimizado para ingestão em massa no Fabric Data Warehouse.",
    },
    {
        "question": "O que distingue as 'Managed Tables' (Tabelas Geridas) das 'External Tables' (Tabelas Externas) num Lakehouse?",
        "options": [
            "As Managed Tables têm os ficheiros subjacentes geridos e guardados na pasta 'Tables' do Lakehouse; as External Tables apontam para localizações de ficheiros personalizadas.",
            "As External Tables são pagas e as Managed são gratuitas.",
            "As Managed Tables só aceitam ficheiros CSV.",
            "Não há qualquer diferença.",
        ],
        "answer": "As Managed Tables têm os ficheiros subjacentes geridos e guardados na pasta 'Tables' do Lakehouse; as External Tables apontam para localizações de ficheiros personalizadas.",
        "explanation": "Nas tabelas geridas (Tables), o Fabric controla o esquema e os ficheiros Delta. Nas externas, a tabela apenas aponta para caminhos de ficheiros específicos.",
    },
]

# Inicializar Estado da Sessão
if "xp" not in st.session_state:
    st.session_state.xp = 0
if "answered_questions" not in st.session_state:
    st.session_state.answered_questions = []
if "current_q_idx" not in st.session_state:
    st.session_state.current_q_idx = random.randint(0, len(QUESTION_BANK) - 1)
if "answered" not in st.session_state:
    st.session_state.answered = False

# Sidebar com Progresso
st.sidebar.title("🏆 O Teu Progresso")
st.sidebar.metric("XP Accumulado", st.session_state.xp)
st.sidebar.metric(
    "Perguntas Concluídas",
    f"{len(st.session_state.answered_questions)} / {len(QUESTION_BANK)}",
)

readiness = min(100, int((len(st.session_state.answered_questions) / 25) * 100))
st.sidebar.progress(readiness / 100)
st.sidebar.caption(f"Prontidão para o Exame DP-700: {readiness}%")

st.title("⚡ DP-700 Prep Quest")

# Botão para proxima pergunta
if st.button("🔄 Sortear Nova Pergunta"):
    st.session_state.current_q_idx = random.randint(0, len(QUESTION_BANK) - 1)
    st.session_state.answered = False
    st.rerun()

# Obter Pergunta Atual
q = QUESTION_BANK[st.session_state.current_q_idx]

st.subheader(f"Pergunta #{st.session_state.current_q_idx + 1}:")
st.write(q["question"])

selected_option = st.radio(
    "Escolhe a tua resposta:",
    q["options"],
    key=f"radio_{st.session_state.current_q_idx}",
)

if st.button("Confirmar Resposta"):
    if not st.session_state.answered:
        st.session_state.answered = True

        if st.session_state.current_q_idx not in st.session_state.answered_questions:
            st.session_state.answered_questions.append(
                st.session_state.current_q_idx
            )

        if selected_option == q["answer"]:
            st.balloons()
            st.success("🎉 Correto! +100 XP")
            st.session_state.xp += 100
        else:
            st.error(f"❌ Errado. A resposta correta é: **{q['answer']}**")

        st.info(f"💡 **Explicação:** {q['explanation']}")
    else:
        st.warning(
            "Já respondeste a esta pergunta. Clica em '🔄 Sortear Nova Pergunta' para continuar!"
        )
        
