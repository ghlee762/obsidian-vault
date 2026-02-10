# -*- coding: utf-8 -*-
"""
10kW 기어박스 설계 - AGMA/ISO 준수
2단 헬리컬 기어 감속 (35:1)
"""
import math
import sys
import io

# 출력 인코딩 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 70)
print("       10kW 기어박스 설계 - AGMA 2001-D04 준수")
print("=" * 70)

# ============================================================
# 1. 기본 입력 사양
# ============================================================
P_kW = 10           # 동력 [kW]
P = P_kW * 1000     # 동력 [W]
n1 = 1750           # 입력 회전수 [RPM]
n_out = 50          # 출력 회전수 [RPM]
total_ratio = n1 / n_out  # 총 감속비 = 35

# 기어 재질: SCM420H (침탄 경화강)
sigma_Fb = 400      # 허용 굽힘 응력 [MPa]
sigma_Hb = 1400     # 허용 접촉 응력 [MPa]
E = 206000          # 탄성계수 [MPa]
poisson = 0.3       # 포아송비

# 헬리컬 기어 파라미터
helix_angle = 20    # 비틀림각 [도]
pressure_angle = 20 # 압력각 [도]

print(f"\n[1] 기본 사양")
print("-" * 50)
print(f"  입력 동력      : {P_kW:.1f} kW")
print(f"  입력 회전수    : {n1} RPM")
print(f"  출력 회전수    : {n_out} RPM")
print(f"  총 감속비      : {total_ratio:.1f}:1")

# ============================================================
# 2. 감속 단계 구성 (2단 감속)
# ============================================================
print(f"\n[2] 감속 단계 구성 (2단 헬리컬)")
print("-" * 50)

# 1단 기어
z1_1 = 18           # 1단 피니언 잇수
z2_1 = 126          # 1단 기어 잇수
ratio_1 = z2_1 / z1_1

# 2단 기어
z1_2 = 20           # 2단 피니언 잇수
z2_2 = 100          # 2단 기어 잇수
ratio_2 = z2_2 / z1_2

actual_ratio = ratio_1 * ratio_2

print(f"  1단: 피니언 {z1_1}T -> 기어 {z2_1}T (감속비 {ratio_1:.2f}:1)")
print(f"  2단: 피니언 {z1_2}T -> 기어 {z2_2}T (감속비 {ratio_2:.2f}:1)")
print(f"  실제 총 감속비: {actual_ratio:.1f}:1")

# ============================================================
# 3. 토크 계산 (단위 주의: kW 사용)
# ============================================================
print(f"\n[3] 각 축 토크 계산")
print("-" * 50)

# T [N.m] = (P[kW] * 9549) / n[RPM]
T1 = (P_kW * 9549) / n1                 # 입력축 토크 [N.m]
n2 = n1 / ratio_1                       # 중간축 회전수
T2 = T1 * ratio_1 * 0.98                # 중간축 토크 (효율 98%)
n3 = n2 / ratio_2                       # 출력축 회전수
T3 = T2 * ratio_2 * 0.98                # 출력축 토크 (효율 98%)

print(f"  입력축 (1축): {n1:.0f} RPM, {T1:.1f} N.m")
print(f"  중간축 (2축): {n2:.0f} RPM, {T2:.1f} N.m")
print(f"  출력축 (3축): {n3:.0f} RPM, {T3:.1f} N.m")

# ============================================================
# 4. 모듈 결정 (AGMA 기반)
# ============================================================
print(f"\n[4] 모듈(Module) 결정 - AGMA 2001-D04")
print("-" * 50)

# 하중 계수 및 속도 계수
Ka = 1.5            # 하중 계수 (중간 충격)
Ks = 1.0            # 크기 계수
Km = 1.2            # 하중 분포 계수
KB = 1.0            # 림 두께 계수

# Lewis 형상 계수 (등가 잇수 기준)
def lewis_factor(z, helix_deg):
    """등가 잇수에 대한 Lewis 형상 계수"""
    z_eq = z / (math.cos(math.radians(helix_deg)) ** 3)
    Y = 0.154 - 0.912 / z_eq
    return max(Y, 0.28)

# 피치선 속도 계산 함수
def pitch_velocity(d, n):
    """피치선 속도 [m/s], d: mm, n: RPM"""
    return (math.pi * d * n) / 60000

# 속도 계수 (AGMA)
def velocity_factor(V):
    """AGMA 속도 계수 Kv (Quality 6 기준)"""
    return (6.1 + V) / 6.1

