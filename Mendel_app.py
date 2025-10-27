import streamlit as st
import random
from collections import defaultdict

# 페이지 설정
st.set_page_config(page_title="완두 자가수분 시뮬레이터", page_icon="🌱", layout="centered")

# 스타일 (버튼, 박스, 텍스트 등)
st.markdown("""
    <style>
        .stApp {
            background-color: #f7f9f9;
            font-family: 'Noto Sans KR', sans-serif;
        }
        .title {
            text-align: center;
            font-size: 2em;
            color: #2e7d32;
            font-weight: 700;
            margin-bottom: 0.3em;
        }
        .subtitle {
            text-align: center;
            color: #558b2f;
            margin-bottom: 2em;
        }
        .result-box {
            background-color: #fffde7;
            border: 2px solid #fbc02d;
            border-radius: 10px;
            padding: 15px;
            margin-top: 10px;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='title'>🌿 완두 자가수분 시뮬레이터</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>멘델의 독립의 법칙을 포함한 자가수분 시뮬레이션</div>", unsafe_allow_html=True)

# 세션 상태 초기화
if "genotype_count" not in st.session_state:
    st.session_state.genotype_count = defaultdict(int)
    st.session_state.phenotype_count = defaultdict(int)
    st.session_state.pollination_count = 0
    st.session_state.last_result = ""

genotype_to_phenotype = {
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

def simulate_self_pollination(times=1):
    for _ in range(times):
        female_R = random.choice(['R', 'r'])
        female_Y = random.choice(['Y', 'y'])
        male_R = random.choice(['R', 'r'])
        male_Y = random.choice(['Y', 'y'])

        offspring_R_genotype = ''.join(sorted([female_R, male_R]))
        offspring_Y_genotype = ''.join(sorted([female_Y, male_Y]))
        offspring_genotype = offspring_R_genotype + offspring_Y_genotype

        offspring_phenotype = genotype_to_phenotype[offspring_genotype]

        st.session_state.genotype_count[offspring_genotype] += 1
        st.session_state.phenotype_count[offspring_phenotype] += 1
        st.session_state.pollination_count += 1

        st.session_state.last_result = (
            f"암술: {female_R}{female_Y}, 수술: {male_R}{male_Y} → "
            f"유전자형: {offspring_genotype}, 표현형: {offspring_phenotype}"
        )

def reset():
    st.session_state.genotype_count = defaultdict(int)
    st.session_state.phenotype_count = defaultdict(int)
    st.session_state.pollination_count = 0
    st.session_state.last_result = ""

# 버튼 구성
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🌼 자가수분 1회"):
        simulate_self_pollination()
with col2:
    if st.button("🌻 자가수분 100회"):
        simulate_self_pollination(100)
with col3:
    if st.button("🔄 초기화"):
        reset()

# 결과 표시
st.markdown("<div class='result-box'>", unsafe_allow_html=True)

if st.session_state.last_result:
    st.write(f"**최근 결과:** {st.session_state.last_result}")

st.write(f"**누적 자가수분 횟수:** {st.session_state.pollination_count}")

if st.session_state.pollination_count > 0:
    st.markdown("#### 🧬 유전자형 누적 통계")
    for key, val in st.session_state.genotype_count.items():
        st.write(f"- {key}: {val}")

    st.markdown("#### 🌼 표현형 누적 통계")
    for key, val in st.session_state.phenotype_count.items():
        st.write(f"- {key}: {val}")
else:
    st.info("아직 자가수분이 실행되지 않았습니다. 위의 버튼을 눌러 시작하세요 🌱")

st.markdown("</div>", unsafe_allow_html=True)