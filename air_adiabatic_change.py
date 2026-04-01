import streamlit as st
import streamlit.components.v1 as components

# 1. 페이지 설정
st.set_page_config(page_title="Adiabatic Simulation", layout="wide")

st.title("🌪️ 단열 변화 인터랙티브 시뮬레이터")

# 2. 사이드바 설정 (슬라이더 변수들)
st.sidebar.header("⚙️ 환경 변수 조절")
s_gamma = st.sidebar.slider("단열 지수 (Gamma)", 1.1, 1.7, 1.4, 0.01)
s_temp_g = st.sidebar.slider("지표면 기온 (K)", 200.0, 400.0, 288.15, 0.1)
s_press_g = st.sidebar.slider("지표면 기압 (kPa)", 50.0, 150.0, 101.3, 0.1)
s_lapse = st.sidebar.slider("기온 감률 (K/m)", 0.001, 0.02, 0.0065, 0.0001, format="%.4f")
s_mass = st.sidebar.number_input("공기 질량 (kg)", value=1.0, step=0.1)

# 3. p5.js 소스 코드
# 변수 변화를 즉시 반영하기 위해 f-string을 사용합니다.
p5_code = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.4.0/p5.js"></script>
    <style>
        body {{ margin: 0; padding: 0; overflow: hidden; background-color: #add8e6; }}
        canvas {{ display: block; }}
    </style>
</head>
<body>
<script>
// Python에서 주입된 상수들
const GAMMA = {s_gamma};
const T0 = {s_temp_g};
const P0 = {s_press_g};
const LAPSE = {s_lapse};
const MASS = {s_mass};

const R_SPECIFIC = 287.05;
const G = 9.81;
const MAX_ALT = 10000;

function setup() {{
  createCanvas(window.innerWidth, window.innerHeight);
  textAlign(LEFT, CENTER);
}}

function draw() {{
  background(173, 216, 230);

  let groundY = height - 60;
  let centerX = width / 2;

  // 마우스 위치 및 고도 계산
  let mY = constrain(mouseY, 50, groundY - 50);
  let alt = map(mY, groundY - 50, 50, 0, MAX_ALT);

  // --- 물리 법칙 계산 ---
  // 1. 주변 기압 (P = P0 * (1 - Lh/T0)^(g/RL))
  let pAmb = P0 * pow(1 - (LAPSE * alt) / T0, G / (R_SPECIFIC * LAPSE));
  
  // 2. 공기 덩어리 온도 (T = T0 * (P/P0)^((gamma-1)/gamma))
  let tParcel = T0 * pow(pAmb / P0, (GAMMA - 1) / GAMMA);
  
  // 3. 부피 계산 (V = mRT / P)
  let volParcel = (MASS * R_SPECIFIC * tParcel) / (pAmb * 1000);

  // --- 시각화 크기 결정 ---
  // 부피에 따라 반지름(r) 결정 (부피의 세제곱근 혹은 제곱근으로 스케일링)
  // 여기서는 변화가 뚜렷하도록 sqrt를 사용하고 범위를 넓게 잡았습니다.
  let r = map(sqrt(volParcel), 0.1, 1.5, 30, 200);

  // 공기 덩어리 그리기
  fill(255, 255, 255, 180);
  stroke(255);
  strokeWeight(2);
  ellipse(centerX, mY, r * 2, r * 2);

  // --- 화살표 그리기 (외부/내부) ---
  let num = 8;
  let extArrowLen = map(pAmb, 50, 150, 10, 60); // 기압이 높을수록 외부 화살표가 길어짐
  
  for (let i = 0; i < num; i++) {{
    let angle = i * (TWO_PI / num);
    
    // 1. 외부 압력 (파란색, 안으로 향함)
    stroke(0, 70, 200);
    strokeWeight(2);
    let x1_ext = centerX + (r + extArrowLen) * cos(angle);
    let y1_ext = mY + (r + extArrowLen) * sin(angle);
    let x2_ext = centerX + r * cos(angle);
    let y2_ext = mY + r * sin(angle);
    line(x1_ext, y1_ext, x2_ext, y2_ext);
    
    // 외부 화살표 머리
    push();
    translate(x2_ext, y2_ext);
    rotate(angle + PI);
    line(0, 0, -6, -4);
    line(0, 0, -6, 4);
    pop();

    // 2. 내부 팽창력 (주황색, 밖으로 향함)
    stroke(255, 120, 0);
    let intLen = 25; 
    let x1_int = centerX + (r - intLen) * cos(angle);
    let y1_int = mY + (r - intLen) * sin(angle);
    let x2_int = centerX + r * cos(angle);
    let y2_int = mY + r * sin(angle);
    line(x1_int, y1_int, x2_int, y2_int);

    // 내부 화살표 머리
    push();
    translate(x2_int, y2_int);
    rotate(angle);
    line(0, 0, -6, -4);
    line(0, 0, -6, 4);
    pop();
  }}

  // --- 텍스트 정보 ---
  noStroke();
  fill(0);
  textSize(16);
  text("📍 Altitude: " + nf(alt, 0, 0) + " m", 25, 40);
  text("☁️ Pressure: " + nf(pAmb * 10, 0, 1) + " hPa", 25, 65);
  text("📦 Volume: " + nf(volParcel, 0, 3) + " m³", 25, 90);
  text("🌡️ Temp: " + nf(tParcel - 273.15, 0, 1) + " °C", 25, 115);

  // 지면 표시
  stroke(120, 80, 50);
  strokeWeight(5);
  line(0, groundY, width, groundY);
}}

function windowResized() {{
  resizeCanvas(window.innerWidth, window.innerHeight);
}}
</script>
</body>
</html>
"""

# 4. Streamlit 컴포넌트 실행
# key를 고정된 문자열로 변경하여 TypeError를 방지합니다.
# HTML 내용이 바뀌면 Streamlit은 알아서 iframe을 새로고침합니다.
components.html(p5_code, height=700, key="adiabatic_sim_main")