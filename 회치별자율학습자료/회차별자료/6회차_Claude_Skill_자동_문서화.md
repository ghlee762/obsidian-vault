>[!info]
>**Author**: Baekdong Cha (차백동)
>**Email**: orientpine@gmail.com | orientpine@kimm.re.kr
>**Affiliation**: Korea Institute of Machinery and Materials (한국기계연구원)
>**Created**: 2026-01-27
>**Location**: 퇴직준비세미나/세미나자료/회차별강의자료
>**Tag**: #세미나 #퇴직준비 #6회차 #Claude #자동문서화 #RAG #MCP
>**License**: CC BY 4.0

---

# 6회차: 구조화된 사고 → 자동 문서화 파이프라인

> "AI에게 단순히 글을 써달라고 하는 단계를 넘어,  
> 나의 지식 베이스와 도구를 연결하여 자동으로 문서를 생성하는 시스템을 구축합니다."

---

## 🎯 학습 목표

이번 세션을 완료하면 다음을 할 수 있습니다:

- [ ] RAG(Retrieval-Augmented Generation)의 기본 개념과 작동 원리를 이해한다
- [ ] MCP(Model Context Protocol)를 통해 Claude에게 로컬 파일 및 외부 맥락을 제공할 수 있다
- [ ] Claude의 문서 작성 능력을 극대화하는 구조화된 프롬프트 기법을 습득한다
- [ ] 템플릿 기반의 자동 문서화 파이프라인(회의록, 연구노트 등)을 구축한다
- [ ] Phase 4 과제인 Obsidian PARA 구조 구축 및 지식 연결을 시작한다

---

## 📋 강의 개요 (3시간)

| 시간 | 내용 | 형식 |
|------|------|------|
| 00:00-00:40 | Part 1: RAG 기초 개념 | 강의 |
| 00:40-00:50 | 휴식 | - |
| 00:50-01:30 | Part 2: MCP로 AI에게 맥락 제공 | 강의 + 실습 |
| 01:30-01:40 | 휴식 | - |
| 01:40-02:20 | Part 3: Claude 문서 작성 능력 극대화 기법 | 강의 + 실습 |
| 02:20-02:30 | 휴식 | - |
| 02:30-03:00 | Part 4: 자동 문서화 파이프라인 구축 실습 + Phase 4 과제 | 워크숍 |

---

## Part 1: RAG 기초 개념 (40분)

### 1.1 RAG(Retrieval-Augmented Generation)란?

RAG는 LLM의 지식을 **외부 데이터 소스로 확장**하는 기술입니다.

```
사용자 질문 → 관련 문서 검색(Retrieval) → 검색 결과 + 질문을 LLM에 전달 → 답변 생성(Generation)
```

### 1.2 왜 RAG가 필요한가?

| 문제점 | RAG 해결 방식 |
|------|---------------|
| **지식 컷오프** | 최신 문서를 실시간으로 검색하여 반영 |
| **할루시네이션** | 제공된 실제 문서 근거를 바탕으로 답변 생성 |
| **도메인 지식 부족** | 내부 보고서, 특정 분야 논문 DB 등과 연동 |
| **보안 및 비용** | 모델 전체를 재학습(Fine-tuning)하지 않고도 지식 업데이트 가능 |

### 1.3 RAG의 핵심 구성 요소

1. **Document Loader**: PDF, 웹페이지, DB 등에서 문서 수집
2. **Text Splitter**: 문서를 의미 있는 단위(Chunk)로 분할
3. **Embedding Model**: 텍스트를 컴퓨터가 이해하는 숫자 벡터로 변환
4. **Vector Store**: 벡터화된 정보를 저장하고 유사도 검색 수행
5. **Retriever**: 질문과 가장 관련 있는 청크를 찾아냄
6. **LLM**: 검색된 정보를 바탕으로 최종 답변 생성

### 1.4 RAG 구현 예시 (Python + LangChain)

