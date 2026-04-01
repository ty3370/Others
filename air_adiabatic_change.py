import streamlit as st
import streamlit.components.v1 as components

# 1. 페이지 설정
st.set_page_config(page_title="Interactive Adiabatic Parcel", layout="wide")

st.title("🌪️ 단열 변화 인터랙티브 시뮬레이터")
st.markdown("사이드바에서 물리 상수를 조절하고, 화면에서 마우스를 움직여 고도를 변화시켜 보세요.")

# 2. 사이드바 슬라이더 설정 (사용자 조절 변수)
st.sidebar.header("⚙️ 환경 및 물리 변수")

# 단열 지수 (보통 공기는 1.4)
s_gamma = st.sidebar.slider("단열 지수 (Gamma: γ)", 1.1, 1.7, 1.4, 0.01)

# 지표면 기온 (K)
s_temp_g = st.sidebar.slider("지표면 기온 (K)", 250.0, 320.0, 288.15, 0.1)

# 지표면 기압 (kPa)
s_press_g = st.sidebar.slider("지표면 기압 (kPa)", 80.0, 120.0, 101.3, 0.1)

# 기온 감률 (Lapse Rate)
s_lapse = st.sidebar.slider("기온 감률 (Lapse Rate, K/m)", 0.001, 0.01, 0.0065, 0.0005, format="%.4f")

# 공기 덩어리 질량 (kg)
s_mass = st.sidebar.number_input("공기 덩어리 질량 (kg)", value=1.0, step=0.1)

# 3. p5.js 시각화 코드 (f-string을 사용하여 Python 변수를 JS로 전달)
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
// --- Python에서 넘어온 변수들 ---
const gamma = {s_gamma};
const initialTemperatureGround = {s_temp_g};
const initialPressureGround = {s_press_g};
const lapseRate = {s_lapse};
const airParcelMass = {s_mass};

const R_specific = 287.05;
const g = 9.81;

let minAltitude = 0;
let maxAltitude = 10000;

let minVolumeAtGround;
let maxVolumeAtAltitude;

function setup() {{
  createCanvas(window.innerWidth, window.innerHeight);

  // 1. 최소 부피 계산 (지표면)
  minVolumeAtGround = airParcelMass * R_specific * initialTemperatureGround / (initialPressureGround * 1000);

  // 2. 최대 고도에서의 최대 부피 계산 (정규화를 위해)
  let pMaxAlt = initialPressureGround * pow(1 - (lapse_rate * maxAltitude) / initialTemperatureGround, g / (R_specific * lapseRate));
  let tParcelMaxAlt = initialTemperatureGround * pow(pMaxAlt / initialPressureGround, (gamma - 1) / gamma);
  maxVolumeAtAltitude = airParcelMass * R_specific * tParcelMaxAlt / (pMaxAlt * 1000);

  textAlign(LEFT, CENTER);
}}

