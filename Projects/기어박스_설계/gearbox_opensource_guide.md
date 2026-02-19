# 오픈소스 기반 기어박스 R&D 환경 구축 가이드

## 1. 개요

상용 기어 설계 소프트웨어(KISSsoft, Romax, MASTA)는 라이선스 비용이 수천만 원에 달합니다. 이 가이드는 **100% 무료 오픈소스 도구**만을 조합하여 기어박스 연구개발에 필요한 **설계 → 3D 모델링 → 구조/열/진동 해석** 파이프라인을 구축하는 방안을 제시합니다.

---

## 2. 전체 툴체인 아키텍처

```
┌──────────────────────────────────────────────────────────────────┐
│                    기어박스 R&D 워크플로우                          │
├──────────────┬──────────────┬──────────────┬────────────────────┤
│   ① 기어 설계  │  ② 3D 모델링  │  ③ 메싱     │  ④ 해석 (FEA/CFD)  │
│              │              │              │                    │
│ Python 계산   │  FreeCAD     │  Gmsh        │  CalculiX (구조)    │
│ python-gearbox│  + FCGear WB │  Salome-Meca │  Elmer (멀티피직스) │
│ pyGear       │  + InvGears  │  Netgen      │  OpenFOAM (CFD)    │
│ DrivetrainHub│  CadQuery    │              │  Code_Aster (고급)  │
│              │              │              │                    │
├──────────────┴──────────────┴──────────────┴────────────────────┤
│   ⑤ 후처리: ParaView  │  ⑥ 자동화: Python + Jupyter Notebook     │
│   ⑦ MCP 연동: Claude + FreeCAD MCP Server                       │
└──────────────────────────────────────────────────────────────────┘
```

---

## 3. 단계별 도구 상세

### 3.1 기어 설계/계산 (① 단계)

KISSsoft를 대체할 수 있는 오픈소스 기어 계산 도구들입니다.

| 도구 | 언어 | 기능 | GitHub/링크 |
|------|------|------|-------------|
| **python-gearbox** | Python | ISO/AGMA 표준 기반 기어 하중용량 계산 | `pip install python-gearbox` (PyPI) |
| **pyGear** | Python | 인볼루트 기어 형상 생성, 동적 특성 계산, pythonOCC 기반 CAE/CAD 전처리 | github.com/e-dub/pygear |
| **py_gear_gen** | Python | 인볼루트 스퍼기어 생성, SVG/DXF 출력, 내접(링)기어 지원 | github.com/heartworm/py_gear_gen |
| **DrivetrainHub Notebooks** | Jupyter | ISO 6336, AGMA 2001 기반 기어 강도 계산, 인볼루트 형상, 유성기어 운동학 교육 자료 | drivetrainhub.com/notebooks |
| **AGMA 수식 직접 구현** | Python/Excel | Lewis 방정식, AGMA 벤딩/접촉 응력, 수명 계산을 직접 코딩 | 자체 구현 |

**추천 워크플로우:**

```python
# 예시: python-gearbox를 활용한 기본 기어 설계
from gearbox import Gear

# 기어 파라미터 정의
pinion = Gear(module=3, teeth=20, pressure_angle=20)
gear = Gear(module=3, teeth=60, pressure_angle=20)

# ISO/AGMA 기반 강도 계산
# → 결과를 FreeCAD로 넘겨 3D 모델링
```

```python
# 예시: pyGear를 활용한 정밀 기어 형상 생성
# pythonOCC 기반으로 STEP/IGES 출력 가능
# → CalculiX FEA 메싱에 직접 활용
```

### 3.2 3D CAD 모델링 (② 단계)

