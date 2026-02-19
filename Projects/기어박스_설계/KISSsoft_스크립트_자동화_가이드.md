---
tags: [KISSsoft, COM인터페이스, Python, 기어설계, 자동화, SKRIPT]
생성일: 2026-02-14
상태: 변수명_확인_대기중
---

# KISSsoft 스크립트 자동화 가이드

> KISSsoft를 스크립트로 제어하여 기어 설계를 자동화하는 방법 정리

---

## 1. KISSsoft 스크립트 방식 개요

KISSsoft는 **2가지 스크립트 방식**을 제공한다.

| 방식 | 모듈 | 언어 | 용도 |
|------|------|------|------|
| **SKRIPT** (내장) | CC3 | BASIC 유사 | KISSsoft 내부에서 직접 실행 |
| **COM Interface** (외부) | CC1/CC2 | Python, VBA, MATLAB 등 | 외부 프로그램에서 원격 제어 |

---

## 2. SKRIPT — 내장 스크립트 언어 (모듈 CC3)

### 2.1 기본 문법

```
// 변수 선언
number x
string s1, s2

// KISSsoft 계산 변수에 직접 접근 (대소문자 구분)
ZR[0].b = 44        // 기어 0번의 이폭(face width) 설정
ZR[0].z = 25        // 잇수 설정

// 계산 실행
Calculate()

// 결과 출력
write("이폭: " + ZR[0].b)
```

### 2.2 제어 구조

```
// 조건문
if safety_value < 1.5 then
    write("안전율 부족!")
end

// 반복문 (for)
for i = 1 to 5
    ZR[0].z = 20 + i
    Calculate()
    write("잇수=" + ZR[0].z + " 결과=" + result)
end

// 반복문 (while)
number flag = 1
while flag == 1 do
    // 반복 계산...
    if condition then
        flag = 0
    end
end
```

### 2.3 파일 입출력 (결과를 CSV로 내보내기)

```
open_file("C:/results/gear_output.csv")
write_to_file("잇수, 안전율, 이폭")
for i = 1 to 10
    ZR[0].z = 20 + i
    Calculate()
    write_to_file(ZR[0].z + "," + safety + "," + ZR[0].b)
end
close_file()
```

### 2.4 스크립트 실행 시점 (6가지)

| 유형 | 실행 시점 | 용도 |
|---|---|---|
| `direct` | 사용자가 수동 실행 | 파라미터 스터디, 최적화 |
| `preCalc` | 계산 전 자동 | 입력값 검증/변환 |
| `postCalc` | 계산 후 자동 | 결과 후처리, 리포트 |
| `onReport` | 리포트 생성 전 | 커스텀 리포트 항목 추가 |
| `preSave` | 파일 저장 전 | 데이터 정리 |
| `postLoad` | 파일 로드 후 | 초기값 설정 |

### 2.5 내장 함수 (60개 이상)

- **수학**: `abs`, `sqrt`, `pow`, `sin`, `cos`, `tan`, `log`, `exp`, `ceil`, `floor`, `round`
- **삼각함수**: `asin`, `acos`, `atan`, `sinh`, `cosh`, `tanh`
- **문자열**: `strlength`, `strreplace`, `substr`, `strtrim`, `strfind`, `strlowercase`, `struppercase`
- **파일**: `open_file`, `read_line`, `write_to_file`, `read`, `write_all`, `close_file`
- **기타**: `write` (콘솔 출력), `size` (요소 개수)

### 2.6 에디터 기능

- 구문 강조 및 괄호 매칭
- 자동 완성 (변수 및 함수)
- 브레이크포인트 디버깅
- 단계 실행 (`next line`) 및 브레이크포인트까지 실행 (`next breakpoint`)

---

## 3. COM Interface — 외부 프로그램 연동 (모듈 CC1/CC2)

### 3.1 COM Basic vs Expert 비교

| 기능 | COM Basic (CC1) | COM Expert (CC1+CC2) |
|---|---|---|
| 파라미터 읽기/쓰기 | O | O |
| 계산 실행 | O | O |
| 결과 조회 | O | O |
| 러프/파인 사이징 | X | O |
| 접촉 해석(Contact Analysis) | X | O |
| 텍스트 포맷 출력 | X | O |

