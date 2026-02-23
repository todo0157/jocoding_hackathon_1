"""
한국 법령 API 연동 서비스
- 국가법령정보센터 Open API
- 대법원 판례 검색 API
- 계약 유형별 필수 조항 체크리스트
"""
import httpx
import xml.etree.ElementTree as ET
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum
import asyncio
import re

from app.core.config import get_settings

settings = get_settings()


class ContractType(Enum):
    """계약서 유형"""
    INVESTMENT = "투자계약서"
    EMPLOYMENT = "근로계약서"
    LEASE = "임대차계약서"
    SERVICE = "용역계약서"
    NDA = "비밀유지계약서"
    SALES = "매매계약서"
    GENERAL = "일반계약서"


@dataclass
class LawArticle:
    """법령 조항"""
    law_name: str
    article_number: str
    article_title: str
    content: str
    effective_date: Optional[str] = None


@dataclass
class CourtCase:
    """판례 정보"""
    case_number: str
    case_name: str
    court: str
    decision_date: str
    summary: str
    full_text: Optional[str] = None
    relevance_score: float = 0.0


class KoreanLawAPIClient:
    """국가법령정보센터 API 클라이언트"""

    BASE_URL = "https://www.law.go.kr/DRF/lawService.do"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or getattr(settings, 'law_api_key', None)
        self.client = httpx.AsyncClient(timeout=30.0)

    async def search_law(
        self,
        query: str,
        target: str = "law",  # law, ordin, admrul
        display: int = 10
    ) -> List[Dict[str, Any]]:
        """
        법령 검색

        Args:
            query: 검색어
            target: 검색 대상 (law: 법령, ordin: 조례/규칙, admrul: 행정규칙)
            display: 검색 결과 수
        """
        params = {
            "OC": self.api_key or "test",
            "target": target,
            "type": "XML",
            "query": query,
            "display": display,
        }

        try:
            response = await self.client.get(self.BASE_URL, params=params)
            response.raise_for_status()
            return self._parse_law_search_result(response.text)
        except Exception as e:
            print(f"법령 검색 오류: {e}")
            return []

    async def get_law_detail(self, law_id: str) -> Optional[Dict[str, Any]]:
        """법령 상세 조회"""
        params = {
            "OC": self.api_key or "test",
            "target": "law",
            "type": "XML",
            "ID": law_id,
        }

        try:
            response = await self.client.get(self.BASE_URL, params=params)
            response.raise_for_status()
            return self._parse_law_detail(response.text)
        except Exception as e:
            print(f"법령 상세 조회 오류: {e}")
            return None

    def _parse_law_search_result(self, xml_text: str) -> List[Dict[str, Any]]:
        """검색 결과 XML 파싱"""
        results = []
        try:
            root = ET.fromstring(xml_text)
            for item in root.findall(".//law"):
                results.append({
                    "law_id": self._get_text(item, "법령ID"),
                    "law_name": self._get_text(item, "법령명한글"),
                    "promulgation_date": self._get_text(item, "공포일자"),
                    "effective_date": self._get_text(item, "시행일자"),
                    "ministry": self._get_text(item, "소관부처"),
                })
        except ET.ParseError:
            pass
        return results

    def _parse_law_detail(self, xml_text: str) -> Optional[Dict[str, Any]]:
        """법령 상세 XML 파싱"""
        try:
            root = ET.fromstring(xml_text)
            articles = []
            for article in root.findall(".//조문"):
                articles.append({
                    "number": self._get_text(article, "조문번호"),
                    "title": self._get_text(article, "조문제목"),
                    "content": self._get_text(article, "조문내용"),
                })
            return {
                "law_name": self._get_text(root, "법령명"),
                "articles": articles,
            }
        except ET.ParseError:
            return None

    def _get_text(self, element, tag: str) -> str:
        """XML 요소에서 텍스트 추출"""
        found = element.find(f".//{tag}")
        return found.text if found is not None and found.text else ""

    async def close(self):
        await self.client.aclose()


