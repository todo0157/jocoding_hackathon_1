# ContractPilot

> AI 기반 계약서 위험 분석 서비스
> 조코딩 x OpenAI x 프라이머 해커톤

## 기술 스택

### Backend
- **FastAPI** - Python 웹 프레임워크
- **OpenAI GPT-4o** - 계약서 분석 AI
- **Pinecone** - 판례 벡터 검색 (RAG)
- **PyPDF2** - PDF 텍스트 추출

### Frontend
- **Next.js 14** - React 프레임워크
- **Tailwind CSS** - 스타일링
- **Framer Motion** - 애니메이션
- **Lucide React** - 아이콘

## 빠른 시작

### 1. 환경 변수 설정

```bash
# backend/.env
cp backend/.env.example backend/.env
# OpenAI API 키와 Pinecone API 키 입력
```

### 2. Backend 실행

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 3. Frontend 실행

```bash
cd frontend
npm install
npm run dev
```

### 4. 접속

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 프로젝트 구조

```
ContractPilot/
├── backend/
│   ├── app/
│   │   ├── api/          # API 라우트
│   │   ├── core/         # 설정, OpenAI 클라이언트
│   │   ├── models/       # Pydantic 스키마
│   │   └── services/     # 비즈니스 로직
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── app/          # Next.js App Router
│       ├── components/   # React 컴포넌트
│       └── lib/          # API 클라이언트
└── data/                 # 샘플 계약서, 판례 데이터
```

## API 엔드포인트

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/v1/health` | 서버 상태 확인 |
| POST | `/api/v1/analyze` | 계약서 PDF 분석 |

## 해커톤 체크리스트

- [x] 프로젝트 구조 설정
- [x] FastAPI 백엔드 기본 구조
- [x] OpenAI 연동
- [x] PDF 텍스트 추출
- [x] 조항 분리 로직
- [x] 위험 분석 Agent
- [x] Next.js 프론트엔드
- [x] 파일 업로드 UI
- [x] 분석 결과 표시
- [ ] Pinecone 판례 인덱싱
- [ ] 배포 (Vercel + Railway)
- [ ] 데모 영상 녹화

## 라이선스

MIT License
