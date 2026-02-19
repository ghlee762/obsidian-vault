# 로봇 액추에이터용 하모닉 드라이브 설계·해석 개발 가이드

## 1. 왜 하모닉 드라이브는 일반 기어 설계 SW로 안 되는가

하모닉 드라이브(Strain Wave Gear)는 일반 인볼루트 기어와 근본적으로 다른 메커니즘입니다.

### 일반 기어 vs 하모닉 드라이브 핵심 차이

| 항목 | 일반 인볼루트 기어 | 하모닉 드라이브 |
|------|-------------------|---------------|
| **구성** | 강체 기어 2개 | 웨이브 제너레이터 + 플렉스스플라인(탄성체) + 서큘러 스플라인 |
| **치형** | 인볼루트 곡선 | 이중 원호(Double Circular Arc), S-tooth 등 특수 치형 |
| **변형** | 미소 변형 (강체 가정) | **대변형** — 플렉스스플라인이 타원형으로 탄성 변형 |
| **접촉** | 1~2쌍 치면 접촉 | 전체 치수의 **~30%가 동시 물림** |
| **해석 핵심** | 치면 접촉 응력, 굽힘 응력 | **대변형 + 다체 접촉 + 피로** 동시 고려 |
| **KISSsoft 등** | 완전 지원 | **지원 불가** — 강체 기어 전제 위반 |

**핵심 난이도:**
- 플렉스스플라인의 **기하학적 비선형**(대변형)과 **접촉 비선형**(다수 치면 동시 접촉)을 동시 처리
- 웨이브 제너레이터 캠 프로파일이 플렉스스플라인 변형형상을 결정 → 치면 물림에 연쇄 영향
- 플렉시블 베어링의 변형도 연성적으로 고려 필요
- 일반 기어 설계 SW(KISSsoft, Romax, MASTA)는 이 문제를 풀 수 있는 솔버가 없음

---

## 2. 하모닉 드라이브 개발의 4대 기술 영역

```
┌─────────────────────────────────────────────────────────────┐
│            로봇 액추에이터용 하모닉 드라이브 개발              │
├──────────────┬──────────────┬──────────────┬───────────────┤
│  A. 치형 설계  │  B. 구조 해석 │  C. 동역학   │  D. 시스템    │
│              │   (FEA)      │              │  통합         │
│ 캠 프로파일   │ 플렉스스플라인│ 전달 오차    │ 모터+감속기   │
│ 치형 곡선     │ 응력/변형    │ 백래시       │ 열 관리       │
│ 물림 비율     │ 접촉 해석    │ 효율        │ 제어 통합     │
│ 전위 계수     │ 피로 수명    │ 강성 모델    │ 토크 리플     │
└──────────────┴──────────────┴──────────────┴───────────────┘
```

---

## 3. 개발 단계별 오픈소스/공개 도구 활용 방안

### 3.1 단계 A: 치형 설계 및 캠 프로파일 설계

이 단계는 **수학적 모델링**이 핵심이며, Python으로 직접 구현하는 것이 가장 효과적입니다.

#### A-1. 웨이브 제너레이터 캠 프로파일 설계

```python
import numpy as np
import matplotlib.pyplot as plt

def wave_generator_profile(a, b, theta_array):
    """
    기본 타원형 웨이브 제너레이터 프로파일
    a: 장축 반경, b: 단축 반경
    
    고급 설계: Support Function 기반 폐곡선으로 확장 가능
    (ML 최적화와 결합하여 응력 21.7% 저감 달성 가능 - 최신 연구)
    """
    x = a * np.cos(theta_array)
    y = b * np.sin(theta_array)
    return x, y

def flexspline_neutral_curve(R0, w0, theta):
    """
    플렉스스플라인 중립면 변형 곡선
    R0: 원래 반경, w0: 최대 반경 변형량
    
    w(theta) = w0 * cos(2*theta)  (2파 변형, 기본형)
    """
    w = w0 * np.cos(2 * theta)
    r = R0 + w
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    return x, y, w

# 설계 파라미터
R0 = 40.0    # 플렉스스플라인 중립면 반경 [mm]
w0 = 0.8     # 최대 반경 변형량 [mm]
theta = np.linspace(0, 2*np.pi, 1000)

x, y, w = flexspline_neutral_curve(R0, w0, theta)
```

#### A-2. 치형 곡선 설계 (이중 원호 치형)

하모닉 드라이브의 표준적인 치형은 **이중 원호(Double Circular Arc)** 또는 
Harmonic Drive사의 특허인 **S-tooth profile**입니다.

