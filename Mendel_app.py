import streamlit as st
import random
from collections import defaultdict

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
st.markdown("<div class='subtitle'>독립의 법칙 포함 / 빠른 실행 버전 ⚡</div>", unsafe_allow_html=True)

# ---- 캐시된 자료 ----
@st.cache_resource
def get_genotype_map():
    return {
        'RRYY': '둥근 노란색 완두', 'RrYY': '둥근 노란색 완두', 'rrYY': '주름진 노란색 완두',
        'RRyy': '둥근 녹색 완두', 'Rryy': '둥근 녹색 완두', 'rryy': '주름진 녹색 완두',
        'RRYy': '둥근 노란색 완두', 'RrYy': '둥근 노란색 완두', 'rrYy': '주름진 노란색 완두'
    }

genotype_to_phenotype = get_genotype_map()

# ---- 세션 상태 ----
if "data" not in st.session_state:
    st.session_state.data = {
        "genotype": defaultdict(int),
        "phenotype": defaultdict(int),
        "count": 0,
        "last": ""
    }

data = st.session_state.data

# ---- 함수 ----
def simulate(n=1):
    gmap = genotype_to_phenotype
    genos = data["genotype"]
    phenos = data["phenotype"]
    for _ in range(n):
        female_R, female_Y = random.choice(['R','r']), random.choice(['Y','y'])
        male_R, male_Y = random.choice(['R','r']), random.choice(['Y','y'])
        off_R = ''.join(sorted([female_R, male_R]))
        off_Y = ''.join(sorted([female_Y, male_Y]))
        geno = off_R + off_Y
        pheno = gmap[geno]
        genos[geno] += 1
        phenos[pheno] += 1
        data["count"] += 1
        data["last"] = f"암술: {female_R}{female_Y}, 수술: {male_R}{male_Y} → {geno} ({pheno})"

def reset():
    st.session_state.data = {
        "genotype": defaultdict(int),
        "phenotype": defaultdict(int),
        "count": 0,
        "last": ""
    }

# ---- UI ----
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🌼 1회 자가수분"):
        simulate()
with col2:
    if st.button("🌻 100회 자가수분"):
        simulate(100)
with col3:
    if st.button("🔄 초기화"):
        reset()

# ---- 결과 ----
st.markdown("<div class='result-box'>", unsafe_allow_html=True)

if data["count"]:
    if data["last"]:
        st.markdown(f"**최근 결과:** {data['last']}")
    st.write(f"**누적 자가수분 횟수:** {data['count']}")
    st.markdown("#### 🧬 유전자형 누적")
    st.text("\n".join([f"{k}: {v}" for k, v in data["genotype"].items()]))
    st.markdown("#### 🌼 표현형 누적")
    st.text("\n".join([f"{k}: {v}" for k, v in data["phenotype"].items()]))
else:
    st.info("버튼을 눌러 시뮬레이션을 시작하세요 🌱")

st.markdown("</div>", unsafe_allow_html=True)