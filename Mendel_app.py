import streamlit as st
import random
from collections import defaultdict
import plotly.graph_objects as go

# --- 페이지 설정 ---
st.set_page_config(page_title="완두 자가수분 시뮬레이터", page_icon="🌱", layout="centered")

# --- 스타일 ---
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
st.markdown("<div class='subtitle'>초고속 버전 — 독립의 법칙 포함 ⚡</div>", unsafe_allow_html=True)

# --- 기본 데이터 ---
GENO_ORDER = ['RRYY','RrYY','rrYY','RRyy','Rryy','rryy','RRYy','RrYy','rrYy']
PHENO_ORDER = ['둥근 노란색 완두','주름진 노란색 완두','둥근 녹색 완두','주름진 녹색 완두']
GENO2PHENO = {
    'RRYY':'둥근 노란색 완두','RrYY':'둥근 노란색 완두','rrYY':'주름진 노란색 완두',
    'RRyy':'둥근 녹색 완두','Rryy':'둥근 녹색 완두','rryy':'주름진 녹색 완두',
    'RRYy':'둥근 노란색 완두','RrYy':'둥근 노란색 완두','rrYy':'주름진 노란색 완두'
}

# --- 세션 상태 ---
if "geno" not in st.session_state:
    st.session_state.geno = defaultdict(int)
    st.session_state.pheno = defaultdict(int)
    st.session_state.count = 0
    st.session_state.last = ""

geno = st.session_state.geno
pheno = st.session_state.pheno

# --- 빠른 함수들 ---
def simulate(n=1):
    for _ in range(n):
        fR, fY, mR, mY = random.choice("Rr"), random.choice("Yy"), random.choice("Rr"), random.choice("Yy")
        offR, offY = ''.join(sorted([fR,mR])), ''.join(sorted([fY,mY]))
        g = offR + offY
        p = GENO2PHENO[g]
        geno[g]+=1; pheno[p]+=1; st.session_state.count+=1
        st.session_state.last = f"암술 {fR}{fY}, 수술 {mR}{mY} → {g} ({p})"

def reset():
    geno.clear(); pheno.clear()
    st.session_state.count = 0; st.session_state.last = ""

# --- 버튼 UI ---
col1,col2,col3 = st.columns(3)
with col1:
    if st.button("🌼 자가수분 1회"):
        simulate()
with col2:
    if st.button("🌻 자가수분 100회"):
        simulate(100)
with col3:
    if st.button("🔄 초기화"):
        reset()

# --- 결과 영역 ---
st.markdown("<div class='result-box'>", unsafe_allow_html=True)

if st.session_state.count:
    st.write(f"**최근 결과:** {st.session_state.last}")
    st.write(f"**누적 자가수분 횟수:** {st.session_state.count}")

    st.markdown("#### 🧬 유전자형 누적")
    st.text("\n".join([f"{g}: {geno[g]}" for g in GENO_ORDER]))

    st.markdown("#### 🌼 표현형 누적")
    st.text("\n".join([f"{p}: {pheno[p]}" for p in PHENO_ORDER]))

    # --- Plotly 그래프 ---
    st.markdown("#### 📊 시각화 결과")
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=GENO_ORDER, y=[geno[g] for g in GENO_ORDER],
        name="유전자형", marker_color="green"
    ))
    fig.add_trace(go.Bar(
        x=PHENO_ORDER, y=[pheno[p] for p in PHENO_ORDER],
        name="표현형", marker_color="goldenrod"
    ))
    fig.update_layout(barmode='group', height=400, showlegend=True)
    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("자가수분을 실행하면 결과가 여기에 표시됩니다 🌱")

st.markdown("</div>", unsafe_allow_html=True)