```python
def double_circular_arc_tooth(module, z, alpha, r_a, r_f, theta):
    """
    이중 원호 치형 생성기
    module: 모듈
    z: 잇수
    alpha: 압력각
    r_a: 어덴덤 원호 반경
    r_f: 디덴덤 원호 반경
    
    참고: Chen et al. (2014) "The parametric design of 
    double-circular-arc tooth profile"
    """
    pitch = module * np.pi
    # 어덴덤 원호
    theta_a = np.linspace(-alpha, alpha, 100)
    x_a = r_a * np.sin(theta_a)
    y_a = r_a * (1 - np.cos(theta_a))
    
    # 디덴덤 원호 (공통 접선 조건)
    # ... 상세 구현 필요
    
    return x_a, y_a

def engagement_analysis(fs_teeth, cs_teeth, module, w0, R0):
    """
    물림 해석: 플렉스스플라인-서큘러 스플라인 동시 물림 치수 계산
    목표: 물림 비율(engagement ratio) 최대화
    
    하모닉 드라이브 특성: 전체 치수의 ~30%가 동시 물림 가능
    """
    # 변형에 따른 각 치면 위치의 간섭/간극 계산
    diff_teeth = cs_teeth - fs_teeth  # 보통 2
    reduction_ratio = fs_teeth / diff_teeth
    
    print(f"감속비: {reduction_ratio}:1")
    print(f"잇수 차: {diff_teeth}")
    
    return reduction_ratio
```

#### A-3. 최적화 (Python 기반)

```python
from scipy.optimize import minimize, differential_evolution

def objective_function(params):
    """
    다목적 최적화 목표함수
    - 최소화: 플렉스스플라인 최대 Von Mises 응력
    - 최대화: 물림 비율 (engagement ratio)
    - 최소화: 캠 곡률 변화율
    
    최신 연구에서는 XGBoost 서로게이트 모델 + 유전 알고리즘으로
    응력 21.7% 저감, 물림비 12.4% 향상 달성
    """
    cam_params = params[:4]  # 캠 프로파일 파라미터
    tooth_params = params[4:]  # 치형 파라미터
    
    stress = compute_stress(cam_params, tooth_params)  # FEA 또는 서로게이트
    engagement = compute_engagement(cam_params, tooth_params)
    curvature = compute_curvature(cam_params)
    
    # 가중 합 (다목적 → 단목적 변환)
    return 0.5 * stress - 0.3 * engagement + 0.2 * curvature

# 유전 알고리즘 최적화
bounds = [(0.5, 1.5)] * 8  # 파라미터 범위
result = differential_evolution(objective_function, bounds, 
                                 maxiter=500, seed=42)
```

### 3.2 단계 B: 구조 해석 (FEA) — 핵심 단계

하모닉 드라이브 해석의 **가장 중요하고 가장 어려운 단계**입니다.

#### B-1. 해석 전략 (2-Step 접근법)

학술 논문에서 검증된 표준 접근법:

**Step 1: 조립 해석 (Assembly)**
- 웨이브 제너레이터를 플렉스스플라인 내부에 삽입
- 플렉스스플라인이 타원형으로 대변형
- 서큘러 스플라인과 치면이 접촉 시작

**Step 2: 전달 하중 해석 (Transmission)**
- 토크 부하 적용
- 다체 치면 접촉 + 마찰
- Von Mises 응력, 접촉 응력, 전달 오차 추출

#### B-2. 오픈소스 FEA 구현 (CalculiX)