class CourtCaseSearchClient:
    """대법원 판례 검색 클라이언트"""

    BASE_URL = "https://www.law.go.kr/DRF/lawService.do"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or getattr(settings, 'law_api_key', None)
        self.client = httpx.AsyncClient(timeout=30.0)

    async def search_cases(
        self,
        query: str,
        court: Optional[str] = None,  # 대법원, 고등법원, 지방법원
        display: int = 10
    ) -> List[CourtCase]:
        """
        판례 검색

        Args:
            query: 검색어
            court: 법원 종류
            display: 검색 결과 수
        """
        params = {
            "OC": self.api_key or "test",
            "target": "prec",
            "type": "XML",
            "query": query,
            "display": display,
        }

        try:
            response = await self.client.get(self.BASE_URL, params=params)
            response.raise_for_status()
            return self._parse_case_search_result(response.text, court)
        except Exception as e:
            print(f"판례 검색 오류: {e}")
            return []

    async def get_case_detail(self, case_id: str) -> Optional[CourtCase]:
        """판례 상세 조회"""
        params = {
            "OC": self.api_key or "test",
            "target": "prec",
            "type": "XML",
            "ID": case_id,
        }

        try:
            response = await self.client.get(self.BASE_URL, params=params)
            response.raise_for_status()
            return self._parse_case_detail(response.text)
        except Exception as e:
            print(f"판례 상세 조회 오류: {e}")
            return None

    def _parse_case_search_result(
        self,
        xml_text: str,
        court_filter: Optional[str] = None
    ) -> List[CourtCase]:
        """판례 검색 결과 파싱"""
        results = []
        try:
            root = ET.fromstring(xml_text)
            for item in root.findall(".//prec"):
                court = self._get_text(item, "법원명")
                if court_filter and court_filter not in court:
                    continue

                results.append(CourtCase(
                    case_number=self._get_text(item, "사건번호"),
                    case_name=self._get_text(item, "사건명"),
                    court=court,
                    decision_date=self._get_text(item, "선고일자"),
                    summary=self._get_text(item, "판례내용"),
                ))
        except ET.ParseError:
            pass
        return results

    def _parse_case_detail(self, xml_text: str) -> Optional[CourtCase]:
        """판례 상세 파싱"""
        try:
            root = ET.fromstring(xml_text)
            return CourtCase(
                case_number=self._get_text(root, "사건번호"),
                case_name=self._get_text(root, "사건명"),
                court=self._get_text(root, "법원명"),
                decision_date=self._get_text(root, "선고일자"),
                summary=self._get_text(root, "판시사항"),
                full_text=self._get_text(root, "판결요지"),
            )
        except ET.ParseError:
            return None

    def _get_text(self, element, tag: str) -> str:
        found = element.find(f".//{tag}")
        return found.text if found is not None and found.text else ""

    async def close(self):
        await self.client.aclose()


