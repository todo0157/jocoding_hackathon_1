"""
통합 문서 처리 서비스
PDF, HWP, HWPX 파일 지원
"""
from typing import Tuple
from app.services.pdf_service import extract_text_from_pdf, split_into_clauses, get_contract_type
from app.services.hwp_service import extract_text_from_hwp, is_hwp_file, get_supported_extensions


# 지원 파일 형식
SUPPORTED_EXTENSIONS = ['.pdf', '.hwp', '.hwpx']
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def get_file_extension(filename: str) -> str:
    """파일 확장자 추출"""
    if '.' in filename:
        return '.' + filename.rsplit('.', 1)[1].lower()
    return ''


def is_supported_file(filename: str) -> bool:
    """지원하는 파일 형식인지 확인"""
    ext = get_file_extension(filename)
    return ext in SUPPORTED_EXTENSIONS


def extract_text_from_document(file_bytes: bytes, filename: str) -> str:
    """
    파일 형식에 따라 적절한 텍스트 추출 방법 사용

    Args:
        file_bytes: 파일 바이트 데이터
        filename: 파일명 (확장자 확인용)

    Returns:
        추출된 텍스트
    """
    ext = get_file_extension(filename)

    if ext == '.pdf':
        return extract_text_from_pdf(file_bytes)
    elif ext in ['.hwp', '.hwpx']:
        return extract_text_from_hwp(file_bytes)
    else:
        raise ValueError(f"지원하지 않는 파일 형식입니다: {ext}")


def validate_file(filename: str, file_size: int) -> Tuple[bool, str]:
    """
    파일 유효성 검사

    Returns:
        (유효 여부, 오류 메시지)
    """
    # 확장자 검사
    if not is_supported_file(filename):
        supported = ', '.join(SUPPORTED_EXTENSIONS)
        return False, f"지원하지 않는 파일 형식입니다. 지원 형식: {supported}"

    # 파일 크기 검사
    if file_size > MAX_FILE_SIZE:
        max_mb = MAX_FILE_SIZE // (1024 * 1024)
        return False, f"파일 크기가 {max_mb}MB를 초과합니다."

    return True, ""


def get_supported_formats_message() -> str:
    """지원 형식 안내 메시지"""
    return "PDF, HWP, HWPX 파일을 지원합니다 (최대 10MB)"
