import streamlit as st
import streamlit.components.v1 as components

# 1. 페이지 설정
st.set_page_config(page_title="Interactive Adiabatic Simulation", layout="wide")

st.title("🌪️ 단열 변화 인터랙티브 시뮬레이터")

# 2. 사이드바 설정 (변수 조절)
st.sidebar.header("⚙️ 환경 변수 조절")
s_gamma = st.sidebar.slider("단열 지수 (Gamma)", 1.1, 1.7, 1.4, 0.01)
s_temp_g = st.sidebar.slider("지표면 기온 (K)", 200.0, 400.0, 288.15, 0.1)
s_press_g = st.sidebar.slider("지표면 기압 (kPa)", 50.0, 150.0, 101.3, 0.1)
s_lapse = st.sidebar.slider("기온 감률 (K/m)", 0.001, 0.02, 0.0065, 0.0001, format="%.4f")
s_mass = st.sidebar.number_input("공기 질량 (kg)", value=1.0, step=0.1)

# 3. JavaScript 코드 작성 (로직 강화)
# 변수가 바뀔 때마다 f-string을 통해 JS 상수가 새로 주입됩니다.
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
const maxAlt = 10000;

let minVol, maxVol;

function setup() {{
  createCanvas(window.innerWidth, window.innerHeight);
  
  // 현재 파라미터 기준 지표면 부피 계산
  minVol = (MASS * R_SPECIFIC * T0) / (P0 * 1000);
  
  // 현재 파라미터 기준 10km 상공 부피 계산 (스케일링용)
  let pAtMax = P0 * pow(1 - (LAPSE * maxAlt) / T0, G / (R_SPECIFIC * LAPSE));
  let tAtMax = T0 * pow(pAtMax / P0, (GAMMA - 1) / GAMMA);
  maxVol = (MASS * R_SPECIFIC * tAtMax) / (pAtMax * 1000);

  textAlign(LEFT, CENTER);
}}

function draw() {{
  background(173, 216, 230);

  let groundY = height - 60;
  let centerX = width / 2;

  // 마우스 위치 및 고도 계산
  let mY = constrain(mouseY, 50, groundY - 50);
  let alt = map(mY, groundY - 50, 50, 0, maxAlt);

  // 물리 법칙 계산
  let pAmb = P0 * pow(1 - (LAPSE * alt) / T0, G / (R_SPECIFIC * LAPSE));
  let tParcel = T0 * pow(pAmb / P0, (GAMMA - 1) / GAMMA);
  let volParcel = (MASS * R_SPECIFIC * tParcel) / (pAmb * 1000);

  // 반지름 시각화 (극단적인 변화도 잘 보이도록 범위 확장)
  // 현재 설정된 조건에서의 minVol과 maxVol 사이에서 원의 크기를 40~150 사이로 매핑
  let r = map(sqrt(volParcel), sqrt(minVol), sqrt(maxVol), 40, 150);

  // 공기 덩어리 본체
  fill(255, 255, 255, 180);
  stroke(255);
  strokeWeight(2);
  ellipse(centerX, mY, r * 2, r * 2);

  // 화살표 그리기 (외부/내부 모두 표시)
  let extArrowLen = map(pAmb, 0, 150, 5, 60); // 기압에 따른 길이 변화
  drawArrows(centerX, mY, r, extArrowLen);

  // 정보창
  drawInfo(alt, pAmb, volParcel, tParcel);

  // 지면
  stroke(100, 70, 40);
  strokeWeight(4);
  line(0, groundY, width, groundY);
}}

function drawArrows(x, y, r, extLen) {{
  let num = 8;
  for (let i = 0; i < num; i++) {{
    let angle = i * (TWO_PI / num);
    
    // 1. 외부 기압 화살표 (파란색, 밖에서 안으로)
    stroke(0, 50, 200);
    strokeWeight(2);
    let x1_ext = x + (r + extLen) * cos(angle);
    let y1_ext = y + (r + extLen) * sin(angle);
    let x2_ext = x + r * cos(angle);
    let y2_ext = y + r * sin(angle);
    line(x1_ext, y1_ext, x2_ext, y2_ext);
    
    // 외부 화살표 머리
    push();
    translate(x2_ext, y2_ext);
    rotate(angle + PI);
    line(0, 0, -6, -4);
    line(0, 0, -6, 4);
    pop();

    // 2. 내부 팽창력 화살표 (주황색, 안에서 밖으로)
    stroke(255, 100, 0);
    let intLen = 25; // 내부 화살표는 고정 길이 혹은 부피 비례 가능
    let x1_int = x + (r - intLen) * cos(angle);
    let y1_int = y + (r - intLen) * sin(angle);
    let x2_int = x + r * cos(angle);
    let y2_int = y + r * sin(angle);
    line(x1_int, y1_int, x2_int, y2_int);

    // 내부 화살표 머리
    push();
    translate(x2_ext, y2_ext);
    rotate(angle);
    line(0, 0, -6, -4);
    line(0, 0, -6, 4);
    pop();
  }}
}}

function drawInfo(alt, p, v, t) {{
  noStroke();
  fill(0);
  textSize(16);
  let textX = 25;
  text("📏 Altitude: " + nf(alt, 0, 0) + " m", textX, 40);
  text("☁️ Ambient P: " + nf(p * 10, 0, 1) + " hPa", textX, 65);
  text("📦 Parcel Vol: " + nf(v, 0, 3) + " m³", textX, 90);
  text("🌡️ Parcel Temp: " + nf(t - 273.15, 0, 1) + " °C", textX, 115);
  
  textSize(12);
  fill(100);
  text("Gamma: " + GAMMA + " | T0: " + T0 + "K | P0: " + P0 + "kPa", textX, 145);
}}

function windowResized() {{
  resizeCanvas(window.innerWidth, window.innerHeight);
}}
</script>
</body>
</html>
"""

# 4. Streamlit 컴포넌트 호출
# 'key' 인자에 슬라이더 변수들을 튜플로 묶어 전달하면, 변수가 바뀔 때마다 컴포넌트가 강제로 새로고침됩니다.
components.html(
    p5_code, 
    height=750, 
    key=f"p5_sim_{s_gamma}_{s_temp_g}_{s_press_g}_{s_lapse}_{s_mass}"
)