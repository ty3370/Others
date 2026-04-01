import streamlit as st
import numpy as np
import plotly.graph_objects as go

# 페이지 설정
st.set_page_config(page_title="공기 덩어리 변수 조절 시뮬레이션", layout="wide")

st.title("공기 덩어리 단열 변화 시뮬레이션")

# --- 사이드바: 사용자 조절 변수 설정 ---
st.sidebar.header("🛠️ 물리 변수 설정")

# 1. 고도 (기존)
altitude = st.sidebar.slider("현재 고도 (m)", 0, 10000, 0, step=100)

st.sidebar.markdown("---")
st.sidebar.subheader("환경 변수 설정")

# 2. 지표면 초기 기온 (섭씨로 입력받아 켈빈으로 변환)
temp_ground_c = st.sidebar.slider("지표면 기온 (°C)", -20.0, 50.0, 15.0)
initial_temp_ground = temp_ground_c + 273.15

# 3. 지표면 초기 기압
initial_press_ground = st.sidebar.number_input("지표면 기압 (kPa)", value=101.3)

# 4. 기온 감률 (Lapse Rate) - 기본값 0.0065 K/m
lapse_rate = st.sidebar.slider("기온 감률 (K/m)", 0.001, 0.010, 0.0065, step=0.0001, format="%.4f")

st.sidebar.markdown("---")
st.sidebar.subheader("공기 덩어리 속성")

# 5. 단열 지수 (Gamma) - 공기는 보통 1.4
gamma = st.sidebar.slider("단열 지수 (Gamma)", 1.1, 1.7, 1.4, step=0.05)

# 6. 공기 덩어리 질량
air_parcel_mass = st.sidebar.number_input("공기 질량 (kg)", value=1.0)

# --- 고정 상수 ---
R_specific = 287.05           # J/kg·K
g = 9.81                      # m/s²

# --- 물리량 계산 로직 ---

# 1. 주변 기온
temp_ambient = initial_temp_ground - lapse_rate * altitude

# 2. 주변 기압 (기압 공식)
# 분모가 0이 되는 것을 방지하기 위해 lapse_rate가 0일 때 처리가 필요할 수 있으나 슬라이더 범위를 0.001로 제한함
press_ambient = initial_press_ground * (1 - (lapse_rate * altitude) / initial_temp_ground) ** (g / (R_specific * lapse_rate))

# 3. 공기 덩어리 내부 온도 (단열 변화 과정)
if altitude == 0:
    temp_parcel = initial_temp_ground
else:
    # Poisson's Equation: T2 = T1 * (P2/P1)^((gamma-1)/gamma)
    temp_parcel = initial_temp_ground * (press_ambient / initial_press_ground) ** ((gamma - 1) / gamma)

# 4. 공기 덩어리 부피 (V = mRT/P)
volume_parcel = (air_parcel_mass * R_specific * temp_parcel) / (press_ambient * 1000)

# --- 시각화를 위한 크기 매핑 ---
# 최소/최대 부피를 대략적으로 계산하여 원의 크기 결정
min_vol = (air_parcel_mass * R_specific * 253.15) / (101.3 * 1000) # 대략적인 최소값
max_vol = (air_parcel_mass * R_specific * 323.15) / (20.0 * 1000)  # 대략적인 최대값
display_size = np.interp(volume_parcel, [min_vol, max_vol], [50, 300])

# --- 화면 레이아웃 구성 ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📊 실시간 데이터")
    st.metric("현재 고도", f"{altitude} m")
    st.metric("주변 기압", f"{press_ambient * 10:.1f} hPa")
    st.metric("주변 기온", f"{temp_ambient - 273.15:.1f} °C")
    st.metric("공기 덩어리 온도", f"{temp_parcel - 273.15:.1f} °C", 
              delta=f"{(temp_parcel - temp_ambient):.1f} °C (주변대비)", delta_color="inverse")
    st.metric("공기 덩어리 부피", f"{volume_parcel:.3f} m³")

with col2:
    fig = go.Figure()

    # 공기 덩어리 시각화
    fig.add_trace(go.Scatter(
        x=[0], y=[altitude],
        mode="markers",
        marker=dict(
            size=display_size,
            color='rgba(255, 255, 255, 0.8)',
            line=dict(width=3, color='RoyalBlue'),
            symbol="circle"
        )
    ))

    fig.update_layout(
        xaxis=dict(range=[-1, 1], showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(range=[-500, 11000], title="고도 (m)", gridcolor='lightgray'),
        plot_bgcolor='rgb(173, 216, 230)',
        height=700,
        showlegend=False,
        title="고도에 따른 공기 덩어리 상태"
    )

    # 지면 표시
    fig.add_shape(type="rect", x0=-1, y0=-500, x1=1, y1=0, fillcolor="sienna", opacity=0.3)

    st.plotly_chart(fig, use_container_width=True)

st.success("💡 **실험 팁:** 감률(Lapse Rate)을 높이면 주변 공기가 고도에 따라 더 빨리 차가워집니다. 단열 지수(Gamma)를 바꾸면 공기 덩어리의 팽창 효율이 달라집니다.")