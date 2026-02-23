# ContractPilot - 프로젝트 문서

> AI 기반 계약서 위험 분석 & 노동상담 서비스
> 조코딩 x OpenAI x 프라이머 해커톤

## 🌐 배포 URL

| 서비스 | URL |
|--------|-----|
| **Frontend** | https://contractpilot.pages.dev |
| **Backend API** | https://contractpilot-production.up.railway.app |
| **API Docs** | https://contractpilot-production.up.railway.app/docs |

## 프로젝트 개요

**ContractPilot**은 한국 판례 기반 AI를 활용하여 계약서의 위험 조항을 자동으로 분석하고 수정안을 제안하는 B2B SaaS 서비스입니다.

**노동톡**은 AI 기반 노동상담 서비스로, 근로자들의 노동법 관련 고민을 상담하고 필요시 전문 노무사를 연결해주는 수익 모델입니다.

### 핵심 가치
- 변호사 비용 90% 절감 (건당 200만원 → 월 9.9만원 구독)
- 검토 시간 단축 (2~3일 → 10분)
- 한국 판례 기반 법적 근거 제시
- 노동상담 → 전문 노무사 연결 수수료 수익 모델

### 🆕 한국 시장 진입 대응 (v0.2.0)
- **HWP/HWPX 파일 지원**: 한글 문서 형식 완벽 지원
- **개인정보 익명화**: 이름, 전화번호, 주민번호 등 자동 마스킹
- **멀티 LLM 지원**: OpenAI, Upstage Solar, Anthropic Claude, 로컬 LLM
- **한국 법률 API 연동**: 국가법령정보센터, 대법원 판례 검색
- **계약서 유형별 체크리스트**: 6종 계약서별 필수 조항 검증
- **협업 기능**: 공유, 댓글, 버전 관리
- **법적 면책조항**: 변호사법 준수를 위한 명확한 고지

---

## 기술 스택

### Backend
| 기술 | 버전 | 용도 |
|------|------|------|
| Python | 3.13 | 런타임 |
| FastAPI | 0.122+ | 웹 프레임워크 |
| OpenAI | 2.21+ | GPT-4o API |
| Anthropic | 0.18+ | Claude API |
| PyPDF2 | 3.0.1 | PDF 텍스트 추출 |
| olefile | 0.47+ | HWP 파일 파싱 |
| python-docx | 0.8.11+ | Word 문서 생성 |
| reportlab | 4.0+ | PDF 리포트 생성 |
| Pydantic | 2.12+ | 데이터 검증 |

### Frontend
| 기술 | 버전 | 용도 |
|------|------|------|
| Next.js | 14.1 | React 프레임워크 |
| Tailwind CSS | 3.4 | 스타일링 |
| React Dropzone | 14.2 | 파일 업로드 |
| Lucide React | 0.323 | 아이콘 |

---

## 프로젝트 구조

