import streamlit as st
import random
import numpy as np
import pandas as pd

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
st.markdown("<div class='subtitle'>최적화된 비율 그래프 — 초고속 실행 ⚡</div>", unsafe_allow_html=True)

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
st.markdown("<div class='result-box'>", unsafe_allow_html=True)
if st.session_state.count > 0:
    st.write(f"**최근 결과:** {st.session_state.last}")
    st.write(f"**누적 자가수분 횟수:** {st.session_state.count}")

    st.markdown("#### 🧬 유전자형 누적")
    st.text("\n".join([f"{k}: {v}" for k,v in geno.items()]))

    st.markdown("#### 🌼 표현형 누적")
    st.text("\n".join([f"{k}: {v}" for k,v in pheno.items()]))

    # ---- 비율 계산 (numpy 활용, 초고속) ----
    geno_vals = np.array(list(geno.values()), dtype=float)
    pheno_vals = np.array(list(pheno.values()), dtype=float)
    geno_ratio = (geno_vals / geno_vals.sum() * 100) if geno_vals.sum() > 0 else np.zeros_like(geno_vals)
    pheno_ratio = (pheno_vals / pheno_vals.sum() * 100) if pheno_vals.sum() > 0 else np.zeros_like(pheno_vals)

    # ---- 그래프: 유전자형 ----
    st.markdown("#### 📈 유전자형 비율 (%)")
    geno_df = pd.DataFrame({"유전자형": GENO_ORDER, "비율(%)": geno_ratio})
    st.bar_chart(geno_df, x="유전자형", y="비율(%)", use_container_width=True)

    # ---- 그래프: 표현형 ----
    st.markdown("#### 📊 표현형 비율 (%)")
    pheno_df = pd.DataFrame({"표현형": PHENO_ORDER, "비율(%)": pheno_ratio})
    st.bar_chart(pheno_df, x="표현형", y="비율(%)", use_container_width=True)

else:
    st.info("자가수분을 실행하면 결과가 여기에 표시됩니다 🌱")

st.markdown("</div>", unsafe_allow_html=True)