function draw() {{
  background(173, 216, 230); // 하늘색 배경

  let groundY = height - 60;
  let airParcelX = width / 2;

  // 마우스 위치로 고도 결정
  let mouseYConstrained = constrain(mouseY, 50, groundY - 50);
  let currentAltitude = map(mouseYConstrained, groundY - 50, 50, minAltitude, maxAltitude);

  // --- 물리량 계산 ---
  // 주변 기압 계산
  let currentPressureAmbient = initialPressureGround * pow(1 - (lapseRate * currentAltitude) / initialTemperatureGround, g / (R_specific * lapseRate));
  
  // 단열 변화에 따른 공기 덩어리 온도 계산
  let currentTemperatureAirParcel = initialTemperatureGround * pow(currentPressureAmbient / initialPressureGround, (gamma - 1) / gamma);
  
  // 공기 덩어리 부피 계산
  let currentVolumeAirParcel = airParcelMass * R_specific * currentTemperatureAirParcel / (currentPressureAmbient * 1000);

  // --- 시각화 요소 결정 ---
  // 1. 공기 덩어리 크기 (부피에 비례하여 반지름 결정)
  let rawRadiusFactor = sqrt(currentVolumeAirParcel / PI);
  let minRawRadius = sqrt(minVolumeAtGround / PI);
  let maxRawRadius = sqrt(maxVolumeAtAltitude / PI);
  
  // 최소 40px, 최대 120px 사이로 크기 매핑
  let displayRadius = map(rawRadiusFactor, minRawRadius, maxRawRadius, 40, 120);

  // 2. 외부 압력 화살표 길이 (주변 기압에 비례)
  let externalArrowLength = map(currentPressureAmbient, 0, initialPressureGround * 1.5, 5, 50);

  // --- 그리기 ---
  // 공기 덩어리 (원)
  fill(255, 255, 255, 200);
  stroke(255);
  strokeWeight(2);
  ellipse(airParcelX, mouseYConstrained, displayRadius * 2, displayRadius * 2);

  // 화살표 그리기
  let numArrows = 8;
  let arrowAngleStep = TWO_PI / numArrows;
  let arrowHeadSize = 6;

  push();
  translate(airParcelX, mouseYConstrained);
  
  for (let i = 0; i < numArrows; i++) {{
    let angle = i * arrowAngleStep;

    // 외부 기압 화살표 (밖에서 안으로) - 파란색 계열
    stroke(0, 50, 150);
    let extStartX = (displayRadius + externalArrowLength) * cos(angle);
    let extStartY = (displayRadius + externalArrowLength) * sin(angle);
    let extEndX = displayRadius * cos(angle);
    let extEndY = displayRadius * sin(angle);
    line(extStartX, extStartY, extEndX, extEndY);

    // 화살표 머리
    push();
    translate(extEndX, extEndY);
    rotate(angle + PI);
    line(0, 0, -arrowHeadSize, -arrowHeadSize * 0.6);
    line(0, 0, -arrowHeadSize, arrowHeadSize * 0.6);
    pop();

    // 내부 팽창력 화살표 (안에서 밖으로) - 주황색 계열
    stroke(200, 80, 0);
    let intStartX = (displayRadius - 25) * cos(angle);
    let intStartY = (displayRadius - 25) * sin(angle);
    let intEndX = displayRadius * cos(angle);
    let intEndY = displayRadius * sin(angle);
    line(intStartX, intStartY, intEndX, intEndY);
    
    push();
    translate(intEndX, intEndY);
    rotate(angle);
    line(0, 0, -arrowHeadSize, -arrowHeadSize * 0.6);
    line(0, 0, -arrowHeadSize, arrowHeadSize * 0.6);
    pop();
  }}
  pop();

  // 지면
  stroke(100, 70, 40);
  strokeWeight(4);
  line(0, groundY, width, groundY);

  // 정보 텍스트 표시
  noStroke();
  fill(0);
  textSize(15);
  text("🏠 Ground Level", width - 130, groundY + 25);
  
  textSize(14);
  let infoY = 40;
  fill(30);
  text("📍 현재 고도: " + nf(currentAltitude, 0, 0) + " m", 20, infoY);
  text("🌪️ 주변 기압: " + nf(currentPressureAmbient * 10, 0, 1) + " hPa", 20, infoY + 25);
  text("📦 덩어리 부피: " + nf(currentVolumeAirParcel, 0, 3) + " m³", 20, infoY + 50);
  text("🌡️ 덩어리 온도: " + nf(currentTemperatureAirParcel - 273.15, 0, 1) + " °C", 20, infoY + 75);
}}

function windowResized() {{
  resizeCanvas(window.innerWidth, window.innerHeight);
}}
</script>
</body>
</html>
"""

# 4. Streamlit에 HTML/JS 렌더링
components.html(p5_code, height=650)

# 5. 하단 설명
st.info("""
**시각화 가이드:**
- **원의 크기**: 단열 팽창 법칙($PV^\gamma = const$)에 따라 고도가 높아질수록(기압이 낮아질수록) 부피가 커집니다.
- **파란색 화살표 (외부)**: 주변 기압을 의미합니다. 고도가 높아질수록 기압이 낮아져 화살표 길이가 짧아집니다.
- **주황색 화살표 (내부)**: 공기 덩어리 내부의 압력을 의미합니다.
""")