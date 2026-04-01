import streamlit as st
import streamlit.components.v1 as components

# 페이지 설정
st.set_page_config(page_title="공기의 단열 팽창", layout="wide")

# 사이드바에서 변수 조절
st.sidebar.header("🕹️ 제어 파라미터")
s_gamma = st.sidebar.slider("단열 지수 (Gamma)", 1.1, 1.7, 1.4, 0.01)
s_temp = st.sidebar.slider("지표면 기온 (K)", 250.0, 320.0, 288.15, 0.1)
s_press = st.sidebar.slider("지표면 기압 (kPa)", 80.0, 120.0, 101.3, 0.1)
s_lapse = st.sidebar.slider("기온 감률 (Lapse Rate)", 0.001, 0.01, 0.0065, 0.0001, format="%.4f")

# JavaScript(p5.js) 코드 구성
p5_code = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.4.0/p5.js"></script>
    <style>
        body {{ margin: 0; padding: 0; overflow: hidden; }}
        canvas {{ display: block; }}
    </style>
</head>
<body>
<script>
let gamma = {s_gamma};
let initialTemperatureGround = {s_temp};
let initialPressureGround = {s_press};
let lapseRate = {s_lapse};

let R_specific = 287.05;
let g = 9.81;

let currentAltitude;
let currentPressureAmbient;
let currentTemperatureAmbient;
let currentVolumeAirParcel;
let currentTemperatureAirParcel;

let minAltitude = 0;
let maxAltitude = 10000;
let airParcelMass = 1;

let minVolumeAtGround;
let maxVolumeAtAltitude;

function setup() {{
  createCanvas(window.innerWidth, window.innerHeight);

  let tempAtGround = initialTemperatureGround;
  let pressureAtGround = initialPressureGround;
  minVolumeAtGround = airParcelMass * R_specific * tempAtGround / (pressureAtGround * 1000);

  let tempAmbientAtMaxAlt = initialTemperatureGround - lapseRate * maxAltitude;
  let pressureAmbientAtMaxAlt = initialPressureGround * pow(1 - (lapseRate * maxAltitude) / initialTemperatureGround, g / (R_specific * lapseRate));
  let tempAirParcelAtMaxAlt = initialTemperatureGround * pow(pressureAmbientAtMaxAlt / initialPressureGround, (gamma - 1) / gamma);
  maxVolumeAtAltitude = airParcelMass * R_specific * tempAirParcelAtMaxAlt / (pressureAmbientAtMaxAlt * 1000);

  textAlign(LEFT, CENTER);
  textSize(14);
}}

