import streamlit as st
import pandas as pd
import unicodedata
import re

st.set_page_config(page_title="Radar Comercial Inteligente", layout="wide")

# =========================
# IDENTIDADE VISUAL
# =========================

st.markdown("""
<style>
:root {
    --azul: #0D1B2A;
    --vermelho: #C62828;
    --verde: #1B8A3D;
    --amarelo: #F9A825;
    --cinza: #F5F7FA;
    --borda: #E5E7EB;
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}

h1, h2, h3 {
    color: var(--azul);
    font-family: Arial, Helvetica, sans-serif;
}

[data-testid="stSidebar"] {
    background-color: #0D1B2A;
}

[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span {
    color: white !important;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: white !important;
}

.stMetric {
    background-color: #FFFFFF;
    border: 1px solid var(--borda);
    padding: 14px;
    border-radius: 14px;
    box-shadow: 0 2px 8px rgba(13,27,42,0.06);
}

div[data-testid="stMetricLabel"] {
    color: #475569;
    font-weight: 600;
}

div[data-testid="stMetricValue"] {
    color: #0D1B2A;
    font-weight: 800;
}

.stDataFrame {
    border-radius: 12px;
    overflow: hidden;
}

button {
    border-radius: 10px !important;
    font-weight: 600 !important;
}

.app-header {
    background: linear-gradient(90deg, #0D1B2A 0%, #13293D 60%, #C62828 100%);
    padding: 24px 28px;
    border-radius: 18px;
    margin-bottom: 22px;
    color: white;
}

.app-header h1 {
    color: white;
    margin-bottom: 4px;
    font-size: 34px;
}

.app-header p {
    color: #E5E7EB;
    font-size: 16px;
    margin: 0;
}

.section-card {
    background-color: white;
    border: 1px solid #E5E7EB;
    border-radius: 16px;
    padding: 18px;
    margin-bottom: 18px;
    box-shadow: 0 2px 10px rgba(13,27,42,0.05);
}

.small-muted {
    color: #64748B;
    font-size: 14px;
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="app-header">
    <h1>📡 Radar Comercial Inteligente</h1>
    <p>Sistema inteligente para decidir quem visitar, corrigir desvios e acelerar suas vendas.</p>
</div>
""", unsafe_allow_html=True)

# =========================
# FUNÇÕES
# =========================

def limpar_filtros():
    for key in list(st.session_state.keys()):
        if key.startswith("filtro_"):
            del st.session_state[key]

def limpar_nome(txt):
    txt = str(txt).strip().upper()
    txt = unicodedata.normalize("NFKD", txt).encode("ASCII", "ignore").decode("utf-8")
    return txt

def limpar_cnpj(valor):
    return re.sub(r"\D", "", str(valor))

def numero(valor):
    if pd.isna(valor):
        return 0.0
    if isinstance(valor, (int, float)):
        return float(valor)
    valor = str(valor).strip().replace("R$", "").replace("%", "")
    valor = valor.replace(".", "").replace(",", ".")
    valor = valor.replace("-", "0") if valor == "-" else valor
    try:
        return float(valor)
    except:
        return 0.0

def moeda(valor):
    try:
        return f"R$ {float(valor):,.0f}".replace(",", ".")
    except:
        return "R$ 0"

def pct(valor):
    try:
        return f"{float(valor) * 100:,.1f}%".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "0,0%"

def pct_cmv(valor):
    try:
        return f"{float(valor) * 100:,.2f}%".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "0,00%"

def achar_coluna(df, opcoes, exata=False):
    for opcao in opcoes:
        for col in df.columns:
            if limpar_nome(col) == limpar_nome(opcao):
                return col

    if not exata:
        for opcao in opcoes:
            for col in df.columns:
                if limpar_nome(opcao) in limpar_nome(col):
                    return col

    return None

def setor_limpo(valor):
    achou = re.search(r"\d+", str(valor))
    return achou.group() if achou else ""

