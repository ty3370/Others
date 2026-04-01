import streamlit as st
import streamlit.components.v1 as components

# 페이지 설정
st.set_page_config(page_title="공기의 단열 팽창 (온도 시각화)", layout="wide")

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

  // 외부 환경 및 공기 덩어리 상태 계산 (패러미터 적용 유지)
  currentTemperatureAmbient = initialTemperatureGround - lapseRate * currentAltitude;
  currentPressureAmbient = initialPressureGround * pow(1 - (lapseRate * currentAltitude) / initialTemperatureGround, g / (R_specific * lapseRate));

  if (currentAltitude === 0) {{
    currentTemperatureAirParcel = initialTemperatureGround;
  }} else {{
    currentTemperatureAirParcel = initialTemperatureGround * pow(currentPressureAmbient / initialPressureGround, (gamma - 1) / gamma);
  }}
  currentVolumeAirParcel = airParcelMass * R_specific * currentTemperatureAirParcel / (currentPressureAmbient * 1000);

  // 반지름 계산
  let rawRadiusFactor = sqrt(currentVolumeAirParcel / PI);
  let minRawRadiusFactor = sqrt(minVolumeAtGround / PI);
  let maxRawRadiusFactor = sqrt(maxVolumeAtAltitude / PI);
  let displayRadius = map(rawRadiusFactor, minRawRadiusFactor, maxRawRadiusFactor, 40, 100);
  displayRadius = constrain(displayRadius, 40, 120);

  // --- 핵심 수정: 공기 온도를 색상으로 시각화 ---
  // 온도에 따른 색상 결정 (lerpColor 사용)
  // 범위: 220K (차가움) ~ 320K (뜨거움) 매핑 (실제 온도 범위를 고려하여 조정)
  let tempNorm = map(currentTemperatureAirParcel, 220, 320, 0, 1);
  tempNorm = constrain(tempNorm, 0, 1); // 범위를 0~1로 제한

  // 차가운 색 (차가운 파란색) -> 뜨거운 색 (뜨거운 빨간색)
  // 투명도를 유지하기 위해 마지막에 알파 값을 추가
  let colorCool = color(100, 150, 255, 180);
  let colorHot = color(255, 100, 100, 180);
  let parcelColor = lerpColor(colorCool, colorHot, tempNorm);

  fill(parcelColor); // 흰색 대신 온도 기반 색상 적용
  noStroke();
  ellipse(airParcelX, mouseYConstrained, displayRadius * 2, displayRadius * 2);

  // --- 교육적 비평형 화살표 로직 (그대로 유지) ---
  let externalArrowLength = map(currentPressureAmbient, 0, initialPressureGround * 1.2, 5, 40);
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

    // 내부 화살표 (원래 형식)
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
### 🛠️ 핵심 시각화 업데이트
* **온도 색상 시각화**: 공기 덩어리(원)의 내부 온도가 **색상 그라데이션**으로 표현됩니다. 온도가 높으면 **빨간색**, 낮으면 **파란색**으로 변합니다.
* **패러미터 반응성**: 왼쪽 슬라이더를 통해 $\gamma, T_0, P_0, \Gamma$ 값을 조절하면, 공기 덩어리의 온도 계산에 영향을 주어 **실시간으로 색상이 변하는 것을 볼 수 있습니다.**
* **비평형 화살표**: 사용자의 의도대로 외부 기압 화살표는 고도에 따라 줄어들지만, 내부 기압 화살표는 사용자가 설정한 패러미터에 따라 버티는 교육적 비평형을 유지합니다.
""")