# 계약 유형별 필수 조항 체크리스트
CONTRACT_CHECKLIST: Dict[ContractType, List[Dict[str, Any]]] = {
    ContractType.INVESTMENT: [
        {"clause": "투자금액", "law": "상법 제329조", "required": True},
        {"clause": "지분율", "law": "상법 제329조", "required": True},
        {"clause": "투자 조건", "law": "상법", "required": True},
        {"clause": "이사회 구성", "law": "상법 제382조", "required": False},
        {"clause": "우선주 조건", "law": "상법 제344조", "required": False},
        {"clause": "희석 방지", "law": "상법", "required": False},
        {"clause": "동반매도권", "law": "계약자유원칙", "required": False},
        {"clause": "우선매수권", "law": "계약자유원칙", "required": False},
        {"clause": "계약 해지", "law": "민법 제543조", "required": True},
        {"clause": "분쟁 해결", "law": "중재법", "required": True},
    ],
    ContractType.EMPLOYMENT: [
        {"clause": "근로계약기간", "law": "근로기준법 제16조", "required": True},
        {"clause": "근무장소", "law": "근로기준법 제17조", "required": True},
        {"clause": "업무내용", "law": "근로기준법 제17조", "required": True},
        {"clause": "근로시간", "law": "근로기준법 제50조", "required": True},
        {"clause": "휴게시간", "law": "근로기준법 제54조", "required": True},
        {"clause": "휴일", "law": "근로기준법 제55조", "required": True},
        {"clause": "임금", "law": "근로기준법 제17조", "required": True},
        {"clause": "임금지급일", "law": "근로기준법 제43조", "required": True},
        {"clause": "연차휴가", "law": "근로기준법 제60조", "required": True},
        {"clause": "퇴직금", "law": "근로자퇴직급여보장법", "required": True},
        {"clause": "해고사유", "law": "근로기준법 제23조", "required": False},
        {"clause": "비밀유지", "law": "부정경쟁방지법", "required": False},
        {"clause": "경업금지", "law": "판례법", "required": False},
    ],
    ContractType.LEASE: [
        {"clause": "임대 목적물", "law": "민법 제618조", "required": True},
        {"clause": "임대차 기간", "law": "주택임대차보호법 제4조", "required": True},
        {"clause": "보증금", "law": "주택임대차보호법", "required": True},
        {"clause": "차임(월세)", "law": "민법 제618조", "required": True},
        {"clause": "차임 지급일", "law": "민법", "required": True},
        {"clause": "관리비", "law": "주택임대차보호법", "required": False},
        {"clause": "수선의무", "law": "민법 제623조", "required": True},
        {"clause": "전대 금지", "law": "민법 제629조", "required": False},
        {"clause": "계약 해지", "law": "민법 제635조", "required": True},
        {"clause": "원상복구", "law": "민법 제654조", "required": True},
        {"clause": "보증금 반환", "law": "주택임대차보호법 제3조", "required": True},
    ],
    ContractType.SERVICE: [
        {"clause": "용역 내용", "law": "민법 제664조", "required": True},
        {"clause": "용역 기간", "law": "민법", "required": True},
        {"clause": "대금", "law": "민법 제664조", "required": True},
        {"clause": "대금 지급 방법", "law": "민법", "required": True},
        {"clause": "납품/인도", "law": "민법 제665조", "required": True},
        {"clause": "검수", "law": "민법", "required": True},
        {"clause": "하자 담보", "law": "민법 제667조", "required": True},
        {"clause": "지식재산권", "law": "저작권법", "required": False},
        {"clause": "비밀유지", "law": "부정경쟁방지법", "required": False},
        {"clause": "손해배상", "law": "민법 제390조", "required": True},
        {"clause": "계약 해지", "law": "민법 제543조", "required": True},
    ],
    ContractType.NDA: [
        {"clause": "비밀정보 정의", "law": "부정경쟁방지법 제2조", "required": True},
        {"clause": "비밀유지 의무", "law": "부정경쟁방지법", "required": True},
        {"clause": "비밀유지 기간", "law": "계약자유원칙", "required": True},
        {"clause": "사용 범위 제한", "law": "부정경쟁방지법", "required": True},
        {"clause": "복제/복사 제한", "law": "부정경쟁방지법", "required": False},
        {"clause": "반환/폐기 의무", "law": "계약자유원칙", "required": True},
        {"clause": "예외 사항", "law": "계약자유원칙", "required": True},
        {"clause": "손해배상", "law": "민법 제390조", "required": True},
        {"clause": "분쟁 해결", "law": "민사소송법", "required": False},
    ],
    ContractType.SALES: [
        {"clause": "매매 목적물", "law": "민법 제563조", "required": True},
        {"clause": "매매 대금", "law": "민법 제563조", "required": True},
        {"clause": "대금 지급 방법", "law": "민법", "required": True},
        {"clause": "소유권 이전", "law": "민법 제186조", "required": True},
        {"clause": "인도 시기/방법", "law": "민법 제568조", "required": True},
        {"clause": "위험 부담", "law": "민법 제537조", "required": False},
        {"clause": "하자 담보", "law": "민법 제580조", "required": True},
        {"clause": "계약 해제", "law": "민법 제543조", "required": True},
        {"clause": "손해배상", "law": "민법 제390조", "required": True},
    ],
    ContractType.GENERAL: [
        {"clause": "계약 당사자", "law": "민법", "required": True},
        {"clause": "계약 목적", "law": "민법", "required": True},
        {"clause": "권리/의무", "law": "민법", "required": True},
        {"clause": "계약 기간", "law": "민법", "required": False},
        {"clause": "대금/비용", "law": "민법", "required": False},
        {"clause": "손해배상", "law": "민법 제390조", "required": False},
        {"clause": "계약 해지/해제", "law": "민법 제543조", "required": True},
        {"clause": "분쟁 해결", "law": "민사소송법", "required": False},
    ],
}