### 3.2 Python 예시 (win32com 사용)

```python
import win32com.client

# KISSsoft COM 객체 생성
ks = win32com.client.Dispatch("KISSsoftCOM.KISSsoft")

# 계산 파일 열기
ks.OpenFile("C:\\KISSsoft\\example\\CylGearPair.z12")

# 파라미터 읽기/쓰기
z1 = ks.GetVar("ZR[0].z")          # 피니언 잇수 읽기
ks.SetVar("ZR[0].z", 25)           # 피니언 잇수 설정
ks.SetVar("ZR[1].z", 30)           # 기어 잇수 설정
ks.SetVar("ZR[0].b", 28.4)         # 이폭 설정

# 계산 실행
ks.Calculate()

# 결과 읽기
safety = ks.GetVar("ZR[0].SafetyRoot")
print(f"치근 안전율: {safety}")

# 파일 저장 및 종료
ks.SaveFile("C:\\KISSsoft\\output\\result.z12")
ks.Close()
```

### 3.3 Excel VBA 예시

```vb
Sub RunKISSsoft()
    Dim ks As Object
    Set ks = CreateObject("KISSsoftCOM.KISSsoft")

    ks.OpenFile "C:\KISSsoft\example\CylGearPair.z12"

    ' 파라미터 변경
    ks.SetVar "ZR[0].z", 25

    ' 계산 실행
    ks.Calculate

    ' 결과를 Excel 셀에 기록
    Cells(1, 1).Value = ks.GetVar("ZR[0].SafetyRoot")

    ks.Close
    Set ks = Nothing
End Sub
```

---

## 4. COM Expert를 활용한 기어 최적화 워크플로우

### 4.1 전체 파이프라인

```
[내장 예제 로드] → [하중 +10% 변경] → [Fine Sizing 최적화]
    → [수명 계산] → [KISSsys 시스템 반영] → [3D 모델 STEP 출력]
```

### 4.2 필요 모듈

| 모듈 | 용도 | 필수 여부 |
|---|---|---|
| **CC1** (COM Basic) | 변수 읽기/쓰기, 계산 실행 | 필수 |
| **CC2** (COM Expert) | Fine Sizing, 접촉해석 | 필수 |
| **CC3** (SKRIPT) | 내장 스크립트 자동화 | 선택 |
| **Z05x** | 3D 기어 모델 생성/STEP 출력 | 필수 |
| **KISSsys** | 시스템 레벨 모델링 | 필수 |

### 4.3 Python 스크립트

전체 자동화 스크립트가 아래 경로에 저장되어 있다:

📄 **`회차별자율학습자료/tools/kisssoft_gear_optimization.py`**

스크립트 구조:

| 단계 | 함수 | 역할 |
|---|---|---|
| 1 | `step1_load_and_increase_load()` | 예제 로드, 토크/동력 +10% |
| 2 | `step2_fine_sizing()` | Fine Sizing으로 잇수/모듈/이폭 최적화 |
| 3 | `step3_calculate_and_get_results()` | 강도 계산, 안전율/수명 획득 |
| 4 | `step4_kisssys_3d_export()` | KISSsys 반영, STEP 3D 출력 |
| 5 | `step5_generate_report()` | Markdown 비교 리포트 생성 |

### 4.4 생성되는 파일

```
Files/KISSsoft_Results/
├── optimized_gear_110pct.z12       ← 최적화된 KISSsoft 계산 파일
├── gearbox_optimized_110pct.ksys   ← KISSsys 시스템 파일
├── gearbox_optimized_110pct.step   ← 3D STEP 모델
└── 기어최적화_결과리포트.md          ← 결과 비교 리포트
```

---

## 5. 변수명 검증 결과

> ⚠️ **중요**: 아래 변수명은 공개 문서 기반 조사 결과이며, KISSsoft GUI에서 `View > Show variable name`으로 최종 확인이 필요하다.

### 5.1 확인된 변수명 (공식 SKRIPT 문서에서 확인)

