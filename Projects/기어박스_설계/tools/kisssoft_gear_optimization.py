"""
KISSsoft COM Expert 기어 최적화 스크립트
- 내장 예제 모델의 하중을 10% 증가
- Fine Sizing으로 기어 Spec. 최적화
- 수명/안전율 계산
- KISSsys 시스템 모델에 반영 및 3D STEP 출력

필요 모듈: CC1 (COM Basic), CC2 (COM Expert), Z05x (3D), KISSsys
필요 패키지: pip install pywin32
"""

import sys
import os
from datetime import datetime

try:
    import win32com.client
except ImportError:
    print("오류: pywin32가 설치되지 않았습니다.")
    print("설치: pip install pywin32")
    sys.exit(1)


# ============================================================
# 설정값 (사용 환경에 맞게 수정하세요)
# ============================================================
KISSSOFT_EXAMPLE = r"C:\Program Files\KISSsoft 2025\example\CylGearPair1.z12"
KISSSYS_EXAMPLE = r"C:\Program Files\KISSsoft 2025\example\SingleStageGearbox.ksys"
OUTPUT_DIR = r"C:\task\Obsidian_Vault\이근호\퇴직준비세미나_이근호\Files\KISSsoft_Results"
LOAD_INCREASE_FACTOR = 1.10  # 하중 증가 비율 (10%)