# 주요 계약 관련 법령 데이터 (오프라인 캐시)
ESSENTIAL_LAWS = {
    "민법": {
        "제103조": {
            "title": "반사회질서의 법률행위",
            "content": "선량한 풍속 기타 사회질서에 위반한 사항을 내용으로 하는 법률행위는 무효로 한다."
        },
        "제104조": {
            "title": "불공정한 법률행위",
            "content": "당사자의 궁박, 경솔 또는 무경험으로 인하여 현저하게 공정을 잃은 법률행위는 무효로 한다."
        },
        "제390조": {
            "title": "채무불이행과 손해배상",
            "content": "채무자가 채무의 내용에 좇은 이행을 하지 아니한 때에는 채권자는 손해배상을 청구할 수 있다."
        },
        "제398조": {
            "title": "배상액의 예정",
            "content": "당사자는 채무불이행에 관한 손해배상액을 예정할 수 있다. 손해배상의 예정액이 부당히 과다한 경우에는 법원은 적당히 감액할 수 있다."
        },
        "제543조": {
            "title": "해지, 해제권",
            "content": "계약 또는 법률의 규정에 의하여 당사자의 일방이나 쌍방이 해지 또는 해제의 권리가 있는 때에는 그 해지 또는 해제는 상대방에 대한 의사표시로 한다."
        },
        "제618조": {
            "title": "임대차의 의의",
            "content": "임대차는 당사자 일방이 상대방에게 목적물을 사용, 수익하게 할 것을 약정하고 상대방이 이에 대하여 차임을 지급할 것을 약정함으로써 그 효력이 생긴다."
        },
        "제664조": {
            "title": "도급의 의의",
            "content": "도급은 당사자 일방이 어느 일을 완성할 것을 약정하고 상대방이 그 일의 결과에 대하여 보수를 지급할 것을 약정함으로써 그 효력이 생긴다."
        },
    },
    "근로기준법": {
        "제17조": {
            "title": "근로조건의 명시",
            "content": "사용자는 근로계약을 체결할 때에 근로자에게 임금, 소정근로시간, 휴일, 연차유급휴가 등을 명시하여야 한다."
        },
        "제23조": {
            "title": "해고 등의 제한",
            "content": "사용자는 근로자에게 정당한 이유 없이 해고, 휴직, 정직, 전직, 감봉, 그 밖의 징벌을 하지 못한다."
        },
        "제50조": {
            "title": "근로시간",
            "content": "1주 간의 근로시간은 휴게시간을 제외하고 40시간을 초과할 수 없다."
        },
        "제60조": {
            "title": "연차유급휴가",
            "content": "사용자는 1년간 80퍼센트 이상 출근한 근로자에게 15일의 유급휴가를 주어야 한다."
        },
    },
    "상법": {
        "제329조": {
            "title": "주식의 액면미달발행",
            "content": "주식은 액면미달의 가액으로 발행하지 못한다."
        },
        "제344조": {
            "title": "종류주식",
            "content": "회사는 이익의 배당, 잔여재산의 분배, 주주총회에서의 의결권의 행사, 상환 및 전환 등에 관하여 내용이 다른 종류의 주식을 발행할 수 있다."
        },
    },
}


