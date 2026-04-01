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
let currentTemperatureAirParcel;
let currentVolumeAirParcel;

let minAltitude = 0;
let maxAltitude = 10000;
let airParcelMass = 1;

function setup() {{
  createCanvas(window.innerWidth, window.innerHeight);
  textAlign(LEFT, CENTER);
  textSize(14);
}}

function draw() {{
  background(173, 216, 230); // 기본 배경색

  let groundY = height - 50;
  let airParcelX = width / 2;

  // 마우스 위치에 따른 고도 계산
  let mouseYConstrained = constrain(mouseY, 50, groundY - 50);
  currentAltitude = map(mouseYConstrained, groundY - 50, 50, minAltitude, maxAltitude);

  // 대기압 및 단열 팽창 물리 법칙 적용
  currentPressureAmbient = initialPressureGround * pow(1 - (lapseRate * currentAltitude) / initialTemperatureGround, g / (R_specific * lapseRate));
  currentTemperatureAirParcel = initialTemperatureGround * pow(currentPressureAmbient / initialPressureGround, (gamma - 1) / gamma);
  currentVolumeAirParcel = (airParcelMass * R_specific * currentTemperatureAirParcel) / (currentPressureAmbient * 1000);

  // 부피를 기반으로 한 표시 반지름 계산
  let displayRadius = map(sqrt(currentVolumeAirParcel), 0.8, 2.5, 40, 120);

  // 공기 덩어리 그리기 (원래의 흰색 반투명)
  fill(255, 255, 255, 180);
  noStroke();
  ellipse(airParcelX, mouseYConstrained, displayRadius * 2, displayRadius * 2);

  // --- 화살표 로직 (기존 형식 유지, 길이만 가변) ---
  // 현재 압력에 비례하여 화살표 길이 결정
  let arrowLength = map(currentPressureAmbient, 20, 120, 10, 45);
  let numArrows = 8;
  let arrowAngleStep = TWO_PI / numArrows;
  let arrowHeadSize = 5;

  push();
  translate(airParcelX, mouseYConstrained);
  stroke(50, 50, 50); // 원래의 짙은 회색
  strokeWeight(2);

  for (let i = 0; i < numArrows; i++) {{
    let angle = i * arrowAngleStep;

    // 외부 압력 화살표 (안쪽을 향함)
    let externalStartX = (displayRadius + arrowLength) * cos(angle);
    let externalStartY = (displayRadius + arrowLength) * sin(angle);
    let externalEndX = displayRadius * cos(angle);
    let externalEndY = displayRadius * sin(angle);
    line(externalStartX, externalStartY, externalEndX, externalEndY);

    push();
    translate(externalEndX, externalEndY);
    rotate(angle + PI);
    line(0, 0, -arrowHeadSize, -arrowHeadSize * 0.6);
    line(0, 0, -arrowHeadSize, arrowHeadSize * 0.6);
    pop();

    // 내부 압력 화살표 (바깥쪽을 향함)
    let internalStartX = (displayRadius - arrowLength) * cos(angle);
    let internalStartY = (displayRadius - arrowLength) * sin(angle);
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

  // 정보 표시
  fill(0);
  noStroke();
  text("Altitude: " + nf(currentAltitude, 0, 0) + " m", 30, 40);
  text("Pressure: " + nf(currentPressureAmbient * 10, 0, 1) + " hPa", 30, 65);
  text("Volume: " + nf(currentVolumeAirParcel, 0, 2) + " m³", 30, 90);
  text("Parcel Temp: " + nf(currentTemperatureAirParcel - 273.15, 0, 1) + " °C", 30, 115);

  // 지표면
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
### 💡 수정 사항
- **화살표 디자인 고정**: 원래 코드의 단순 선 형태와 색상(`stroke(50, 50, 50)`)을 그대로 유지합니다.
- **가변 길이**: `arrowLength`를 `currentPressureAmbient`에 매핑하여, 고도가 높아지고 기압이 낮아질수록 화살표가 짧아지도록 했습니다.
- **물리적 일관성**: 내부 압력 화살표와 외부 압력 화살표가 동일한 길이를 가지며 평형을 이루는 단열 변화를 시각화합니다.
""")