cos_beta = math.cos(math.radians(helix_angle))
psi = 10            # 폭/모듈 비

# 1단 기어 모듈 결정
Y1 = lewis_factor(z1_1, helix_angle)
m1 = 2.0            # 초기값 [mm]

for _ in range(20):
    d1_1 = m1 * z1_1 / cos_beta
    V1 = pitch_velocity(d1_1, n1)
    Kv1 = velocity_factor(V1)
    b1 = psi * m1
    Wt1 = (2 * T1 * 1000) / d1_1  # 접선력 [N], T1을 N.mm로 변환
    sigma_calc = (Wt1 * Ka * Kv1 * Ks * Km * KB) / (b1 * m1 * Y1)
    if sigma_calc > sigma_Fb:
        m1 += 0.5
    else:
        break

m1 = math.ceil(m1 * 2) / 2  # 0.5 단위로 올림
d1_1 = m1 * z1_1 / cos_beta
V1 = pitch_velocity(d1_1, n1)
Kv1 = velocity_factor(V1)

print(f"  1단 기어 모듈: m = {m1:.1f} mm")
print(f"    - 피치선 속도: V = {V1:.2f} m/s")
print(f"    - 속도 계수: Kv = {Kv1:.3f}")
print(f"    - Lewis 형상계수: Y = {Y1:.3f}")

# 2단 기어 모듈 결정
Y2 = lewis_factor(z1_2, helix_angle)
m2 = 2.5            # 초기값 [mm]

for _ in range(20):
    d1_2 = m2 * z1_2 / cos_beta
    V2 = pitch_velocity(d1_2, n2)
    Kv2 = velocity_factor(V2)
    b2 = psi * m2
    Wt2 = (2 * T2 * 1000) / d1_2
    sigma_calc = (Wt2 * Ka * Kv2 * Ks * Km * KB) / (b2 * m2 * Y2)
    if sigma_calc > sigma_Fb:
        m2 += 0.5
    else:
        break

m2 = math.ceil(m2 * 2) / 2
d1_2 = m2 * z1_2 / cos_beta
V2 = pitch_velocity(d1_2, n2)
Kv2 = velocity_factor(V2)

print(f"\n  2단 기어 모듈: m = {m2:.1f} mm")
print(f"    - 피치선 속도: V = {V2:.2f} m/s")
print(f"    - 속도 계수: Kv = {Kv2:.3f}")
print(f"    - Lewis 형상계수: Y = {Y2:.3f}")

# ============================================================
# 5. 기어 치수 계산
# ============================================================
print(f"\n[5] 기어 치수 계산")
print("-" * 50)

# 1단 기어
d1_pinion = m1 * z1_1 / cos_beta    # 피니언 피치원 직경
d1_gear = m1 * z2_1 / cos_beta      # 기어 피치원 직경
a1 = (d1_pinion + d1_gear) / 2      # 중심 거리
b1 = psi * m1                        # 기어 폭

# 2단 기어
d2_pinion = m2 * z1_2 / cos_beta
d2_gear = m2 * z2_2 / cos_beta
a2 = (d2_pinion + d2_gear) / 2
b2 = psi * m2

print(f"\n  [1단 기어] (m = {m1:.1f} mm)")
print(f"    피니언: z={z1_1}T, d={d1_pinion:.1f}mm")
print(f"    기  어: z={z2_1}T, d={d1_gear:.1f}mm")
print(f"    중심거리: a = {a1:.1f} mm")
print(f"    기어 폭: b = {b1:.1f} mm")

print(f"\n  [2단 기어] (m = {m2:.1f} mm)")
print(f"    피니언: z={z1_2}T, d={d2_pinion:.1f}mm")
print(f"    기  어: z={z2_2}T, d={d2_gear:.1f}mm")
print(f"    중심거리: a = {a2:.1f} mm")
print(f"    기어 폭: b = {b2:.1f} mm")

# ============================================================
# 6. 축 직경 계산 (ASME 기준)
# ============================================================
print(f"\n[6] 축 직경 계산 - ASME 기준")
print("-" * 50)

# 축 재질: S45C
tau_allow = 55      # 허용 전단 응력 [MPa]
Kt = 2.0            # 응력 집중 계수
Cm = 1.5            # 굽힘 모멘트 계수
Ct = 1.0            # 비틀림 모멘트 계수