def prioridade(row):
    gap = row["GAP"]
    perc_gap = row["PERC_GAP"]

    if gap >= 0:
        return "🟢 AUMENTAR VENDA"

    if perc_gap <= -0.20:
        return "🔴 URGENTE"

    return "🟡 ATENÇÃO"

def acao(row):
    gap = row["GAP"]
    perc_gap = row["PERC_GAP"]

    if gap >= 0:
        return "Aumentar venda"

    if perc_gap <= -0.20:
        return "Recuperar venda urgente"

    return "Acompanhar e recuperar venda"

def cor_prioridade(valor):
    if "URGENTE" in str(valor):
        return "background-color: #F8D7DA; color: #842029; font-weight: bold"
    if "ATENÇÃO" in str(valor):
        return "background-color: #FFF3CD; color: #664D03; font-weight: bold"
    if "AUMENTAR" in str(valor):
        return "background-color: #D1E7DD; color: #0F5132; font-weight: bold"
    return ""

def cor_numero(valor):
    try:
        v = float(valor)
        if v < 0:
            return "color: #C62828; font-weight: bold"
        if v > 0:
            return "color: #1B8A3D; font-weight: bold"
    except:
        pass
    return ""

def cor_prazo(valor):
    try:
        v = float(valor)
        if v <= 0:
            return "color: #1B8A3D; font-weight: bold"
        return "color: #C62828; font-weight: bold"
    except:
        return ""

def cor_cmv(valor):
    try:
        v = float(valor)
        if v <= 0:
            return "color: #1B8A3D; font-weight: bold"
        return "color: #C62828; font-weight: bold"
    except:
        return ""

# =========================
# UPLOAD
# =========================

st.markdown("## 📁 Carregar bases")

col_up1, col_up2 = st.columns(2)

with col_up1:
    curva_file = st.file_uploader("📊 Subir Curva semanal", type=["xlsx"])

with col_up2:
    cmk_file = st.file_uploader("📍 Subir CMK/endereço", type=["xlsx"])

if not curva_file or not cmk_file:
    st.info("Suba a Curva semanal e o CMK para iniciar a análise.")
    st.stop()

try:
    curva = pd.read_excel(curva_file, sheet_name="DADOS")
except:
    curva = pd.read_excel(curva_file)

cmk = pd.read_excel(cmk_file)

curva.columns = [limpar_nome(c) for c in curva.columns]
cmk.columns = [limpar_nome(c) for c in cmk.columns]

# =========================
# COLUNAS
# =========================

col_cliente = achar_coluna(curva, ["CLIENTE"], exata=True)
col_cnpj_curva = achar_coluna(curva, ["CNPJ"], exata=True)
col_cnpj_cmk = achar_coluna(cmk, ["CNPJ"], exata=True)
col_bandeira = achar_coluna(curva, ["BANDEIRA"], exata=True)
col_supervisor = achar_coluna(curva, ["SUPERVISOR"])
col_setor = achar_coluna(curva, ["COD.SETOR", "COD SETOR", "SETOR"])

col_meta = achar_coluna(curva, ["META"], exata=True)
col_real = achar_coluna(curva, ["REAL"], exata=True)
col_proj = achar_coluna(curva, ["REAL PROJ", "REAL PROJ AC"])
col_gap_planilha = achar_coluna(curva, ["DESVIO PROJ"], exata=True)
col_perc_gap = achar_coluna(curva, ["% DESVIO"], exata=True)
col_2025 = achar_coluna(curva, ["2025"], exata=True)
col_cresc = achar_coluna(curva, ["% CRESC PROJ", "% CRESC PROJ AC", "CRESC"])

col_meta_pv = achar_coluna(curva, ["META PV"])
col_pven = achar_coluna(curva, ["P.VEN", "P VEN", "PVEN"])
col_desvio_pv = achar_coluna(curva, ["DESVIO PV"])

