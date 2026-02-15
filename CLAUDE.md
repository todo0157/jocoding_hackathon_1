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
│   │   │   └── analysis_service.py # 분석 로직
│   │   └── main.py                # FastAPI 앱
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env                       # API 키 (gitignore)
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx           # 메인 페이지
│   │   │   ├── layout.tsx
│   │   │   └── globals.css
│   │   ├── components/
│   │   │   ├── FileUpload.tsx     # 드래그앤드롭 업로드
│   │   │   ├── LoadingState.tsx   # 로딩 애니메이션
│   │   │   └── AnalysisResult.tsx # 결과 표시
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
- [x] 수정안 생성 Agent
- [x] Next.js 프론트엔드
- [x] 드래그앤드롭 파일 업로드
- [x] 분석 결과 UI
- [x] 로딩 애니메이션
- [x] GitHub 연동

### 진행 예정 📋
- [ ] Pinecone 판례 벡터 DB 연동
- [ ] 실제 판례 데이터 수집 (국가법령정보센터)
- [ ] 배포 (Vercel + Railway)
- [ ] 데모 영상 녹화
- [ ] 발표 자료 제작

---

## 환경 변수

### backend/.env
```env
OPENAI_API_KEY=sk-...
PINECONE_API_KEY=...  # 선택사항
PINECONE_INDEX_NAME=contract-pilot
```

### frontend/.env.local
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 해커톤 전략

### 핵심 차별점
1. **한국 판례 기반**: 단순 GPT Wrapper가 아닌 RAG 파이프라인
2. **B2B SaaS 모델**: 투자자 친화적 비즈니스 모델
3. **실제 문제 해결**: 중소기업 400만개의 Pain Point

### 데모 시나리오 (2분)
1. PDF 드래그앤드롭 업로드
2. 실시간 분석 진행 애니메이션
3. 위험 조항 하이라이트
4. 판례 근거 표시
5. 수정안 복사 버튼

---

## 참고 자료

- [OpenAI API Docs](https://platform.openai.com/docs)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Next.js Docs](https://nextjs.org/docs)
- [국가법령정보센터](https://www.law.go.kr/)

---

## 팀 정보

- **해커톤**: 조코딩 x OpenAI x 프라이머 AI 해커톤
- **프로젝트**: ContractPilot
- **GitHub**: https://github.com/todo0157/jocoding_hackathon_1

---

*Last Updated: 2026-02-15*