| 도구 | 특징 | 기어 관련 기능 |
|------|------|--------------|
| **FreeCAD 1.0+** | 오픈소스 파라메트릭 3D CAD, Python 스크립팅 완벽 지원 | Part Design에 인볼루트 기어 생성기 내장 |
| **FCGear Workbench** | FreeCAD 외부 워크벤치 (Addon Manager로 설치) | 인볼루트 기어, 내접기어, 사이클로이드, 베벨, 웜, 크라운, 래크, 타이밍 기어 등 12종+ |
| **InvGears Workbench** | FreeCAD 워크벤치 | 인볼루트 기어쌍 자동 생성, 구면 인볼루트 기어, 캐스케이드 기어 |
| **GearWorkBench** | FreeCAD 워크벤치 (개발 중) | 스퍼, 헬리컬, 래크, 베벨, 크라운, 웜, 글로보이드, 더블 헬리컬 기어 |
| **Planetary Gears WB** | FreeCAD 워크벤치 | 유성기어 계산기 (선기어-유성-링기어 자동 배치) |
| **CadQuery** | Python 스크립트 기반 3D 모델링 | 코드로 파라메트릭 기어 형상 생성, STEP/STL 출력 |

**FreeCAD에서 유성기어 어셈블리 생성 예시 (Python 매크로):**

```python
import FreeCAD
import InvoluteGearFeature

def makeGear(name, teeth, module=2, pressure_angle=20, external=True):
    involute = InvoluteGearFeature.makeInvoluteGear(name)
    involute.NumberOfTeeth = teeth
    involute.Modules = module
    involute.PressureAngle = pressure_angle
    involute.ExternalGear = external
    involute.HighPrecision = True
    return involute

# 유성기어 구성
sun = makeGear("Sun", teeth=20, module=2)
planet = makeGear("Planet", teeth=30, module=2)
ring = makeGear("Ring", teeth=80, module=2, external=False)

# → Pad (돌출)로 3D 솔리드 생성
# → STEP 파일로 내보내기
```

### 3.3 메싱 (③ 단계)

| 도구 | 특징 | 용도 |
|------|------|------|
| **Gmsh** | 오픈소스 3D 유한요소 메싱, Python API (`pygmsh`) | 구조 해석용 고품질 4면체/6면체 메시 |
| **Salome-Meca** | 통합 전처리/메싱/해석 환경 | Code_Aster와 완벽 통합 |
| **Netgen/NGSolve** | 자동 메싱 + FEA 솔버 통합 | 복잡한 형상의 적응형 메싱 |
| **snappyHexMesh** | OpenFOAM 내장 메싱 | CFD 해석용 메싱 (윤활유 유동 등) |
| **FreeCAD FEM WB** | FreeCAD 내장 | Gmsh/Netgen 연동으로 GUI 기반 메싱 |

### 3.4 해석 - FEA/CFD (④ 단계)

#### 구조 해석 (기어 치면 응력, 접촉, 피로)

| 도구 | 특징 | 기어박스 적용 |
|------|------|-------------|
| **CalculiX** | Abaqus 호환 입력 포맷, 비선형/접촉 해석 | 기어 치면 접촉 응력, 굽힘 응력, 모달 해석 |
| **PrePoMax** | CalculiX용 GUI (Windows), 사용자 친화적 | FEA 입문자에게 추천, 빠른 설정 |
| **FreeCAD FEM** | CalculiX/Elmer/Z88 연동 | CAD→해석 원스톱 워크플로우 |
| **Code_Aster** | EDF(프랑스전력) 개발, 산업급 솔버 | 비선형 접촉, 피로, 열-구조 연성 해석 |
| **Salome-Meca** | Salome (전처리) + Code_Aster (솔버) 통합 | 대규모 기어박스 시스템 해석 |
| **Elmer** | 멀티피직스 (구조+열+전자기+유동) | 전동기 일체형 기어박스의 열-구조 연성 |

#### CFD 해석 (윤활유 유동, 열 관리)

| 도구 | 특징 | 기어박스 적용 |
|------|------|-------------|
| **OpenFOAM** | 산업 표준급 오픈소스 CFD | 기어박스 내부 오일 유동, 비산, 열전달 |
| **preCICE** | 멀티솔버 커플링 프레임워크 | OpenFOAM(유동) + CalculiX(구조) 연성 해석 (FSI) |

#### NVH (소음/진동) 해석

| 도구 | 특징 | 기어박스 적용 |
|------|------|-------------|
| **CalculiX 모달** | 고유진동수/모드 해석 | 기어 메시 주파수, 하우징 공진 예측 |
| **OpenFOAM + acoustics** | 음향 해석 라이브러리 | 기어 소음 전파 시뮬레이션 |
| **Python (SciPy)** | 진동 신호 처리 | 전달 오차(TE) 분석, FFT, 오더 분석 |

