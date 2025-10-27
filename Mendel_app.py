import streamlit as st
import random
import plotly.graph_objects as go

# ---- 페이지 설정 ----
st.set_page_config(page_title="완두 자가수분 시뮬레이터", page_icon="🌱", layout="centered")

# ---- 스타일 ----
st.markdown("""
<style>
    .stApp { background-color: #fafafa; font-family: 'Noto Sans KR', sans-serif; }
    .title {
        text-align:center;
        font-size:2em;
        color:#2e7d32;
        font-weight:700;
        margin-bottom:0.2em;
    }
    .subtitle {
        text-align:center;
        color:#8e24aa; /* 보라색 */
        font-size:1.6em;
        font-weight:700;
        margin-bottom:1.5em;
    }
    .purple-heart {
        color:#8e24aa;
        font-size:1.6em;
        margin:0 8px;
    }
</style>
""", unsafe_allow_html=True)

# ---- 제목 및 학교명 ----
st.markdown("<div class='title'>🌿 완두 자가수분 시뮬레이터</div>", unsafe_allow_html=True)
st.markdown("""
<div class='subtitle'>
    <span class='purple-heart'>💜</span>
    보라중학교
    <span class='purple-heart'>💜</span>
</div>
""", unsafe_allow_html=True)

# ---- 데이터 정의 ----
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

geno, pheno = st.session_state.geno, st.session_state.pheno

# ---- 함수 ----
def simulate(n=1):
    for _ in range(n):
        fR, fY, mR, mY = random.choice("Rr"), random.choice("Yy"), random.choice("Rr"), random.choice("Yy")
        g = ''.join(sorted([fR,mR])) + ''.join(sorted([fY,mY]))
        p = GENO2PHENO[g]
        geno[g]+=1; pheno[p]+=1
        st.session_state.count += 1
        st.session_state.last = f"암술 {fR}{fY}, 수술 {mR}{mY} → {g} ({p})"

def reset():
    for k in geno: geno[k]=0
    for k in pheno: pheno[k]=0
    st.session_state.count=0
    st.session_state.last=""

# ---- 버튼 ----
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
if st.session_state.count > 0:
    st.write(f"**최근 결과:** {st.session_state.last}")
    st.write(f"**누적 자가수분 횟수:** {st.session_state.count}")

    st.markdown("#### 🧬 유전자형 누적")
    st.text("\n".join([f"{k}: {v}" for k,v in geno.items()]))

    st.markdown("#### 🌼 표현형 누적")
    st.text("\n".join([f"{k}: {v}" for k,v in pheno.items()]))

    # ---- 유전자형 그래프 (개수 기준) ----
    st.markdown("#### 📈 유전자형 개수")
    fig1 = go.Figure(data=[
        go.Bar(x=list(geno.keys()), y=list(geno.values()), text=[str(v) for v in geno.values()],
               textposition='outside', marker_color="#4CAF50")
    ])
    fig1.update_layout(yaxis_title="개수", height=350, margin=dict(l=10,r=10,t=40,b=20))
    st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar": False})

    # ---- 표현형 그래프 (개수 기준) ----
    st.markdown("#### 📊 표현형 개수")
    fig2 = go.Figure(data=[
        go.Bar(x=list(pheno.keys()), y=list(pheno.values()), text=[str(v) for v in pheno.values()],
               textposition='outside', marker_color="#AB47BC")
    ])
    fig2.update_layout(yaxis_title="개수", height=350, margin=dict(l=10,r=10,t=40,b=20))
    st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

else:
    st.info("자가수분을 실행하면 결과가 여기에 표시됩니다 🌱")