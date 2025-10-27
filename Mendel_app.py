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
    .subtitle { text-align:center; color:#558b2f; margin-bottom:1.5em; }
    .result-box { background-color:#fffde7; border:2px solid #fbc02d; border-radius:10px;
                  padding:15px; margin-top:10px; }
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='title'>🌿 완두 자가수분 시뮬레이터</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>독립의 법칙 포함 — 초고속 & 그래프 분리 버전 ⚡</div>", unsafe_allow_html=True)

# ---- 기본 데이터 ----
GENO_ORDER = ['RRYY','RrYY','rrYY','RRyy','Rryy','rryy','RRYy','RrYy','rrYy']
PHENO_ORDER = ['둥근 노란색 완두','주름진 노란색 완두','둥근 녹색 완두','주름진 녹색 완두']

GENO2PHENO = {
    'RRYY':'둥근 노란색 완두','RrYY':'둥근 노란색 완두','rrYY':'주름진 노란색 완두',
    'RRyy':'둥근 녹색 완두','Rryy':'둥근 녹색 완두','rryy':'주름진 녹색 완두',
    'RRYy':'둥근 노란색 완두','RrYy':'둥근 노란색 완두','rrYy':'주름진 노란색 완두'
}

# ---- 세션 상태 ----
if "geno" not in st.session_state:
    st.session_state.geno = {k: 0 for k in GENO_ORDER}
    st.session_state.pheno = {k: 0 for k in PHENO_ORDER}
    st.session_state.count = 0
    st.session_state.last = ""

geno = st.session_state.geno
pheno = st.session_state.pheno

# ---- 함수들 ----
@st.cache_resource
def _choices():
    R = ['R','r']
    Y = ['Y','y']
    return R, Y

R, Y = _choices()

def simulate(n=1):
    g2p = GENO2PHENO
    g = geno; p = pheno
    for _ in range(n):
        fR, fY, mR, mY = random.choice(R), random.choice(Y), random.choice(R), random.choice(Y)
        offR, offY = ''.join(sorted([fR,mR])), ''.join(sorted([fY,mY]))
        gtype = offR + offY
        ptype = g2p[gtype]
        g[gtype]+=1; p[ptype]+=1
        st.session_state.count += 1
        st.session_state.last = f"암술 {fR}{fY}, 수술 {mR}{mY} → {gtype} ({ptype})"

def reset():
    for k in geno: geno[k]=0
    for k in pheno: pheno[k]=0
    st.session_state.count=0
    st.session_state.last=""

# ---- UI ----
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🌼 자가수분 1회", use_container_width=True):
        simulate(1)
with col2:
    if st.button("🌻 자가수분 100회", use_container_width=True):
        simulate(100)
with col3:
    if st.button("🔄 초기화", use_container_width=True):
        reset()

# ---- 결과 ----
st.markdown("<div class='result-box'>", unsafe_allow_html=True)
if st.session_state.count > 0:
    st.write(f"**최근 결과:** {st.session_state.last}")
    st.write(f"**누적 자가수분 횟수:** {st.session_state.count}")

    # 유전자형 누적
    st.markdown("#### 🧬 유전자형 누적 (순서 유지)")
    st.text("\n".join([f"{k}: {v}" for k,v in geno.items()]))

    # 표현형 누적
    st.markdown("#### 🌼 표현형 누적 (순서 유지)")
    st.text("\n".join([f"{k}: {v}" for k,v in pheno.items()]))

    # --- 그래프: 유전자형 ---
    st.markdown("#### 📈 유전자형 분포")
    fig1 = go.Figure(data=[go.Bar(
        x=list(geno.keys()), y=list(geno.values()),
        marker_color="#4CAF50"
    )])
    fig1.update_layout(height=350, margin=dict(l=20,r=20,t=40,b=20))
    st.plotly_chart(fig1, use_container_width=True)

    # --- 그래프: 표현형 ---
    st.markdown("#### 📊 표현형 분포")
    fig2 = go.Figure(data=[go.Bar(
        x=list(pheno.keys()), y=list(pheno.values()),
        marker_color="#FFD54F"
    )])
    fig2.update_layout(height=350, margin=dict(l=20,r=20,t=40,b=20))
    st.plotly_chart(fig2, use_container_width=True)

else:
    st.info("자가수분을 실행하면 결과가 여기에 표시됩니다 🌱")

st.markdown("</div>", unsafe_allow_html=True)