| 변수명 | 의미 | 출처 |
|---|---|---|
| `ZR[0].b` | 기어 0번 이폭 | SKRIPT 문서 예제: `ZR[0].b = 44` |
| `ZR[1].b` | 기어 1번 이폭 | SKRIPT 문서 예제 |
| `ZR[0].z` | 잇수 | SKRIPT 변수 규칙 |
| `ZR[j].Geo.mn` | 모듈 (Geo 접두사 포함 경로) | SKRIPT 문서 |
| `ZR[0].alfn` | 압력각 (normal section) | KISSsoft 매뉴얼 |
| `ZR[0].beta` | 비틀림각 (helix angle) | KISSsoft 매뉴얼 |
| `ZPP[0].Flanke.SH` | 치면 안전율 | SKRIPT 문서 직접 확인 |
| `ZPP[0].Fuss.SFnorm` | 치근 안전율 | SKRIPT 문서 직접 확인 |
| `Calculate()` | 계산 실행 함수 | SKRIPT 문서 예제 |
| `KA` | 사용계수 (Application factor) | KISSsys 변수 문서 |
| `Mn` | 모듈 (Normal module) | KISSsys 변수 문서 |
| `A` | 중심거리 (Centre distance) | KISSsys 변수 문서 |

### 5.2 수정이 필요할 수 있는 변수명

| 스크립트 현재값 | 문제 | 실제 가능한 변수명 |
|---|---|---|
| `ZS.Torque` | `.Torque` 속성명 미확인 | `ZS.T` 또는 `ZS.Md` (독일어 Drehmoment) |
| `ZS.Power` | `.Power` 속성명 미확인 | `ZS.P` |
| `ZS.Speed` | `.Speed` 속성명 미확인 | `ZS.n` (n = 회전수) |
| `ZS.Ka` | 경로 미확인 | `ZS.KA` 또는 `ZR[0].KA` |
| `ZS.Hlife` | 미확인 | `ZS.H` 또는 별도 경로 |
| `ZS.aw` | 부분 확인 | `ZS.aw` 또는 `ZS.a` |
| `ZR[0].d` | 계산 결과값 | `ZR[0].Geo.d` |
| `ZR[0].mn` | 부분 확인 | `ZR[0].Geo.mn`이 더 정확할 수 있음 |
| `ZR[0].SafetyFlank` | **틀릴 가능성 높음** | **`ZPP[0].Flanke.SH`** |
| `ZR[0].SafetyRoot` | **틀릴 가능성 높음** | **`ZPP[0].Fuss.SFnorm`** |
| `ZR[0].LifeFlank` | 미확인 | 별도 확인 필요 |
| `ZR[0].LifeRoot` | 미확인 | 별도 확인 필요 |

### 5.3 COM 메서드명 (미확인)

| 메서드 | 상태 | 비고 |
|---|---|---|
| `Dispatch("KISSsoftCOM.KISSsoft")` | 부분 확인 | 버전 번호 포함 가능: `KISSsoftCOM2025.KISSsoft` |
| `SetSilentMode(True)` | 미확인 | |
| `OpenFile()` | 미확인 (존재 가능성 높음) | |
| `GetVar()` / `SetVar()` | 미확인 | `GetVal`/`SetVal` 가능성도 있음 |
| `CalculateFineSizing()` | 미확인 | |
| `SetFineSizingSolution()` | 미확인 | |
| `SaveFile()` | 미확인 | |
| `Export3D()` | 미확인 | |

### 5.4 변수명 확인 방법

KISSsoft GUI에서 직접 확인하는 것이 가장 정확하다:

1. KISSsoft 실행 → 예제 파일 열기
2. 메뉴: **View > Show variable name** (변수명 표시 활성화)
3. GUI의 각 입력 필드 위에 마우스를 올리면 실제 변수명이 표시됨
4. 또는: **View > Variable list** → 전체 변수 목록 확인

### 5.5 확인이 필요한 핵심 항목 체크리스트