class KoreanLawService:
    """한국 법령 통합 서비스"""

    def __init__(self):
        self.law_client = KoreanLawAPIClient()
        self.case_client = CourtCaseSearchClient()

    async def get_relevant_laws(
        self,
        clause_text: str,
        contract_type: str
    ) -> List[Dict[str, Any]]:
        """
        조항에 관련된 법령 조회

        Args:
            clause_text: 분석할 조항 텍스트
            contract_type: 계약서 유형

        Returns:
            관련 법령 목록
        """
        relevant_laws = []

        # 1. 오프라인 캐시에서 검색
        keywords = self._extract_keywords(clause_text)
        for law_name, articles in ESSENTIAL_LAWS.items():
            for article_num, article_data in articles.items():
                if any(kw in article_data["content"] for kw in keywords):
                    relevant_laws.append({
                        "law_name": law_name,
                        "article_number": article_num,
                        "article_title": article_data["title"],
                        "content": article_data["content"],
                        "source": "cache"
                    })

        # 2. API 검색 (캐시에 없는 경우)
        if len(relevant_laws) < 2 and keywords:
            try:
                api_results = await self.law_client.search_law(
                    " ".join(keywords[:3]),
                    display=5
                )
                for result in api_results:
                    relevant_laws.append({
                        "law_name": result.get("law_name", ""),
                        "article_number": "",
                        "article_title": "",
                        "content": "",
                        "source": "api"
                    })
            except Exception:
                pass

        return relevant_laws[:5]

    async def search_similar_cases(
        self,
        clause_text: str,
        top_k: int = 3
    ) -> List[CourtCase]:
        """
        유사 판례 검색

        Args:
            clause_text: 분석할 조항 텍스트
            top_k: 반환할 판례 수
        """
        keywords = self._extract_keywords(clause_text)

        if not keywords:
            return []

        try:
            cases = await self.case_client.search_cases(
                " ".join(keywords[:3]),
                display=top_k * 2
            )
            # 관련성 점수 계산
            for case in cases:
                case.relevance_score = self._calculate_relevance(
                    clause_text, case.summary
                )

            # 관련성 높은 순으로 정렬
            cases.sort(key=lambda x: x.relevance_score, reverse=True)
            return cases[:top_k]
        except Exception:
            return []

    def get_checklist(self, contract_type: str) -> List[Dict[str, Any]]:
        """
        계약 유형별 필수 조항 체크리스트 반환

        Args:
            contract_type: 계약서 유형 문자열
        """
        # 문자열을 ContractType으로 변환
        type_mapping = {
            "투자계약서": ContractType.INVESTMENT,
            "근로계약서": ContractType.EMPLOYMENT,
            "임대차계약서": ContractType.LEASE,
            "용역계약서": ContractType.SERVICE,
            "비밀유지계약서": ContractType.NDA,
            "NDA": ContractType.NDA,
            "매매계약서": ContractType.SALES,
        }

        contract_enum = type_mapping.get(contract_type, ContractType.GENERAL)
        return CONTRACT_CHECKLIST.get(contract_enum, CONTRACT_CHECKLIST[ContractType.GENERAL])

    def check_missing_clauses(
        self,
        contract_type: str,
        clauses: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        누락된 필수 조항 체크

        Args:
            contract_type: 계약서 유형
            clauses: 분석된 조항 목록

        Returns:
            누락된 조항 목록
        """
        checklist = self.get_checklist(contract_type)
        clause_text = " ".join([c.get("content", "") for c in clauses])

        missing = []
        for item in checklist:
            if item["required"]:
                # 간단한 키워드 매칭으로 조항 존재 여부 확인
                clause_name = item["clause"]
                if clause_name not in clause_text:
                    missing.append({
                        "clause": clause_name,
                        "law": item["law"],
                        "severity": "high" if item["required"] else "medium"
                    })

        return missing

    def _extract_keywords(self, text: str) -> List[str]:
        """텍스트에서 법률 관련 키워드 추출"""
        # 법률 관련 주요 키워드
        legal_keywords = [
            "해지", "해제", "손해배상", "위약금", "계약", "의무", "권리",
            "책임", "면책", "보증", "담보", "이행", "불이행", "위반",
            "취소", "무효", "효력", "기간", "갱신", "연장", "종료",
            "양도", "전대", "임대", "임차", "매매", "대금", "지급",
            "인도", "검수", "하자", "하자담보", "경업금지", "비밀유지",
            "근로", "임금", "퇴직", "해고", "휴가", "수당",
        ]

        found = []
        for kw in legal_keywords:
            if kw in text:
                found.append(kw)

        return found

    def _calculate_relevance(self, source: str, target: str) -> float:
        """관련성 점수 계산 (0.0 ~ 1.0)"""
        source_keywords = set(self._extract_keywords(source))
        target_keywords = set(self._extract_keywords(target))

        if not source_keywords:
            return 0.0

        intersection = source_keywords & target_keywords
        return len(intersection) / len(source_keywords)

    async def close(self):
        await self.law_client.close()
        await self.case_client.close()


# 싱글톤 인스턴스
_law_service: Optional[KoreanLawService] = None


def get_law_service() -> KoreanLawService:
    """법령 서비스 인스턴스 반환"""
    global _law_service
    if _law_service is None:
        _law_service = KoreanLawService()
    return _law_service


async def get_relevant_laws(clause_text: str, contract_type: str) -> List[Dict[str, Any]]:
    """관련 법령 조회 헬퍼 함수"""
    service = get_law_service()
    return await service.get_relevant_laws(clause_text, contract_type)


async def search_court_cases(clause_text: str, top_k: int = 3) -> List[CourtCase]:
    """판례 검색 헬퍼 함수"""
    service = get_law_service()
    return await service.search_similar_cases(clause_text, top_k)


def get_contract_checklist(contract_type: str) -> List[Dict[str, Any]]:
    """체크리스트 조회 헬퍼 함수"""
    service = get_law_service()
    return service.get_checklist(contract_type)


def check_missing_clauses(contract_type: str, clauses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """누락 조항 체크 헬퍼 함수"""
    service = get_law_service()
    return service.check_missing_clauses(contract_type, clauses)