col_meta_cmv = achar_coluna(curva, ["META CMV %", "META CMV"])
col_cmv_real = achar_coluna(curva, ["CMV %", "CMV"])
col_desvio_cmv = achar_coluna(curva, ["DESVIO CMV %", "DESVIO CMV"])

col_cidade = achar_coluna(cmk, ["CIDADE"])
col_endereco = achar_coluna(cmk, ["ENDERECO", "ENDEREÇO"])
col_bairro = achar_coluna(cmk, ["BAIRRO"])

obrigatorias = {
    "CLIENTE": col_cliente,
    "CNPJ Curva": col_cnpj_curva,
    "CNPJ CMK": col_cnpj_cmk,
    "META": col_meta,
    "REAL": col_real,
    "PROJEÇÃO": col_proj,
    "DESVIO PROJ": col_gap_planilha,
    "% DESVIO": col_perc_gap,
    "2025": col_2025,
    "% CRESC PROJ": col_cresc,
    "META PV": col_meta_pv,
    "P.VEN": col_pven,
    "DESVIO PV": col_desvio_pv,
    "META CMV": col_meta_cmv,
    "CMV REAL": col_cmv_real,
    "DESVIO CMV": col_desvio_cmv,
    "CIDADE": col_cidade
}

faltando = [nome for nome, valor in obrigatorias.items() if valor is None]

if faltando:
    st.error("Não encontrei estas colunas obrigatórias:")
    st.write(faltando)
    st.write("Colunas encontradas na Curva:")
    st.write(list(curva.columns))
    st.write("Colunas encontradas no CMK:")
    st.write(list(cmk.columns))
    st.stop()

# =========================
# CRUZAMENTO
# =========================

curva["CNPJ_KEY"] = curva[col_cnpj_curva].apply(limpar_cnpj)
cmk["CNPJ_KEY"] = cmk[col_cnpj_cmk].apply(limpar_cnpj)

cols_cmk = ["CNPJ_KEY", col_cidade]

if col_endereco:
    cols_cmk.append(col_endereco)
if col_bairro:
    cols_cmk.append(col_bairro)

cmk_reduzido = cmk[cols_cmk].copy()

renomear_cmk = {col_cidade: "CIDADE"}

if col_endereco:
    renomear_cmk[col_endereco] = "ENDERECO"
if col_bairro:
    renomear_cmk[col_bairro] = "BAIRRO"

cmk_reduzido = cmk_reduzido.rename(columns=renomear_cmk)

df = curva.merge(cmk_reduzido, on="CNPJ_KEY", how="left")

# =========================
# TRATAMENTO
# =========================

df["CLIENTE_FINAL"] = df[col_cliente].astype(str)
df["SETOR_FINAL"] = df[col_setor].apply(setor_limpo) if col_setor else ""
df["BANDEIRA_FINAL"] = df[col_bandeira].astype(str) if col_bandeira else "SEM BANDEIRA"

df["META"] = df[col_meta].apply(numero)
df["REALIZADO"] = df[col_real].apply(numero)
df["PROJECAO"] = df[col_proj].apply(numero)
df["GAP"] = df[col_gap_planilha].apply(numero)
df["PERC_GAP"] = df[col_perc_gap].apply(numero)
df["VALOR_2025"] = df[col_2025].apply(numero)
df["CRESCIMENTO"] = df[col_cresc].apply(numero)

df["META_PV"] = df[col_meta_pv].apply(numero)
df["PRAZO_REAL"] = df[col_pven].apply(numero)
df["DESVIO_PRAZO"] = df[col_desvio_pv].apply(numero)

df["META_CMV"] = df[col_meta_cmv].apply(numero)
df["CMV_REAL"] = df[col_cmv_real].apply(numero)
df["DESVIO_CMV"] = df[col_desvio_cmv].apply(numero)

df["PRIORIDADE"] = df.apply(prioridade, axis=1)
df["ACAO"] = df.apply(acao, axis=1)