- [ ] COM ProgID: `KISSsoftCOM.KISSsoft` 또는 다른 형식?
- [ ] 토크 변수: `ZS.Torque` vs `ZS.T` vs `ZS.Md`?
- [ ] 동력 변수: `ZS.Power` vs `ZS.P`?
- [ ] 회전수 변수: `ZS.Speed` vs `ZS.n`?
- [ ] 잇수: `ZR[0].z` 그대로?
- [ ] 모듈: `ZR[0].mn` vs `ZR[0].Geo.mn`?
- [ ] 이폭: `ZR[0].b` 그대로?
- [ ] 중심거리: `ZS.aw` vs `ZS.a`?
- [ ] 치면 안전율: `ZPP[0].Flanke.SH` 확인
- [ ] 치근 안전율: `ZPP[0].Fuss.SFnorm` 확인
- [ ] 수명 변수: 어떤 경로?
- [ ] Fine Sizing 관련 메서드명?

---

## 6. 논문 PDF 번역 에이전트

기어 관련 논문 PDF를 자동 번역하는 에이전트도 구성되어 있다.

### 6.1 구성 파일

| 파일 | 설명 |
|---|---|
| `tools/extract_pdf_images.py` | PDF에서 이미지 추출 (PyMuPDF + Pillow) |
| `.claude/agents/paper-translator.md` | 논문 번역 에이전트 정의 |

### 6.2 번역 완료 논문

**"The Effectiveness of Shrouding on Reducing Meshed Spur Gear Power Loss – Test Results"**
- 저자: I. R. Delgado (NASA), M. J. Hurrell (HX5 Sierra LLC)
- 번역본: [[번역_슈라우딩의_기어_윈디지_손실_저감_효과]]
- 요약본: [[요약_슈라우딩의_기어_윈디지_손실_저감_효과]]
- 이미지: `Files/Effectiveness_Shrouding/fig1~fig11.png` (11개)

### 6.3 논문 핵심 내용

- NASA Glenn Research Center에서 맞물림 평기어(meshed spur gears) 슈라우딩 시험 수행
- C31 구성(최대 축방향/최소 반경방향 간극)에서 **최대 29% 윈디지 동력 손실(WPL) 감소**
- 15,000 ft/min (~5,210 RPM, 피니언 11 in. 기준) 이상에서 슈라우드 효과 발현
- 반경방향 간극 최소화가 WPL 저감에 가장 효과적

#### 표면 속도-RPM 환산표 (피니언 11 in. 기준)

| 표면 속도 (ft/min) | RPM | 비고 |
|---|---|---|
| 10,000 | ~3,470 | WPL이 유의미해지기 시작 |
| 15,000 | ~5,210 | 슈라우드 효과 발현 임계점 |
| 25,000 | ~8,680 | 슈라우딩 시 10~29% WPL 감소 |
| 28,000 | ~9,720 | 본 시험의 최대 속도 (~10,000 RPM) |

---

## 7. 참고 자료

### KISSsoft 공식 자료
- [COM Basic and Expert Interface](https://gearsolutions.com/news/com-basic-and-expert-interface-to-integrate-kisssoft-software/)
- [SKRIPT for Tailor-Made Calculations](https://www.kisssoft.com/en/news-and-events/newsroom/skript-for-tailor-made-calculations)
- [SKRIPT Documentation](https://www.readkong.com/page/skript-documentation-of-the-built-in-language-in-kisssoft-4655940)
- [KISSsoft System Module](https://www.kisssoft.com/en/products/product-overview/kisssoft-system-module)
- [3D Export / Exchange Formats](https://www.kisssoft.com/en/products/interfaces-and-partners/exchange-formats)
- [Script and COM Interface Training](https://www.kisssoft.com/en/academy/events/script-and-com-interface-1)

### 설치 요구사항
```bash
pip install pywin32       # Python COM 인터페이스
pip install PyMuPDF Pillow  # PDF 이미지 추출 (논문 번역용)
```

### 권장 학습 순서
1. KISSsoft GUI에서 예제를 열고 `View > Show variable name` 활성화하여 변수명 파악
2. COM Basic(CC1)으로 변수 읽기/쓰기 먼저 연습
3. COM Expert(CC2)로 Fine Sizing 호출 추가
4. KISSsys 연동은 단일 기어 자동화가 안정된 후 진행