def ensure_output_dir():
    """출력 디렉토리가 없으면 생성"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def connect_kisssoft():
    """KISSsoft COM 객체 생성 및 연결"""
    try:
        ks = win32com.client.Dispatch("KISSsoftCOM.KISSsoft")
        ks.SetSilentMode(True)
        print("[OK] KISSsoft COM 연결 성공")
        return ks
    except Exception as e:
        print(f"[오류] KISSsoft COM 연결 실패: {e}")
        print("  - KISSsoft가 설치되어 있는지 확인하세요")
        print("  - COM 서버가 등록되어 있는지 확인하세요 (regsvr32)")
        sys.exit(1)


def connect_kisssys():
    """KISSsys COM 객체 생성 및 연결"""
    try:
        ksys = win32com.client.Dispatch("KISSsysCOM.KISSsys")
        print("[OK] KISSsys COM 연결 성공")
        return ksys
    except Exception as e:
        print(f"[경고] KISSsys COM 연결 실패: {e}")
        print("  - KISSsys 모듈이 없으면 3D 출력 단계를 건너뜁니다")
        return None


# ============================================================
# 단계 1: 예제 모델 로드 및 하중 10% 증가
# ============================================================
def step1_load_and_increase_load(ks):
    """예제 모델을 열고 하중을 10% 증가시킨다."""
    print("\n" + "=" * 60)
    print("단계 1: 예제 모델 로드 및 하중 10% 증가")
    print("=" * 60)

    ks.OpenFile(KISSSOFT_EXAMPLE)
    print(f"  파일 열기: {KISSSOFT_EXAMPLE}")

    # 현재 하중 조건 읽기
    original = {
        "토크 [Nm]": ks.GetVar("ZS.Torque"),
        "동력 [kW]": ks.GetVar("ZS.Power"),
        "회전수 [rpm]": ks.GetVar("ZS.Speed"),
        "사용계수 Ka": ks.GetVar("ZS.Ka"),
        "요구수명 [hr]": ks.GetVar("ZS.Hlife"),
    }

    print("\n  [원본 하중 조건]")
    for k, v in original.items():
        print(f"    {k}: {v}")

    # 하중 10% 증가
    new_torque = original["토크 [Nm]"] * LOAD_INCREASE_FACTOR
    new_power = original["동력 [kW]"] * LOAD_INCREASE_FACTOR

    ks.SetVar("ZS.Torque", new_torque)
    ks.SetVar("ZS.Power", new_power)

    print(f"\n  [하중 +{int((LOAD_INCREASE_FACTOR - 1) * 100)}% 적용]")
    print(f"    토크: {original['토크 [Nm]']:.2f} → {new_torque:.2f} Nm")
    print(f"    동력: {original['동력 [kW]']:.2f} → {new_power:.2f} kW")

    return original


# ============================================================
# 단계 2: Fine Sizing으로 기어 Spec. 최적화
# ============================================================
def step2_fine_sizing(ks):
    """COM Expert(CC2)의 Fine Sizing을 실행하여 최적 기어 제원을 탐색한다."""
    print("\n" + "=" * 60)
    print("단계 2: Fine Sizing 최적화 (COM Expert CC2)")
    print("=" * 60)

    # Fine Sizing 탐색 범위 설정
    sizing_params = {
        "ZR[0].z.min": 18,     # 피니언 최소 잇수
        "ZR[0].z.max": 30,     # 피니언 최대 잇수
        "ZR[0].mn.min": 2.0,   # 최소 모듈 [mm]
        "ZR[0].mn.max": 4.0,   # 최대 모듈 [mm]
        "ZR[0].b.min": 20.0,   # 최소 이폭 [mm]
        "ZR[0].b.max": 40.0,   # 최대 이폭 [mm]
    }

    print("  [Fine Sizing 탐색 범위]")
    for k, v in sizing_params.items():
        ks.SetVar(k, v)
        print(f"    {k} = {v}")

    # Fine Sizing 실행
    print("\n  Fine Sizing 실행 중...")
    ks.CalculateFineSizing()

    num_solutions = ks.GetVar("FineSizing.NumResults")
    print(f"  탐색 완료: {num_solutions}개 솔루션 발견")

    if num_solutions > 0:
        # 최적(첫 번째) 솔루션 적용
        ks.SetFineSizingSolution(0)
        print("  최적 솔루션(#1) 적용 완료")
    else:
        print("  [경고] Fine Sizing 결과가 없습니다. 범위를 넓혀보세요.")


# ============================================================
# 단계 3: 재계산 및 수명/안전율 결과 획득
# ============================================================
def step3_calculate_and_get_results(ks):
    """강도 계산을 실행하고 최적화된 기어 Spec.과 수명/안전율을 읽는다."""
    print("\n" + "=" * 60)
    print("단계 3: 강도 계산 및 결과 획득")
    print("=" * 60)

    ks.Calculate()
    print("  강도 계산 완료")

    # 최적화된 기어 제원 읽기
    gear_spec = {
        "피니언 잇수": ks.GetVar("ZR[0].z"),
        "기어 잇수": ks.GetVar("ZR[1].z"),
        "모듈 [mm]": ks.GetVar("ZR[0].mn"),
        "이폭 [mm]": ks.GetVar("ZR[0].b"),
        "압력각 [deg]": ks.GetVar("ZR[0].alfn"),
        "비틀림각 [deg]": ks.GetVar("ZR[0].beta"),
        "피치직경-피니언 [mm]": ks.GetVar("ZR[0].d"),
        "피치직경-기어 [mm]": ks.GetVar("ZR[1].d"),
        "중심거리 [mm]": ks.GetVar("ZS.aw"),
    }

    # 수명/안전율 결과 읽기
    life_results = {
        "치면 안전율 (SH)": ks.GetVar("ZR[0].SafetyFlank"),
        "치근 안전율 (SF)": ks.GetVar("ZR[0].SafetyRoot"),
        "계산수명-치면 [hr]": ks.GetVar("ZR[0].LifeFlank"),
        "계산수명-치근 [hr]": ks.GetVar("ZR[0].LifeRoot"),
        "요구수명 [hr]": ks.GetVar("ZS.Hlife"),
    }

    print("\n  [최적화된 기어 제원]")
    for k, v in gear_spec.items():
        print(f"    {k}: {v}")

    print("\n  [수명/안전율 결과]")
    for k, v in life_results.items():
        print(f"    {k}: {v}")

    # 최적화된 KISSsoft 파일 저장
    optimized_file = os.path.join(OUTPUT_DIR, "optimized_gear_110pct.z12")
    ks.SaveFile(optimized_file)
    print(f"\n  저장: {optimized_file}")

    return gear_spec, life_results


# ============================================================
# 단계 4: KISSsys 시스템 모델에 반영 및 3D 출력
# ============================================================
def step4_kisssys_3d_export(ksys, gear_spec, new_torque):
    """KISSsys 시스템 모델에 최적화 결과를 반영하고 3D STEP을 출력한다."""
    print("\n" + "=" * 60)
    print("단계 4: KISSsys 시스템 반영 및 3D 모델 출력")
    print("=" * 60)

    if ksys is None:
        print("  [건너뜀] KISSsys COM 연결이 없습니다.")
        return

    ksys.OpenFile(KISSSYS_EXAMPLE)
    print(f"  파일 열기: {KISSSYS_EXAMPLE}")

    # 기어 쌍 서브컴포넌트에 최적화 결과 반영
    ksys.SetVar("GearPair1.ZS.Torque", new_torque)
    ksys.SetVar("GearPair1.ZR[0].z", gear_spec["피니언 잇수"])
    ksys.SetVar("GearPair1.ZR[1].z", gear_spec["기어 잇수"])
    ksys.SetVar("GearPair1.ZR[0].mn", gear_spec["모듈 [mm]"])
    ksys.SetVar("GearPair1.ZR[0].b", gear_spec["이폭 [mm]"])
    print("  최적화 결과 반영 완료")

    # 시스템 레벨 재계산
    ksys.Calculate()
    print("  시스템 계산 완료")

    # 3D STEP 파일 출력
    step_file = os.path.join(OUTPUT_DIR, "gearbox_optimized_110pct.step")
    ksys.Export3D(step_file)
    print(f"  3D STEP 출력: {step_file}")

    # KISSsys 파일 저장
    ksys_file = os.path.join(OUTPUT_DIR, "gearbox_optimized_110pct.ksys")
    ksys.SaveFile(ksys_file)
    print(f"  저장: {ksys_file}")

    ksys.Close()


# ============================================================
# 단계 5: 결과 비교 리포트 생성 (Markdown)
# ============================================================
def step5_generate_report(original, gear_spec, life_results):
    """원본 vs 최적화 결과를 Markdown 비교표로 출력한다."""
    print("\n" + "=" * 60)
    print("단계 5: 결과 비교 리포트 생성")
    print("=" * 60)

    today = datetime.now().strftime("%Y-%m-%d")
    increase_pct = int((LOAD_INCREASE_FACTOR - 1) * 100)

    report = f"""---
