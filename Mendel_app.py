import streamlit as st
import random
import plotly.graph_objects as go

# ---- 페이지 설정 ----
st.set_page_config(page_title="완두 자가수분 시뮬레이터", page_icon="🌱", layout="centered")

# ---- 스타일 ----
st.markdown("""
<style>
    .stApp { background-color: #fafafa; font-family: 'Noto Sans KR', sans-serif; }
    .title { text-align:center; font-size:2em; color:#2e7d32; font-weight:700; margin-bottom:0.2em; }
    .subtitle { text-align:center; color:#8e24aa; font-size:1.6em; font-weight:700; margin-bottom:1.5em; }
    .purple-heart { color:#8e24aa; font-size:1.6em; margin:0 8px; }
</style>
""", unsafe_allow_html=True)

# ---- 제목 ----
st.markdown("<div class='title'>🌿 완두 자가수분 시뮬레이터</div>", unsafe_allow_html=True)
st.markdown("""
<div class='subtitle'>
    <span class='purple-heart'>💜</span> 보라중학교 <span class='purple-heart'>💜</span>
</div>
""", unsafe_allow_html=True)

# ---- 기본 데이터 ----
GENO_ORDER = ['RRYY','RrYY','rrYY','RRyy','Rryy','rryy','RRYy','RrYy','rrYy']
PHENO_ORDER = ['둥근 노란색 완두','주름진 노란색 완두','둥근 녹색 완두','주름진 녹색 완두']
GENO2PHENO = {
    'RRYY':'둥근 노란색 완두','RrYY':'둥근 노란색 완두','rrYY':'주름진 노란색 완두',
    'RRyy':'둥근 녹색 완두','Rryy':'둥근 녹색 완두','rryy':'주름진 녹색 완두',
    'RRYy':'둥근 노란색 완두','RrYy':'둥근 노란색 완두','rrYy':'주름진 노란색 완두'
}

# ---- 탭 스타일 (탭 글씨 크게) ----
st.markdown("""
<style>
    div[data-baseweb="tab"] > button > div[data-testid="stMarkdownContainer"] > p {
        font-size: 1.3rem !important;
        font-weight: 700 !important;
    }
</style>
""", unsafe_allow_html=True)

# ---- 탭 생성 ----
tab1, tab2 = st.tabs(["🌾 분리의 법칙", "🌿 독립의 법칙"])
# -----------------------------------------------
# 🔹 분리의 법칙 탭 (Y/y 유전자만)
# -----------------------------------------------
with tab1:
    st.subheader("분리의 법칙 (완두 색깔)")
    if "sep_geno" not in st.session_state:
        st.session_state.sep_geno = {'YY':0,'Yy':0,'yy':0}
        st.session_state.sep_pheno = {'노란색 완두':0,'녹색 완두':0}
        st.session_state.sep_count = 0
        st.session_state.sep_last = ""

    sep_geno = st.session_state.sep_geno
    sep_pheno = st.session_state.sep_pheno

    def simulate_sep(n=1):
        for _ in range(n):
            fY, mY = random.choice("Yy"), random.choice("Yy")
            g = ''.join(sorted([fY,mY]))
            p = "노란색 완두" if "Y" in g else "녹색 완두"
            sep_geno[g]+=1; sep_pheno[p]+=1
            st.session_state.sep_count += 1
            st.session_state.sep_last = f"암술 {fY}, 수술 {mY} → {g} ({p})"

    def reset_sep():
        for k in sep_geno: sep_geno[k]=0
        for k in sep_pheno: sep_pheno[k]=0
        st.session_state.sep_count=0
        st.session_state.sep_last=""

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🌼 자가수분 1회", key="sep1", use_container_width=True):
            simulate_sep(1)
    with col2:
        if st.button("🌻 자가수분 100회", key="sep100", use_container_width=True):
            simulate_sep(100)
    with col3:
        if st.button("🔄 초기화", key="sep_reset", use_container_width=True):
            reset_sep()

    if st.session_state.sep_count > 0:
        st.write(f"**최근 결과:** {st.session_state.sep_last}")
        st.write(f"**누적 자가수분 횟수:** {st.session_state.sep_count}")

        st.markdown("#### 🧬 유전자형 누적")
        st.text("\n".join([f"{k}: {v}" for k,v in sep_geno.items()]))

        st.markdown("#### 🌼 표현형 누적")
        st.text("\n".join([f"{k}: {v}" for k,v in sep_pheno.items()]))

        # ✅ 색상 변경됨 (유전자형 = 초록색 / 표현형 = 보라색)
        fig1 = go.Figure([go.Bar(
            x=list(sep_geno.keys()), y=list(sep_geno.values()),
            text=[str(v) for v in sep_geno.values()],
            textposition='outside', marker_color="#4CAF50"  # 초록색
        )])
        fig1.update_layout(yaxis_title="개수", height=350, margin=dict(l=10,r=10,t=40,b=20))
        st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar": False, "staticPlot": True})

        fig2 = go.Figure([go.Bar(
            x=list(sep_pheno.keys()), y=list(sep_pheno.values()),
            text=[str(v) for v in sep_pheno.values()],
            textposition='outside', marker_color="#AB47BC"  # 보라색
        )])
        fig2.update_layout(yaxis_title="개수", height=350, margin=dict(l=10,r=10,t=40,b=20))
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False, "staticPlot": True})
    else:
        st.info("자가수분을 실행하면 결과가 여기에 표시됩니다 🌱")

