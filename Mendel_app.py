import streamlit as st
import random
from collections import defaultdict
import matplotlib.pyplot as plt

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
st.markdown("<div class='subtitle'>독립의 법칙 포함 — 빠른 실행 & 순서 유지 버전 ⚡</div>", unsafe_allow_html=True)

# --- 유전자형과 표현형 매핑 ---
GENOTYPE_ORDER = ['RRYY', 'RrYY', 'rrYY', 'RRyy', 'Rryy', 'rryy', 'RRYy', 'RrYy', 'rrYy']
PHENOTYPE_ORDER = ['둥근 노란색 완두', '주름진 노란색 완두', '둥근 녹색 완두', '주름진 녹색 완두']

GENOTYPE_TO_PHENOTYPE = {
    'RRYY': '둥근 노란색 완두',
    'RrYY': '둥근 노란색 완두',
    'rrYY': '주름진 노란색 완두',
    'RRyy': '둥근 녹색 완두',
    'Rryy': '둥근 녹색 완두',
    'rryy': '주름진 녹색 완두',
    'RRYy': '둥근 노란색 완두',
    'RrYy': '둥근 노란색 완두',
    'rrYy': '주름진 노란색 완두'
}

# --- 세션 상태 초기화 ---
if "geno_count" not in st.session_state:
    st.session_state.geno_count = defaultdict(int)
    st.session_state.pheno_count = defaultdict(int)
    st.session_state.poll_count = 0
    st.session_state.last_result = ""

geno = st.session_state.geno_count
pheno = st.session_state.pheno_count

# --- 시뮬레이션 함수 ---
def simulate(n=1):
    for _ in range(n):
        fR, fY = random.choice(['R','r']), random.choice(['Y','y'])
        mR, mY = random.choice(['R','r']), random.choice(['Y','y'])
        offR = ''.join(sorted([fR, mR]))
        offY = ''.join(sorted([fY, mY]))
        geno_type = offR + offY
        pheno_type = GENOTYPE_TO_PHENOTYPE[geno_type]

        geno[geno_type] += 1
        pheno[pheno_type] += 1
        st.session_state.poll_count += 1
        st.session_state.last_result = f"암술: {fR}{fY}, 수술: {mR}{mY} → {geno_type} ({pheno_type})"

# --- 빠른 초기화 ---
def fast_reset():
    geno.clear()
    pheno.clear()
    st.session_state.poll_count = 0
    st.session_state.last_result = ""

# --- UI 버튼 ---
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🌼 자가수분 1회"):
        simulate(1)
with col2:
    if st.button("🌻 자가수분 100회"):
        simulate(100)
with col3:
    if st.button("🔄 초기화"):
        fast_reset()

# --- 결과 박스 ---
st.markdown("<div class='result-box'>", unsafe_allow_html=True)
if st.session_state.poll_count > 0:
    st.write(f"**최근 결과:** {st.session_state.last_result}")
    st.write(f"**누적 자가수분 횟수:** {st.session_state.poll_count}")

    # 유전자형 누적 결과
    st.markdown("#### 🧬 유전자형 누적 (순서 유지)")
    geno_lines = [f"{g}: {geno[g]}" for g in GENOTYPE_ORDER]
    st.text("\n".join(geno_lines))

    # 표현형 누적 결과
    st.markdown("#### 🌼 표현형 누적 (순서 유지)")
    pheno_lines = [f"{p}: {pheno[p]}" for p in PHENOTYPE_ORDER]
    st.text("\n".join(pheno_lines))

    # --- 그래프 시각화 ---
    st.markdown("#### 📊 결과 시각화")
    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    
    # 유전자형 그래프
    ax[0].bar(GENOTYPE_ORDER, [geno[g] for g in GENOTYPE_ORDER])
    ax[0].set_title("유전자형 분포")
    ax[0].tick_params(axis='x', rotation=45)
    
    # 표현형 그래프
    ax[1].bar(PHENOTYPE_ORDER, [pheno[p] for p in PHENOTYPE_ORDER], color='gold')
    ax[1].set_title("표현형 분포")
    ax[1].tick_params(axis='x', rotation=30)
    
    st.pyplot(fig)

else:
    st.info("자가수분을 실행하면 결과가 여기에 표시됩니다 🌱")

st.markdown("</div>", unsafe_allow_html=True)