```
# CalculiX 입력 파일 구조 (*.inp, Abaqus 호환 포맷)
# 하모닉 드라이브 2-Step 비선형 접촉 해석

*HEADING
Harmonic Drive - Flexspline Stress Analysis

*NODE
# FreeCAD/Gmsh에서 생성한 노드 좌표
# 플렉스스플라인: 셸 요소 (S4R 또는 S8R)
# 치형 부분: 솔리드 요소 (C3D8I 또는 C3D10)
# 웨이브 제너레이터: 강체 (Rigid Body)
# 서큘러 스플라인: 강체 또는 솔리드

*ELEMENT, TYPE=S4R, ELSET=FLEXSPLINE
# 플렉스스플라인 컵 부분 (쉘 요소)

*ELEMENT, TYPE=C3D8I, ELSET=FS_TEETH
# 플렉스스플라인 치형 부분 (솔리드 요소)

*MATERIAL, NAME=SNCM439
# 일반적인 플렉스스플라인 재질: SNCM439 (고강도 합금강)
*ELASTIC
206000, 0.3
*PLASTIC
# 비선형 재료 모델 (필요 시)

*SURFACE, NAME=FS_OUTER
# 플렉스스플라인 외면 (치면)
*SURFACE, NAME=CS_INNER
# 서큘러 스플라인 내면 (치면)
*SURFACE, NAME=WG_OUTER
# 웨이브 제너레이터 외면

*CONTACT PAIR, INTERACTION=FRIC1
FS_OUTER, CS_INNER
*SURFACE INTERACTION, NAME=FRIC1
*FRICTION
0.1

*CONTACT PAIR, INTERACTION=FRIC2
FS_INNER, WG_OUTER
*SURFACE INTERACTION, NAME=FRIC2
*FRICTION
0.05

** ========= STEP 1: 조립 (WG 삽입) =========
*STEP, NLGEOM=YES, INC=100
*STATIC
0.01, 1.0, 1e-6, 0.1

*BOUNDARY
# 서큘러 스플라인 고정
CS_REF_NODE, 1, 6, 0.0
# 플렉스스플라인 다이어프램 끝단 고정
FS_DIAPHRAGM, 1, 6, 0.0
# 웨이브 제너레이터 삽입 (변위 제어)

*END STEP

** ========= STEP 2: 토크 전달 =========
*STEP, NLGEOM=YES, INC=200
*STATIC
0.005, 1.0, 1e-8, 0.05

*CLOAD
# 웨이브 제너레이터에 회전 토크 적용
WG_REF_NODE, 6, 10.0  # 10 Nm 토크

*NODE PRINT
U, S, RF
*EL PRINT
S, E
*END STEP
```

#### B-3. 솔버별 특성 비교 (하모닉 드라이브 해석 적합도)

| 솔버 | 대변형 | 접촉 | 쉘+솔리드 혼합 | 적합도 | 비고 |
|------|--------|------|-------------|--------|------|
| **CalculiX** | ✅ NLGEOM | ✅ Node-to-Surface | ✅ | ★★★★☆ | Abaqus 호환 포맷, 학습 자료 풍부 |
| **Code_Aster** | ✅ | ✅ 고급 접촉 | ✅ | ★★★★★ | 가장 강력, 학습 곡선 높음 |
| **PrePoMax+CalculiX** | ✅ | ✅ | ✅ | ★★★★☆ | GUI 제공으로 설정 편의성 |
| **FreeCAD FEM** | ✅ | △ 제한적 | ✅ | ★★★☆☆ | 단순 모델 검증용 |
| **Elmer** | ✅ | △ | ✅ | ★★★☆☆ | 멀티피직스 연성 강점 |

**추천:** PrePoMax(GUI) + CalculiX(솔버) 조합으로 시작 → 고급 해석은 Code_Aster

#### B-4. 3D 모델링 → FEA 워크플로우

```
FreeCAD                    Gmsh              CalculiX
┌──────────┐         ┌──────────┐      ┌──────────────┐
│ FCGear로  │  STEP   │ 접촉면   │ .inp │ 비선형 접촉   │
│ 기어 치형 │───────→│ 메싱     │─────→│ 대변형 해석   │
│ + 컵 모델 │  출력   │ 세분화   │ 파일 │ 2-Step 방식   │
└──────────┘         └──────────┘      └──────┬───────┘
                                              │
                                              ▼
                                       ┌──────────────┐
                                       │ ParaView     │
                                       │ 응력 분포    │
                                       │ 변형 형상    │
                                       │ 접촉 압력    │
                                       └──────────────┘
```

### 3.3 단계 C: 동역학 해석

#### C-1. 전달 오차(Transmission Error) 해석

```python
import numpy as np
from scipy.fft import fft

def transmission_error_analysis(input_angle, output_angle, ratio):
    """
    전달 오차 = 실제 출력 각도 - 이론적 출력 각도
    
    TE(θ_input) = θ_output_actual - θ_input / ratio
    
    FEA 결과에서 추출한 각변위 데이터 사용
    """
    theoretical_output = input_angle / ratio
    TE = output_angle - theoretical_output  # [arc-min]
    
    # FFT로 주파수 성분 분석
    TE_fft = fft(TE)
    freqs = np.fft.fftfreq(len(TE))
    
    # 주요 성분: 2배 하모닉 (2-wave 변형에 의한)
    # → NVH 설계에 활용
    
    return TE, TE_fft, freqs

def torsional_stiffness_model(torque_array, deflection_array):
    """
    하모닉 드라이브 비선형 강성 모델
    
    특성: 낮은 토크에서 부드럽고, 높은 토크에서 경화
    → 로봇 제어기 모델에 필수 파라미터
    """
    # 비선형 강성 K(θ) = dT/dθ
    K = np.gradient(torque_array) / np.gradient(deflection_array)
    
    # 히스테리시스 모델 (Dhaouadi et al.)
    # T = K_s * θ + D * dθ/dt + T_friction * sign(dθ/dt)
    
    return K
```

