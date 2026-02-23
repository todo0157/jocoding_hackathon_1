"""
개인정보 익명화 서비스
개인정보보호법 준수를 위한 데이터 마스킹 처리
"""
import re
from typing import Tuple, Dict, List
from dataclasses import dataclass
import hashlib


@dataclass
class AnonymizationResult:
    """익명화 결과"""
    anonymized_text: str
    mapping: Dict[str, str]  # 마스킹된 값 -> 원본 값
    stats: Dict[str, int]  # 익명화된 항목 통계


class PersonalDataAnonymizer:
    """개인정보 익명화 처리기"""

    def __init__(self):
        # 마스킹 패턴 정의
        self.patterns = {
            # 한국 주민등록번호 (000000-0000000)
            'resident_number': (
                r'\b(\d{6})[-\s]?(\d{7})\b',
                self._mask_resident_number
            ),
            # 한국 전화번호 (010-0000-0000, 02-000-0000 등)
            'phone': (
                r'\b(0\d{1,2})[-.\s]?(\d{3,4})[-.\s]?(\d{4})\b',
                self._mask_phone
            ),
            # 이메일 주소
            'email': (
                r'\b([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b',
                self._mask_email
            ),
            # 한국 사업자등록번호 (000-00-00000)
            'business_number': (
                r'\b(\d{3})[-\s]?(\d{2})[-\s]?(\d{5})\b',
                self._mask_business_number
            ),
            # 계좌번호 (10-14자리 숫자)
            'account_number': (
                r'\b(\d{2,6})[-\s]?(\d{2,6})[-\s]?(\d{2,6})[-\s]?(\d{0,4})\b',
                self._mask_account_number
            ),
            # 한국 주소 (시/도, 구/군, 동/읍/면)
            'address': (
                r'(서울|부산|대구|인천|광주|대전|울산|세종|경기|강원|충북|충남|전북|전남|경북|경남|제주)'
                r'(특별시|광역시|특별자치시|도|특별자치도)?[\s]?'
                r'([가-힣]+[시군구])[\s]?'
                r'([가-힣]+[동읍면로길])?[\s]?'
                r'(\d+[-\d]*)?',
                self._mask_address
            ),
            # 한국 이름 (2-4글자 한글, 성+이름 패턴)
            'korean_name': (
                r'\b([김이박최정강조윤장임한오서신권황안송류홍전고문양손배백허유남심노하곽성차주우구신임나전민유진지엄채원천방공강현함변염양변여추도석선설마길연위표명기반왕금옥육인맹제모남궁제갈선우독고황보동방사공])([가-힣]{1,3})\b',
                self._mask_korean_name
            ),
            # 금액 (원, 만원, 억원 등)
            'amount': (
                r'\b(\d{1,3}(?:,\d{3})*|\d+)\s*(원|만원|억원|천원|백만원|달러|USD|KRW)\b',
                self._mask_amount
            ),
        }

        self.mapping: Dict[str, str] = {}
        self.reverse_mapping: Dict[str, str] = {}
        self.stats: Dict[str, int] = {}

    def anonymize(self, text: str, preserve_amounts: bool = False) -> AnonymizationResult:
        """
        텍스트에서 개인정보를 익명화

        Args:
            text: 원본 텍스트
            preserve_amounts: True면 금액 정보 보존

        Returns:
            AnonymizationResult: 익명화된 텍스트, 매핑 정보, 통계
        """
        self.mapping = {}
        self.reverse_mapping = {}
        self.stats = {key: 0 for key in self.patterns.keys()}

        anonymized = text

        # 각 패턴에 대해 익명화 수행
        for pattern_name, (pattern, mask_func) in self.patterns.items():
            # 금액 보존 옵션
            if pattern_name == 'amount' and preserve_amounts:
                continue

            anonymized = self._apply_pattern(
                anonymized, pattern, mask_func, pattern_name
            )

        return AnonymizationResult(
            anonymized_text=anonymized,
            mapping=self.reverse_mapping,
            stats=self.stats
        )

    def restore(self, anonymized_text: str, mapping: Dict[str, str]) -> str:
        """익명화된 텍스트를 원본으로 복원"""
        restored = anonymized_text
        for masked, original in mapping.items():
            restored = restored.replace(masked, original)
        return restored

    def _apply_pattern(
        self,
        text: str,
        pattern: str,
        mask_func,
        pattern_name: str
    ) -> str:
        """패턴에 맞는 텍스트를 마스킹"""

        def replacer(match):
            original = match.group(0)
            masked = mask_func(match)

            if masked != original:
                self.stats[pattern_name] += 1
                self.mapping[original] = masked
                self.reverse_mapping[masked] = original

            return masked

        return re.sub(pattern, replacer, text)

    def _mask_resident_number(self, match) -> str:
        """주민등록번호 마스킹: 앞 6자리만 보존"""
        front = match.group(1)
        return f"{front}-*******"

    def _mask_phone(self, match) -> str:
        """전화번호 마스킹: 가운데 자리 숨김"""
        area = match.group(1)
        last = match.group(3)
        return f"{area}-****-{last}"

    def _mask_email(self, match) -> str:
        """이메일 마스킹: 아이디 일부만 표시"""
        username = match.group(1)
        domain = match.group(2)
        if len(username) > 2:
            masked_username = username[:2] + '*' * (len(username) - 2)
        else:
            masked_username = '*' * len(username)
        return f"{masked_username}@{domain}"

    def _mask_business_number(self, match) -> str:
        """사업자등록번호 마스킹"""
        return "***-**-*****"

    def _mask_account_number(self, match) -> str:
        """계좌번호 마스킹"""
        return "****-****-****"

    def _mask_address(self, match) -> str:
        """주소 마스킹: 시/도만 표시"""
        region = match.group(1)
        suffix = match.group(2) or ""
        return f"{region}{suffix} ***"

    def _mask_korean_name(self, match) -> str:
        """한국 이름 마스킹: 성만 표시"""
        surname = match.group(1)
        given_name = match.group(2)
        return surname + '*' * len(given_name)

    def _mask_amount(self, match) -> str:
        """금액 마스킹: [금액]으로 표시"""
        return "[금액정보]"


# 싱글톤 인스턴스
_anonymizer = PersonalDataAnonymizer()


def anonymize_text(text: str, preserve_amounts: bool = True) -> Tuple[str, Dict[str, str]]:
    """
    텍스트 익명화 헬퍼 함수

    Args:
        text: 원본 텍스트
        preserve_amounts: 금액 정보 보존 여부 (계약서에서는 보통 보존)

    Returns:
        (익명화된 텍스트, 복원용 매핑)
    """
    result = _anonymizer.anonymize(text, preserve_amounts=preserve_amounts)
    return result.anonymized_text, result.mapping


def restore_text(anonymized_text: str, mapping: Dict[str, str]) -> str:
    """익명화된 텍스트 복원"""
    return _anonymizer.restore(anonymized_text, mapping)


def get_anonymization_stats(text: str) -> Dict[str, int]:
    """익명화 통계 조회 (실제 익명화 없이 통계만)"""
    result = _anonymizer.anonymize(text)
    return result.stats


# 빠른 익명화 체크 (개인정보 포함 여부)
def contains_personal_data(text: str) -> bool:
    """텍스트에 개인정보가 포함되어 있는지 확인"""
    result = _anonymizer.anonymize(text)
    return sum(result.stats.values()) > 0
