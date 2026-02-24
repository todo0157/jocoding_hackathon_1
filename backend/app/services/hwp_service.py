"""
HWP 파일 처리 서비스
한국 시장 진입을 위한 한글 문서(.hwp, .hwpx) 지원
"""
import re
import zlib
import zipfile
import xml.etree.ElementTree as ET
from io import BytesIO
from typing import Optional

# HWP5 형식 지원을 위한 라이브러리
try:
    import olefile
    HWP5_AVAILABLE = True
except ImportError:
    HWP5_AVAILABLE = False

# OCR 지원 (스캔 문서용)
try:
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False


def extract_text_from_hwp(file_bytes: bytes) -> str:
    """HWP 파일에서 텍스트 추출 (hwp, hwpx 모두 지원)"""

    # 먼저 HWPX (ZIP 기반) 형식인지 확인
    if _is_hwpx(file_bytes):
        return _extract_from_hwpx(file_bytes)

    # HWP5 (OLE 기반) 형식 처리
    if HWP5_AVAILABLE:
        return _extract_from_hwp5(file_bytes)

    raise ValueError(
        "HWP 파일 처리를 위해 olefile 패키지가 필요합니다. "
        "pip install olefile 명령으로 설치해주세요."
    )


def _is_hwpx(file_bytes: bytes) -> bool:
    """HWPX (ZIP 기반) 형식인지 확인"""
    return file_bytes[:4] == b'PK\x03\x04'


def _extract_from_hwpx(file_bytes: bytes) -> str:
    """HWPX (ZIP 기반 XML) 파일에서 텍스트 추출"""
    text_parts = []

    try:
        with zipfile.ZipFile(BytesIO(file_bytes), 'r') as zf:
            # HWPX 내의 섹션 파일들에서 텍스트 추출
            for name in zf.namelist():
                if name.startswith('Contents/section') and name.endswith('.xml'):
                    xml_content = zf.read(name)
                    text = _parse_hwpx_section(xml_content)
                    if text:
                        text_parts.append(text)
    except zipfile.BadZipFile:
        raise ValueError("유효하지 않은 HWPX 파일입니다.")

    return '\n'.join(text_parts)


def _parse_hwpx_section(xml_content: bytes) -> str:
    """HWPX 섹션 XML에서 텍스트 파싱"""
    try:
        # 네임스페이스 제거 (파싱 단순화)
        xml_str = xml_content.decode('utf-8')
        xml_str = re.sub(r'xmlns[^"]*"[^"]*"', '', xml_str)

        root = ET.fromstring(xml_str)

        # 모든 텍스트 노드 추출
        text_parts = []
        for elem in root.iter():
            if elem.text and elem.text.strip():
                text_parts.append(elem.text.strip())

        return ' '.join(text_parts)
    except ET.ParseError:
        return ""


def _extract_from_hwp5(file_bytes: bytes) -> str:
    """HWP5 (OLE Compound) 파일에서 텍스트 추출"""
    if not HWP5_AVAILABLE:
        raise ValueError("olefile 패키지가 필요합니다.")

    try:
        ole = olefile.OleFileIO(BytesIO(file_bytes))

        # 압축 여부 확인
        is_compressed = False
        if ole.exists('FileHeader'):
            header = ole.openstream('FileHeader').read()
            if len(header) > 36:
                flags = header[36]
                is_compressed = (flags & 0x01) != 0

        # HWP5 본문 스트림 찾기
        text_parts = []

        # 본문 섹션 추출
        if ole.exists('BodyText/Section0'):
            section_idx = 0
            while ole.exists(f'BodyText/Section{section_idx}'):
                stream = ole.openstream(f'BodyText/Section{section_idx}')
                data = stream.read()

                # 압축된 경우 해제
                if is_compressed:
                    try:
                        data = zlib.decompress(data, -15)
                    except zlib.error:
                        pass  # 이미 압축 해제되어 있거나 다른 형식

                # HWP5 텍스트 디코딩
                text = _decode_hwp5_section(data)
                if text:
                    text_parts.append(text)

                section_idx += 1

        ole.close()
        return '\n'.join(text_parts)

    except Exception as e:
        raise ValueError(f"HWP5 파일 파싱 오류: {str(e)}")


def _decode_hwp5_section(data: bytes) -> str:
    """HWP5 섹션 데이터에서 텍스트 디코딩"""
    # HWP5 레코드 구조 파싱
    text_chars = []
    pos = 0

    while pos < len(data):
        try:
            # 레코드 헤더 (4바이트)
            if pos + 4 > len(data):
                break

            header = int.from_bytes(data[pos:pos+4], 'little')
            tag_id = header & 0x3FF
            level = (header >> 10) & 0x3FF
            size = (header >> 20) & 0xFFF

            pos += 4

            # 확장 크기 처리
            if size == 0xFFF:
                if pos + 4 > len(data):
                    break
                size = int.from_bytes(data[pos:pos+4], 'little')
                pos += 4

            # HWPTAG_PARA_TEXT (태그 ID: 67) 처리
            if tag_id == 67 and pos + size <= len(data):
                record_data = data[pos:pos+size]
                # UTF-16LE로 디코딩
                try:
                    # 제어 문자 필터링
                    text = ""
                    i = 0
                    while i < len(record_data) - 1:
                        char_code = int.from_bytes(record_data[i:i+2], 'little')
                        if char_code >= 32 and char_code < 0xD800:
                            text += chr(char_code)
                        elif char_code in [0x0A, 0x0D]:  # 줄바꿈
                            text += '\n'
                        i += 2
                    text_chars.append(text)
                except:
                    pass

            pos += size

        except Exception:
            break

    return ''.join(text_chars)


def extract_text_with_ocr(image_bytes: bytes) -> str:
    """OCR을 사용하여 이미지/스캔 문서에서 텍스트 추출"""
    if not OCR_AVAILABLE:
        raise ValueError(
            "OCR 기능을 위해 pytesseract와 Pillow가 필요합니다. "
            "pip install pytesseract Pillow 명령으로 설치해주세요."
        )

    try:
        image = Image.open(BytesIO(image_bytes))
        # 한국어 OCR
        text = pytesseract.image_to_string(image, lang='kor+eng')
        return text.strip()
    except Exception as e:
        raise ValueError(f"OCR 처리 오류: {str(e)}")


def is_hwp_file(filename: str) -> bool:
    """HWP 파일 확장자 확인"""
    lower_name = filename.lower()
    return lower_name.endswith('.hwp') or lower_name.endswith('.hwpx')


def get_supported_extensions() -> list[str]:
    """지원하는 파일 확장자 목록"""
    return ['.pdf', '.hwp', '.hwpx']