#### C-2. 다체 동역학 (MFBD) — 오픈소스 옵션

| 도구 | 특징 | 하모닉 드라이브 적용 |
|------|------|-------------------|
| **MBDyn** | 오픈소스 다체동역학 | 탄성체 연성 모델링 가능 |
| **Chrono** | 오픈소스 물리 엔진 | 기어 접촉 + 유연체 |
| **PyDy / SymPy** | 심볼릭 동역학 | 해석적 전달함수 도출 |
| **Drake (MIT)** | 로봇 시뮬레이션 | 액추에이터 레벨 시뮬레이션 |

### 3.4 단계 D: 로봇 액추에이터 시스템 통합

#### D-1. 모터 + 하모닉 드라이브 통합 설계

```python
class RobotActuator:
    """로봇 액추에이터 시스템 모델"""
    
    def __init__(self):
        # 모터 파라미터
        self.motor_torque_constant = 0.05  # Nm/A
        self.motor_inertia = 1e-5          # kg·m²
        self.motor_max_speed = 6000        # rpm
        
        # 하모닉 드라이브 파라미터
        self.ratio = 100                   # 감속비
        self.fs_teeth = 200                # 플렉스스플라인 잇수
        self.cs_teeth = 202                # 서큘러 스플라인 잇수
        self.hd_efficiency = 0.85          # 효율
        self.hd_stiffness = 1e4            # Nm/rad (비선형)
        self.hd_hysteresis = 0.5           # arc-min
        
        # 출력 사양
        self.output_torque = self.motor_torque_constant * \
                            self.ratio * self.hd_efficiency
        self.output_speed = self.motor_max_speed / self.ratio
    
    def thermal_analysis(self, duty_cycle, ambient_temp=25):
        """
        열 해석: 플렉스스플라인 히스테리시스 열 + 베어링 열 + 모터 열
        → 하모닉 드라이브는 고속 회전 시 내부 발열이 수명에 직결
        """
        power_loss = (1 - self.hd_efficiency) * \
                     self.output_torque * self.output_speed
        # 간이 열저항 모델
        thermal_resistance = 5.0  # °C/W
        temp_rise = power_loss * thermal_resistance * duty_cycle
        return ambient_temp + temp_rise
    
    def fatigue_life_estimation(self, stress_amplitude, mean_stress,
                                  material_Sut=1200):  # MPa, SNCM439
        """
        플렉스스플라인 피로 수명 추정
        
        핵심: 매 회전마다 2회 굽힘 반전 → 극심한 피로 환경
        (웨이브 제너레이터 1회전 → 플렉스스플라인 2회 굽힘 사이클)
        """
        # Modified Goodman 기준
        Se = 0.5 * material_Sut  # 피로 한도 추정
        safety_factor = 1 / (stress_amplitude/Se + mean_stress/material_Sut)
        
        # S-N 곡선 기반 수명 (Basquin 방정식)
        # N = (sigma_a / sigma_f')^(-1/b)
        
        return safety_factor
```

#### D-2. Me Virtuoso 하모닉 드라이브 시뮬레이터 (무료 웹 도구)

온라인에서 바로 사용 가능한 무료 하모닉 드라이브 설계 도구:
- **URL:** mevirtuoso.com/harmonic-drive-simulator
- **기능:** 플렉스스플라인, 서큘러 스플라인, 웨이브 제너레이터 파라미터 설정
- **출력:** 기어 물림 시각화, 기본 기구학 계산

---

## 4. 전체 개발 파이프라인 요약

