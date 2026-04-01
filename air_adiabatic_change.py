import streamlit as st
import streamlit.components.v1 as components

# 페이지 설정
st.set_page_config(page_title="공기의 단열 팽창 시뮬레이터", layout="wide")

# 사이드바에서 변수 조절
st.sidebar.header("🕹️ 물리 제어 파라미터")
st.sidebar.markdown("각 수치가 공기의 상태에 미치는 영향을 관찰하세요.")

s_gamma = st.sidebar.slider("단열 지수 (Gamma)", 1.1, 1.7, 1.4, 0.01, help="값이 클수록 기온 하강이 빠르고 팽창 폭이 줄어듭니다.")
s_temp = st.sidebar.slider("지표면 기온 (K)", 250.0, 320.0, 288.15, 0.1, help="초기 부피(크기)를 결정합니다.")
s_press = st.sidebar.slider("지표면 기압 (kPa)", 80.0, 120.0, 101.3, 0.1, help="외부 압력의 시작점과 초기 압축도를 결정합니다.")
s_lapse = st.sidebar.slider("기온 감률 (Lapse Rate)", 0.001, 0.01, 0.0065, 0.0001, format="%.4f", help="값이 클수록 고도에 따른 외부 압력이 급격히 낮아집니다.")

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
let initialT0 = {s_temp};
let initialP0 = {s_press};
let lapseRate = {s_lapse};

let R_specific = 287.05;
let g = 9.81;

let currentAlt, currentP_amb, currentT_amb, currentV_parcel, currentT_parcel;
let minAlt = 0, maxAlt = 10000;
let airMass = 1.0;

function setup() {{
  createCanvas(window.innerWidth, window.innerHeight);
  textAlign(LEFT, CENTER);
  textSize(14);
}}

function draw() {{
  background(200, 230, 255); // 대기 배경색

  let groundY = height - 60;
  let parcelX = width / 2;

  // 1. 고도 계산 (마우스 위치)
  let mouseYConstrained = constrain(mouseY, 60, groundY - 40);
  currentAlt = map(mouseYConstrained, groundY - 40, 60, minAlt, maxAlt);

  // 2. 물리 방정식 적용
  // 외부 압력 (Barometric Formula)
  currentT_amb = initialT0 - lapseRate * currentAlt;
  currentP_amb = initialP0 * pow(1 - (lapseRate * currentAlt) / initialT0, g / (R_specific * lapseRate));

  // 단열 변화에 따른 공기 덩어리 온도 (Poisson's Equation)
  currentT_parcel = initialT0 * pow(currentP_amb / initialP0, (gamma - 1) / gamma);

  // 이상기체 상태 방정식에 따른 부피 (V = mRT/P)
  currentV_parcel = (airMass * R_specific * currentT_parcel) / (currentP_amb * 1000);

  // 3. 시각화 수치 변환
  // 부피를 반지름으로 변환 (시각적 과장을 위해 sqrt 사용 및 매핑)
  let displayRadius = map(sqrt(currentV_parcel), 0.8, 2.5, 30, 150);
  
  // 온도에 따른 색상 결정 (250K ~ 320K 매핑)
  let tempCol = map(currentT_parcel, 220, 320, 0, 1);
  let parcelColor = lerpColor(color(100, 150, 255), color(255, 100, 100), tempCol);

  // 4. 공기 덩어리 그리기
  fill(parcelColor);
  stroke(255);
  strokeWeight(2);
  ellipse(parcelX, mouseYConstrained, displayRadius * 2, displayRadius * 2);

  // 5. 압력 화살표 그리기 (내부 P_in와 외부 P_out의 평형 상태)
  // 압력이 낮아질수록 화살표 길이를 짧게 표현
  let arrowLen = map(currentP_amb, 20, 120, 10, 50);
  let numArrows = 10;
  let arrowHead = 6;

  for (let i = 0; i < numArrows; i++) {{
    let angle = TWO_PI / numArrows * i;
    
    // 외부 압력 화살표 (공기를 누름)
    let x1 = parcelX + (displayRadius + arrowLen + 5) * cos(angle);
    let y1 = mouseYConstrained + (displayRadius + arrowLen + 5) * sin(angle);
    let x2 = parcelX + (displayRadius + 5) * cos(angle);
    let y2 = mouseYConstrained + (displayRadius + 5) * sin(angle);
    stroke(50, 50, 200); // 파란색: 외부 압력
    line(x1, y1, x2, y2);
    
    // 내부 압력 화살표 (공기가 밀어냄)
    let ix1 = parcelX + (displayRadius - arrowLen - 5) * cos(angle);
    let iy1 = mouseYConstrained + (displayRadius - arrowLen - 5) * sin(angle);
    let ix2 = parcelX + (displayRadius - 5) * cos(angle);
    let iy2 = mouseYConstrained + (displayRadius - 5) * sin(angle);
    stroke(200, 50, 50); // 빨간색: 내부 압력
    line(ix1, iy1, ix2, iy2);
  }}

  // 6. 데이터 출력
  drawUI(currentAlt, currentP_amb, currentV_parcel, currentT_parcel);

  // 지표면 표현
  stroke(100);
  strokeWeight(4);
  line(0, groundY, width, groundY);
  noStroke();
  fill(50);
  text("GROUND LEVEL (P0 = " + initialP0 + " kPa)", width - 200, groundY + 25);
}}

function drawUI(alt, press, vol, temp) {{
  fill(0, 150);
  rect(10, 10, 280, 150, 10);
  fill(255);
  noStroke();
  text("현재 고도: " + nf(alt, 0, 0) + " m", 25, 35);
  text("주변 기압 (P_out): " + nf(press, 0, 2) + " kPa", 25, 60);
  text("내부 기압 (P_in): " + nf(press, 0, 2) + " kPa (평형)", 25, 85);
  text("공기 부피 (V): " + nf(vol, 0, 2) + " m³", 25, 110);
  text("공기 온도 (T): " + nf(temp - 273.15, 0, 1) + " °C", 25, 135);
  
  fill(50);
  text("💡 마우스를 위로 움직이면 공기가 상승하며 단열 팽창합니다.", 25, height - 30);
}}

function windowResized() {{
  resizeCanvas(window.innerWidth, window.innerHeight);
}}
</script>
</body>
</html>
"""

# Streamlit 화면에 HTML/JS 렌더링
components.html(p5_code, height=700)

# 하단 가이드 추가
st.info("""
**물리적 관전 포인트:**
- **단열 지수($\gamma$):** 이 값을 높이면 상승할 때 온도가 더 급격히 떨어지며, 부피 팽창 속도가 약간 둔화됩니다.
- **기온 감률:** 감률을 높이면 고도에 따른 외부 기압이 더 빨리 낮아져 공기 덩어리가 훨씬 더 크게 팽창하는 것을 볼 수 있습니다.
- **색상 변화:** 공기 덩어리가 상승하면서 에너지를 소모(일)하여 온도가 파랗게 변하는 '단열 냉각'을 확인하세요.
""")