### 3.5 후처리 & 시각화 (⑤ 단계)

| 도구 | 용도 |
|------|------|
| **ParaView** | FEA/CFD 결과 3D 시각화, 응력 분포, 유동 패턴 |
| **Matplotlib / Plotly** | Python 기반 2D/3D 차트, 설계 파라미터 그래프 |
| **Jupyter Notebook** | 대화형 분석 보고서, 코드+결과+설명 통합 |

### 3.6 Python 자동화 & Claude MCP 연동 (⑥⑦ 단계)

#### FreeCAD MCP 서버 설정 (Claude ↔ FreeCAD 연동)

```json
// Claude Desktop: claude_desktop_config.json
{
  "mcpServers": {
    "freecad": {
      "command": "python3",
      "args": ["/path/to/.freecad-mcp/working_bridge.py"]
    }
  }
}
```

설치 방법:
```bash
pip install mcp
npm install -g freecad-mcp-setup@latest
npx freecad-mcp-setup setup
```

연동 후 Claude에게 자연어로 요청:
- "모듈 3, 잇수 20/60인 스퍼기어 쌍을 FreeCAD에서 모델링해줘"
- "유성기어 세트를 만들어서 STEP 파일로 내보내줘"
- "기어 하우징에 베어링 시트를 추가해줘"

#### 전체 자동화 파이프라인 예시

```python
#!/usr/bin/env python3
"""
기어박스 설계-해석 자동화 파이프라인
"""

# 1단계: 기어 설계 계산
from gearbox_calc import design_gear_pair  # 자체 AGMA/ISO 모듈
gear_params = design_gear_pair(
    power=50e3,      # 50 kW
    speed=1500,      # 1500 rpm
    ratio=3.0,       # 감속비
    standard="ISO"
)

# 2단계: FreeCAD에서 3D 모델 생성
import subprocess
subprocess.run(["freecad", "-c", "generate_gears.py", 
                "--params", str(gear_params)])

# 3단계: Gmsh로 메싱
import gmsh
gmsh.initialize()
gmsh.open("gearbox_assembly.step")
gmsh.model.mesh.generate(3)
gmsh.write("gearbox.inp")  # CalculiX 포맷

# 4단계: CalculiX로 구조 해석
subprocess.run(["ccx", "gearbox_analysis"])

# 5단계: 결과 후처리
import pyvista as pv
mesh = pv.read("gearbox_analysis.frd")
mesh.plot(scalars="stress", cmap="jet")
```

---

## 4. 상용 SW 기능 대비 오픈소스 커버리지

| 기능 영역 | KISSsoft/Romax/MASTA | 오픈소스 대체 | 커버리지 |
|-----------|---------------------|-------------|---------|
| 기어 강도 계산 (ISO/AGMA) | ★★★★★ | python-gearbox + 자체 코드 | ★★★☆☆ |
| 기어 형상 생성 | ★★★★★ | pyGear + FCGear | ★★★★☆ |
| 3D 기어박스 모델링 | ★★★★☆ | FreeCAD + CadQuery | ★★★★☆ |
| 치면 접촉 해석 (LTCA) | ★★★★★ | CalculiX 접촉 해석 | ★★★☆☆ |
| 베어링 수명 계산 | ★★★★★ | Python 자체 구현 | ★★☆☆☆ |
| NVH/전달 오차 | ★★★★★ | CalculiX 모달 + Python | ★★☆☆☆ |
| 열/효율 해석 | ★★★★☆ | OpenFOAM + Elmer | ★★★☆☆ |
| 시스템 수준 해석 | ★★★★★ | Python 통합 스크립트 | ★★☆☆☆ |
| 자동화/스크립팅 | ★★★☆☆ | Python 완전 자동화 | ★★★★★ |
| AI 연동 (MCP) | ☆☆☆☆☆ | Claude + FreeCAD MCP | ★★★★☆ |

---

## 5. 설치 가이드 (Ubuntu/Linux 기준)