```python
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.llms import Claude

# 1. 문서 로드
loader = PyPDFLoader("research_paper.pdf")
documents = loader.load()

# 2. 청크 분할
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = splitter.split_documents(documents)

# 3. 벡터 저장소 생성
embeddings = OpenAIEmbeddings()
vectorstore = Chroma.from_documents(chunks, embeddings)

# 4. RAG 체인 구성
qa_chain = RetrievalQA.from_chain_type(
    llm=Claude(),
    chain_type="stuff",
    retriever=vectorstore.as_retriever()
)

# 5. 질의
answer = qa_chain.run("이 논문의 주요 기여는 무엇인가요?")
```

> [!info] **핵심 인사이트**
> RAG는 AI에게 "오픈북 테스트"를 시키는 것과 같습니다.  
> AI가 모든 것을 외우게 하는 대신, 필요한 책을 찾아보고 답하게 하는 방식입니다.

---

## Part 2: MCP로 AI에게 맥락 제공 (40분)

### 2.1 MCP(Model Context Protocol) 개념

MCP는 Anthropic이 제안한 **LLM과 외부 도구/데이터 소스를 연결하는 표준 프로토콜**입니다.

```
Claude Desktop ↔ MCP Server ↔ 외부 서비스 (파일시스템, DB, API 등)
```

### 2.2 주요 구성 요소

- **MCP Server**: 외부 도구/데이터를 제공하는 서버 (예: 파일 시스템 접근 서버)
- **MCP Client**: LLM 애플리케이션 (예: Claude Desktop)
- **Tools**: MCP 서버가 제공하는 구체적인 기능 (함수)
- **Resources**: MCP 서버가 제공하는 데이터 (파일 내용 등)
- **Prompts**: 미리 정의된 프롬프트 템플릿

### 2.3 Claude Desktop에서 MCP 설정 (실습)

**설정 파일 위치**:
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`

**Filesystem MCP 설정 예시**:
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "C:/Users/YourName/Documents/ObsidianVault"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "your-token"
      }
    }
  }
}
```

### 2.4 실습: 로컬 파일 맥락 제공하기

1. `claude_desktop_config.json` 파일을 열고 본인의 Obsidian Vault 경로를 추가합니다.
2. Claude Desktop을 재시작합니다.
3. Claude에게 다음과 같이 요청해 봅니다:
   - "내 Obsidian Vault의 `Projects` 폴더에 있는 파일 목록을 보여줘."
   - "`회의록_20260127.md` 파일 내용을 읽고 핵심 내용을 요약해줘."

---

## Part 3: Claude 문서 작성 능력 극대화 기법 (40분)

### 3.1 구조화된 프롬프트 설계 (RCIF)

단순한 요청 대신, 문서의 구조와 스타일을 명확히 정의해야 합니다.

#### 1️⃣ 역할 부여 (Role)
"당신은 20년 경력의 기술 문서 전문가이자, 복잡한 연구 데이터를 일반인도 이해하기 쉽게 설명하는 과학 커뮤니케이터입니다."

#### 2️⃣ 맥락 제공 (Context)
"이 문서는 정부 과제 중간 보고서의 일부로 사용될 예정입니다. 독자는 기술 분야 전문가이지만, 우리 프로젝트의 세부 진행 상황은 모르는 상태입니다."

#### 3️⃣ 지시 사항 (Instruction)
"제공된 실험 데이터(CSV)를 분석하여 주요 성과 3가지를 도출하고, 이를 바탕으로 '향후 연구 방향' 섹션을 작성하세요."

#### 4️⃣ 형식 지정 (Format)
"마크다운 형식을 사용하고, 각 섹션은 H3 제목을 사용하세요. 성과는 표 형식으로 정리하고, 문체는 '~함', '~임'의 개조식을 사용하세요."

### 3.2 템플릿 활용 기법 (Few-shot)

Claude에게 원하는 문서의 예시(Template)를 제공하면 품질이 비약적으로 향상됩니다.