function draw() {{
  background(173, 216, 230);

  let groundY = height - 50;
  let airParcelX = width / 2;

  let mouseYConstrained = constrain(mouseY, 50, groundY - 50);
  currentAltitude = map(mouseYConstrained, groundY - 50, 50, minAltitude, maxAltitude);

  // 외부 환경 계산
  currentTemperatureAmbient = initialTemperatureGround - lapseRate * currentAltitude;
  currentPressureAmbient = initialPressureGround * pow(1 - (lapseRate * currentAltitude) / initialTemperatureGround, g / (R_specific * lapseRate));

  // 공기 덩어리 상태 계산
  if (currentAltitude === 0) {{
    currentTemperatureAirParcel = initialTemperatureGround;
  }} else {{
    currentTemperatureAirParcel = initialTemperatureGround * pow(currentPressureAmbient / initialPressureGround, (gamma - 1) / gamma);
  }}
  currentVolumeAirParcel = airParcelMass * R_specific * currentTemperatureAirParcel / (currentPressureAmbient * 1000);

  let rawRadiusFactor = sqrt(currentVolumeAirParcel / PI);
  let minRawRadiusFactor = sqrt(minVolumeAtGround / PI);
  let maxRawRadiusFactor = sqrt(maxVolumeAtAltitude / PI);
  
  let displayRadius = map(rawRadiusFactor, minRawRadiusFactor, maxRawRadiusFactor, 40, 100);
  displayRadius = constrain(displayRadius, 40, 120);

  fill(255, 255, 255, 180);
  noStroke();
  ellipse(airParcelX, mouseYConstrained, displayRadius * 2, displayRadius * 2);

  // --- 화살표 로직 (비평형 유지하며 패러미터 반영) ---
  
  // 1. 외부 압력 화살표 (기존 형식 유지)
  let externalArrowLength = map(currentPressureAmbient, 0, initialPressureGround * 1.2, 5, 40);
  
  // 2. 내부 압력 화살표 (원래의 '30'을 기준으로 하되 패러미터의 영향을 받음)
  // 단열 지수(gamma)가 높거나 기온(temp)이 높으면 팽창하려는 '내부 힘'이 강하게 표현되도록 설정
  // 하지만 외부 화살표와 계산식을 달리하여 의도적인 '비평형'을 시각화함
  let internalForceBase = (initialPressureGround / 101.3) * (initialTemperatureGround / 288.15) * 30;
  let internalArrowLength = internalForceBase * pow(currentVolumeAirParcel / minVolumeAtGround, -0.2); 

  let numArrows = 8;
  let arrowAngleStep = TWO_PI / numArrows;
  let arrowHeadSize = 5;

  push();
  translate(airParcelX, mouseYConstrained);
  stroke(50, 50, 50);
  strokeWeight(2);

  for (let i = 0; i < numArrows; i++) {{
    let angle = i * arrowAngleStep;

    // 외부 화살표 (원래 형식)
    let externalStartX = (displayRadius + externalArrowLength) * cos(angle);
    let externalStartY = (displayRadius + externalArrowLength) * sin(angle);
    let externalEndX = displayRadius * cos(angle);
    let externalEndY = displayRadius * sin(angle);
    line(externalStartX, externalStartY, externalEndX, externalEndY);

    push();
    translate(externalEndX, externalEndY);
    rotate(angle + PI);
    line(0, 0, -arrowHeadSize, -arrowHeadSize * 0.6);
    line(0, 0, -arrowHeadSize, arrowHeadSize * 0.6);
    pop();

    // 내부 화살표 (원래 형식, 길이는 위에서 계산한 비평형 internalArrowLength 사용)
    let internalStartX = (displayRadius - internalArrowLength) * cos(angle);
    let internalStartY = (displayRadius - internalArrowLength) * sin(angle);
    let internalEndX = displayRadius * cos(angle);
    let internalEndY = displayRadius * sin(angle);
    line(internalStartX, internalStartY, internalEndX, internalEndY);

    push();
    translate(internalEndX, internalEndY);
    rotate(angle);
    line(0, 0, -arrowHeadSize, -arrowHeadSize * 0.6);
    line(0, 0, -arrowHeadSize, arrowHeadSize * 0.6);
    pop();
  }}
  pop();

  // 텍스트 정보
  fill(0);
  noStroke();
  text("Altitude: " + nf(currentAltitude, 0, 0) + " m", 30, 40);
  text("Ambient Pressure: " + nf(currentPressureAmbient * 10, 0, 1) + " hPa", 30, 65);
  text("Air Parcel Volume: " + nf(currentVolumeAirParcel, 0, 2) + " m³", 30, 90);
  text("Air Parcel Temp: " + nf(currentTemperatureAirParcel - 273.15, 0, 1) + " °C", 30, 115);

  stroke(0);
  strokeWeight(3);
  line(0, groundY, width, groundY);
  noStroke();
  fill(0);
  text("Ground Level", width - 120, groundY - 15);
}}

function windowResized() {{
  resizeCanvas(window.innerWidth, window.innerHeight);
}}
</script>
</body>
</html>
"""

# Streamlit 화면에 HTML/JS 렌더링
components.html(p5_code, height=600)

st.markdown("""
---
### 🛠️ 수정 핵심 (교육적 비평형 유지)
* **외부 화살표**: 고도 상승에 따라 외부 기압이 낮아지면 **실시간으로 짧아집니다.** (지표 기압과 감률의 영향)
* **내부 화살표**: 기존의 고정값(`30`) 개념을 유지하되, **지표 기온과 기압 설정값**에 따라 기본 길이가 달라집니다. 또한 상승 시 외부 압력보다 **천천히 변하게 설계**하여, 둘 사이의 '길이 차이(압력차)'가 공기를 팽창시키는 동력임을 시각적으로 보여줍니다.
* **단열 지수($\gamma$)**: 이 값이 변하면 내부 온도와 부피가 변하며, 이에 따라 내부 화살표의 반응 속도가 미세하게 달라집니다.
""")