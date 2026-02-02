# Phase 1 과제: 기본 환경 설정 및 도구 설치

>[!info]
>**과제 제출 기한**: 1회차 세미나 3일 전
>**제출 방법**: 이메일 (orientpine@kimm.re.kr)
>**과제 목적**: AI 시대 생존을 위한 핵심 도구 3종(Obsidian, Claude Code, Git) 설치 및 환경 검증

---

## 📋 과제 체크리스트

| 항목 | 완료 여부 |
|------|----------|
| Obsidian 설치 및 Vault 생성 | ☐ |
| Claude Code 설치 (Pro 구독 필요) | ☐ |
| Git 설치 및 버전 확인 | ☐ |
| GitHub 계정 생성 및 Obsidian Vault를 Public 저장소로 업로드 | ☐ |
| Node.js 설치 및 버전 확인 | ☐ |
| Python 설치 및 버전 확인 | ☐ |

---

## 1. Obsidian 설치 및 신규 Vault 생성

### 1.1 Obsidian이란?

Obsidian은 **"제2의 뇌"**를 구축하기 위한 지식 관리 도구입니다. 마크다운 기반으로 노트를 작성하고, 노트 간 연결을 통해 지식 네트워크를 형성합니다.

**핵심 철학**: "File over app" - 모든 노트는 일반 마크다운 파일로 저장되어 영원히 소유할 수 있습니다.

### 1.2 설치 절차