# =========================
# FILTROS
# =========================

st.sidebar.markdown("## 📡 Radar Comercial")
st.sidebar.caption("Filtros de decisão")

if st.sidebar.button("🔄 Limpar filtros"):
    limpar_filtros()
    st.rerun()

st.sidebar.markdown("---")

busca = st.sidebar.text_input(
    "Buscar cliente",
    key="filtro_busca"
)

if busca:
    df = df[df["CLIENTE_FINAL"].str.contains(busca, case=False, na=False)]

if col_supervisor:
    supervisores = ["Todos"] + sorted(df[col_supervisor].dropna().astype(str).unique().tolist())
    f_supervisor = st.sidebar.selectbox(
        "Supervisor",
        supervisores,
        key="filtro_supervisor"
    )

    if f_supervisor != "Todos":
        df = df[df[col_supervisor].astype(str) == f_supervisor]

setores = ["Todos"] + sorted(df["SETOR_FINAL"].dropna().astype(str).unique().tolist())
f_setor = st.sidebar.selectbox(
    "Setor",
    setores,
    key="filtro_setor"
)

if f_setor != "Todos":
    df = df[df["SETOR_FINAL"] == f_setor]

bandeiras = ["Todas"] + sorted(df["BANDEIRA_FINAL"].dropna().astype(str).unique().tolist())
f_bandeira = st.sidebar.selectbox(
    "Bandeira",
    bandeiras,
    key="filtro_bandeira"
)

if f_bandeira != "Todas":
    df = df[df["BANDEIRA_FINAL"] == f_bandeira]

cidades = ["Todas"] + sorted(df["CIDADE"].dropna().astype(str).unique().tolist())
f_cidade = st.sidebar.selectbox(
    "Cidade",
    cidades,
    key="filtro_cidade"
)

if f_cidade != "Todas":
    df = df[df["CIDADE"].astype(str) == f_cidade]

prioridades = ["Todas", "🔴 URGENTE", "🟡 ATENÇÃO", "🟢 AUMENTAR VENDA"]
f_prioridade = st.sidebar.selectbox(
    "Prioridade",
    prioridades,
    key="filtro_prioridade"
)

if f_prioridade != "Todas":
    df = df[df["PRIORIDADE"] == f_prioridade]

if df.empty:
    st.warning("Nenhum cliente encontrado com os filtros aplicados.")
    st.stop()

# =========================
# ORDEM
# =========================

ordem = {
    "🔴 URGENTE": 1,
    "🟡 ATENÇÃO": 2,
    "🟢 AUMENTAR VENDA": 3
}

df["ORDEM"] = df["PRIORIDADE"].map(ordem).fillna(9)
df = df.sort_values(by=["ORDEM", "GAP"], ascending=[True, True])

# =========================
# DASHBOARD
# =========================

st.markdown("## 📊 Visão Executiva")

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("Clientes analisados", len(df))
c2.metric("Clientes positivos", len(df[df["GAP"] >= 0]))
c3.metric("Clientes negativos", len(df[df["GAP"] < 0]))
c4.metric("Urgentes", len(df[df["PRIORIDADE"] == "🔴 URGENTE"]))

urgentes = df[df["PRIORIDADE"] == "🔴 URGENTE"]

if not urgentes.empty:
    cidade_critica = urgentes["CIDADE"].value_counts().idxmax()
    qtd_cidade = urgentes["CIDADE"].value_counts().max()
    c5.metric("Cidade crítica", f"{cidade_critica} ({qtd_cidade})")
else:
    c5.metric("Cidade crítica", "-")

m1, m2, m3, m4 = st.columns(4)

m1.metric("Meta total", moeda(df["META"].sum()))
m2.metric("Realizado", moeda(df["REALIZADO"].sum()))
m3.metric("Projeção", moeda(df["PROJECAO"].sum()))
m4.metric("Gap total", moeda(df["GAP"].sum()))

