# 퇴직준비세미나 Obsidian Vault - 이근호

## 프로젝트 개요

퇴직준비 세미나 학습을 위한 Obsidian 볼트입니다. AI 도구(Claude Code)를 활용한
지식 관리, 문서 자동화, 연구 지원을 목적으로 구성되어 있습니다.

## 폴더 구조 (PARA 방식)

```
볼트 루트/
├── Inbox/              ← 미분류 새 메모 (vault-organizer가 주기적으로 정리)
├── Projects/           ← 진행 중 프로젝트
│   ├── 기어박스_설계/     ← AGMA, KISSsoft, 플라스틱 기어 연구
│   ├── 회전익기_동력전달/ ← 헬리콥터 기어트레인 연구
│   └── 투자_재무설계/    ← ETF, 포트폴리오, 연금 계획
├── References/         ← 논문 번역/요약 (번역_, 요약_ 접두사)
├── Seminars/           ← 세미나 자료
│   ├── 회차별자료/       ← 1~10회차 강의 MD 파일
│   ├── Homework/        ← 과제 제출
│   └── 공지사항/
├── Daily Notes/        ← 날짜별 작업 요약 (YYYY-MM-DD_*.md)
├── Guides/             ← 사용법, 가이드 문서
├── Templates/          ← 문서 템플릿
├── Attachments/        ← 이미지, PDF 첨부파일
├── Archive/            ← 완료/오래된 자료
├── Files/              ← 추출된 이미지 등 보조 파일
└── 회치별자율학습자료/   ← 원본 강의 자료 (수정 금지)
```

## Claude 에이전트 (.claude/agents/)

| 에이전트 | 역할 | 호출 예시 |
|---------|------|----------|
| `vault-organizer` | Inbox 파일 자동 분류 + 프론트매터 추가 | "볼트 정리해줘" |
| `paper-translator` | PDF 논문 → 한국어 번역 + 요약 MD 생성 | "이 논문 번역해줘: path/to.pdf" |
| `retirement-seminar-tutor` | 회차별 강의 AI 튜터 | "2회차 강의 시작해줘" |

## 핵심 규칙

- **절대 파일 삭제 금지**: 불필요 파일은 `Archive/`로 이동
- **`회치별자율학습자료/`** 폴더는 원본 보존 - 수정하지 않음
- **`.claude/`, `.obsidian/`, `.git/`, `.trash/`** 폴더 미조작
- **프론트매터 형식**: `created`, `tags`, `category`, `status` 필드 사용
- **파일명 규칙**: `번역_`, `요약_` 접두사는 References 폴더용

## 자동화 스크립트 (.claude/scripts/)

- `vault_organizer.py`: 볼트 정리 스크립트 (매주 월요일 자동 실행)
- `organizer_log.md`: 정리 작업 로그

## Git 워크플로우

- 브랜치: `main`
- 커밋 후 로그: `Daily Notes/`에 작업 요약 기록
- 민감 정보 커밋 금지 (개인 재무 데이터 등)

## 세미나 학습 진행 현황

- 1회차: 오리엔테이션 & 환경설정
- 2회차: 프롬프트 엔지니어링 기초 (RCIF 공식)
- 3회차: AI Agent 개념과 아키텍처
- Phase 2: Claude Code 자동화 (현재 진행 중)
