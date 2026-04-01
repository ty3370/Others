import streamlit as st
import streamlit.components.v1 as components

# 1. 페이지 설정
st.set_page_config(page_title="Adiabatic Simulation", layout="wide")

st.title("🌪️ 단열 변화 인터랙티브 시뮬레이터")

# 2. 사이드바 설정
st.sidebar.header("⚙️ 환경 변수 조절")
s_gamma = st.sidebar.slider("단열 지수 (Gamma)", 1.1, 1.7, 1.4, 0.01)
s_temp_g = st.sidebar.slider("지표면 기온 (K)", 250.0, 320.0, 288.15, 0.1)
s_press_g = st.sidebar.slider("지표면 기압 (kPa)", 80.0, 120.0, 101.3, 0.1)
s_lapse = st.sidebar.slider("기온 감률 (K/m)", 0.001, 0.01, 0.0065, 0.0001, format="%.4f")
s_mass = st.sidebar.number_input("공기 질량 (kg)", value=1.0, step=0.1)

# 3. HTML/JavaScript 코드 (변수명 오타 수정 및 안정성 강화)
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
// Python에서 넘어온 값을 상수로 고정
const GAMMA = {s_gamma};
const T0 = {s_temp_g};
const P0 = {s_press_g};
const LAPSE = {s_lapse};
const MASS = {s_mass};

const R_SPECIFIC = 287.05;
const G = 9.81;

let minVol, maxVol;
const maxAlt = 10000;

function setup() {{
  // 부모 요소(Streamlit iframe)의 크기에 맞게 생성
  createCanvas(window.innerWidth, window.innerHeight);
  
  // 지표면 부피 (최소값 기준)
  minVol = (MASS * R_SPECIFIC * T0) / (P0 * 1000);
  
  // 10km 상공에서의 부피 계산 (최대값 기준)
  let pAtMax = P0 * pow(1 - (LAPSE * maxAlt) / T0, G / (R_SPECIFIC * LAPSE));
  let tAtMax = T0 * pow(pAtMax / P0, (GAMMA - 1) / GAMMA);
  maxVol = (MASS * R_SPECIFIC * tAtMax) / (pAtMax * 1000);

  textAlign(LEFT, CENTER);
}}

function draw() {{
  background(173, 216, 230);

  let groundY = height - 60;
  let centerX = width / 2;

  // 마우스 위치 제한 및 고도 매핑
  let mY = constrain(mouseY, 50, groundY - 50);
  let alt = map(mY, groundY - 50, 50, 0, maxAlt);

  // 물리 계산
  let pAmb = P0 * pow(1 - (LAPSE * alt) / T0, G / (R_SPECIFIC * LAPSE));
  let tParcel = T0 * pow(pAmb / P0, (GAMMA - 1) / GAMMA);
  let volParcel = (MASS * R_SPECIFIC * tParcel) / (pAmb * 1000);

  // 반지름 결정 (부피의 제곱근에 비례)
  let r = map(sqrt(volParcel), sqrt(minVol), sqrt(maxVol), 40, 120);

  // 공기 덩어리 그리기
  fill(255, 255, 255, 200);
  stroke(255);
  strokeWeight(2);
  ellipse(centerX, mY, r * 2, r * 2);

  // 화살표 표시 (기압 시각화)
  let arrowLen = map(pAmb, 0, P0 * 1.2, 5, 50);
  drawArrows(centerX, mY, r, arrowLen);

  // 정보 텍스트
  drawInfo(alt, pAmb, volParcel, tParcel);

  // 지면
  stroke(100, 70, 40);
  strokeWeight(4);
  line(0, groundY, width, groundY);
}}

function drawArrows(x, y, r, len) {{
  let num = 8;
  for (let i = 0; i < num; i++) {{
    let angle = i * (TWO_PI / num);
    
    // 외부 기압 (파란색)
    stroke(0, 80, 200);
    let x1 = x + (r + len) * cos(angle);
    let y1 = y + (r + len) * sin(angle);
    let x2 = x + r * cos(angle);
    let y2 = y + r * sin(angle);
    line(x1, y1, x2, y2);
    
    // 화살표 머리
    push();
    translate(x2, y2);
    rotate(angle + PI);
    line(0, 0, -5, -3);
    line(0, 0, -5, 3);
    pop();
  }}
}}

function drawInfo(alt, p, v, t) {{
  noStroke();
  fill(30);
  textSize(16);
  text("📍 Altitude: " + nf(alt, 0, 0) + " m", 20, 40);
  text("🌪️ Pressure: " + nf(p * 10, 0, 1) + " hPa", 20, 65);
  text("📦 Volume: " + nf(v, 0, 3) + " m³", 20, 90);
  text("🌡️ Parcel Temp: " + nf(t - 273.15, 0, 1) + " °C", 20, 115);
}}

function windowResized() {{
  resizeCanvas(window.innerWidth, window.innerHeight);
}}
</script>
</body>
</html>
"""

# HTML 컴포넌트 실행
components.html(p5_code, height=700)