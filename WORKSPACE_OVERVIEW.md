# Workspace Overview

> 경로: `C:\Users\urp\Desktop\workspace`  
> 기준일: 2026-04-20

---

## 목차

1. [프로젝트 요약 표](#프로젝트-요약-표)
2. [ai-practice](#1-ai-practice)
3. [ai-rag-search](#2-ai-rag-search)
4. [demo](#3-demo)
5. [game_project](#4-game_project)
6. [rag-gemini-search](#5-rag-gemini-search)
7. [rag-gemini-search-uv](#6-rag-gemini-search-uv)
8. [test](#7-test)
9. [공통 패턴 및 기술 스택](#공통-패턴-및-기술-스택)

---

## 프로젝트 요약 표

| 프로젝트 | 유형 | 언어 | 프레임워크 | 상태 |
|---------|------|------|-----------|------|
| ai-practice | LLM 튜토리얼 | Python | Gemini API, LangChain | 학습/개발 중 |
| ai-rag-search | RAG 앱 (프로토타입) | Python | Gemini, FAISS | 동작 가능 |
| demo | 웹 앱 스캐폴드 | Java | Spring Boot 4.0 | 템플릿 |
| game_project | 게임 개발 | Python / HTML5 | Pygame, Canvas | 활발히 개발 중 |
| rag-gemini-search | RAG 앱 (고도화) | Python | FastAPI, LangChain, FAISS | 동작 가능 |
| rag-gemini-search-uv | RAG 앱 (프로덕션) | Python | FastAPI, LangChain, Docker, Qdrant | 프로덕션 준비 |
| test | 플레이스홀더 | Java | IntelliJ IDEA | 비어있음 |

---

## 1. ai-practice

**유형:** Python LLM/RAG 단계별 학습 프로젝트  
**목적:** Gemini API 기반 LLM → RAG → Agent 학습 커리큘럼

### 기술 스택
- Python 3.x
- Google Gemini API
- LangChain, LangGraph
- FAISS (벡터 DB)

### 디렉토리 구조
```
ai-practice/
├── .env                      # API 키
├── venv/                     # Python 가상환경
├── check_env.py              # 환경변수 확인
├── env_load.py               # .env 로드
├── step1_llm.py              # Gemini API 기본 사용
├── step2_prompt.py           # 프롬프트 엔지니어링
├── step3_tool_calling.py     # Function Calling / Tool Use
├── step4_rag_basic.py        # 기본 RAG 구현
├── step5_vectordb.py         # 벡터 DB 활용
├── step6_agent.py            # Agent 패턴
├── step7_lanchain_rag.py     # LangChain RAG 통합
└── step8_langgraph_agent.py  # LangGraph 에이전트 오케스트레이션
```

### 학습 커리큘럼 (Step 1 → 8)
| 단계 | 파일 | 내용 |
|------|------|------|
| 1 | step1_llm.py | LLM 기본 호출 |
| 2 | step2_prompt.py | 프롬프트 설계 |
| 3 | step3_tool_calling.py | 도구 호출 |
| 4 | step4_rag_basic.py | RAG 기초 |
| 5 | step5_vectordb.py | 벡터 데이터베이스 |
| 6 | step6_agent.py | 에이전트 |
| 7 | step7_lanchain_rag.py | LangChain RAG |
| 8 | step8_langgraph_agent.py | LangGraph 에이전트 |

---

## 2. ai-rag-search

**유형:** Python RAG 기반 문서 검색/Q&A 앱 (프로토타입)  
**목적:** 회사 문서를 벡터화하여 자연어로 검색 및 답변 생성

### 기술 스택
- Python 3.x
- Google Gemini API (`google-genai`)
- FAISS (벡터 인덱스)
- Sentence Transformers (임베딩)
- NumPy

### 디렉토리 구조
```
ai-rag-search/
├── documents/          # 입력 문서 폴더
├── requirements.txt    # 의존성 (4개 패키지)
├── venv/               # Python 가상환경
├── documents.pkl       # 직렬화된 문서 저장소
├── vector.index        # FAISS 벡터 인덱스
├── ingest.py          # 문서 → 벡터 DB 인제스트
├── rag_chat.py        # 대화형 RAG 채팅 인터페이스
├── search.py          # 벡터 검색 모듈
└── readme.txt         # 프로젝트 설명
```

### 의존성 (`requirements.txt`)
```
google-genai
sentence-transformers
faiss-cpu
numpy
```

### 실행 방법
```bash
# 1. 문서 인제스트
python ingest.py

# 2. 검색
python search.py

# 3. 채팅
python rag_chat.py
```

---

## 3. demo

**유형:** Java Spring Boot 웹 앱 스캐폴드  
**목적:** Spring Boot 4.0 기반 프로젝트 템플릿

### 기술 스택
- Java 17
- Spring Boot 4.0.5
- Maven
- Embedded Tomcat

### 디렉토리 구조
```
demo/
├── .git/
├── .mvn/                           # Maven Wrapper
├── src/
│   ├── main/
│   │   ├── java/com/example/demo/
│   │   │   ├── DemoApplication.java       # 메인 진입점
│   │   │   └── ServletInitializer.java    # WAR 배포용 초기화
│   │   └── resources/
│   │       └── application.yaml           # 애플리케이션 설정
│   └── test/
│       └── java/.../DemoApplicationTests.java
├── pom.xml                         # Maven 설정
└── mvnw / mvnw.cmd                 # Maven Wrapper 스크립트
```

### `pom.xml` 주요 설정
```xml
<parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>4.0.5</version>
</parent>

<dependencies>
    spring-boot-starter-webmvc
    spring-boot-starter-tomcat
    spring-boot-starter-test
</dependencies>
```

### 실행 방법
```bash
./mvnw spring-boot:run
```

---

## 4. game_project

**유형:** Python / HTML5 멀티 게임 프로젝트  
**목적:** Pygame 런처 + 테트리스, 마리오 게임 구현

### 기술 스택
- Python 3.12+
- Pygame (데스크탑 게임)
- HTML5 Canvas / JavaScript (웹 게임)
- uv / pip (패키지 관리)

### 디렉토리 구조
```
game_project/
├── .git/
├── .venv/
├── pyproject.toml      # 프로젝트 메타데이터
├── GAME_PLAN.md        # 개발 전략 문서
├── main.py             # 게임 런처 / 메뉴
├── mario.py            # 마리오 게임 (Python)
├── tetris.py           # 테트리스 게임 (Python)
└── tetris.html         # 테트리스 웹 버전 (HTML5 Canvas)
```

### `pyproject.toml`
```toml
[project]
name = "game_project"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = []
```

### 게임 스펙

#### 테트리스
- 클래식 블록 쌓기 퍼즐
- 점수 및 레벨 시스템
- 충돌 감지
- Python(Pygame) + HTML5 Canvas 두 버전 제공

#### 마리오
- 횡스크롤 액션 플랫포머
- 플레이어 이동 및 점프
- 적 (굼바) 조우
- 무한 스크롤 배경
- 코인 수집 시스템
- 목숨 시스템 (3개)

### 실행 방법
```bash
# Pygame 런처 실행
python main.py

# 또는 개별 게임
python tetris.py
python mario.py

# 웹 버전 (브라우저에서 열기)
open tetris.html
```

---

## 5. rag-gemini-search

**유형:** Python RAG 앱 (고도화 버전)  
**목적:** 기업 문서 AI 챗봇 — 하이브리드 검색 + 에이전트 라우팅

### 기술 스택
- Python 3.12
- FastAPI + Uvicorn (API 서버)
- Streamlit (채팅 UI)
- Google Gemini 2.0 Flash Lite (LLM)
- LangChain / LangGraph (에이전트 오케스트레이션)
- FAISS (벡터 검색)
- BM25 (키워드 검색)
- Sentence Transformers — `all-MiniLM-L6-v2` (임베딩)
- CrossEncoder (리랭킹)

### 디렉토리 구조
```
rag-gemini-search/
├── .python-version         # Python 3.12
├── pyproject.toml
├── requirements.txt        # 140+ 패키지 (frozen)
├── uv.lock
├── agents/
│   ├── agent.py           # 질문 라우팅 에이전트
│   └── tools.py           # LangChain 도구 정의
├── api/
│   └── main.py            # FastAPI 진입점
├── data/
│   └── company.txt        # 소스 문서
├── memory/
│   └── conversation_memory.py  # 세션 기반 대화 히스토리
├── rag/
│   ├── config.py          # 전역 설정
│   ├── embedding.py       # SentenceTransformer 임베딩
│   ├── hybrid_retriever.py   # FAISS + BM25 하이브리드 검색
│   ├── keyword_search.py  # BM25 키워드 검색
│   ├── prompt.py          # 프롬프트 템플릿
│   ├── query_rewriter.py  # 질문 재작성
│   ├── rag_engine.py      # RAG 오케스트레이션
│   ├── reranker.py        # CrossEncoder 리랭킹
│   ├── retriever.py       # 검색기 인터페이스
│   └── vector_store.py    # FAISS 벡터 DB
├── router/
│   └── router.py          # FastAPI 라우트
├── scripts/
│   └── ingest.py          # 문서 → 벡터 DB 인제스트
├── ui/
│   └── chat_ui.py         # Streamlit 채팅 UI
├── vector_store/          # FAISS 인덱스 저장
├── app.py                 # CLI 인터페이스
└── run_server.py          # FastAPI 서버 실행
```

### 아키텍처
```
사용자 질문
    └─→ Agent (질문 분류)
            ├─→ [회사 문서 관련]
            │       └─→ RAG Engine
            │               ├─→ Query Rewriter (대화 히스토리 기반)
            │               ├─→ HybridRetriever (FAISS + BM25)
            │               ├─→ CrossEncoder Reranker
            │               └─→ Gemini LLM → 응답 생성
            └─→ [일반 질문]
                    └─→ Gemini LLM 직접 호출
```

### 주요 설정
| 항목 | 값 |
|------|----|
| LLM 모델 | Gemini 2.0 Flash Lite |
| 임베딩 모델 | all-MiniLM-L6-v2 |
| Top-K 문서 수 | 3 |
| 최대 대화 턴 수 | 10 |
| 필수 환경변수 | `GEMINI_API_KEY` |

### 실행 방법
```bash
# API 서버
python run_server.py

# Streamlit UI
streamlit run ui/chat_ui.py

# CLI
python app.py

# 문서 인제스트
python scripts/ingest.py
```

---

## 6. rag-gemini-search-uv

**유형:** Python RAG 앱 (프로덕션 준비 / Docker 컨테이너화)  
**목적:** 기업 문서 AI 챗봇 — Docker 기반 배포, Qdrant 벡터 DB 통합

### 기술 스택
- Python 3.12
- FastAPI + Uvicorn
- Streamlit
- Google Gemini API
- LangChain / LangGraph
- FAISS + **Qdrant** (벡터 DB)
- BM25, Sentence Transformers, CrossEncoder
- **Docker / Docker Compose**
- **uv** (패키지 관리자)

### 디렉토리 구조
```
rag-gemini-search-uv/
├── .env                    # 실제 환경변수
├── .env.example           # 환경변수 템플릿
├── .python-version        # Python 3.12
├── .dockerignore
├── .git/
├── pyproject.toml         # 명시적 의존성 관리
├── requirements.txt       # Frozen 의존성 (140+)
├── docker-compose.yml     # 멀티 컨테이너 오케스트레이션
├── Dockerfile.api         # FastAPI 컨테이너
├── Dockerfile.ui          # Streamlit 컨테이너
├── agents/
├── api/
├── data/
├── memory/
├── rag/
├── router/
├── scripts/
├── ui/
├── qdrant_storage/        # Qdrant 벡터 DB 영속성 저장소
├── vector_store/          # FAISS 인덱스 (레거시)
├── app.py
├── main.py
└── run_server.py
```

### `pyproject.toml` 의존성
```toml
[project]
name = "rag-gemini-search-uv"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.135.2",
    "google-generativeai>=0.8.6",
    "langchain>=1.2.13",
    "langchain-core>=1.2.23",
    "langchain-google-genai>=4.2.1",
    "numpy>=2.4.4",
    "pydantic>=2.12.5",
    "python-dotenv>=1.2.2",
    "rank-bm25>=0.2.2",
    "sentence-transformers>=5.3.0",
    "streamlit>=1.55.0",
    "uvicorn>=0.42.0",
    "qdrant-client>=1.9.0",
    "faiss-cpu>=1.13.2",
    "requests>=2.33.1",
]
```

### Docker 서비스 (`docker-compose.yml`)
| 서비스 | 이미지 | 포트 | 역할 |
|--------|--------|------|------|
| qdrant | qdrant/qdrant | 6333, 6334 | 벡터 데이터베이스 |
| api | Dockerfile.api | 8000 | FastAPI 백엔드 |
| ui | Dockerfile.ui | 8501 | Streamlit 프론트엔드 |

### 환경변수 (`.env.example`)
```env
GEMINI_API_KEY=your-gemini-api-key-here
```

### 실행 방법
```bash
# 로컬 개발 (uv)
uv sync
uv run python run_server.py
uv run streamlit run ui/chat_ui.py

# Docker (프로덕션)
docker compose up --build

# 문서 인제스트
uv run python scripts/ingest.py
```

### rag-gemini-search 대비 주요 차이점
| 항목 | rag-gemini-search | rag-gemini-search-uv |
|------|-------------------|----------------------|
| 패키지 관리 | pip | uv |
| 의존성 명세 | requirements.txt만 | pyproject.toml + lock |
| 벡터 DB | FAISS만 | FAISS + Qdrant |
| 컨테이너화 | 없음 | Docker Compose |
| 배포 준비도 | 개발/프로토타입 | 프로덕션 |

---

## 7. test

**유형:** 플레이스홀더 / 빈 프로젝트  
**목적:** IntelliJ IDEA 프로젝트 초기화 흔적, 실질적 코드 없음

### 디렉토리 구조
```
test/
├── .git/        # 초기화된 Git 저장소 (커밋 없음)
├── .idea/       # IntelliJ IDEA 설정
├── .venv/       # 미사용 Python 가상환경
└── test.iml     # IntelliJ IDEA 프로젝트 파일
```

---

## 공통 패턴 및 기술 스택

### 주요 AI/ML 기술
| 기술 | 사용 프로젝트 | 역할 |
|------|-------------|------|
| Google Gemini API | 전체 (Java 제외) | LLM 추론 |
| LangChain | rag-gemini-search, rag-gemini-search-uv, ai-practice | RAG/에이전트 오케스트레이션 |
| FAISS | ai-rag-search, rag-gemini-search, rag-gemini-search-uv | 벡터 검색 |
| Sentence Transformers | ai-rag-search, rag-gemini-search, rag-gemini-search-uv | 텍스트 임베딩 |
| BM25 | rag-gemini-search, rag-gemini-search-uv | 키워드 검색 |
| CrossEncoder | rag-gemini-search, rag-gemini-search-uv | 문서 리랭킹 |
| Qdrant | rag-gemini-search-uv | 프로덕션 벡터 DB |

### 백엔드 / 인프라
| 기술 | 사용 프로젝트 |
|------|-------------|
| FastAPI + Uvicorn | rag-gemini-search, rag-gemini-search-uv |
| Streamlit | rag-gemini-search, rag-gemini-search-uv |
| Spring Boot 4.0 | demo |
| Docker Compose | rag-gemini-search-uv |
| uv | rag-gemini-search, rag-gemini-search-uv |

### 개발 단계 분류
```
학습        →  ai-practice
프로토타입  →  ai-rag-search, game_project
고도화      →  rag-gemini-search
프로덕션    →  rag-gemini-search-uv
템플릿      →  demo
미사용      →  test
```

---

*생성일: 2026-04-20*