# -----------------------------------------------
# 🔹 독립의 법칙 탭 (R/r, Y/y 두 형질)
# -----------------------------------------------
with tab2:
    st.subheader("독립의 법칙 (완두 모양 + 색깔)")
    if "ind_geno" not in st.session_state:
        st.session_state.ind_geno = {k:0 for k in GENO_ORDER}
        st.session_state.ind_pheno = {k:0 for k in PHENO_ORDER}
        st.session_state.ind_count = 0
        st.session_state.ind_last = ""

    ind_geno = st.session_state.ind_geno
    ind_pheno = st.session_state.ind_pheno

    def simulate_ind(n=1):
        for _ in range(n):
            fR, fY, mR, mY = random.choice("Rr"), random.choice("Yy"), random.choice("Rr"), random.choice("Yy")
            g = ''.join(sorted([fR,mR])) + ''.join(sorted([fY,mY]))
            p = GENO2PHENO[g]
            ind_geno[g]+=1; ind_pheno[p]+=1
            st.session_state.ind_count += 1
            st.session_state.ind_last = f"암술 {fR}{fY}, 수술 {mR}{mY} → {g} ({p})"

    def reset_ind():
        for k in ind_geno: ind_geno[k]=0
        for k in ind_pheno: ind_pheno[k]=0
        st.session_state.ind_count=0
        st.session_state.ind_last=""

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🌼 자가수분 1회", key="ind1", use_container_width=True):
            simulate_ind(1)
    with col2:
        if st.button("🌻 자가수분 100회", key="ind100", use_container_width=True):
            simulate_ind(100)
    with col3:
        if st.button("🔄 초기화", key="ind_reset", use_container_width=True):
            reset_ind()

    if st.session_state.ind_count > 0:
        st.write(f"**최근 결과:** {st.session_state.ind_last}")
        st.write(f"**누적 자가수분 횟수:** {st.session_state.ind_count}")

        st.markdown("#### 🧬 유전자형 누적")
        st.text("\n".join([f"{k}: {v}" for k,v in ind_geno.items()]))

        st.markdown("#### 🌼 표현형 누적")
        st.text("\n".join([f"{k}: {v}" for k,v in ind_pheno.items()]))

        fig1 = go.Figure([go.Bar(
            x=list(ind_geno.keys()), y=list(ind_geno.values()),
            text=[str(v) for v in ind_geno.values()],
            textposition='outside', marker_color="#4CAF50"
        )])
        fig1.update_layout(yaxis_title="개수", height=350, margin=dict(l=10,r=10,t=40,b=20))
        st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar": False, "staticPlot": True})

        fig2 = go.Figure([go.Bar(
            x=list(ind_pheno.keys()), y=list(ind_pheno.values()),
            text=[str(v) for v in ind_pheno.values()],
            textposition='outside', marker_color="#AB47BC"
        )])
        fig2.update_layout(yaxis_title="개수", height=350, margin=dict(l=10,r=10,t=40,b=20))
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False, "staticPlot": True})
    else:
        st.info("자가수분을 실행하면 결과가 여기에 표시됩니다 🌱")