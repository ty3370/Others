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

  // 초기 상태 및 최대 고도에서의 부피 계산 (매핑용)
  let pressureAtGround = initialPressureGround;
  minVolumeAtGround = airParcelMass * R_specific * initialTemperatureGround / (pressureAtGround * 1000);

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

  // 외부 압력 계산 (지표 기압과 감률의 영향)
  currentTemperatureAmbient = initialTemperatureGround - lapseRate * currentAltitude;
  currentPressureAmbient = initialPressureGround * pow(1 - (lapseRate * currentAltitude) / initialTemperatureGround, g / (R_specific * lapseRate));

  // 단열 변화에 따른 공기 내부 온도 및 부피 계산
  if (currentAltitude === 0) {{
    currentTemperatureAirParcel = initialTemperatureGround;
  }} else {{
    currentTemperatureAirParcel = initialTemperatureGround * pow(currentPressureAmbient / initialPressureGround, (gamma - 1) / gamma);
  }}
  currentVolumeAirParcel = airParcelMass * R_specific * currentTemperatureAirParcel / (currentPressureAmbient * 1000);

  // 부피 시각화 (반지름 결정)
  let rawRadiusFactor = sqrt(currentVolumeAirParcel / PI);
  let minRawRadiusFactor = sqrt(minVolumeAtGround / PI);
  let maxRawRadiusFactor = sqrt(maxVolumeAtAltitude / PI);
  let displayRadius = map(rawRadiusFactor, minRawRadiusFactor, maxRawRadiusFactor, 40, 100);
  displayRadius = constrain(displayRadius, 40, 120);

  // 공기 덩어리 그리기
  fill(255, 255, 255, 180);
  noStroke();
  ellipse(airParcelX, mouseYConstrained, displayRadius * 2, displayRadius * 2);

  // --- 화살표 로직 수정 ---
  // 외부 및 내부 화살표 길이를 현재 기압(currentPressureAmbient)에 연동
  // 기압이 낮아질수록(상승할수록) 화살표의 길이가 짧아짐
  let dynamicArrowLength = map(currentPressureAmbient, 0, initialPressureGround * 1.2, 5, 40);

  let numArrows = 8;
  let arrowAngleStep = TWO_PI / numArrows;
  let arrowHeadSize = 5;

  push();
  translate(airParcelX, mouseYConstrained);
  stroke(50, 50, 50);
  strokeWeight(2);

  for (let i = 0; i < numArrows; i++) {{
    let angle = i * arrowAngleStep;

    // 외부 압력 화살표 (밖에서 안으로)
    let externalStartX = (displayRadius + dynamicArrowLength) * cos(angle);
    let externalStartY = (displayRadius + dynamicArrowLength) * sin(angle);
    let externalEndX = displayRadius * cos(angle);
    let externalEndY = displayRadius * sin(angle);
    line(externalStartX, externalStartY, externalEndX, externalEndY);

    push();
    translate(externalEndX, externalEndY);
    rotate(angle + PI);
    line(0, 0, -arrowHeadSize, -arrowHeadSize * 0.6);
    line(0, 0, -arrowHeadSize, arrowHeadSize * 0.6);
    pop();

    // 내부 압력 화살표 (안에서 밖으로 - 길이를 dynamicArrowLength로 변경하여 평형 시각화)
    let internalStartX = (displayRadius - dynamicArrowLength) * cos(angle);
    let internalStartY = (displayRadius - dynamicArrowLength) * sin(angle);
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

  // 텍스트 정보 출력
  fill(0);
  noStroke();
  text("Altitude: " + nf(currentAltitude, 0, 0) + " m", 30, 40);
  text("Ambient Pressure: " + nf(currentPressureAmbient * 10, 0, 1) + " hPa", 30, 65);
  text("Air Parcel Volume: " + nf(currentVolumeAirParcel, 0, 2) + " m³", 30, 90);
  text("Air Parcel Temp: " + nf(currentTemperatureAirParcel - 273.15, 0, 1) + " °C", 30, 115);
  text("마우스를 위아래로 움직여 고도를 조절하세요.", 30, 145);

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
### 💡 반영된 물리 원리
1. **기압과 화살표 길이**: `s_press`(지표 기압)와 `s_lapse`(감률)에 의해 계산된 현재 기압이 화살표 길이에 직접 반영됩니다. 고도가 높아져 기압이 낮아지면 화살표가 짧아집니다.
2. **내부/외부 압력 평형**: 원래 코드에서 고정값이었던 내부 화살표 길이를 외부 기압 화살표와 동일하게 설정하여, 단열 팽창 시 안팎의 압력이 평형을 이루며 함께 작아지는 것을 묘사했습니다.
3. **부피 변화**: `s_gamma`(단열 지수)와 `s_temp`(지표 기온)가 공기 덩어리의 온도 변화와 부피 팽창 속도에 영향을 주어 원의 크기가 결정됩니다.
""")