def shaft_diameter(T, tau_allow=55, Kt=2.0):
    """
    ASME 공식에 의한 축 직경 계산
    T: 토크 [N.m]
    """
    M = T * 0.3  # 굽힘 모멘트 추정 (토크의 30%)
    # d^3 = (16/pi*tau) * sqrt[(Cm*M)^2 + (Ct*T)^2]
    # 단위: N.m -> N.mm (x1000)
    term = math.sqrt((Cm * M * 1000)**2 + (Ct * T * 1000)**2)
    d_cubed = (16 / (math.pi * tau_allow)) * Kt * term
    d = d_cubed ** (1/3)
    return math.ceil(d / 5) * 5  # 5mm 단위로 올림

d_input = shaft_diameter(T1)
d_intermediate = shaft_diameter(T2)
d_output = shaft_diameter(T3)

print(f"  입력축 (1축) 직경:  dia {d_input:.0f} mm  (토크 {T1:.1f} N.m)")
print(f"  중간축 (2축) 직경:  dia {d_intermediate:.0f} mm  (토크 {T2:.1f} N.m)")
print(f"  출력축 (3축) 직경:  dia {d_output:.0f} mm  (토크 {T3:.1f} N.m)")

# ============================================================
# 7. 강도 검증 (AGMA)
# ============================================================
print(f"\n[7] 강도 검증 - AGMA 2001-D04")
print("-" * 50)

# 탄성 계수 (강-강)
Ze = 191            # [MPa^0.5]

# AGMA 기하계수
def agma_J_factor(z, helix_deg):
    """굽힘 강도용 기하계수 J"""
    z_eq = z / (math.cos(math.radians(helix_deg)) ** 3)
    J = 0.45 + 0.003 * z_eq
    return min(J, 0.55)

def agma_I_factor(z1, z2, pressure_angle):
    """면압 강도용 기하계수 I"""
    phi = math.radians(pressure_angle)
    mg = z2 / z1
    I = (math.cos(phi) * math.sin(phi)) / (2 * (1 + 1/mg))
    return I

# 1단 기어 강도 검증
J1 = agma_J_factor(z1_1, helix_angle)
I1 = agma_I_factor(z1_1, z2_1, pressure_angle)
b1 = psi * m1
Wt1 = (2 * T1 * 1000) / d1_pinion

# 굽힘 응력
sigma_F1 = (Wt1 * Ka * Kv1 * Ks * Km * KB) / (b1 * m1 * J1)
SF1 = sigma_Fb / sigma_F1  # 굽힘 안전율

# 접촉 응력
sigma_H1 = Ze * math.sqrt((Wt1 * Ka * Kv1 * Ks * Km) / (d1_pinion * b1 * I1))
SH1 = sigma_Hb / sigma_H1  # 면압 안전율

print(f"\n  [1단 기어 강도]")
print(f"    접선력 Wt = {Wt1:.1f} N")
print(f"    굽힘 응력 sigmaF = {sigma_F1:.1f} MPa (허용: {sigma_Fb} MPa)")
print(f"    굽힘 안전율 SF = {SF1:.2f} {'[OK]' if SF1 >= 1.5 else '[NG]'}")
print(f"    접촉 응력 sigmaH = {sigma_H1:.1f} MPa (허용: {sigma_Hb} MPa)")
print(f"    면압 안전율 SH = {SH1:.2f} {'[OK]' if SH1 >= 1.2 else '[NG]'}")

# 2단 기어 강도 검증
J2 = agma_J_factor(z1_2, helix_angle)
I2 = agma_I_factor(z1_2, z2_2, pressure_angle)
b2 = psi * m2
Wt2 = (2 * T2 * 1000) / d2_pinion

sigma_F2 = (Wt2 * Ka * Kv2 * Ks * Km * KB) / (b2 * m2 * J2)
SF2 = sigma_Fb / sigma_F2

sigma_H2 = Ze * math.sqrt((Wt2 * Ka * Kv2 * Ks * Km) / (d2_pinion * b2 * I2))
SH2 = sigma_Hb / sigma_H2

print(f"\n  [2단 기어 강도]")
print(f"    접선력 Wt = {Wt2:.1f} N")
print(f"    굽힘 응력 sigmaF = {sigma_F2:.1f} MPa (허용: {sigma_Fb} MPa)")
print(f"    굽힘 안전율 SF = {SF2:.2f} {'[OK]' if SF2 >= 1.5 else '[NG]'}")
print(f"    접촉 응력 sigmaH = {sigma_H2:.1f} MPa (허용: {sigma_Hb} MPa)")
print(f"    면압 안전율 SH = {SH2:.2f} {'[OK]' if SH2 >= 1.2 else '[NG]'}")

