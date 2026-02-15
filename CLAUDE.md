# ContractPilot - 프로젝트 문서

> AI 기반 계약서 위험 분석 서비스
> 조코딩 x OpenAI x 프라이머 해커톤

## 프로젝트 개요

**ContractPilot**은 한국 판례 기반 AI를 활용하여 계약서의 위험 조항을 자동으로 분석하고 수정안을 제안하는 B2B SaaS 서비스입니다.

### 핵심 가치
- 변호사 비용 90% 절감 (건당 200만원 → 월 9.9만원 구독)
- 검토 시간 단축 (2~3일 → 10분)
- 한국 판례 기반 법적 근거 제시

---

## 기술 스택

### Backend
| 기술 | 버전 | 용도 |
|------|------|------|
| Python | 3.13 | 런타임 |
| FastAPI | 0.122+ | 웹 프레임워크 |
| OpenAI | 2.21+ | GPT-4o API |
| PyPDF2 | 3.0.1 | PDF 텍스트 추출 |
| python-docx | 0.8.11+ | Word 문서 생성 |
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
│   │   │   └── openai_client.py   # OpenAI 연동
│   │   ├── models/
│   │   │   └── schemas.py         # Pydantic 스키마
│   │   ├── services/
│   │   │   ├── pdf_service.py     # PDF 처리
│   │   │   ├── rag_service.py     # 판례 검색 (샘플)
│   │   │   ├── analysis_service.py # 분석 로직
│   │   │   ├── chat_service.py    # 챗봇 서비스
│   │   │   └── docx_generator.py  # Word 문서 생성
│   │   └── main.py                # FastAPI 앱
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env                       # API 키 (gitignore)
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx           # 메인 페이지
│   │   │   ├── chat/page.tsx      # 챗봇 페이지
│   │   │   ├── layout.tsx
│   │   │   └── globals.css
│   │   ├── components/
│   │   │   ├── FileUpload.tsx     # 드래그앤드롭 업로드
│   │   │   ├── LoadingState.tsx   # 로딩 애니메이션
│   │   │   ├── AnalysisResult.tsx # 결과 표시
│   │   │   ├── ChatInterface.tsx  # 챗봇 인터페이스
│   │   │   └── DownloadButton.tsx # 계약서 다운로드 버튼
│   │   └── lib/
│   │       └── api.ts             # API 클라이언트
│   ├── package.json
│   └── tailwind.config.ts
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

| Method | Path | 설명 |
|--------|------|------|
| GET | `/` | 서버 정보 |
| GET | `/api/v1/health` | 헬스체크 |
| POST | `/api/v1/analyze` | 계약서 PDF 분석 |
| POST | `/api/v1/analyze/text` | 텍스트 직접 분석 (테스트용) |
| POST | `/api/v1/chat` | 판례 기반 법률 상담 챗봇 |
| POST | `/api/v1/generate-safe-contract` | 수정된 계약서 Word 다운로드 |

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

### 현재 상태 ⚠️
- 판례 데이터: **샘플 5건** (하드코딩)
- 판례 검색: **키워드 매칭** (벡터 검색 아님)
- 배포: **로컬 환경만**

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

#### 2.3 분석 리포트 PDF 생성 기능 ⭐ NEW
```
예상 시간: 2~3시간
우선순위: 중간

기능 설명:
- 계약서 분석 결과를 전문적인 PDF 리포트로 생성
- 요약, 위험 조항, 수정 제안 등 포함
- 클라이언트/상사에게 공유하기 좋은 형식

구현 방법:
1. 새 API 엔드포인트: POST /api/v1/generate-report
2. reportlab 또는 weasyprint로 PDF 생성
3. 프론트엔드에 "분석 리포트 다운로드" 버튼 추가

PDF 리포트 구성:
- 표지: 계약서 유형, 분석 일시
- 요약: 전체 위험도, 고위험 조항 수
- 조항별 분석: 원문, 문제점, 수정 제안
- 관련 판례 목록
- 면책 조항

필요한 파일:
- backend/app/services/pdf_report_generator.py (신규)
- backend/app/api/routes.py (수정)
- frontend/src/components/ReportDownloadButton.tsx (신규)

필요한 패키지:
- reportlab>=4.0.0
- 또는 weasyprint>=60.0
```

### 🟢 Phase 3: 배포 & 마무리

#### 3.1 배포
```
예상 시간: 1~2시간

Frontend (Vercel):
1. vercel.com 연동
2. 환경변수 설정: NEXT_PUBLIC_API_URL

Backend (Railway):
1. railway.app 연동
2. 환경변수 설정: OPENAI_API_KEY, PINECONE_API_KEY
3. Dockerfile 사용
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
OPENAI_API_KEY=sk-...
PINECONE_API_KEY=...  # TODO: 추가 필요
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

*Last Updated: 2026-02-15 (챗봇 & 계약서 다운로드 기능 추가)*
