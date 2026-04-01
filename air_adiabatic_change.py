import streamlit as st
import streamlit.components.v1 as components

# 1. 페이지 설정
st.set_page_config(page_title="Adiabatic Simulation", layout="wide")

st.title("🌪️ 단열 변화 인터랙티브 시뮬레이터")

# 2. 사이드바 설정 (사용자 조절 변수)
st.sidebar.header("⚙️ 환경 변수 조절")
s_gamma = st.sidebar.slider("단열 지수 (Gamma)", 1.1, 1.7, 1.4, 0.01)
s_temp_g = st.sidebar.slider("지표면 기온 (K)", 200.0, 400.0, 288.15, 0.1)
s_press_g = st.sidebar.slider("지표면 기압 (kPa)", 50.0, 150.0, 101.3, 0.1)
s_lapse = st.sidebar.slider("기온 감률 (K/m)", 0.001, 0.02, 0.0065, 0.0001, format="%.4f")
s_mass = st.sidebar.number_input("공기 질량 (kg)", value=1.0, step=0.1)

# 3. p5.js 소스 코드 템플릿
# f-string 대신 치환 방식을 사용하여 문법 에러를 원천 차단합니다.
html_template = """
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.4.0/p5.js"></script>
    <style>
        body { margin: 0; padding: 0; overflow: hidden; background-color: #add8e6; }
        canvas { display: block; }
    </style>
</head>
<body>
<script>
const GAMMA = __GAMMA__;
const T0 = __T0__;
const P0 = __P0__;
const LAPSE = __LAPSE__;
const MASS = __MASS__;

const R_SPECIFIC = 287.05;
const G = 9.81;
const MAX_ALT = 10000;

function setup() {
  createCanvas(window.innerWidth, window.innerHeight);
  textAlign(LEFT, CENTER);
}

function draw() {
  background(173, 216, 230);

  let groundY = height - 60;
  let centerX = width / 2;

  let mY = constrain(mouseY, 50, groundY - 50);
  let alt = map(mY, groundY - 50, 50, 0, MAX_ALT);

  // --- 물리 계산 ---
  // 주변 기압
  let pAmb = P0 * pow(1 - (LAPSE * alt) / T0, G / (R_SPECIFIC * LAPSE));
  // 공기 덩어리 온도 (단열 과정)
  let tParcel = T0 * pow(pAmb / P0, (GAMMA - 1) / GAMMA);
  // 부피 계산
  let volParcel = (MASS * R_SPECIFIC * tParcel) / (pAmb * 1000);

  // 반지름 시각화 (변화가 잘 보이도록 스케일링 강화)
  let r = map(sqrt(volParcel), 0.1, 1.5, 30, 220);

  // 공기 덩어리 본체
  fill(255, 255, 255, 200);
  stroke(255);
  strokeWeight(2);
  ellipse(centerX, mY, r * 2, r * 2);

  // --- 화살표 그리기 (내부/외부 모두 포함) ---
  let num = 8;
  let extLen = map(pAmb, 50, 150, 10, 80); 
  
  for (let i = 0; i < num; i++) {
    let angle = i * (TWO_PI / num);
    
    // 1. 외부 압력 (파란색, 안으로)
    stroke(0, 80, 220);
    strokeWeight(2);
    let x1_ext = centerX + (r + extLen) * cos(angle);
    let y1_ext = mY + (r + extLen) * sin(angle);
    let x2_ext = centerX + r * cos(angle);
    let y2_ext = mY + r * sin(angle);
    line(x1_ext, y1_ext, x2_ext, y2_ext);
    
    push();
    translate(x2_ext, y2_ext);
    rotate(angle + PI);
    line(0, 0, -7, -4);
    line(0, 0, -7, 4);
    pop();

    // 2. 내부 팽창력 (주황색, 밖으로)
    stroke(255, 80, 0);
    let intLen = 35; 
    let x1_int = centerX + (r - intLen) * cos(angle);
    let y1_int = mY + (r - intLen) * sin(angle);
    let x2_int = centerX + r * cos(angle);
    let y2_int = mY + r * sin(angle);
    line(x1_int, y1_int, x2_int, y2_int);

    push();
    translate(x2_int, y2_int);
    rotate(angle);
    line(0, 0, -7, -4);
    line(0, 0, -7, 4);
    pop();
  }

  // --- 데이터 표시 ---
  noStroke();
  fill(0);
  textSize(16);
  text("📏 Altitude: " + nf(alt, 0, 0) + " m", 25, 40);
  text("☁️ Ambient Pressure: " + nf(pAmb * 10, 0, 1) + " hPa", 25, 65);
  text("📦 Parcel Volume: " + nf(volParcel, 0, 4) + " m³", 25, 90);
  text("🌡️ Parcel Temp: " + nf(tParcel - 273.15, 0, 1) + " °C", 25, 115);

  // 지면 표시
  stroke(100, 60, 30);
  strokeWeight(6);
  line(0, groundY, width, groundY);
}

function windowResized() {
  resizeCanvas(window.innerWidth, window.innerHeight);
}
</script>
</body>
</html>
"""

# 4. 값 치환 및 컴포넌트 실행
p5_code = html_template.replace("__GAMMA__", str(s_gamma)) \
                       .replace("__T0__", str(s_temp_g)) \
                       .replace("__P0__", str(s_press_g)) \
                       .replace("__LAPSE__", str(s_lapse)) \
                       .replace("__MASS__", str(s_mass))

# key값에 해시를 사용하여 TypeError를 방지하면서도 리프레시를 보장합니다.
comp_key = hash((s_gamma, s_temp_g, s_press_g, s_lapse, s_mass))
components.html(p5_code, height=750, key=str(comp_key))