# ============================================================
# 8. 열 방출 및 냉각 검토
# ============================================================
print(f"\n[8] 열 방출 및 냉각 검토")
print("-" * 50)

# 효율 및 열손실 계산
eta_gear = 0.98     # 기어 1쌍당 효율
eta_bearing = 0.99  # 베어링 1개당 효율
n_gear_pairs = 2
n_bearings = 6      # 3축 x 2개

eta_total = (eta_gear ** n_gear_pairs) * (eta_bearing ** n_bearings)
P_loss = P * (1 - eta_total)  # 열손실 [W]

print(f"  총 전달 효율: eta = {eta_total*100:.1f}%")
print(f"  열 손실: Q = {P_loss:.0f} W")

# 하우징 방열 면적 추정
L_housing = (a1 + a2) * 1.3 / 1000  # 길이 [m]
W_housing = max(d1_gear, d2_gear) * 0.6 / 1000  # 폭 [m]
H_housing = max(d1_gear, d2_gear) * 0.5 / 1000  # 높이 [m]

A_housing = 2 * (L_housing * W_housing + W_housing * H_housing + H_housing * L_housing)

# 열전달 계수
h_natural = 10      # [W/m2.K] (자연 대류)
h_forced = 25       # [W/m2.K] (강제 대류)
T_ambient = 25      # 주변 온도 [C]
T_max_oil = 80      # 최대 허용 오일 온도 [C]
dT_allow = T_max_oil - T_ambient

# 방열량 계산
Q_natural = h_natural * A_housing * dT_allow
Q_forced = h_forced * A_housing * dT_allow

print(f"\n  하우징 크기 (추정):")
print(f"    L x W x H = {L_housing*1000:.0f} x {W_housing*1000:.0f} x {H_housing*1000:.0f} mm")
print(f"    방열 면적: A = {A_housing:.3f} m2")
print(f"\n  방열 능력 비교:")
print(f"    자연 대류: {Q_natural:.0f} W")
print(f"    강제 대류: {Q_forced:.0f} W")
print(f"    필요 방열량: {P_loss:.0f} W")

if P_loss <= Q_natural:
    cooling_result = "자연 대류로 충분 -> 방열 핀 불필요"
    fin_needed = False
elif P_loss <= Q_forced:
    cooling_result = "냉각 팬 권장 (방열 핀 선택사항)"
    fin_needed = False
else:
    cooling_result = "방열 핀 + 냉각 팬 필요"
    fin_needed = True

print(f"\n  >> 판정: {cooling_result}")

# ============================================================
# 9. 설계 결과 요약
# ============================================================
print(f"\n{'='*70}")
print(f"                    [설계 결과 요약]")
print(f"{'='*70}")

print(f"""
+--------------------------------------------------------------------+
|                     기어박스 최종 사양                             |
+--------------------------------------------------------------------+
| 동력: {P_kW:.0f} kW | 감속비: {actual_ratio:.0f}:1 | 효율: {eta_total*100:.1f}%                  |
+--------------------------------------------------------------------+

  [1단 헬리컬 기어]               [2단 헬리컬 기어]
  -----------------------         -----------------------
  모듈:     m = {m1:.1f} mm            모듈:     m = {m2:.1f} mm
  피니언:   {z1_1}T (dia {d1_pinion:.0f}mm)        피니언:   {z1_2}T (dia {d2_pinion:.0f}mm)
  기  어:   {z2_1}T (dia {d1_gear:.0f}mm)       기  어:   {z2_2}T (dia {d2_gear:.0f}mm)
  중심거리: {a1:.0f} mm                중심거리: {a2:.0f} mm
  기어 폭:  {b1:.0f} mm                 기어 폭:  {b2:.0f} mm
  감속비:   {ratio_1:.1f}:1                감속비:   {ratio_2:.1f}:1

+--------------------------------------------------------------------+
| [축 직경]                                                          |
|   입력축: dia {d_input:.0f}mm | 중간축: dia {d_intermediate:.0f}mm | 출력축: dia {d_output:.0f}mm          |
+--------------------------------------------------------------------+
| [안전율]                                                           |
|   1단 - 굽힘: SF = {SF1:.2f}  면압: SH = {SH1:.2f}                     |
|   2단 - 굽힘: SF = {SF2:.2f}  면압: SH = {SH2:.2f}                     |
+--------------------------------------------------------------------+
| [냉각]                                                             |
|   {cooling_result:<50}         |
+--------------------------------------------------------------------+
""")

print("계산 완료!")
