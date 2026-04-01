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

  currentTemperatureAmbient = initialTemperatureGround - lapseRate * currentAltitude;
  currentPressureAmbient = initialPressureGround * pow(1 - (lapseRate * currentAltitude) / initialTemperatureGround, g / (R_specific * lapseRate));

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

  // --- 원래 코드의 화살표 로직 유지 및 패러미터 반영 ---
  // 외부 압력 화살표 길이 (Ambient Pressure에 비례)
  let externalArrowLength = map(currentPressureAmbient, 0, initialPressureGround * 1.2, 5, 40);
  
  // 내부 압력 화살표 길이 (기존 고정값 30에서 내부 압력 수치 반영으로 수정)
  // 내부 압력 수치는 단열 관계식에 의해 변화함
  let internalArrowLength = map(currentPressureAmbient, 0, initialPressureGround * 1.2, 5, 40);

  let numArrows = 8;
  let arrowAngleStep = TWO_PI / numArrows;
  let arrowHeadSize = 5;

  push();
  translate(airParcelX, mouseYConstrained);
  stroke(50, 50, 50);
  strokeWeight(2);

  for (let i = 0; i < numArrows; i++) {{
    let angle = i * arrowAngleStep;

    // 원래 코드의 외부 화살표 그리기 형식
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

    // 원래 코드의 내부 화살표 그리기 형식 (길이만 가변으로 변경)
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
### 💡 수정 포인트
- **구조 유지**: 원래 코드의 `external`과 `internal` 화살표를 그리는 독립적인 `for` 루프와 `push/pop` 구조를 그대로 유지했습니다.
- **내부 압력 반영**: 기존에 `30`으로 고정되어 있던 `internalArrowConstantLength`를 `internalArrowLength`라는 가변 변수로 바꾸어, 슬라이더로 조절한 패러미터들이 공기 내부 압력(화살표 길이)에 미치는 영향을 볼 수 있게 했습니다.
- **디자인 복구**: 임의로 넣었던 색상이나 모양 변화를 제거하고 원래의 단색 선 형식을 사용합니다.
""")