```markdown
예시 템플릿:
## [날짜] 연구 일지
- 주요 작업: 
- 발생한 문제: 
- 해결 방안: 
- 내일의 계획: 

위 템플릿을 사용하여 오늘 내가 수행한 [작업 내용]을 정리해줘.
```

---

## Part 4: 자동 문서화 파이프라인 구축 실습 (30분)

### 4.1 파이프라인 설계: 입력 → 처리 → 출력

1. **입력(Input)**: 녹취록, 거친 메모, 실험 데이터, 관련 논문 PDF
2. **처리(Process)**: Claude + MCP(파일 읽기) + RAG(관련 지식 검색)
3. **출력(Output)**: 정제된 보고서, 회의록, 연구노트 (Obsidian에 자동 저장)

### 4.2 실습: 회의록 자동 생성기 만들기

1. Obsidian에 `Templates/Meeting_Note_Template.md`를 생성합니다.
2. Claude에게 회의 녹취록(또는 메모)과 템플릿 파일을 읽게 합니다.
3. 템플릿 형식에 맞춰 회의록을 작성하게 한 뒤, 결과를 Obsidian의 `Projects` 폴더에 저장하도록 지시합니다.

### 4.3 Phase 4 과제 안내

이번 회차부터는 본격적으로 Obsidian을 활용한 지식 관리 시스템을 구축합니다.

---

## 📝 오늘 배운 내용 정리

### 핵심 요약

1. **RAG**: 외부 데이터를 검색하여 AI의 답변 품질을 높이고 할루시네이션을 줄이는 기술
2. **MCP**: Claude가 내 컴퓨터의 파일이나 외부 도구에 직접 접근할 수 있게 해주는 표준 규격
3. **자동 문서화**: 구조화된 프롬프트와 템플릿, 그리고 MCP를 결합하여 반복적인 문서 작업을 자동화
4. **지식 연결**: Obsidian의 PARA 구조와 양방향 링크를 통해 파편화된 정보를 체계적인 지식으로 전환

---

## 다음 회차 예고 및 과제 안내

### 7회차 예고: 1인 연구자의 무기들

> **"디스포저블 앱 - 필요할 때 만들고, 쓰고, 버린다"**

다음 시간에는 1인 연구 인프라 구축과 '디스포저블 앱' 개념을 배웁니다:
- 1인 연구 인프라(Personal Research Stack) 구축 철학
- Flywheel 사이클: 필요 발생 → 도구 생성 → 문제 해결 → 폐기
- 논문 리뷰 자동화 에이전트 구축 실습

### Phase 4 과제 (다음 회차 전까지 완료)

>[!warning] **필수 제출**
> **제목**: Obsidian PARA 구조 구축 및 지식 연결
> **마감**: 7회차 세미나 3일 전
>
> **제출물**:
> 1. Obsidian Vault에 PARA 폴더 구조 생성 (Projects/Areas/Resources/Archive)
> 2. 각 폴더에 최소 3개 이상의 노트 작성 (총 12개 이상)
> 3. 양방향 링크([[]])를 활용한 노트 간 연결 최소 10건
> 4. 그래프 뷰 스크린샷 제출 (연결된 노드 확인)
>
> **제출 방법**: 이메일 (orientpine@kimm.re.kr)

자세한 내용: [[Phase4_Obsidian_PARA_구조_구축]]

---

## 📚 관련 문서

- [[퇴직준비_세미나_소개]] - 세미나 전체 개요
- [[5회차_Obsidian_제2의_뇌_구축]] - 이전 강의
- [[Phase4_Obsidian_PARA_구조_구축]] - Phase 4 과제 상세

---

## ✅ 6회차 완료 체크리스트

오늘 세미나를 마치며 다음을 확인하세요:

- [ ] RAG의 기본 개념(검색 기반 생성)을 이해했다
- [ ] MCP의 역할과 Claude Desktop 설정 방법을 익혔다
- [ ] 구조화된 프롬프트(RCIF)로 문서 품질을 높이는 법을 배웠다
- [ ] 템플릿을 활용한 자동 문서화 과정을 실습했다
- [ ] Phase 4 과제 내용을 확인하고 계획을 세웠다

**모든 체크가 완료되면 6회차를 성공적으로 마친 것입니다! 🎉**

---

> 다음 회차: [[7회차_1인_연구자의_무기들]]

---

### [부록] RAG 및 MCP 심화 학습 자료

#### RAG (Retrieval-Augmented Generation)
- **개념**: LLM의 지식을 외부 데이터 소스로 확장하는 기술
- **장점**: 최신 정보 반영, 할루시네이션 감소, 도메인 특화 지식 활용
- **구성**: Document Loader → Text Splitter → Embedding → Vector Store → Retriever → LLM

#### MCP (Model Context Protocol)
- **개념**: LLM과 외부 도구/데이터 소스를 연결하는 표준 프로토콜
- **주요 서버**:
  - `@modelcontextprotocol/server-filesystem`: 파일 시스템 접근
  - `@modelcontextprotocol/server-github`: GitHub 연동
  - `@modelcontextprotocol/server-postgres`: PostgreSQL 쿼리
  - `@modelcontextprotocol/server-slack`: Slack 메시지
  - `@modelcontextprotocol/server-memory`: 지속적 메모리

#### 자동 문서화 파이프라인 예시
1. **회의록**: 녹취록 → Claude(MCP로 템플릿 읽기) → 정제된 회의록 → Obsidian 저장
2. **연구노트**: 실험 데이터(CSV) → Claude(데이터 분석) → 시각화 및 요약 → Obsidian 저장
3. **보고서**: 관련 논문(PDF) → RAG 검색 → 핵심 내용 추출 → 보고서 초안 작성

---

### [심화] RAG 아키텍처 상세 가이드

#### 1. 데이터 전처리 (Data Preprocessing)
RAG의 성능은 데이터의 품질과 구조에 크게 좌우됩니다.
- **Cleaning**: 불필요한 HTML 태그, 특수 문자, 중복 데이터 제거
- **Chunking Strategy**: 
  - Fixed-size chunking: 고정된 글자 수로 분할 (구현이 쉬움)
  - Recursive character splitting: 문단, 문장 단위로 의미를 보존하며 분할 (권장)
  - Semantic chunking: 의미적 유사성을 바탕으로 분할 (고급 기법)

#### 2. 임베딩 및 벡터 저장소 (Embedding & Vector Store)
- **Embedding**: 텍스트를 고차원 벡터 공간의 좌표로 변환. 유사한 의미를 가진 텍스트는 가까운 위치에 배치됨.
- **Vector DB 선택**:
  - **Chroma**: 로컬 환경에서 가볍게 시작하기 좋음 (오픈 소스)
  - **Pinecone**: 클라우드 기반 대규모 데이터 처리에 적합
  - **FAISS**: Facebook에서 개발한 고속 유사도 검색 라이브러리

#### 3. 검색 기법 (Retrieval Techniques)
- **Similarity Search**: 코사인 유사도 등을 이용한 단순 검색
- **Hybrid Search**: 키워드 검색(BM25)과 벡터 검색을 결합하여 정확도 향상
- **Re-ranking**: 검색된 결과들을 다시 한번 정밀하게 순위 매김

---

### [심화] MCP 서버 구축 및 활용

#### 1. 커스텀 MCP 서버가 필요한 이유
- 조직 내 고유한 데이터베이스나 API에 Claude를 연결하고 싶을 때
- 특정 업무 프로세스를 자동화하는 전용 도구를 만들고 싶을 때

#### 2. MCP 서버 개발 스택
- **Language**: TypeScript (권장), Python
- **Library**: `@modelcontextprotocol/sdk`
- **Transport**: Stdio (표준 입출력), HTTP/SSE

