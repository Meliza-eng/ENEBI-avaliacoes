import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
import io
import base64
import re

try:
    import qrcode
except ImportError:
    qrcode = None

try:
    import gspread
    from google.oauth2.service_account import Credentials
except ImportError:
    gspread = None
    Credentials = None


# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(
    page_title="Avaliação Oral — ENEBI 26",
    page_icon="📝",
    layout="centered",
    initial_sidebar_state="collapsed",
)

BASE = Path(__file__).parent
DATA = BASE / "data"
ASSETS = BASE / "assets"

TRABALHOS = DATA / "trabalhos.csv"
AVALIACOES_LOCAL = DATA / "avaliacoes.csv"
LOGO = ASSETS / "logo.png"

AZUL = "#0B4F72"
VERDE = "#377C7D"
AQUA = "#92CCC8"
FUNDO = "#F7FAFA"
TEXTO = "#263238"
CINZA = "#60757D"


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
<style>

#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }

.stApp {
    background: #F7FAFA;
}

[data-testid="stAppViewContainer"] {
    background: #F7FAFA !important;
}

[data-testid="stHeader"] {
    background: #F7FAFA !important;
}

[data-testid="stSidebar"] {
    background: #F7FAFA !important;
}

html, body {
    background: #F7FAFA !important;
}

.block-container {
    max-width: 700px;
    padding: 1rem 1rem 5rem;
}