st.divider()

# =========================
# TABELA PRINCIPAL
# =========================

st.markdown("## 🧭 Base Completa de Decisão")
st.caption("Use esta visão para priorizar clientes, cidades e ações comerciais.")

tabela = df[[
    "CLIENTE_FINAL",
    "CIDADE",
    "PRIORIDADE",
    "META",
    "REALIZADO",
    "PROJECAO",
    "GAP",
    "PERC_GAP",
    "VALOR_2025",
    "CRESCIMENTO",
    "META_PV",
    "PRAZO_REAL",
    "DESVIO_PRAZO",
    "META_CMV",
    "CMV_REAL",
    "DESVIO_CMV",
    "ACAO"
]].copy()

tabela.columns = [
    "CLIENTE",
    "CIDADE",
    "PRIORIDADE",
    "META R$",
    "REALIZADO R$",
    "PROJEÇÃO R$",
    "GAP R$",
    "% GAP",
    "2025 R$",
    "CRESC. VS 2025",
    "META PV",
    "PRAZO REAL",
    "DESVIO PRAZO",
    "META CMV",
    "CMV REAL",
    "DESVIO CMV",
    "AÇÃO"
]

style = tabela.style.format({
    "META R$": moeda,
    "REALIZADO R$": moeda,
    "PROJEÇÃO R$": moeda,
    "GAP R$": moeda,
    "% GAP": pct,
    "2025 R$": moeda,
    "CRESC. VS 2025": pct,
    "META PV": "{:.1f}",
    "PRAZO REAL": "{:.1f}",
    "DESVIO PRAZO": "{:.1f}",
    "META CMV": pct_cmv,
    "CMV REAL": pct_cmv,
    "DESVIO CMV": pct_cmv,
}).applymap(cor_prioridade, subset=["PRIORIDADE"]) \
  .applymap(cor_numero, subset=["GAP R$", "CRESC. VS 2025"]) \
  .applymap(cor_prazo, subset=["DESVIO PRAZO"]) \
  .applymap(cor_cmv, subset=["DESVIO CMV"])

st.dataframe(style, use_container_width=True, hide_index=True, height=520)

# =========================
# ROTEIRO INTELIGENTE DO DIA — V10
# =========================

st.divider()
st.markdown("## 📍 Roteiro Inteligente do Dia")
st.caption("Gera uma sugestão de rota com os clientes mais importantes para visitar primeiro.")

if st.button("🚀 Gerar roteiro do dia"):

    df_urgente = df[df["PRIORIDADE"] == "🔴 URGENTE"].copy()
    df_atencao = df[df["PRIORIDADE"] == "🟡 ATENÇÃO"].copy()

    df_urgente = df_urgente.sort_values(by=["CIDADE", "GAP"], ascending=[True, True])
    df_atencao = df_atencao.sort_values(by=["CIDADE", "GAP"], ascending=[True, True])

    roteiro = pd.concat([df_urgente, df_atencao]).head(10)

    if roteiro.empty:
        st.warning("Nenhum cliente urgente ou em atenção encontrado para hoje.")
    else:
        st.success("Roteiro gerado com sucesso!")

        for cidade in roteiro["CIDADE"].dropna().unique():
            bloco = roteiro[roteiro["CIDADE"] == cidade]

            st.markdown(f"### 📍 {cidade}")

            for i, row in enumerate(bloco.itertuples(), start=1):
                st.markdown(f"""
**{i}. {row.CLIENTE_FINAL}**  
Prioridade: **{row.PRIORIDADE}**  
Gap: **{moeda(row.GAP)}**  
% Gap: **{pct(row.PERC_GAP)}**  
Ação: **{row.ACAO}**
""")

# =========================
# RESUMO POR CIDADE
# =========================

st.divider()
st.markdown("## 📍 Resumo por Cidade")