```bash
# === 기어 설계 ===
pip install python-gearbox numpy scipy matplotlib

# pyGear (pythonOCC 필요)
pip install pygear
# 또는
git clone https://github.com/e-dub/pygear.git

# === 3D CAD ===
# FreeCAD 1.0+
sudo apt install freecad
# FCGear 워크벤치: FreeCAD → Addon Manager에서 설치

# CadQuery
pip install cadquery

# === 메싱 ===
pip install gmsh pygmsh meshio

# === FEA 솔버 ===
# CalculiX
sudo apt install calculix-ccx
# PrePoMax (Windows GUI): prepomax.fs.um.si

# Code_Aster / Salome-Meca
# https://code-aster.org → Salome-Meca 패키지 다운로드

# Elmer
sudo apt install elmer elmerfem-csc

# === CFD ===
# OpenFOAM
sudo apt install openfoam

# === 후처리 ===
sudo apt install paraview
pip install pyvista

# === MCP 연동 ===
pip install mcp
npm install -g freecad-mcp-setup@latest
```

---

## 6. 실전 적용 시나리오

### 시나리오 A: 소형 유성기어 감속기 설계

1. Python으로 AGMA 2001 기반 기어 강도 계산 → 잇수/모듈/전위 최적화
2. FreeCAD FCGear로 선기어/유성/링기어 3D 모델 생성
3. 하우징, 샤프트, 베어링 시트를 FreeCAD Part Design으로 모델링
4. Gmsh로 메싱 → CalculiX로 치면 접촉 응력 FEA
5. ParaView로 응력 분포 확인 및 설계 수정
6. Claude + FreeCAD MCP로 설계 변경 자동화

### 시나리오 B: EV 감속기 NVH 검토

1. python-gearbox로 헬리컬 기어 설계 + 전달 오차 추정
2. FreeCAD에서 기어-샤프트-하우징 어셈블리 모델링
3. CalculiX 모달 해석 → 고유진동수/모드형상 확인
4. Python(SciPy)으로 기어 메시 주파수와 공진 영역 비교
5. 마이크로지오메트리(크라우닝/릴리프) 파라미터 스터디 자동화

### 시나리오 C: 기어박스 윤활유 유동 해석

1. FreeCAD에서 기어박스 내부 공간 모델링 (유체 영역 추출)
2. snappyHexMesh로 CFD 메시 생성
3. OpenFOAM interFoam 솔버로 오일 비산/유면 해석
4. preCICE로 열전달 연성 (OpenFOAM↔CalculiX)
5. ParaView에서 오일 분포 및 온도장 시각화

---

## 7. 한계점과 보완 방안

### 상용 SW 대비 부족한 영역

- **Loaded Tooth Contact Analysis (LTCA):** 상용 SW 수준의 자동화된 LTCA는 없지만, CalculiX 접촉 해석으로 유사 결과 가능 (설정에 노력 필요)
- **베어링 내부 해석:** SKF/Timken급 베어링 카탈로그 통합은 부재, Python으로 ISO 281 수명 계산 자체 구현 필요
- **체계적인 NVH 예측:** Romax Spectrum/MASTA 수준의 기어 와인 예측은 어려움, 모달 해석 + 후처리로 보완
- **표준 인증 보고서:** KISSsoft처럼 자동 생성되는 표준 적합성 보고서 없음, Jupyter Notebook으로 자체 양식 구축

### 보완 전략

- Claude AI를 활용하여 AGMA/ISO 계산 코드를 작성하고 검증
- Jupyter Notebook 기반 계산서 템플릿 구축 (재사용 가능)
- 점진적 구축: 기본 기어 설계 → 3D 모델링 → FEA 순서로 확장
- 학술 논문과 교재의 벤치마크 예제로 검증

---

## 8. 참고 자료

- FreeCAD 기어 워크벤치: github.com/looooo/freecad.gears
- FreeCAD MCP 서버: github.com/contextform/freecad-mcp
- DrivetrainHub 교육 노트북: drivetrainhub.com/notebooks
- python-gearbox: pypi.org/project/python-gearbox
- CalculiX 공식: calculix.de
- OpenFOAM 공식: openfoam.com
- ParaView: paraview.org
- Gmsh: gmsh.info
- PrePoMax (CalculiX GUI): prepomax.fs.um.si
- CadQuery: github.com/CadQuery/cadquery
- FEA4free 블로그: fea4free.com