#### Step 1: 다운로드
1. [Obsidian 공식 사이트](https://obsidian.md/) 접속
2. 운영체제에 맞는 설치 파일 다운로드 (Windows/Mac/Linux 지원)

#### Step 2: 설치
1. 다운로드된 설치 파일 실행
2. 설치 마법사 지시에 따라 설치 완료

#### Step 3: Vault 생성
1. Obsidian 실행
2. "Create new vault" 선택
3. Vault 이름 입력 (예: `퇴직준비세미나_홍길동`)
4. 저장 위치 선택 (권장: `C:\Users\[사용자명]\Documents\` 또는 원하는 위치)
5. "Create" 버튼 클릭

#### Step 4: 기본 설정
1. 좌측 하단 톱니바퀴(⚙️) 클릭
2. **Options > General**
   - Language: 한국어 선택
3. **Options > Editor**
   - Default editing mode: "Live Preview" 권장
4. **Options > Files & Links**
   - Default location for new notes: "In the folder specified below"

### 1.3 제출물
- [ ] **Obsidian Vault를 GitHub에 업로드** (섹션 4 참조)
  - Vault 생성 후 GitHub Public 저장소에 올리면 제출 완료!

---

## 2. Claude Code 설치 (Pro 구독 필요)

### 2.1 Claude Code란?

Claude Code는 Anthropic에서 개발한 **AI 코딩 어시스턴트 CLI(Command Line Interface) 도구**입니다. 터미널에서 직접 실행되며, 코드베이스를 이해하고 코드 작성, 디버깅, Git 워크플로우 등을 자연어 명령으로 수행할 수 있습니다.

> [!warning] **Claude Pro 구독 필요**
> Claude Code를 사용하려면 **Claude Pro 구독** (월 $20)이 필요합니다.
> 1. 먼저 [Claude.ai](https://claude.ai/)에서 계정을 생성하세요
> 2. Settings > Subscription에서 Pro 플랜으로 업그레이드하세요
> 3. 결제 완료 후 Claude Code 인증이 가능합니다

### 2.2 시스템 요구사항

| 항목 | 요구사항 |
|------|----------|
| 운영체제 | Windows 10+ (WSL 또는 Git Bash), macOS 13.0+, Ubuntu 20.04+ |
| 메모리 | 4GB RAM 이상 |
| 네트워크 | 인터넷 연결 필수 |
| 선행 설치 | Node.js 18+ (npm 설치 방식 사용 시) |

### 2.3 설치 절차

#### Windows 설치 방법

**방법 1: PowerShell 스크립트 (권장)**

1. **PowerShell을 관리자 권한으로 실행**
   - 시작 메뉴에서 "PowerShell" 검색
   - 우클릭 → "관리자 권한으로 실행"

2. **설치 명령어 실행**
   ```powershell
   irm https://claude.ai/install.ps1 | iex
   ```

3. **설치 확인**
   ```powershell
   claude --version
   ```

**방법 2: WinGet으로 설치**

```powershell
winget install Anthropic.ClaudeCode
```

**방법 3: npm으로 설치** (Node.js 필요)

```bash
npm install -g @anthropic-ai/claude-code
```

#### Mac 설치 방법

**방법 1: 설치 스크립트 (권장)**

1. **터미널 열기** (Command + Space → "Terminal" 입력)

2. **설치 명령어 실행**
   ```bash
   curl -fsSL https://claude.ai/install.sh | bash
   ```

3. **쉘 설정 다시 로드**
   ```bash
   source ~/.zshrc
   # 또는 bash 사용 시: source ~/.bashrc
   ```

4. **설치 확인**
   ```bash
   claude --version
   ```

**방법 2: Homebrew로 설치**

```bash
brew install --cask claude-code
```

### 2.4 Claude Code 인증 (로그인)

설치 후 처음 실행하면 인증이 필요합니다:

1. **터미널에서 Claude Code 실행**
   ```bash
   claude
   ```

2. **브라우저에서 인증**
   - 자동으로 브라우저가 열리며 Claude.ai 로그인 페이지로 이동
   - Claude Pro 계정으로 로그인
   - "Authorize" 버튼 클릭하여 CLI 접근 허용

3. **인증 완료 확인**
   - 터미널에 "Authentication successful" 메시지 표시
   - 이제 Claude Code 사용 가능!

### 2.5 설치 검증 (claude doctor)

설치가 제대로 되었는지 확인하려면:

```bash
claude doctor
```

이 명령어는 설치 상태, 인증 상태, 환경 설정 등을 진단하고 문제가 있으면 해결 방법을 안내합니다.

### 2.6 첫 사용 테스트

프로젝트 폴더에서 Claude Code를 실행해보세요:

```bash
# 원하는 프로젝트 폴더로 이동
cd ~/Documents/퇴직준비세미나_홍길동

# Claude Code 실행
claude

# 대화창에서 다음 메시지 입력
> 안녕하세요! 이 폴더의 구조를 설명해주세요.
```

### 2.7 제출물
- [ ] **`claude --version` 또는 `claude doctor` 실행 결과 스크린샷**

---

## 3. Git 설치 및 버전 확인

### 3.1 Git이란?

Git은 **'코드와 문서의 타임머신'**입니다. 파일의 변경 이력을 모두 기록하고 언제든지 과거의 특정 시점으로 되돌아갈 수 있습니다.

**핵심 장점**:
- 📜 **버전 관리**: 누가, 언제, 무엇을 바꿨는지 추적
- 👥 **협업**: 여러 사람이 동시에 같은 파일 수정 가능
- 💾 **백업**: 온라인 저장소에 올리면 안전하게 보관

### 3.2 설치 절차

#### Windows

1. [Git 공식 사이트](https://git-scm.com/) 접속
2. "Download for Windows" 클릭
3. 설치 파일 실행
4. 설치 옵션 설정 (대부분 기본값으로 Next):
   - **Default editor**: VS Code 또는 Notepad++ 선택 권장
   - **PATH environment**: "Git from the command line and also from 3rd-party software" 선택
   - **Line ending conversions**: "Checkout Windows-style, commit Unix-style line endings" 선택
5. 설치 완료

#### Mac

1. Terminal 열기 (Command + Space → "Terminal" 입력)
2. `git --version` 입력
3. 설치되어 있지 않으면 팝업에서 "Install" 클릭
4. 또는 Homebrew로 설치: `brew install git`

### 3.3 버전 확인

**Windows**: 
1. 시작 메뉴에서 "Git Bash" 또는 "명령 프롬프트" 실행
2. 다음 명령어 입력:

```bash
git --version
```

**예상 출력**:
```
git version 2.43.0.windows.1
```

### 3.4 최초 설정 (필수!)

```bash
# 이름 설정 (본인 이름으로 변경)
git config --global user.name "홍길동"

# 이메일 설정 (본인 이메일로 변경)
git config --global user.email "hong@example.com"

# 기본 브랜치 이름을 main으로 설정
git config --global init.defaultBranch main

# 설정 확인
git config --list
```

### 3.5 제출물
- [ ] **`git --version` 실행 결과 스크린샷**

---

## 4. GitHub 계정 생성 및 Obsidian Vault를 Public 저장소로 업로드

### 4.1 GitHub란?

GitHub는 Git 저장소를 온라인으로 호스팅하는 서비스입니다. 코드와 문서를 클라우드에 백업하고, 다른 사람과 공유할 수 있습니다.

### 4.2 GitHub 계정 생성

1. [GitHub](https://github.com/) 접속
2. "Sign up" 클릭
3. 이메일, 비밀번호, 사용자명 입력
4. 이메일 인증 완료
5. 로그인 확인

### 4.3 새 Public 저장소 생성

1. GitHub 로그인 후 우측 상단 **"+"** 버튼 클릭
2. **"New repository"** 선택
3. 저장소 정보 입력:
   - **Repository name**: `obsidian-퇴직준비세미나` (또는 원하는 이름)
   - **Description**: `퇴직준비 세미나 Obsidian Vault` (선택사항)
   - **⚠️ Public 선택** (반드시 Public으로!)
   - "Add a README file" 체크 **해제** (나중에 직접 추가)
4. **"Create repository"** 버튼 클릭
5. 생성된 저장소 URL 복사 (예: `https://github.com/사용자명/obsidian-퇴직준비세미나.git`)

### 4.4 Obsidian Vault를 GitHub에 업로드

#### Step 1: Obsidian Vault 폴더로 이동

**Windows (Git Bash 또는 명령 프롬프트)**:
```bash
cd "C:\Users\사용자명\Documents\퇴직준비세미나_홍길동"
```

**Mac (터미널)**:
```bash
cd ~/Documents/퇴직준비세미나_홍길동
```

#### Step 2: Git 저장소 초기화

```bash
# Git 저장소 초기화
git init

# 모든 파일 스테이징
git add .

# 첫 번째 커밋 생성
git commit -m "Initial commit: Obsidian Vault 생성"
```

#### Step 3: GitHub 원격 저장소 연결 및 업로드

```bash
# 원격 저장소 연결 (본인의 저장소 URL로 변경!)
git remote add origin https://github.com/사용자명/obsidian-퇴직준비세미나.git

# 기본 브랜치를 main으로 설정
git branch -M main

# GitHub에 업로드 (처음 실행 시 GitHub 로그인 필요)
git push -u origin main
```

> [!tip] **GitHub 인증 방법**
> `git push` 실행 시 GitHub 로그인이 필요합니다:
> - **Windows**: 자동으로 GitHub 로그인 창이 나타납니다
> - **Mac**: Personal Access Token 또는 SSH 키 설정이 필요할 수 있습니다
> - 자세한 인증 설정은 세미나에서 안내드립니다

#### Step 4: 업로드 확인

1. 브라우저에서 본인의 GitHub 저장소 페이지 새로고침
2. Obsidian Vault 파일들이 보이면 성공!

### 4.5 저장소 URL 공유

제출 시 본인의 GitHub 저장소 URL을 공유해주세요:
```
https://github.com/사용자명/obsidian-퇴직준비세미나
```

> [!warning] **반드시 Public 저장소로!**
> Private 저장소는 제가 확인할 수 없습니다. 저장소 설정에서 **Public**인지 확인하세요.

### 4.6 제출물
- [ ] **GitHub 저장소 URL** (예: `https://github.com/사용자명/obsidian-퇴직준비세미나`)
- [ ] **저장소에 Obsidian Vault 파일이 업로드된 스크린샷**

---

## 5. Node.js 설치 및 버전 확인

### 5.1 Node.js란?

Node.js는 JavaScript 런타임 환경입니다. 많은 AI 도구들(Claude Code, oh-my-opencode 등)이 Node.js 기반으로 동작합니다.

### 5.2 설치 절차

#### Windows & Mac

1. [Node.js 공식 사이트](https://nodejs.org/) 접속
2. **LTS (Long Term Support)** 버전 다운로드 (권장)
3. 설치 파일 실행
4. 설치 마법사 지시에 따라 설치 (기본 옵션 유지)
5. 설치 완료 후 터미널/명령 프롬프트 재시작

### 5.3 버전 확인

명령 프롬프트 또는 터미널에서:

```bash
node -v
```

**예상 출력**:
```
v20.11.0
```

npm (Node Package Manager) 버전도 확인:

```bash
npm -v
```

**예상 출력**:
```
10.2.4
```

### 5.4 제출물
- [ ] **`node -v` 실행 결과 스크린샷**

---

## 6. Python 설치 및 버전 확인

### 6.1 Python이란?

Python은 데이터 분석, AI/ML, 자동화 스크립트 등에 널리 사용되는 프로그래밍 언어입니다.

### 6.2 설치 절차

#### Windows

1. [Python 공식 사이트](https://www.python.org/downloads/) 접속
2. "Download Python 3.x.x" 클릭
3. 설치 파일 실행
4. **⚠️ 중요**: "Add Python to PATH" 체크박스 반드시 체크!
5. "Install Now" 클릭
6. 설치 완료

#### Mac

1. Terminal 열기
2. Homebrew로 설치 (권장):
```bash
brew install python
```

또는 [Python 공식 사이트](https://www.python.org/downloads/)에서 다운로드

### 6.3 버전 확인

명령 프롬프트 또는 터미널에서:

```bash
python --version
```

**예상 출력**:
```
Python 3.11.7
```

pip (Python 패키지 관리자) 버전도 확인:

```bash
pip --version
```

**예상 출력**:
```
pip 23.3.2 from ... (python 3.11)
```

> **참고**: Windows에서 `python`이 안 되면 `python3` 또는 `py`로 시도해보세요.

### 6.4 제출물
- [ ] **`python --version` 실행 결과 스크린샷**

---

## 📚 관련 교육 자료

### 내부 Resource 링크
- [[000_PARA/Resource/008_eduDoc/Obsidian/Obsidian 교육 자료]] - Obsidian 상세 학습
- [[000_PARA/Resource/008_eduDoc/Obsidian/Obsidian 소개와 설치]] - 설치 가이드
- [[000_PARA/Resource/008_eduDoc/버전관리/Git 소개와 설치]] - Git 상세 가이드
- [[000_PARA/Resource/008_eduDoc/버전관리/Git 기본 명령어]] - Git 명령어 학습

### 외부 학습 자료

#### Obsidian
- 🔗 [Obsidian 공식 문서](https://help.obsidian.md/)
- 🔗 [Obsidian 한국어 커뮤니티](https://forum.obsidian.md/)
- 📺 [Obsidian 시작하기 (YouTube)](https://www.youtube.com/results?search_query=obsidian+tutorial+beginner)

#### Git
- 🔗 [Git 공식 문서 (한국어)](https://git-scm.com/book/ko/v2)
- 🔗 [생활코딩 Git](https://opentutorials.org/course/3837)
- 📺 [Git & GitHub 튜토리얼](https://www.youtube.com/results?search_query=git+github+tutorial+korean)

#### Claude Code
- 🔗 [Claude Code 공식 문서](https://docs.anthropic.com/en/docs/claude-code)
- 🔗 [Claude Code 설치 가이드](https://code.claude.com/docs/en/setup)
- 🔗 [Claude 프롬프트 엔지니어링 가이드](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering)

#### GitHub
- 🔗 [GitHub 시작하기 (한국어)](https://docs.github.com/ko/get-started)
- 🔗 [GitHub 계정 만들기](https://docs.github.com/ko/get-started/signing-up-for-github)
- 📺 [GitHub 튜토리얼](https://www.youtube.com/results?search_query=github+tutorial+korean+beginner)

---

## 📤 과제 제출 양식

### 이메일 제목
```
[퇴직준비세미나] Phase 1 과제 제출 - 이근호
```

### 이메일 본문
```
안녕하세요, 퇴직준비 세미나 Phase 1 과제를 제출합니다.

■ 이름: 이근호
■ 소속: DX산업기계연구실

■ 과제 완료 현황:
1. Obsidian 설치 및 Vault 생성: ✅ 완료
2. Claude Code 설치: ✅ 완료 (claude --version: 1.1.23)
3. Git 설치: ✅ 완료 (git version 2.52.0.windows.1)
4. GitHub 저장소 생성 및 업로드: ✅ 완료
5. Node.js 설치: ✅ 완료 (버전: v24.13.0py)
6. Python 설치: ✅ 완료 (버전: 3.13.7)

■ GitHub 저장소 URL:
https://github.com/geunho762/-Obsidian-seminar

■ 어려웠던 점 또는 질문사항:
처음하는 것이라 모든 석이 새롭고 쉽지않네요. 여러번 하여 겨우했는데 환경설정이 잘 되었는 모르겠습니다.
Obsidian Vault가 Github에 업로드가 잘 안되는 것 같습니다.
Git과 Obsidian-Vault가 있는 폴더의 연결 문제 같은데?


### 첨부 파일 목록
1. `claude_code_screenshot.png` - Claude Code 설치 확인 화면 (`claude --version` 또는 `claude doctor`)
2. `github_repo_screenshot.png` - GitHub 저장소에 Obsidian Vault가 업로드된 화면

---

## ❓ 자주 묻는 질문 (FAQ)

### Q1: Obsidian Vault를 어디에 만들어야 하나요?
**A**: 본인이 쉽게 찾을 수 있는 위치면 됩니다. 권장: `문서(Documents)` 폴더 내에 생성. 나중에 Git과 연동하면 클라우드 백업도 가능합니다.

### Q2: Git 설치 시 어떤 옵션을 선택해야 하나요?
**A**: 대부분 기본값(Next)으로 진행하면 됩니다. 단, "Add Git to PATH" 옵션은 반드시 선택해야 명령 프롬프트에서 git 명령어를 사용할 수 있습니다.

### Q3: Python 설치 후 `python` 명령어가 안 됩니다.
**A**: Windows에서 `python3` 또는 `py` 명령어를 사용해보세요. 또는 설치 시 "Add Python to PATH"를 체크하지 않았다면 재설치를 권장합니다.

### Q4: Claude Code 사용에 Pro 구독이 필요한가요?
**A**: 네, Claude Code는 **Claude Pro 구독** (월 $20)이 필요합니다. 먼저 [Claude.ai](https://claude.ai/)에서 계정 생성 후 Pro 플랜으로 업그레이드하세요.

### Q5: GitHub 저장소를 Public으로 만들어야 하는 이유가 뭔가요?
**A**: Private 저장소는 본인만 볼 수 있어서 강사가 과제를 확인할 수 없습니다. Public으로 설정해야 제출한 과제를 확인할 수 있습니다.

### Q6: git push 시 인증 오류가 발생합니다.
**A**: GitHub 인증 방식이 변경되었습니다. 
- **Windows**: Git Credential Manager가 자동으로 처리합니다. 브라우저에서 GitHub 로그인하면 됩니다.

---

## ✅ 최종 체크리스트

과제 제출 전 다음 항목들을 확인하세요:

- [ ] Obsidian 실행 가능, Vault 생성됨
- [ ] Claude Code 설치 완료 (`claude --version` 정상 작동)
- [ ] `git --version` 명령어 정상 작동
- [ ] GitHub 계정 생성됨
- [ ] Obsidian Vault가 GitHub **Public** 저장소에 업로드됨
- [ ] `node -v` 명령어 정상 작동
- [ ] `python --version` 명령어 정상 작동
- [ ] 스크린샷 2장 촬영 완료 (Claude Code 설치 화면, GitHub 저장소 화면)
- [ ] 이메일에 GitHub 저장소 URL 포함
- [ ] 이메일 제출 완료

---

> **다음 단계**: Phase 1 과제를 완료하면 1회차 세미나에서 **PARA 폴더 구조 생성** 및 **Claude Code / OpenCode 활용법**을 진행합니다.