tags: [KISSsoft, 기어최적화, 하중변경]
생성일: {today}
---

# KISSsoft 기어 최적화 결과 (하중 +{increase_pct}%)

> 내장 예제 모델의 하중을 {increase_pct}% 증가시킨 후 Fine Sizing으로 최적화한 결과

## 하중 조건 변경

| 항목 | 원본 | 변경 (+{increase_pct}%) |
|------|------|----------------------|
| 토크 [Nm] | {original['토크 [Nm]']:.2f} | {original['토크 [Nm]'] * LOAD_INCREASE_FACTOR:.2f} |
| 동력 [kW] | {original['동력 [kW]']:.2f} | {original['동력 [kW]'] * LOAD_INCREASE_FACTOR:.2f} |
| 회전수 [rpm] | {original['회전수 [rpm]']:.1f} | {original['회전수 [rpm]']:.1f} (변경 없음) |

## 최적화된 기어 제원

| 항목 | 값 |
|------|------|
| 피니언 잇수 | {gear_spec['피니언 잇수']} |
| 기어 잇수 | {gear_spec['기어 잇수']} |
| 모듈 [mm] | {gear_spec['모듈 [mm]']} |
| 이폭 [mm] | {gear_spec['이폭 [mm]']} |
| 압력각 [deg] | {gear_spec['압력각 [deg]']} |
| 비틀림각 [deg] | {gear_spec['비틀림각 [deg]']} |
| 피치직경-피니언 [mm] | {gear_spec['피치직경-피니언 [mm]']} |
| 피치직경-기어 [mm] | {gear_spec['피치직경-기어 [mm]']} |
| 중심거리 [mm] | {gear_spec['중심거리 [mm]']} |

## 수명 및 안전율

| 항목 | 값 |
|------|------|
| 치면 안전율 (SH) | {life_results['치면 안전율 (SH)']} |
| 치근 안전율 (SF) | {life_results['치근 안전율 (SF)']} |
| 계산수명-치면 [hr] | {life_results['계산수명-치면 [hr]']} |
| 계산수명-치근 [hr] | {life_results['계산수명-치근 [hr]']} |
| 요구수명 [hr] | {life_results['요구수명 [hr]']} |

## 출력 파일

- KISSsoft 계산 파일: `optimized_gear_110pct.z12`
- KISSsys 시스템 파일: `gearbox_optimized_110pct.ksys`
- 3D STEP 모델: `gearbox_optimized_110pct.step`
"""

    report_path = os.path.join(OUTPUT_DIR, "기어최적화_결과리포트.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"  리포트 저장: {report_path}")
    print(report)

    return report_path


# ============================================================
# 메인 실행
# ============================================================
def main():
    print("=" * 60)
    print("KISSsoft COM Expert 기어 최적화 스크립트")
    print(f"하중 증가율: +{int((LOAD_INCREASE_FACTOR - 1) * 100)}%")
    print(f"실행 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    ensure_output_dir()

    # COM 연결
    ks = connect_kisssoft()
    ksys = connect_kisssys()

    try:
        # 단계 1: 하중 증가
        original = step1_load_and_increase_load(ks)

        # 단계 2: Fine Sizing 최적화
        step2_fine_sizing(ks)

        # 단계 3: 계산 및 결과 획득
        gear_spec, life_results = step3_calculate_and_get_results(ks)

        # 단계 4: KISSsys 반영 및 3D 출력
        new_torque = original["토크 [Nm]"] * LOAD_INCREASE_FACTOR
        step4_kisssys_3d_export(ksys, gear_spec, new_torque)

        # 단계 5: 리포트 생성
        step5_generate_report(original, gear_spec, life_results)

        print("\n" + "=" * 60)
        print("모든 단계 완료!")
        print("=" * 60)

    except Exception as e:
        print(f"\n[오류] 실행 중 오류 발생: {e}")
        print("  - KISSsoft 라이선스(CC1, CC2 모듈)를 확인하세요")
        print("  - 변수명이 KISSsoft 버전과 일치하는지 확인하세요")
        print("  - GUI에서 View > Show variable name으로 정확한 변수명을 확인하세요")
        raise

    finally:
        try:
            ks.Close()
        except Exception:
            pass


if __name__ == "__main__":
    main()