.hero {
    background: linear-gradient(135deg, #0B4F72 0%, #377C7D 100%);
    color: white;
    padding: 22px 20px;
    border-radius: 22px;
    margin-bottom: 18px;
    box-shadow: 0 8px 24px rgba(11,79,114,.16);
}

.logo-container {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: white;
    padding: 7px 15px;
    border-radius: 12px;
    margin-bottom: 12px;
}

.logo-container img {
    display: block;
    width: 310px;
    max-width: 78%;
    height: auto;
    object-fit: contain;
}

.hero-small {
    opacity: .86;
    font-size: .78rem;
    margin-bottom: 5px;
    letter-spacing: .04em;
}

.hero-title {
    font-size: 1.55rem;
    font-weight: 750;
    line-height: 1.2;
}

.hero-description {
    margin-top: 8px;
    opacity: .92;
    font-size: .9rem;
    line-height: 1.4;
}

.section-title {
    font-size: 1.05rem;
    font-weight: 750;
    color: #0B4F72;
    margin: 20px 0 9px;
}

.work-card {
    background: white;
    border-radius: 18px;
    border: 1px solid #DCE7E7;
    padding: 16px;
    margin: 8px 0 16px;
}

.work-code {
    color: #377C7D;
    font-weight: 750;
    font-size: .8rem;
}

.work-title {
    color: #263238;
    font-size: 1rem;
    font-weight: 650;
    line-height: 1.4;
    margin-top: 5px;
}

.work-authors {
    color: #60757D;
    font-size: .82rem;
    line-height: 1.4;
    margin-top: 7px;
}

.work-meta {
    color: #60757D;
    font-size: .8rem;
    line-height: 1.5;
    margin-top: 10px;
}

.criterion-card {
    background: white;
    border-radius: 16px;
    border: 1px solid #DCE7E7;
    border-left: 4px solid #92CCC8;
    padding: 14px 15px 10px;
    margin: 13px 0 4px;
}

.criterion-title {
    color: #0B4F72;
    font-weight: 700;
    font-size: .93rem;
    line-height: 1.35;
}

.criterion-description {
    color: #60757D;
    font-size: .78rem;
    line-height: 1.45;
    margin-top: 5px;
}

.admin-lock {
    background: #F0F8F7;
    border: 1px solid #92CCC8;
    border-radius: 14px;
    padding: 12px 14px;
    color: #0B4F72;
    font-size: .82rem;
    margin-bottom: 12px;
}

.metric-card {
    background: white;
    border: 1px solid #DCE7E7;
    border-radius: 16px;
    padding: 14px;
    text-align: center;
}

.metric-number {
    color: #0B4F72;
    font-size: 1.45rem;
    font-weight: 750;
}

.metric-label {
    color: #60757D;
    font-size: .76rem;
    margin-top: 2px;
}

.success-card {
    background: white;
    border: 1px solid #92CCC8;
    border-radius: 20px;
    padding: 30px 20px;
    text-align: center;
    margin-top: 20px;
}

.success-icon {
    color: #377C7D;
    font-size: 2.5rem;
}

.success-title {
    color: #0B4F72;
    font-size: 1.4rem;
    font-weight: 750;
    margin-top: 8px;
}

.success-description {
    color: #60757D;
    font-size: .86rem;
    line-height: 1.5;
    margin-top: 8px;
}

.qr-card {
    background: white;
    border: 1px solid #92CCC8;
    border-radius: 20px;
    padding: 20px;
    text-align: center;
    margin-top: 12px;
}

div.stButton > button,
div[data-testid="stFormSubmitButton"] > button {
    border-radius: 13px;
    min-height: 48px;
    font-weight: 700;
}

div.stButton > button[kind="primary"],
div[data-testid="stFormSubmitButton"] > button {
    background: #0B4F72 !important;
    border-color: #0B4F72 !important;
    color: white !important;
}

div.stButton > button[kind="primary"]:hover,
div[data-testid="stFormSubmitButton"] > button:hover {
    background: #377C7D !important;
    border-color: #377C7D !important;
}

/* ============================================================
   CAMPOS INTERATIVOS — TEMA CLARO
   ============================================================ */

div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div,
div[data-baseweb="textarea"] > div {
    background-color: #FFFFFF !important;
    color: #263238 !important;
    border-color: #DCE7E7 !important;
}

div[data-baseweb="input"] input,
div[data-baseweb="textarea"] textarea {
    background-color: #FFFFFF !important;
    color: #263238 !important;
    -webkit-text-fill-color: #263238 !important;
    caret-color: #263238 !important;
}

div[data-baseweb="select"] * {
    color: #263238 !important;
}

div[data-baseweb="select"] > div > div {
    background-color: #FFFFFF !important;
    color: #263238 !important;
}

div[data-baseweb="select"] input {
    color: #263238 !important;
    -webkit-text-fill-color: #263238 !important;
}

div[data-baseweb="input"] > div,
div[data-baseweb="textarea"] > div {
    border-radius: 12px;
}
/* ============================================================
   RADIO BUTTONS — números e opções visíveis
   ============================================================ */

div[data-testid="stRadio"] label {
    color: #263238 !important;
}

div[data-testid="stRadio"] label p {
    color: #263238 !important;
    -webkit-text-fill-color: #263238 !important;
}

div[data-testid="stRadio"] [role="radiogroup"] label {
    color: #263238 !important;
}

div[data-testid="stRadio"] [role="radiogroup"] label span {
    color: #263238 !important;
    -webkit-text-fill-color: #263238 !important;
}

</style>
""",
    unsafe_allow_html=True
)
# ============================================================
# HTML SEGURO PARA O VISUAL
# ============================================================

def render_html(html):
    lines = html.splitlines()
    clean = [line.lstrip() for line in lines]
    st.markdown("\n".join(clean).strip(), unsafe_allow_html=True)


def logo_html():
    if not LOGO.exists():
        return ""
    image = base64.b64encode(LOGO.read_bytes()).decode("utf-8")
    return f"""
    <div class="logo-container">
        <img src="data:image/png;base64,{image}">
    </div>
    """


# ============================================================
# DADOS LOCAIS
# ============================================================

def carregar_trabalhos():
    if not TRABALHOS.exists():
        return pd.DataFrame()

    return pd.read_csv(
        TRABALHOS,
        dtype=str,
        encoding="utf-8-sig"
    ).fillna("")


def carregar_avaliacoes_local():
    if not AVALIACOES_LOCAL.exists():
        return pd.DataFrame()

    return pd.read_csv(
        AVALIACOES_LOCAL,
        dtype=str,
        encoding="utf-8-sig"
    ).fillna("")


# ============================================================
# GOOGLE SHEETS
# ============================================================

HEADERS = [
    "timestamp",
    "avaliador",
    "codigo",
    "titulo",
    "data",
    "dia",
    "sala",
    "sessao",
    "horario",
    "relevancia",
    "originalidade",
    "objetivos",
    "metodologia",
    "resultados",
    "conclusoes",
    "clareza",
    "dominio",
    "material_visual",
    "sintese_tempo",
    "respostas",
    "respeitou_15_min",
    "indicacao_premiacao",
    "comentarios",
]


def google_sheets_configured():
    """Verifica cada etapa da configuração sem expor nenhum segredo."""
    if gspread is None:
        st.session_state["sheets_error"] = (
            "Etapa 1/7 — gspread não está instalado no ambiente. "
            "Verifique o requirements.txt e reinicie o aplicativo."
        )
        return False

    if Credentials is None:
        st.session_state["sheets_error"] = (
            "Etapa 2/7 — google-auth não está instalado no ambiente. "
            "Verifique o requirements.txt e reinicie o aplicativo."
        )
        return False

    try:
        secrets = st.secrets
    except Exception as error:
        st.session_state["sheets_error"] = (
            f"Etapa 3/7 — o Streamlit não conseguiu carregar os Secrets: "
            f"{type(error).__name__}: {error}"
        )
        return False

    if "SPREADSHEET_ID" not in secrets:
        st.session_state["sheets_error"] = (
            "Etapa 4/7 — SPREADSHEET_ID não foi encontrado nos Streamlit Secrets."
        )
        return False

    spreadsheet_id = str(secrets["SPREADSHEET_ID"]).strip()
    if not spreadsheet_id or spreadsheet_id == "COLE_AQUI_O_ID_DA_PLANILHA":
        st.session_state["sheets_error"] = (
            "Etapa 4/7 — SPREADSHEET_ID está vazio ou ainda contém o valor de exemplo."
        )
        return False

    if "google_service_account" not in secrets:
        st.session_state["sheets_error"] = (
            "Etapa 5/7 — a seção [google_service_account] não foi encontrada nos Streamlit Secrets."
        )
        return False

    service_account = secrets["google_service_account"]
    required = ["type", "project_id",
                "private_key", "client_email", "token_uri"]
    missing = [key for key in required if key not in service_account]
    if missing:
        st.session_state["sheets_error"] = (
            "Etapa 5/7 — a configuração da conta de serviço está incompleta. "
            f"Campos ausentes: {', '.join(missing)}."
        )
        return False

    st.session_state["sheets_error"] = "Etapa 6/7 — Secrets encontrados e configuração básica válida."
    return True


@st.cache_resource
def get_google_worksheet():
    if not google_sheets_configured():
        return None

    try:
        service_account_info = dict(st.secrets["google_service_account"])

        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]

        try:
            credentials = Credentials.from_service_account_info(
                service_account_info,
                scopes=scopes,
            )
        except Exception as error:
            st.session_state["sheets_error"] = (
                f"Etapa 6/7 — não foi possível criar as credenciais da conta de serviço: "
                f"{type(error).__name__}: {error}"
            )
            return None

        try:
            client = gspread.authorize(credentials)
            spreadsheet = client.open_by_key(
                str(st.secrets["SPREADSHEET_ID"]).strip()
            )
        except Exception as error:
            st.session_state["sheets_error"] = (
                f"Etapa 7/7 — as credenciais foram lidas, mas não foi possível acessar a planilha: "
                f"{type(error).__name__}: {error}"
            )
            return None

        try:
            worksheet = spreadsheet.worksheet("avaliacoes")
        except gspread.WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(
                title="avaliacoes",
                rows=1000,
                cols=len(HEADERS) + 5,
            )
            worksheet.append_row(HEADERS)

        existing = worksheet.get_all_values()

        if not existing:
            worksheet.append_row(HEADERS)

        st.session_state["sheets_error"] = "Google Sheets conectado com sucesso."
        return worksheet

    except Exception as error:
        st.session_state["sheets_error"] = (
            f"Erro inesperado ao configurar o Google Sheets: "
            f"{type(error).__name__}: {error}"
        )
        return None


def carregar_avaliacoes():
    worksheet = get_google_worksheet()

    if worksheet is not None:
        try:
            values = worksheet.get_all_records()
            return pd.DataFrame(values)

        except Exception as error:
            st.session_state["sheets_error"] = str(error)

    return carregar_avaliacoes_local()


def salvar_avaliacao(dados):
    worksheet = get_google_worksheet()

    if worksheet is not None:
        row = [dados.get(column, "") for column in HEADERS]
        worksheet.append_row(
            row,
            value_input_option="USER_ENTERED"
        )
        st.session_state["salvamento_status"] = "online"
        st.session_state["salvamento_mensagem"] = "Avaliação salva no Google Sheets."
        return "online"

    DATA.mkdir(parents=True, exist_ok=True)
    atual = carregar_avaliacoes_local()
    nova = pd.DataFrame([dados])
    resultado = pd.concat([atual, nova], ignore_index=True)
    resultado.to_csv(
        AVALIACOES_LOCAL,
        index=False,
        encoding="utf-8-sig"
    )

    st.session_state["salvamento_status"] = "local"
    st.session_state["salvamento_mensagem"] = "Avaliação salva apenas no armazenamento local."
    return "local"


# ============================================================
# SESSION
# ============================================================

if "pagina" not in st.session_state:
    st.session_state.pagina = "inicio"

if "avaliador" not in st.session_state:
    st.session_state.avaliador = ""

if "trabalho_id" not in st.session_state:
    st.session_state.trabalho_id = ""

if "admin" not in st.session_state:
    st.session_state.admin = False


# ============================================================
# CARREGAR PROGRAMAÇÃO
# ============================================================

trabalhos = carregar_trabalhos()


# ============================================================
# CABEÇALHO
# ============================================================

render_html(
    f"""
<div class="hero">

{logo_html()}

<div class="hero-small">
ENEBI 26 • 9º ENCONTRO NACIONAL DE ENGENHARIA BIOMECÂNICA
</div>

<div class="hero-title">
Avaliação de Apresentação Oral
</div>

<div class="hero-description">
Avalie a qualidade científica, a apresentação
e o desempenho do apresentador.
</div>

</div>
"""
)


# ============================================================
# INÍCIO
# ============================================================

if st.session_state.pagina == "inicio":

    render_html(
        """
    <div class="section-title">
    Identificação do avaliador
    </div>
    """
    )

    avaliador = st.text_input(
        "Nome do avaliador",
        placeholder="Digite seu nome",
        label_visibility="collapsed"
    )

    render_html(
        """
    <div class="section-title">
    Escolha a apresentação
    </div>
    """
    )

    if trabalhos.empty:
        st.error(
            "A programação não foi encontrada. "
            "Verifique data/trabalhos.csv."
        )
    else:

        datas = list(
            trabalhos["data"].drop_duplicates()
        )

        data_escolhida = st.selectbox(
            "Dia",
            datas,
            format_func=lambda x: {
                "07/10/2026": "Quarta-feira • 07 de outubro",
                "08/10/2026": "Quinta-feira • 08 de outubro",
                "09/10/2026": "Sexta-feira • 09 de outubro",
            }.get(x, x)
        )

        dia_df = trabalhos[
            trabalhos["data"] == data_escolhida
        ]

        salas = list(
            dia_df["sala"].drop_duplicates()
        )

        sala_escolhida = st.selectbox(
            "Sala",
            salas
        )

        sala_df = dia_df[
            dia_df["sala"] == sala_escolhida
        ]

        horarios = list(
            sala_df["horario"].drop_duplicates()
        )

        horario_escolhido = st.selectbox(
            "Horário",
            horarios
        )

        horario_df = sala_df[
            sala_df["horario"] == horario_escolhido
        ]

        if len(horario_df) == 1:

            trabalho = horario_df.iloc[0]

        else:

            opcoes = [
                f"{row.codigo} — {row.titulo}"
                for row in horario_df.itertuples()
            ]

            escolha = st.selectbox(
                "Trabalho",
                opcoes
            )

            codigo = escolha.split(
                " — ",
                1
            )[0]

            trabalho = horario_df[
                horario_df["codigo"] == codigo
            ].iloc[0]

        render_html(
            f"""
        <div class="work-card">

        <div class="work-code">
        {trabalho["codigo"]}
        </div>

        <div class="work-title">
        {trabalho["titulo"]}
        </div>

        <div class="work-meta">
        <b>Sala:</b> {trabalho["sala"]}<br>
        <b>Horário:</b> {trabalho["horario"]}<br>
        <b>Sessão:</b> {trabalho["sessao"]}<br>
        <b>Área:</b> {trabalho["area"]}
        </div>

        </div>
        """
        )

        if st.button(
            "Começar avaliação →",
            type="primary",
            use_container_width=True
        ):

            if not avaliador.strip():

                st.error(
                    "Digite seu nome antes de continuar."
                )

            else:

                st.session_state.avaliador = (
                    avaliador.strip()
                )

                st.session_state.trabalho_id = (
                    trabalho["id"]
                )

                st.session_state.pagina = (
                    "avaliacao"
                )

                st.rerun()


# ============================================================
# AVALIAÇÃO
# ============================================================

elif st.session_state.pagina == "avaliacao":

    trabalho = trabalhos[
        trabalhos["id"] == st.session_state.trabalho_id
    ].iloc[0]

    st.caption(
        f"Avaliador: **{st.session_state.avaliador}**"
    )

    render_html(
        f"""
    <div class="work-card">

    <div class="work-code">
    {trabalho["codigo"]}
    </div>

    <div class="work-title">
    {trabalho["titulo"]}
    </div>

    <div class="work-meta">
    <b>{trabalho["dia"]}</b> •
    {trabalho["data"]}<br>
    <b>Sala:</b> {trabalho["sala"]}<br>
    <b>Horário:</b> {trabalho["horario"]}<br>
    <b>Sessão:</b> {trabalho["sessao"]}
    </div>

    </div>
    """
    )

    escala = [
        "1 — Insuficiente",
        "2 — Regular",
        "3 — Bom",
        "4 — Muito bom",
        "5 — Excelente"
    ]

    notas = {}

    # --------------------------------------------------------
    # CONTEÚDO CIENTÍFICO
    # --------------------------------------------------------

    render_html(
        """
    <div class="section-title">
    1 · Conteúdo científico
    </div>
    """
    )

    st.caption(
        "Avalie a qualidade e a consistência científica "
        "do trabalho apresentado."
    )

    criterios_cientificos = [
        (
            "relevancia",
            "Relevância do tema",
            "Considere a importância e a contribuição do tema para a área de conhecimento."
        ),
        (
            "originalidade",
            "Originalidade e inovação da proposta",
            "Considere o caráter original da abordagem, proposta, método ou contribuição apresentada."
        ),
        (
            "objetivos",
            "Clareza dos objetivos",
            "Considere se os objetivos do trabalho estão claramente apresentados e definidos."
        ),
        (
            "metodologia",
            "Adequação da metodologia",
            "Considere se a metodologia utilizada é adequada aos objetivos propostos e está suficientemente apresentada."
        ),
        (
            "resultados",
            "Qualidade e consistência dos resultados",
            "Considere a qualidade dos resultados apresentados, sua consistência e sua relação com a investigação realizada."
        ),
        (
            "conclusoes",
            "Coerência entre resultados e conclusões",
            "Considere se as conclusões são sustentadas pelos resultados apresentados e respondem aos objetivos do trabalho."
        ),
    ]

    for chave, titulo, descricao in criterios_cientificos:

        render_html(
            f"""
        <div class="criterion-card">

        <div class="criterion-title">
        {titulo}
        </div>

        <div class="criterion-description">
        {descricao}
        </div>

        </div>
        """
        )

        resposta = st.radio(
            titulo,
            escala,
            horizontal=True,
            key=f"cientifico_{chave}",
            label_visibility="collapsed"
        )

        notas[chave] = int(
            resposta[0]
        )

    # --------------------------------------------------------
    # APRESENTAÇÃO ORAL
    # --------------------------------------------------------

    render_html(
        """
    <div class="section-title">
    2 · Apresentação oral
    </div>
    """
    )

    st.caption(
        "Avalie a qualidade da comunicação do trabalho "
        "e o desempenho do apresentador durante a apresentação."
    )

    criterios_apresentacao = [
        (
            "clareza",
            "Clareza e organização da apresentação oral",
            "Considere a clareza da exposição, a organização das informações e a facilidade de compreensão do conteúdo."
        ),
        (
            "dominio",
            "Domínio do tema",
            "Considere o conhecimento e a segurança demonstrados pelo apresentador durante a exposição."
        ),
        (
            "material_visual",
            "Qualidade do material visual",
            "Considere a organização e legibilidade dos slides e o uso adequado de figuras, gráficos, tabelas e outros recursos visuais."
        ),
        (
            "sintese_tempo",
            "Capacidade de síntese e adequação ao tempo",
            "Considere a capacidade de apresentar as informações essenciais de forma objetiva, respeitando o tempo disponível."
        ),
        (
            "respostas",
            "Qualidade das respostas às perguntas",
            "Considere a clareza, pertinência e fundamentação das respostas apresentadas durante a discussão."
        ),
    ]

    for chave, titulo, descricao in criterios_apresentacao:

        render_html(
            f"""
        <div class="criterion-card">

        <div class="criterion-title">
        {titulo}
        </div>

        <div class="criterion-description">
        {descricao}
        </div>

        </div>
        """
        )

        resposta = st.radio(
            titulo,
            escala,
            horizontal=True,
            key=f"apresentacao_{chave}",
            label_visibility="collapsed"
        )

        notas[chave] = int(
            resposta[0]
        )

    # --------------------------------------------------------
    # TEMPO
    # --------------------------------------------------------

    render_html(
        """
    <div class="section-title">
    3 · Controle do tempo
    </div>
    """
    )

    tempo = st.radio(
        "A apresentação respeitou o tempo máximo de 15 minutos?",
        ["Sim", "Não"],
        horizontal=True
    )

    # --------------------------------------------------------
    # PREMIAÇÃO
    # --------------------------------------------------------

    render_html(
        """
    <div class="section-title">
    4 · Indicação para premiação
    </div>
    """
    )

    premiacao = st.radio(
        "Indica este trabalho para premiação?",
        ["Sim", "Não"],
        horizontal=True
    )

    comentarios = st.text_area(
        "Comentários do avaliador",
        placeholder=(
            "Registre, se desejar, observações, "
            "destaques ou aspectos relevantes sobre "
            "o trabalho ou a apresentação."
        ),
        height=140
    )

    if st.button(
        "✓  Enviar avaliação",
        type="primary",
        use_container_width=True
    ):

        dados = {
            "timestamp": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "avaliador": st.session_state.avaliador,
            "codigo": trabalho["codigo"],
            "titulo": trabalho["titulo"],
            "data": trabalho["data"],
            "dia": trabalho["dia"],
            "sala": trabalho["sala"],
            "sessao": trabalho["sessao"],
            "horario": trabalho["horario"],
            **notas,
            "respeitou_15_min": tempo,
            "indicacao_premiacao": premiacao,
            "comentarios": comentarios,
        }

        try:
            armazenamento = salvar_avaliacao(dados)
            st.session_state["ultimo_armazenamento"] = armazenamento
            st.session_state.pagina = "sucesso"
            st.rerun()

        except Exception as error:
            st.error(
                "Não foi possível salvar a avaliação."
            )
            st.exception(error)


# ============================================================
# SUCESSO
# ============================================================

elif st.session_state.pagina == "sucesso":

    render_html(
        """
    <div class="success-card">

    <div class="success-icon">
    ✓
    </div>

    <div class="success-title">
    Obrigado pela avaliação!
    </div>

    <div class="success-description">
    Sua contribuição é fundamental para a avaliação
    das apresentações e para a seleção dos trabalhos
    considerados para premiação.
    </div>

    </div>
    """
    )

    if st.button(
        "Avaliar outro trabalho",
        type="primary",
        use_container_width=True
    ):

        st.session_state.pagina = "inicio"
        st.session_state.trabalho_id = ""
        st.rerun()


# ============================================================
# ADMINISTRAÇÃO
# ============================================================

st.divider()

render_html(
    """
<div class="section-title">
Organização
</div>
"""
)

if not st.session_state.admin:

    render_html(
        """
    <div class="admin-lock">
    🔒 Área restrita à organização do congresso.
    </div>
    """
    )

    senha = st.text_input(
        "Senha administrativa",
        type="password",
        placeholder="Senha da organização",
        label_visibility="collapsed"
    )

    # Durante os testes locais usamos esta senha.
    # Na publicação, ela deve ser movida para Streamlit Secrets.
    try:
        admin_password = str(
            st.secrets.get(
                "ADMIN_PASSWORD",
                "congresso-demo"
            )
        )
    except Exception:
        admin_password = "congresso-demo"

    if st.button(
        "Entrar no painel administrativo",
        use_container_width=True
    ):

        if senha == admin_password:
            st.session_state.admin = True
            st.rerun()
        else:
            st.error("Senha incorreta.")

else:

    st.success(
        "Acesso administrativo ativo."
    )

    if st.button("Sair do painel"):
        st.session_state.admin = False
        st.rerun()

    avaliacoes = carregar_avaliacoes()

    if "sheets_error" in st.session_state:
        st.warning(
            "Google Sheets não está disponível no momento. "
            "O aplicativo está usando o armazenamento local."
        )

    # --------------------------------------------------------
    # MÉTRICAS
    # --------------------------------------------------------

    col1, col2, col3 = st.columns(3)

    with col1:
        render_html(
            f"""
        <div class="metric-card">
        <div class="metric-number">{len(trabalhos)}</div>
        <div class="metric-label">Apresentações</div>
        </div>
        """
        )

    with col2:
        render_html(
            f"""
        <div class="metric-card">
        <div class="metric-number">{len(avaliacoes)}</div>
        <div class="metric-label">Avaliações</div>
        </div>
        """
        )

    if not avaliacoes.empty and "indicacao_premiacao" in avaliacoes.columns:
        indicacoes = int(
            (
                avaliacoes["indicacao_premiacao"].astype(str)
                == "Sim"
            ).sum()
        )
    else:
        indicacoes = 0

    with col3:
        render_html(
            f"""
        <div class="metric-card">
        <div class="metric-number">{indicacoes}</div>
        <div class="metric-label">Indicações</div>
        </div>
        """
        )

    # --------------------------------------------------------
    # FILTROS
    # --------------------------------------------------------

    if not avaliacoes.empty:

        render_html(
            """
        <div class="section-title">
        Filtros
        </div>
        """
        )

        f1, f2 = st.columns(2)

        with f1:
            filtro_data = st.selectbox(
                "Dia",
                ["Todos"] + sorted(
                    avaliacoes["data"].dropna().astype(str).unique().tolist()
                )
            )

        with f2:
            filtro_sala = st.selectbox(
                "Sala",
                ["Todas"] + sorted(
                    avaliacoes["sala"].dropna().astype(str).unique().tolist()
                )
            )

        exibicao = avaliacoes.copy()

        if filtro_data != "Todos":
            exibicao = exibicao[
                exibicao["data"].astype(str) == filtro_data
            ]

        if filtro_sala != "Todas":
            exibicao = exibicao[
                exibicao["sala"].astype(str) == filtro_sala
            ]

        st.dataframe(
            exibicao,
            use_container_width=True,
            hide_index=True
        )

        csv = exibicao.to_csv(
            index=False,
            encoding="utf-8-sig"
        )

        st.download_button(
            "⬇  Baixar avaliações filtradas",
            data=csv,
            file_name="avaliacoes_ENEBI_26.csv",
            mime="text/csv",
            use_container_width=True
        )

    # --------------------------------------------------------
    # QR CODE
    # --------------------------------------------------------

    render_html(
        """
    <div class="section-title">
    QR Code de acesso
    </div>
    """
    )

    st.caption(
        "Depois que o aplicativo estiver publicado, "
        "cole aqui a URL pública."
    )

    url = st.text_input(
        "URL pública do aplicativo",
        placeholder="https://seu-app.streamlit.app"
    )

    if qrcode is None:

        st.warning(
            "Instale qrcode[pil] para gerar o QR Code."
        )

    elif url.strip().startswith(
        ("http://", "https://")
    ):

        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4
        )

        qr.add_data(url.strip())
        qr.make(fit=True)

        image = qr.make_image(
            fill_color=AZUL,
            back_color=FUNDO
        )

        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        qr_bytes = buffer.getvalue()

        render_html(
            """
        <div class="qr-card">
        <b style="color:#0B4F72;">ENEBI 26</b><br>
        <span style="color:#377C7D;">
        Avaliação de Apresentação Oral
        </span>
        </div>
        """
        )

        st.image(
            qr_bytes,
            width=260
        )

        st.download_button(
            "⬇  Baixar QR Code",
            data=qr_bytes,
            file_name="QR_Code_ENEBI_26.png",
            mime="image/png",
            use_container_width=True
        )
