import re
from PyPDF2 import PdfReader
from io import BytesIO


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """PDF에서 텍스트 추출"""
    pdf_file = BytesIO(file_bytes)
    reader = PdfReader(pdf_file)

    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"

    return text.strip()


def split_into_clauses(text: str) -> list[dict]:
    """계약서 텍스트를 조항별로 분리"""
    # 제X조, 제X항, 숫자. 패턴으로 조항 분리
    patterns = [
        r'제\s*(\d+)\s*조[^\n]*\n',  # 제1조, 제 1 조
        r'(\d+)\.\s+',               # 1. 2. 3.
        r'제\s*(\d+)\s*항',          # 제1항
    ]

    clauses = []
    current_clause = ""
    current_title = ""
    clause_number = 0

    lines = text.split('\n')

    for line in lines:
        # 새 조항 시작 감지
        is_new_clause = False
        for pattern in patterns:
            match = re.match(pattern, line.strip())
            if match:
                # 이전 조항 저장
                if current_clause.strip():
                    clauses.append({
                        "number": clause_number,
                        "title": current_title,
                        "content": current_clause.strip()
                    })

                clause_number += 1
                current_title = line.strip()
                current_clause = line + "\n"
                is_new_clause = True
                break

        if not is_new_clause:
            current_clause += line + "\n"

    # 마지막 조항 저장
    if current_clause.strip():
        clauses.append({
            "number": clause_number,
            "title": current_title,
            "content": current_clause.strip()
        })

    return clauses


def get_contract_type(text: str) -> str:
    """계약서 유형 감지"""
    keywords = {
        "투자계약서": ["투자금", "지분", "우선주", "투자자", "배당"],
        "근로계약서": ["근로자", "임금", "근무시간", "휴가", "해고"],
        "임대차계약서": ["임대인", "임차인", "월세", "보증금", "계약기간"],
        "용역계약서": ["용역", "대금", "납품", "검수", "하자"],
        "NDA": ["기밀", "비밀유지", "정보", "공개금지"],
    }

    text_lower = text.lower()
    scores = {}

    for contract_type, words in keywords.items():
        score = sum(1 for word in words if word in text_lower)
        if score > 0:
            scores[contract_type] = score

    if scores:
        return max(scores, key=scores.get)
    return "일반계약서"