```
ContractPilot/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py          # API 엔드포인트
│   │   ├── core/
│   │   │   ├── config.py          # 환경 설정
│   │   │   ├── openai_client.py   # OpenAI 연동
│   │   │   └── llm_client.py      # 🆕 멀티 LLM 클라이언트
│   │   ├── models/
│   │   │   └── schemas.py         # Pydantic 스키마
│   │   ├── services/
│   │   │   ├── pdf_service.py     # PDF 처리
│   │   │   ├── hwp_service.py     # 🆕 HWP/HWPX 처리
│   │   │   ├── document_service.py # 🆕 통합 문서 처리
│   │   │   ├── anonymizer_service.py # 🆕 개인정보 익명화
│   │   │   ├── rag_service.py     # 판례 검색 (샘플)
│   │   │   ├── korean_law_service.py # 🆕 한국 법률 API
│   │   │   ├── collaboration_service.py # 🆕 협업 기능
│   │   │   ├── analysis_service.py # 분석 로직
│   │   │   ├── chat_service.py    # 계약 챗봇 서비스
│   │   │   ├── labor_chat_service.py  # 노동상담 챗봇 서비스
│   │   │   ├── docx_generator.py  # Word 문서 생성
│   │   │   └── pdf_report_generator.py  # PDF 리포트 생성
│   │   └── main.py                # FastAPI 앱
│   ├── start.py                   # Railway 배포용 시작 스크립트
│   ├── requirements.txt
│   ├── railway.json               # Railway 설정
│   ├── Procfile                   # Railway Procfile
│   ├── Dockerfile
│   └── .env                       # API 키 (gitignore)
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx           # 메인 페이지
│   │   │   ├── chat/page.tsx      # 계약 챗봇 페이지
│   │   │   ├── labor/page.tsx     # 노동상담 페이지
│   │   │   ├── layout.tsx
│   │   │   └── globals.css
│   │   ├── components/
│   │   │   ├── FileUpload.tsx     # 드래그앤드롭 업로드
│   │   │   ├── LoadingState.tsx   # 로딩 애니메이션
│   │   │   ├── AnalysisResult.tsx # 결과 표시
│   │   │   ├── ChatInterface.tsx  # 계약 챗봇 인터페이스
│   │   │   ├── LaborChatInterface.tsx  # 노동상담 챗봇
│   │   │   ├── ExpertConnectModal.tsx  # 노무사 연결 모달
│   │   │   ├── DownloadButton.tsx # 계약서 다운로드 버튼
│   │   │   ├── ReportDownloadButton.tsx # PDF 리포트 다운로드 버튼
│   │   │   ├── ComparisonView.tsx # 원본/수정본 비교 뷰
│   │   │   ├── CollaborationPanel.tsx # 🆕 협업 패널
│   │   │   └── LegalReference.tsx # 🆕 법률 참조 컴포넌트
│   │   └── lib/
│   │       └── api.ts             # API 클라이언트
│   ├── package.json
│   └── tailwind.config.ts
├── docs/                          # 🆕 문서
│   ├── 보완 자료.md
│   ├── 보완작업_구현목록.md
│   └── 한국시장_진입_타당성_반박자료.md
├── data/                          # 샘플 데이터
├── docker-compose.yml
├── README.md
├── CLAUDE.md                      # 이 파일
└── .gitignore
```

---