#### 3. 실전 활용 시나리오: 연구 데이터 분석 자동화
1. 연구원이 실험 결과가 담긴 Excel 파일을 특정 폴더에 저장
2. Claude에게 "최신 실험 데이터를 분석해서 보고서 써줘"라고 요청
3. Claude는 Filesystem MCP를 통해 파일을 읽고, Python Code Interpreter(또는 전용 MCP 도구)를 사용하여 통계 분석 수행
4. 분석 결과와 그래프를 포함한 마크다운 보고서를 생성하여 Obsidian에 저장

---

### [워크숍] 나만의 자동 문서화 워크플로우 설계

#### 단계 1: 대상 문서 선정
- 매일/매주 반복적으로 작성하는 문서 (예: 주간 보고서, 실험 일지)
- 데이터 소스가 명확한 문서 (예: 회의 녹취록, 센서 데이터)

#### 단계 2: 데이터 소스 연결
- 어떤 MCP 서버가 필요한가? (Filesystem, Google Drive, Slack 등)
- RAG가 필요한가? (참고해야 할 과거 문서나 전문 지식이 많은가?)

#### 단계 3: 프롬프트 및 템플릿 설계
- 문서의 표준 형식을 마크다운 템플릿으로 작성
- Claude에게 부여할 전문가 역할과 구체적인 작성 규칙 정의

#### 단계 4: 실행 및 피드백
- 실제 데이터를 넣어 실행해보고 결과 확인
- 부족한 부분(맥락, 형식 등)을 프롬프트에 반영하여 지속적 개선

---

### [참고] 주요 학습 리소스

- **LangChain 공식 문서**: RAG 구현의 표준 라이브러리 (python.langchain.com)
- **Anthropic MCP 가이드**: MCP 프로토콜 상세 사양 (modelcontextprotocol.io)
- **Obsidian Community Plugins**: Dataview, Templater 등 자동화 관련 플러그인 활용법
- **Tiago Forte의 PARA 방법론**: 정보 조직화의 기초 (fortelabs.com)

---

### [FAQ] 자주 묻는 질문

**Q: RAG를 쓰면 할루시네이션이 100% 사라지나요?**
A: 아니요, 하지만 획기적으로 줄어듭니다. AI가 검색된 문서 내에서만 답하도록 강제하는 프롬프트를 함께 사용해야 효과적입니다.

**Q: MCP 설정이 너무 복잡해요.**
A: 처음에는 `filesystem` MCP 하나만 제대로 설정해도 충분합니다. 내 컴퓨터의 파일을 Claude가 읽을 수 있게 되는 것만으로도 생산성이 크게 달라집니다.

**Q: Obsidian PARA 구조를 꼭 지켜야 하나요?**
A: PARA는 하나의 제안일 뿐입니다. 하지만 처음 시작할 때는 검증된 방법론을 따르는 것이 시행착오를 줄이는 지름길입니다.

---

> **강사 메모**: 6회차는 기술적인 내용이 많으므로, 이론 설명보다는 실제 Claude Desktop에서 파일이 읽히는 모습을 보여주는 데모에 집중할 것. 수강생들이 본인의 파일을 Claude가 인식했을 때 느끼는 '아하 모먼트(Aha Moment)'가 중요함.

---

### [실습 가이드] Claude Desktop + Filesystem MCP 상세 설정

