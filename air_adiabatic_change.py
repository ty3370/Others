import streamlit as st
import streamlit.components.v1 as components

# 페이지 설정
st.set_page_config(page_title="공기의 단열 팽창 시뮬레이션", layout="wide")

# 사이드바에서 변수 조절
st.sidebar.header("🕹️ 제어 패러미터")
s_gamma = st.sidebar.slider("단열 지수 (Gamma)", 1.1, 1.7, 1.4, 0.01)
s_temp = st.sidebar.slider("지표면 기온 (K)", 250.0, 320.0, 288.15, 0.1)
s_press = st.sidebar.slider("지표면 기압 (kPa)", 80.0, 120.0, 101.3, 0.1)
s_lapse = st.sidebar.slider("기온 감률 (Lapse Rate)", 0.001, 0.01, 0.0065, 0.0001, format="%.4f")

# 사용 방법 (위치 변경: 시뮬레이션 위로)
st.markdown("""

### 💡 사용 방법

1. 왼쪽 사이드바의 **슬라이더**를 조절하여 물리적 환경(기온, 기압 등)을 설정합니다.

2. 메인 화면의 하늘색 영역에서 **마우스를 위아래로 움직이면** 공기 덩어리의 고도가 실시간으로 변합니다.

3. 고도에 따른 공기 덩어리의 부피 팽창과 압력 화살표, 기온의 변화를 관찰하세요.

""")

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
  background(173, 216, 230);

  let groundY = height - 50;
  let airParcelX = width / 2;

  // 터치 입력 대응: 터치 중이면 터치 좌표를, 아니면 마우스 좌표를 사용
  let inputY = (touches.length > 0) ? touches[0].y : mouseY;
  let mouseYConstrained = constrain(inputY, 50, groundY - 50);
  currentAltitude = map(mouseYConstrained, groundY - 50, 50, minAltitude, maxAltitude);

  // 1. 기온 감률이 반영된 대기압 계산 (Barometric formula)
  // 감률이 클수록 고도에 따라 currentPressureAmbient가 급격히 낮아짐
  currentPressureAmbient = initialPressureGround * pow(1 - (lapseRate * currentAltitude) / initialTemperatureGround, g / (R_specific * lapseRate));
  
  // 2. 단열 변화에 따른 내부 온도 및 부피 계산
  currentTemperatureAirParcel = initialTemperatureGround * pow(currentPressureAmbient / initialPressureGround, (gamma - 1) / gamma);
  currentVolumeAirParcel = (airParcelMass * R_specific * currentTemperatureAirParcel) / (currentPressureAmbient * 1000);

  // 3. 온도에 따른 색상 시각화 (220K ~ 320K 범위)
  let tempNorm = map(currentTemperatureAirParcel, 220, 320, 0, 1);
  tempNorm = constrain(tempNorm, 0, 1);
  let colorCool = color(100, 150, 255, 200); // 파란색
  let colorHot = color(255, 100, 100, 200);  // 빨간색
  let parcelColor = lerpColor(colorCool, colorHot, tempNorm);

  // 4. 부피 시각화 (감률에 의한 기압 변화가 크기에 반영됨)
  let displayRadius = map(sqrt(currentVolumeAirParcel), 0.5, 3.5, 30, 180);
  
  fill(parcelColor);
  noStroke();
  ellipse(airParcelX, mouseYConstrained, displayRadius * 2, displayRadius * 2);

  // --- 교육적 비평형 화살표 로직 ---
  // 외부 압력 화살표: 고도가 올라가면 기압이 낮아지므로 짧아짐
  let externalArrowLength = map(currentPressureAmbient, 10, 120, 5, 50);
  
  // 내부 압력 화살표: 교육적 목적을 위해 30을 기준으로 설정값(P0, T0)에만 반응하도록 유지 (비평형)
  let internalArrowLength = 30 * (initialPressureGround / 101.3) * (initialTemperatureGround / 288.15);

  let numArrows = 8;
  let arrowAngleStep = TWO_PI / numArrows;
  let arrowHeadSize = 5;

  push();
  translate(airParcelX, mouseYConstrained);
  stroke(50, 50, 50);
  strokeWeight(2);

  for (let i = 0; i < numArrows; i++) {{
    let angle = i * arrowAngleStep;

    // 외부 압력 (밖에서 안으로)
    let exSX = (displayRadius + externalArrowLength) * cos(angle);
    let exSY = (displayRadius + externalArrowLength) * sin(angle);
    let exEX = displayRadius * cos(angle);
    let exEY = displayRadius * sin(angle);
    line(exSX, exSY, exEX, exEY);
    push();
    translate(exEX, exEY);
    rotate(angle + PI);
    line(0, 0, -arrowHeadSize, -arrowHeadSize * 0.6);
    line(0, 0, -arrowHeadSize, arrowHeadSize * 0.6);
    pop();

    // 내부 압력 (안에서 밖으로)
    let inSX = (displayRadius - internalArrowLength) * cos(angle);
    let inSY = (displayRadius - internalArrowLength) * sin(angle);
    let inEX = displayRadius * cos(angle);
    let inEY = displayRadius * sin(angle);
    line(inSX, inSY, inEX, inEY);
    push();
    translate(inEX, inEY);
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
  text("Ambient Pressure: " + nf(currentPressureAmbient * 10, 0, 1) + " hPa", 30, 65);
  text("Parcel Temp: " + nf(currentTemperatureAirParcel - 273.15, 0, 1) + " °C", 30, 90);
  text("Volume: " + nf(currentVolumeAirParcel, 0, 2) + " m³", 30, 115);

  stroke(0);
  strokeWeight(3);
  line(0, groundY, width, groundY);
  noStroke();
  fill(0);
  text("Ground Level", width - 120, groundY - 15);
}}

// 모바일 스크롤 방지
function touchMoved() {{
  return false;
}}

function windowResized() {{
  resizeCanvas(window.innerWidth, window.innerHeight);
}}
</script>
</body>
</html>
"""

# Streamlit 화면에 HTML/JS 렌더링
components.html(p5_code, height=650)