## 실행 방법

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
# http://127.0.0.1:8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
# http://localhost:3000
```

---

## API 엔드포인트

### 계약서 분석
| Method | Path | 설명 |
|--------|------|------|
| GET | `/` | 서버 정보 |
| GET | `/api/v1/health` | 헬스체크 |
| POST | `/api/v1/analyze` | 계약서 분석 (PDF, HWP, HWPX 지원) |
| POST | `/api/v1/analyze/text` | 텍스트 직접 분석 (테스트용) |
| POST | `/api/v1/chat` | 판례 기반 법률 상담 챗봇 |
| POST | `/api/v1/generate-safe-contract` | 수정된 계약서 Word 다운로드 |
| POST | `/api/v1/generate-report` | 분석 리포트 PDF 다운로드 |

### 🆕 노동상담 (노동톡)
| Method | Path | 설명 |
|--------|------|------|
| POST | `/api/v1/labor-chat` | AI 노동상담 챗봇 |
| POST | `/api/v1/expert-connect` | 전문 노무사 상담 연결 신청 |

### 🆕 시스템 (v0.2.0)
| Method | Path | 설명 |
|--------|------|------|
| GET | `/api/v1/system/llm-info` | 현재 LLM 프로바이더 정보 |
| POST | `/api/v1/system/test-anonymization` | 익명화 테스트 |

### 🆕 한국 법률 API (v0.2.0)
| Method | Path | 설명 |
|--------|------|------|
| GET | `/api/v1/law/search` | 법령 검색 |
| GET | `/api/v1/law/article/{law_id}` | 특정 조문 조회 |
| GET | `/api/v1/law/cases` | 판례 검색 |
| GET | `/api/v1/law/checklist/{contract_type}` | 계약서 체크리스트 |

### 🆕 협업 기능 (v0.2.0)
| Method | Path | 설명 |
|--------|------|------|
| POST | `/api/v1/collaboration/share` | 분석 결과 공유 링크 생성 |
| GET | `/api/v1/collaboration/share/{share_id}` | 공유된 분석 조회 |
| POST | `/api/v1/collaboration/comment` | 댓글 추가 |
| GET | `/api/v1/collaboration/comments/{analysis_id}` | 댓글 목록 조회 |
| DELETE | `/api/v1/collaboration/comment/{comment_id}` | 댓글 삭제 |
| POST | `/api/v1/collaboration/version` | 버전 저장 |
| GET | `/api/v1/collaboration/versions/{analysis_id}` | 버전 목록 조회 |
| PUT | `/api/v1/collaboration/permissions/{share_id}` | 권한 수정 |

### 분석 응답 스키마
```json
{
  "contract_type": "투자계약서",
  "total_clauses": 14,
  "high_risk_clauses": 3,
  "average_risk_score": 5.2,
  "overall_risk_level": "medium",
  "clauses": [
    {
      "number": 1,
      "title": "제1조 (목적)",
      "content": "...",
      "analysis": {
        "risk_score": 3,
        "risk_level": "low",
        "summary": "일반적인 목적 조항",
        "issues": [],
        "suggestion": null
      },
      "similar_cases": [],
      "alternative": null
    }
  ],
  "summary": "분석 요약..."
}
```

---

## 개발 진행 상황

### 완료됨 ✅
- [x] 프로젝트 구조 설정
- [x] FastAPI 백엔드 구현
- [x] OpenAI GPT-4o 연동
- [x] PDF 텍스트 추출 (PyPDF2)
- [x] 조항 분리 로직
- [x] 위험 분석 Agent
- [x] 수정안 생성 Agent (조항별)
- [x] Next.js 프론트엔드
- [x] 드래그앤드롭 파일 업로드
- [x] 분석 결과 UI
- [x] 로딩 애니메이션
- [x] GitHub 연동
- [x] End-to-End 테스트 완료
- [x] 판례 기반 법률 상담 챗봇 (MVP)
- [x] 수정된 계약서 Word 다운로드 기능
- [x] 분석 리포트 PDF 다운로드 기능
- [x] 원본 vs 수정본 비교 뷰 (Side-by-Side)
- [x] 노동상담 AI 챗봇 (노동톡)
- [x] 전문 노무사 연결 신청 기능
- [x] Railway 백엔드 배포 완료
- [x] Cloudflare Pages 프론트엔드 배포 완료

### 🆕 v0.2.0 한국 시장 진입 대응 ✅
- [x] HWP/HWPX 파일 지원 (olefile 기반)
- [x] 법적 면책조항 UI 표시
- [x] 개인정보 익명화 서비스 (이름, 전화번호, 주민번호, 계좌번호 등)
- [x] 멀티 LLM 프로바이더 (OpenAI, Upstage Solar, Anthropic Claude, 로컬 Ollama)
- [x] 한국 법률 API 연동 (국가법령정보센터, 대법원 판례)
- [x] 계약서 유형별 체크리스트 (6종: 근로계약서, 임대차계약서, 투자계약서, 용역계약서, 매매계약서, NDA)
- [x] 협업 기능 (공유 링크, 댓글, 버전 관리, 권한 설정)
- [x] 프론트엔드 개인정보 보호 배지 추가

### 현재 상태 ✅ v0.2.0 배포 준비
- **Frontend**: https://contractpilot.pages.dev (Cloudflare Pages)
- **Backend**: https://contractpilot-production.up.railway.app (Railway)
- 판례 데이터: **샘플 5건** (하드코딩)
- 판례 검색: **키워드 매칭** (벡터 검색 아님)
- 지원 파일: **PDF, HWP, HWPX**
- LLM: **멀티 프로바이더 지원**

---

## TODO: 해야 할 작업

### 🔴 Phase 1: 핵심 인프라 (해커톤 전)

#### 1.1 Pinecone 벡터 DB 연동
```
예상 시간: 1~2시간
우선순위: 높음