#### 1. Node.js 설치 확인
MCP 서버는 대부분 Node.js 환경에서 실행됩니다. 터미널에서 다음 명령어를 입력하여 설치 여부를 확인하세요.
```bash
node -v
npm -v
```
설치되어 있지 않다면 [nodejs.org](https://nodejs.org/)에서 LTS 버전을 다운로드하여 설치하세요.

#### 2. 설정 파일 편집 (Windows 기준)
1. `Win + R` 키를 누르고 `%APPDATA%\Claude`를 입력하여 폴더를 엽니다.
2. `claude_desktop_config.json` 파일을 메모장이나 VS Code로 엽니다.
3. 아래 내용을 복사하여 붙여넣되, `path/to/your/vault` 부분을 실제 본인의 Obsidian Vault 경로로 수정하세요. (역슬래시 `\` 대신 슬래시 `/`를 사용하거나 `\\`로 작성해야 함에 주의하세요)

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "C:/Users/User/Documents/MyObsidianVault"
      ]
    }
  }
}
```

#### 3. 연결 확인 및 테스트
1. Claude Desktop 우측 하단의 '플러그' 모양 아이콘을 클릭합니다.
2. `filesystem` 서버가 초록색 불이 들어와 있는지 확인합니다.
3. 대화창에 다음과 같이 입력해 봅니다.
   - "내 금일 업무 리스트를 `Daily` 폴더에서 찾아줘."
   - "특정 프로젝트의 진행 상황을 요약해줘."

---

### [사례 연구] 연구소 내 자동 문서화 도입 비포 & 애프터

#### Case 1: 주간 업무 보고서 작성
- **Before**: 매주 금요일 오후, 한 주간의 이메일, 메신저, 메모를 뒤져가며 2시간 동안 보고서 작성.
- **After**: Claude가 MCP를 통해 일일 업무 일지와 Git 커밋 로그를 읽어와 1분 만에 초안 생성. 연구원은 내용 검토 및 수정만 수행 (총 10분 소요).

#### Case 2: 실험 데이터 정리 및 분석
- **Before**: 실험 장비에서 나온 CSV 데이터를 엑셀로 옮기고, 그래프를 그리고, 분석 의견을 수동으로 작성.
- **After**: Claude가 CSV 파일을 직접 읽고 통계 분석 및 시각화 코드를 실행. 분석 결과와 인사이트를 포함한 마크다운 문서를 자동으로 생성하여 Obsidian에 저장.

#### Case 3: 논문 리뷰 및 요약
- **Before**: 수십 편의 논문을 일일이 읽고 핵심 내용을 노트에 정리. 과거에 읽은 논문 내용을 찾기 어려움.
- **After**: 논문 PDF를 전용 폴더에 넣으면 RAG 시스템이 내용을 인덱싱. 필요할 때마다 "A 기술과 B 기술의 차이점을 내 논문 DB 기반으로 비교해줘"라고 질문하여 즉시 답변 획득.

---

### [체크리스트] 성공적인 자동 문서화 파이프라인을 위한 5계명

1. **데이터의 구조화**: AI가 읽기 좋게 마크다운 형식을 적극 활용하라.
2. **명확한 템플릿**: 원하는 결과물의 형식을 미리 정의하고 예시를 제공하라.
3. **단계적 자동화**: 처음부터 전체를 자동화하려 하지 말고, 가장 귀찮은 부분부터 하나씩 해결하라.
4. **인간의 검토**: AI가 생성한 문서는 반드시 전문가(나)의 눈으로 최종 검토하라.
5. **지속적인 업데이트**: 업무 환경이 변하면 프롬프트와 템플릿도 함께 진화시켜라.

---

### [마무리] 6회차를 마치며

오늘 우리는 AI를 단순한 '채팅 상대'에서 나의 '지식 파트너'로 격상시키는 방법을 배웠습니다. RAG와 MCP는 그 연결 고리입니다. 이제 여러분의 컴퓨터에 잠들어 있는 수많은 데이터들이 AI의 지능과 결합하여 새로운 가치를 만들어낼 준비가 되었습니다.

다음 시간에는 이렇게 구축된 지식 베이스를 바탕으로, 실제로 작동하는 '도구'를 직접 만들어보는 **디스포저블 앱** 세션으로 이어집니다. 오늘 배운 자동 문서화 기법이 그 기초가 될 것입니다.

수고하셨습니다!

---

### [부록] Obsidian 핵심 플러그인과 자동화 시너지

자동 문서화 파이프라인을 더욱 강력하게 만드는 Obsidian 플러그인들을 소개합니다.

#### 1. Templater
- **기능**: 자바스크립트를 활용한 강력한 템플릿 엔진
- **활용**: 문서 생성 시 날짜, 파일명, 특정 폴더의 정보 등을 자동으로 삽입
- **시너지**: Claude가 생성한 텍스트를 Templater가 정의한 구조 안에 배치하여 일관성 유지

#### 2. Dataview
- **기능**: Obsidian 노드들을 데이터베이스처럼 쿼리(Query)할 수 있는 도구
- **활용**: 특정 프로젝트의 모든 태스크 목록 추출, 연구 분야별 논문 리스트 자동 생성
- **시너지**: Claude에게 "Dataview 쿼리 결과를 바탕으로 이번 달 연구 성과를 요약해줘"라고 요청 가능

#### 3. Tasks
- **기능**: 체크리스트 관리 및 필터링
- **활용**: 마감일, 우선순위가 포함된 할 일 관리
- **시너지**: Claude가 문서를 분석하여 액션 아이템(Action Items)을 Tasks 형식으로 자동 생성

#### 4. Obsidian Git
- **기능**: Vault 전체를 Git으로 자동 백업 및 버전 관리
- **활용**: 변경 이력 추적, 여러 기기 간 동기화
- **시너지**: Claude Code와 같은 에이전트가 Git 히스토리를 읽어 작업 맥락을 파악하는 데 도움

---

### [실습] 나만의 '연구 비서' 프롬프트 만들기

아래 프롬프트를 복사하여 Claude에게 입력해 보세요. (MCP가 설정되어 있어야 합니다)

```markdown
[R: 역할]
당신은 나의 개인 연구 비서입니다. 내 Obsidian Vault의 구조와 내용을 완벽하게 파악하고 있습니다.

[C: 맥락]
나는 현재 [연구 주제]에 대해 연구 중입니다. 내 Vault의 `Resources/Papers` 폴더에는 관련 논문 요약본들이 있고, `Projects/Current` 폴더에는 실험 일지들이 있습니다.

[I: 지시]
1. `Resources/Papers`에서 최근 3개월 내에 추가된 논문들을 찾아 핵심 키워드를 추출하세요.
2. `Projects/Current`의 실험 일지에서 발생한 주요 이슈들을 정리하세요.
3. 위 두 정보를 결합하여, 다음 실험에서 고려해야 할 사항 5가지를 제안하세요.

[F: 형식]
- 마크다운 형식
- 1, 2번은 요약 리스트로 작성
- 3번은 구체적인 근거와 함께 상세 설명
```

---

### [참고] RAG 성능 향상을 위한 팁

- **Metadata 활용**: 문서에 날짜, 저자, 카테고리 등의 메타데이터를 추가하면 검색 정확도가 높아집니다.
- **Query Expansion**: 사용자의 질문을 AI가 더 검색하기 좋은 형태로 다시 작성하게 한 뒤 검색을 수행하세요.
- **Context Window 관리**: 검색된 결과가 너무 많으면 AI가 핵심을 놓칠 수 있습니다. 가장 관련성 높은 상위 3~5개의 청크만 제공하는 것이 효율적입니다.

---

### [마무리 퀴즈] 오늘 배운 내용 확인하기

1. LLM의 지식을 외부 데이터로 확장하는 기술의 약자는? (정답: RAG)
2. Anthropic이 제안한 LLM-도구 연결 표준 프로토콜은? (정답: MCP)
3. 효과적인 프롬프트 구성을 위한 4대 요소(RCIF)는 무엇인가요? (정답: Role, Context, Instruction, Format)
4. Obsidian에서 정보를 실행 가능성에 따라 분류하는 방법론은? (정답: PARA)

---

> **다음 시간 준비물**: 
> - 오늘 설정한 MCP 환경이 정상 작동하는지 다시 한번 확인해 오세요.
> - 본인이 평소에 '이런 도구가 있으면 좋겠다'고 생각했던 아이디어 1가지를 가져오세요.

---