resumo_cidade = df.groupby("CIDADE", dropna=False).agg(
    CLIENTES=("CLIENTE_FINAL", "count"),
    POSITIVOS=("GAP", lambda x: (x >= 0).sum()),
    NEGATIVOS=("GAP", lambda x: (x < 0).sum()),
    URGENTES=("PRIORIDADE", lambda x: (x == "🔴 URGENTE").sum()),
    ATENCAO=("PRIORIDADE", lambda x: (x == "🟡 ATENÇÃO").sum()),
    META_TOTAL=("META", "sum"),
    REALIZADO=("REALIZADO", "sum"),
    PROJECAO=("PROJECAO", "sum"),
    GAP_TOTAL=("GAP", "sum"),
).reset_index().sort_values(by=["URGENTES", "ATENCAO", "GAP_TOTAL"], ascending=[False, False, True])

resumo_style = resumo_cidade.style.format({
    "META_TOTAL": moeda,
    "REALIZADO": moeda,
    "PROJECAO": moeda,
    "GAP_TOTAL": moeda,
}).applymap(cor_numero, subset=["GAP_TOTAL"])

st.dataframe(resumo_style, use_container_width=True, hide_index=True)

# =========================
# ANÁLISE INDIVIDUAL
# =========================

st.divider()
st.markdown("## 🎯 Resumo Objetivo do Cliente")

cliente_escolhido = st.selectbox("Escolha o cliente", df["CLIENTE_FINAL"].astype(str).unique())

d = df[df["CLIENTE_FINAL"].astype(str) == cliente_escolhido].iloc[0]

r1, r2, r3, r4 = st.columns(4)

r1.metric("Meta", moeda(d["META"]))
r2.metric("Realizado", moeda(d["REALIZADO"]))
r3.metric("Projeção", moeda(d["PROJECAO"]))
r4.metric("Gap", moeda(d["GAP"]))

st.markdown(f"""
<div class="section-card">

### 🏪 {d["CLIENTE_FINAL"]}

**Bandeira:** {d["BANDEIRA_FINAL"]}  
**Cidade:** {d.get("CIDADE", "")}  
**Endereço:** {d.get("ENDERECO", "")}  

**Prioridade:** {d["PRIORIDADE"]}  
**Ação sugerida:** {d["ACAO"]}  

---

### 📌 Leitura simples

- Meta do mês: **{moeda(d["META"])}**
- Realizado até agora: **{moeda(d["REALIZADO"])}**
- Projeção: **{moeda(d["PROJECAO"])}**
- Gap: **{moeda(d["GAP"])}**
- % Gap: **{pct(d["PERC_GAP"])}**
- Valor 2025: **{moeda(d["VALOR_2025"])}**
- Crescimento vs 2025: **{pct(d["CRESCIMENTO"])}**
- Prazo: meta **{d["META_PV"]:.1f} dias**, realizado **{d["PRAZO_REAL"]:.1f} dias**, desvio **{d["DESVIO_PRAZO"]:.1f} dias**
- CMV: meta **{pct_cmv(d["META_CMV"])}**, realizado **{pct_cmv(d["CMV_REAL"])}**, desvio **{pct_cmv(d["DESVIO_CMV"])}**

---

### 💬 Abordagem sugerida

"Passei aqui porque sua meta do mês é **{moeda(d["META"])}**, você realizou **{moeda(d["REALIZADO"])}** e está projetando **{moeda(d["PROJECAO"])}**.  
Hoje temos um gap de **{moeda(d["GAP"])}**, com % gap de **{pct(d["PERC_GAP"])}**, contra **{moeda(d["VALOR_2025"])}** em 2025.  
Quero te ajudar a ajustar isso com uma compra mais estratégica."

</div>
""", unsafe_allow_html=True)

primeiro = df.iloc[0]

st.error(
    f"👉 Comece por: {primeiro['CLIENTE_FINAL']} | {primeiro['PRIORIDADE']} | {primeiro['ACAO']}"
)