작업 내용:
1. Pinecone 계정 생성 (https://www.pinecone.io/)
2. 인덱스 생성 (dimension: 3072, metric: cosine)
3. backend/.env에 API 키 추가
4. rag_service.py 수정 - 실제 벡터 검색 구현

필요한 패키지:
- pinecone-client>=3.1.0
```

#### 1.2 실제 판례 데이터 수집
```
예상 시간: 2~3시간
우선순위: 높음

데이터 소스:
- 국가법령정보센터: https://www.law.go.kr/
- 대법원 종합법률정보: https://glaw.scourt.go.kr/

수집 목표: 1,000건 이상
수집 필드:
- case_number: 사건번호
- court: 법원명
- date: 판결일
- summary: 판결 요지
- relevant_text: 핵심 판시사항
- keywords: 관련 키워드
```

#### 1.3 판례 임베딩 & 인덱싱
```
예상 시간: 1시간
우선순위: 높음

작업 내용:
1. 수집한 판례 텍스트 전처리
2. OpenAI text-embedding-3-large로 임베딩 생성
3. Pinecone에 upsert
4. 메타데이터 포함 (사건번호, 법원, 날짜 등)
```

### 🟡 Phase 2: 신규 기능 개발

#### 2.1 수정된 계약서 전체 생성 기능 ✅ 완료
```
완료일: 2026-02-15

구현 내용:
- POST /api/v1/generate-safe-contract 엔드포인트
- python-docx로 Word 파일 생성
- 위험 조항(risk_score >= 7)의 alternative 자동 적용
- 프론트엔드 다운로드 버튼 추가

구현 파일:
- backend/app/services/docx_generator.py
- backend/app/api/routes.py
- backend/app/models/schemas.py (GenerateContractRequest)
- frontend/src/components/DownloadButton.tsx
- frontend/src/components/AnalysisResult.tsx
- frontend/src/lib/api.ts (downloadSafeContract)
```

#### 2.2 판례 기반 법률 상담 챗봇 ✅ 완료 (MVP)
```
완료일: 2026-02-15

구현 내용:
- POST /api/v1/chat 엔드포인트
- GPT-4o 기반 법률 상담
- 샘플 판례 5건 키워드 매칭 (RAG MVP)
- 대화 히스토리 관리
- 계약서 분석 컨텍스트 연동

구현 파일:
- backend/app/services/chat_service.py
- backend/app/api/routes.py
- backend/app/models/schemas.py (ChatRequest, ChatResponse)
- frontend/src/app/chat/page.tsx
- frontend/src/components/ChatInterface.tsx
- frontend/src/lib/api.ts (sendChatMessage)

TODO (향후 개선):
- Pinecone 벡터 DB 연동으로 실제 RAG 구현
- 실제 판례 데이터 수집 및 임베딩
```

#### 2.3 분석 리포트 PDF 생성 기능 ✅ 완료
```
완료일: 2026-02-17

구현 내용:
- POST /api/v1/generate-report 엔드포인트
- reportlab으로 PDF 리포트 생성
- 한글 폰트 지원 (맑은 고딕)
- 표지, 요약, 조항별 분석, 면책 조항 포함
- 프론트엔드 다운로드 버튼 추가

구현 파일:
- backend/app/services/pdf_report_generator.py
- backend/app/api/routes.py
- backend/app/models/schemas.py (GenerateReportRequest)
- frontend/src/components/ReportDownloadButton.tsx
- frontend/src/components/AnalysisResult.tsx
- frontend/src/lib/api.ts (downloadAnalysisReport)

PDF 리포트 구성:
- 표지: 계약서 유형, 분석 일시, ContractPilot 브랜딩
- 요약: 전체 위험도, 고위험 조항 수, 평균 위험도
- 조항별 분석: 원문, 위험도, 문제점, 수정 제안
- 관련 판례 목록
- 면책 조항
```

#### 2.4 노동상담 AI 챗봇 (노동톡) ✅ 완료
```
완료일: 2026-02-20

구현 내용:
- POST /api/v1/labor-chat 엔드포인트
- GPT-4o 기반 노동법 상담 AI
- 임금체불, 부당해고, 직장 내 괴롭힘 등 상담
- 샘플 노동 판례 키워드 매칭
- 전문가 연결 필요 여부 판단

구현 파일:
- backend/app/services/labor_chat_service.py
- backend/app/api/routes.py
- backend/app/models/schemas.py (LaborChatRequest, LaborChatResponse)
- frontend/src/app/labor/page.tsx
- frontend/src/components/LaborChatInterface.tsx
- frontend/src/lib/api.ts (sendLaborChatMessage)
```

#### 2.5 전문 노무사 연결 기능 ✅ 완료
```
완료일: 2026-02-20

구현 내용:
- POST /api/v1/expert-connect 엔드포인트
- 상담 신청 폼 (이름, 연락처, 희망 시간)
- 개인정보 동의 처리
- 상담 요약 자동 전달

수익 모델:
- 노무사 연결 성공 시 수수료 (건당 또는 월정액)
- 향후 변호사 연결로 확장 가능

구현 파일:
- backend/app/api/routes.py
- backend/app/models/schemas.py (ExpertConnectRequest)
- frontend/src/components/ExpertConnectModal.tsx
- frontend/src/lib/api.ts (requestExpertConnect)
```

### 🟢 Phase 3: 배포 & 마무리

#### 3.1 배포 ✅ 완료
```
Frontend (Cloudflare Pages):
✅ URL: https://contractpilot.pages.dev
1. GitHub 연동 완료
2. 빌드 설정:
   - Root directory: frontend
   - Build command: npm run build
   - Build output directory: out
3. next.config.js에 output: 'export' 추가 (정적 빌드)
4. 환경변수: NEXT_PUBLIC_API_URL=https://contractpilot-production.up.railway.app

Backend (Railway):
✅ URL: https://contractpilot-production.up.railway.app
1. railway.app 연동 완료
2. 환경변수: OPENAI_API_KEY
3. start.py로 PORT 환경변수 처리
4. railway.json 설정 파일 사용
```

#### 3.2 발표 자료
```
예상 시간: 2시간

10슬라이드 피칭덱:
1. Cover
2. Problem
3. Market Size (TAM/SAM/SOM)
4. Solution
5. Demo
6. Technology
7. Business Model
8. Traction
9. Team
10. Ask
```

#### 3.3 데모 영상
```
예상 시간: 1시간

내용:
- PDF 업로드 → 분석 → 결과 확인 흐름
- 수정된 계약서 다운로드 (구현 시)
- 챗봇 상담 (구현 시)
```

---

## 환경 변수

### backend/.env
```env
# OpenAI (기본)
OPENAI_API_KEY=sk-...

# 🆕 LLM 프로바이더 설정 (openai, upstage, anthropic, local)
LLM_PROVIDER=openai

# Upstage Solar API (선택)
UPSTAGE_API_KEY=up-...
UPSTAGE_MODEL=solar-pro

# Anthropic Claude API (선택)
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# 로컬 LLM (선택)
LOCAL_LLM_URL=http://localhost:11434/v1
LOCAL_LLM_MODEL=llama3.2

# 🆕 개인정보 익명화 설정
ANONYMIZE_ENABLED=true
ANONYMIZE_BEFORE_LLM=true

# 한국 법률 API (선택)
LAW_API_KEY=...

# Pinecone (TODO)
PINECONE_API_KEY=...
PINECONE_INDEX_NAME=contract-pilot
```

### frontend/.env.local
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 신규 기능 상세 설계

### Feature: 수정된 계약서 생성

```
[사용자 흐름]
1. PDF 업로드 → 분석 완료
2. "수정된 계약서 다운로드" 버튼 클릭
3. AI가 모든 위험 조항을 수정한 버전 생성
4. Word/PDF 파일 다운로드

[기술 구현]
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│ 분석 결과    │ →  │ 조항 교체     │ →  │ 문서 생성    │
│ (clauses)   │     │ (alternatives)│     │ (docx/pdf)  │
└─────────────┘     └──────────────┘     └─────────────┘
```

### Feature: 판례 상담 챗봇

```
[사용자 흐름]
1. 채팅 페이지 접속 (/chat)
2. "계약서에서 손해배상 조항이 불리한 것 같은데 어떻게 해야 하나요?"
3. AI가 관련 판례 인용하며 답변
4. 추가 질문 → 대화 계속

[기술 구현]
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│ 사용자 질문  │ →  │ RAG 검색     │ →  │ GPT-4o 답변 │
└─────────────┘     │ (판례 DB)    │     │ + 판례 인용 │
                    └──────────────┘     └─────────────┘
```

### Feature: 노동상담 AI (노동톡) 🆕

```
[사용자 흐름]
1. 노동상담 페이지 접속 (/labor)
2. "3개월째 월급을 못 받았어요" 또는 "갑자기 해고 통보를 받았어요"
3. AI가 관련 법률 (근로기준법 등) 기반으로 상담
4. 복잡한 케이스의 경우 "전문 노무사 연결" 권유
5. 연결 신청 시 폼 작성 → 노무사 배정

[수익 모델]
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│ AI 무료상담  │ →  │ 복잡한 케이스 │ →  │ 노무사 연결  │
└─────────────┘     │ 전문가 필요   │     │ (수수료 발생)│
                    └──────────────┘     └─────────────┘

[상담 카테고리]
- 임금체불/체불임금
- 부당해고/해고예고
- 직장 내 괴롭힘
- 산업재해/업무상 재해
- 퇴직금/연차휴가
- 근로계약/근로조건
```

---

## 참고 자료

- [OpenAI API Docs](https://platform.openai.com/docs)
- [OpenAI Assistants API](https://platform.openai.com/docs/assistants)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Next.js Docs](https://nextjs.org/docs)
- [Pinecone Docs](https://docs.pinecone.io/)
- [국가법령정보센터](https://www.law.go.kr/)
- [python-docx](https://python-docx.readthedocs.io/)

---

## 팀 정보

- **해커톤**: 조코딩 x OpenAI x 프라이머 AI 해커톤
- **프로젝트**: ContractPilot
- **GitHub**: https://github.com/todo0157/jocoding_hackathon_1

---

---

## 🎯 목표 사용자층

### 10~20대 청년층 타겟팅

| 세그먼트 | 주요 니즈 | 계약서 유형 |
|----------|----------|-------------|
| **첫 취업 준비생** | 근로계약서 검토, 불공정 조항 파악 | 근로계약서, 연봉계약서 |
| **자취/독립 청년** | 보증금 보호, 전세사기 예방 | 임대차계약서, 전대차계약서 |
| **프리랜서/크리에이터** | 정당한 대가, 저작권 보호 | 용역계약서, 저작권양도계약 |
| **청년 창업자** | 투자 조건 이해, 지분 보호 | 투자계약서, 주주간계약서, NDA |

### 차별화 전략
- **친근한 UX**: 법률 용어 → 쉬운 말 변환
- **모바일 최적화**: 카카오톡 봇, 앱 연동
- **무료 기본 서비스**: 진입 장벽 최소화
- **또래 커뮤니티**: 계약 경험 공유, 주의사항 공유

---

*Last Updated: 2026-02-23 (v0.2.0 한국 시장 진입 대응 - HWP 지원, 익명화, 멀티 LLM, 법률 API, 협업 기능)*