```
Phase 1: 개념 설계 (1~2주)
├── Python으로 감속비/잇수/모듈 결정
├── 치형 곡선 수학적 모델링 (이중 원호)
├── 캠 프로파일 초기 설계 (타원형)
└── Me Virtuoso로 기구학 검증

Phase 2: 상세 설계 + FEA (3~6주)
├── FreeCAD에서 3D 모델링
│   ├── 플렉스스플라인 컵 (쉘 + 치형 솔리드)
│   ├── 서큘러 스플라인 (링 + 내부 치형)
│   └── 웨이브 제너레이터 (타원 캠)
├── Gmsh로 접촉면 중심 메싱
├── CalculiX/Code_Aster로 2-Step 비선형 해석
│   ├── Step 1: 조립 변형 → 플렉스스플라인 응력
│   ├── Step 2: 토크 전달 → 치면 접촉 + 전달 오차
│   └── 피로 수명 평가
└── ParaView로 결과 시각화

Phase 3: 최적화 (2~4주)
├── Python 자동화 (파라메트릭 스터디)
│   ├── 캠 프로파일 최적화 (GA/서로게이트)
│   ├── 치형 파라미터 최적화
│   └── 플렉스스플라인 벽 두께 최적화
├── ML 서로게이트 모델 (XGBoost 등)
└── Claude AI로 코드 생성 + 검증

Phase 4: 시스템 통합 (2~3주)
├── 모터 선정 + 열 해석
├── 토크 리플/전달 오차 → 제어기 반영
├── 강성/히스테리시스 모델 → ROS 연동
└── 프로토타입 설계 (3D 프린트 검증)
```

---

## 5. 설치 및 환경 구축

```bash
# === 수학/최적화 ===
pip install numpy scipy matplotlib sympy
pip install scikit-learn xgboost  # ML 서로게이트 모델

# === 3D CAD ===
sudo apt install freecad
# FreeCAD에서 Addon Manager → FCGear 설치

# === 메싱 ===
pip install gmsh pygmsh meshio

# === FEA 솔버 ===
sudo apt install calculix-ccx
# PrePoMax (Windows): https://prepomax.fs.um.si
# Code_Aster: https://code-aster.org

# === 후처리 ===
sudo apt install paraview
pip install pyvista

# === 다체 동역학 ===
pip install pydy sympy
# MBDyn: https://www.mbdyn.org
# Project Chrono: https://projectchrono.org

# === 로봇 시뮬레이션 ===
pip install drake  # MIT Drake
# ROS 2: https://docs.ros.org
```

---

## 6. 핵심 참고 문헌 (무료 접근 가능)

### 치형 설계
- Chen et al. (2014) "The parametric design of double-circular-arc tooth profile and its influence on the functional backlash of harmonic drive" - Mechanism and Machine Theory
- Song et al. (2022) "Parameter design of double-circular-arc tooth profile and its influence on meshing characteristics" - Mechanism and Machine Theory

### FEA 해석
- Kayabasi & Erzincanli (2007) "Shape optimization of tooth profile of a flexspline for a harmonic drive by FEM" - Materials & Design
- Chen et al. (2017) "Study of a harmonic drive with involute profile flexspline by 2D FEA" - Engineering Computations
- Ostapski (2010) "Analysis of the stress state in the harmonic drive generator-flexspline system" - Bulletin of the Polish Academy of Sciences

### ML 최적화 (최신)
- Guo et al. (2026) "Machine learning based design optimization method for wave generators of harmonic drives" - J. Mech. Sci. Tech.

### 종합 리뷰
- Bansal et al. (2025) "Harmonic Drives: Evolution of Design and Technology for High-Precision Motion Control" - CEES 2025, Springer

### GrabCAD 무료 3D 모델
- grabcad.com에서 "harmonic drive" 검색 → 다수의 참고용 3D 모델 다운로드 가능

---

## 7. 상용 SW 없이도 가능한 이유

하모닉 드라이브는 역설적으로 **상용 기어 설계 SW로 할 수 없기 때문에**, 오히려 오픈소스 접근이 불리하지 않습니다.

| 접근법 | 도구 | 비용 |
|--------|------|------|
| 상용 FEA (Abaqus/Ansys) | 범용 비선형 FEA + Python 스크립팅 | 수천만원/년 |
| RecurDyn MFBD | 전용 다체동역학 | 수천만원/년 |
| **오픈소스 방안 (본 가이드)** | Python + FreeCAD + CalculiX/Code_Aster | **무료** |

학술 논문에서도 대부분 **범용 FEA + 자체 Python 코드**로 연구하고 있으며, 하모닉 드라이브 전용 상용 설계 SW는 존재하지 않습니다. 따라서 오픈소스 도구로 구축하는 것이 학술/산업 모두에서 합리적인 선택입니다.

**Claude AI 활용 포인트:**
- 치형 곡선 수학 코드 생성/검증
- CalculiX 입력 파일(.inp) 작성 자동화
- FEA 결과 파싱 + 시각화 스크립트
- 최적화 루프 코드 생성
- FreeCAD Python 매크로 작성 (MCP 연동)
