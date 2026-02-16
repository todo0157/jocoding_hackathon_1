"""PDF 분석 리포트 생성 서비스"""

import os
from datetime import datetime
from io import BytesIO
from typing import List, Dict, Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def register_korean_font():
    """한글 폰트 등록 (맑은 고딕 사용)"""
    font_paths = [
        "C:/Windows/Fonts/malgun.ttf",      # Windows 맑은 고딕
        "C:/Windows/Fonts/NanumGothic.ttf", # 나눔고딕
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",  # Linux
        "/System/Library/Fonts/AppleGothic.ttf",  # macOS
    ]

    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont('Korean', font_path))
                return 'Korean'
            except Exception:
                continue

    # 폰트를 찾지 못한 경우 기본 폰트 사용
    return 'Helvetica'


def get_styles(font_name: str) -> dict:
    """PDF 스타일 정의"""
    styles = getSampleStyleSheet()

    # 제목 스타일
    styles.add(ParagraphStyle(
        name='KoreanTitle',
        fontName=font_name,
        fontSize=24,
        leading=30,
        alignment=1,  # center
        spaceAfter=10
    ))

    # 부제 스타일
    styles.add(ParagraphStyle(
        name='KoreanSubtitle',
        fontName=font_name,
        fontSize=14,
        leading=18,
        alignment=1,
        textColor=colors.gray,
        spaceAfter=20
    ))

    # 섹션 헤더 스타일
    styles.add(ParagraphStyle(
        name='SectionHeader',
        fontName=font_name,
        fontSize=16,
        leading=20,
        spaceBefore=15,
        spaceAfter=10,
        textColor=colors.HexColor('#1a365d')
    ))

    # 본문 스타일
    styles.add(ParagraphStyle(
        name='KoreanBody',
        fontName=font_name,
        fontSize=10,
        leading=14,
        spaceAfter=6
    ))

    # 작은 글씨 스타일
    styles.add(ParagraphStyle(
        name='KoreanSmall',
        fontName=font_name,
        fontSize=8,
        leading=10,
        textColor=colors.gray
    ))

    # 위험 조항 스타일
    styles.add(ParagraphStyle(
        name='HighRisk',
        fontName=font_name,
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#c53030')
    ))

    # 안전 조항 스타일
    styles.add(ParagraphStyle(
        name='Safe',
        fontName=font_name,
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#2f855a')
    ))

    return styles


def get_risk_label(score: int) -> tuple:
    """위험도 점수에 따른 라벨과 색상 반환"""
    if score >= 8:
        return ('위험', colors.HexColor('#c53030'), colors.HexColor('#fed7d7'))
    elif score >= 6:
        return ('주의', colors.HexColor('#c05621'), colors.HexColor('#feebc8'))
    elif score >= 4:
        return ('보통', colors.HexColor('#b7791f'), colors.HexColor('#fefcbf'))
    else:
        return ('안전', colors.HexColor('#2f855a'), colors.HexColor('#c6f6d5'))


def get_risk_level_korean(level: str) -> str:
    """위험 수준 한글 변환"""
    mapping = {
        'critical': '심각 (Critical)',
        'high': '높음 (High)',
        'medium': '중간 (Medium)',
        'low': '낮음 (Low)'
    }
    return mapping.get(level, level)


def generate_analysis_report(
    contract_type: str,
    clauses: List[Dict[str, Any]],
    summary: str,
    total_clauses: int,
    high_risk_clauses: int,
    average_risk_score: float,
    overall_risk_level: str
) -> BytesIO:
    """
    계약서 분석 결과를 PDF 리포트로 생성

    Args:
        contract_type: 계약서 유형
        clauses: 분석된 조항 리스트
        summary: 분석 요약
        total_clauses: 총 조항 수
        high_risk_clauses: 고위험 조항 수
        average_risk_score: 평균 위험도
        overall_risk_level: 전체 위험 수준

    Returns:
        BytesIO: PDF 파일 바이트 스트림
    """
    buffer = BytesIO()

    # 폰트 등록
    font_name = register_korean_font()
    styles = get_styles(font_name)

    # PDF 문서 생성
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=20*mm
    )

    story = []

    # ===== 표지 =====
    story.append(Spacer(1, 30*mm))
    story.append(Paragraph("ContractPilot", styles['KoreanTitle']))
    story.append(Paragraph("AI 계약서 분석 리포트", styles['KoreanSubtitle']))
    story.append(Spacer(1, 20*mm))

    # 계약서 정보 테이블
    now = datetime.now().strftime("%Y년 %m월 %d일 %H:%M")
    info_data = [
        ['계약서 유형', contract_type],
        ['분석 일시', now],
        ['전체 위험 수준', get_risk_level_korean(overall_risk_level)]
    ]

    info_table = Table(info_data, colWidths=[60*mm, 100*mm])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.gray),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(info_table)

    story.append(PageBreak())

    # ===== 분석 요약 =====
    story.append(Paragraph("분석 요약", styles['SectionHeader']))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e2e8f0')))
    story.append(Spacer(1, 5*mm))

    # 요약 통계 테이블
    summary_data = [
        ['총 조항 수', f'{total_clauses}개'],
        ['고위험 조항', f'{high_risk_clauses}개'],
        ['평균 위험도', f'{average_risk_score}/10'],
    ]

    summary_table = Table(summary_data, colWidths=[50*mm, 40*mm])
    summary_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f7fafc')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 5*mm))

    # 요약 텍스트
    story.append(Paragraph(summary, styles['KoreanBody']))
    story.append(Spacer(1, 10*mm))

    # ===== 조항별 분석 결과 =====
    story.append(Paragraph("조항별 분석 결과", styles['SectionHeader']))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e2e8f0')))
    story.append(Spacer(1, 5*mm))

    for clause in clauses:
        analysis = clause.get('analysis', {})
        if isinstance(analysis, dict):
            risk_score = analysis.get('risk_score', 0)
            clause_summary = analysis.get('summary', '')
            issues = analysis.get('issues', [])
        else:
            risk_score = 0
            clause_summary = ''
            issues = []

        label, text_color, bg_color = get_risk_label(risk_score)
        alternative = clause.get('alternative', '')
        similar_cases = clause.get('similar_cases', [])

        # 조항 헤더
        title = clause.get('title', f"제{clause.get('number', '')}조")
        header_text = f"[{label}] {title} (위험도: {risk_score}/10)"

        header_style = ParagraphStyle(
            name='ClauseHeader',
            fontName=font_name,
            fontSize=12,
            leading=16,
            textColor=text_color,
            spaceBefore=10,
            spaceAfter=5
        )
        story.append(Paragraph(header_text, header_style))

        # 조항 내용 박스
        content = clause.get('content', '')
        if len(content) > 300:
            content = content[:300] + '...'

        content_data = [[Paragraph(f"<b>원문:</b> {content}", styles['KoreanBody'])]]
        content_table = Table(content_data, colWidths=[160*mm])
        content_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f7fafc')),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(content_table)

        # 분석 결과
        if clause_summary:
            story.append(Paragraph(f"<b>분석:</b> {clause_summary}", styles['KoreanBody']))

        # 문제점
        if issues:
            issues_text = "<b>문제점:</b><br/>" + "<br/>".join([f"  - {issue}" for issue in issues])
            story.append(Paragraph(issues_text, styles['KoreanBody']))

        # 수정 제안
        if alternative:
            alt_data = [[Paragraph(f"<b>수정 제안:</b><br/>{alternative}", styles['KoreanBody'])]]
            alt_table = Table(alt_data, colWidths=[160*mm])
            alt_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#c6f6d5')),
                ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#9ae6b4')),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            story.append(alt_table)

        # 관련 판례
        if similar_cases:
            cases_text = "<b>관련 판례:</b><br/>"
            for case in similar_cases:
                case_num = case.get('case_number', '')
                case_summary = case.get('summary', '')
                cases_text += f"  - {case_num}: {case_summary}<br/>"
            story.append(Paragraph(cases_text, styles['KoreanSmall']))

        story.append(Spacer(1, 5*mm))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#e2e8f0')))

    # ===== 면책 조항 =====
    story.append(Spacer(1, 15*mm))
    story.append(Paragraph("면책 조항", styles['SectionHeader']))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e2e8f0')))
    story.append(Spacer(1, 3*mm))

    disclaimer_text = """
    본 리포트는 ContractPilot AI가 생성한 참고 자료입니다.
    이 분석은 법률 자문을 대체하지 않으며, 최종 판단은 사용자의 몫입니다.
    중요한 계약 체결 전에는 반드시 법률 전문가와 상담하시기 바랍니다.

    AI 분석의 정확도는 100%가 아니며, 계약서의 특수한 상황이나
    맥락에 따라 다른 해석이 가능할 수 있습니다.
    """

    disclaimer_style = ParagraphStyle(
        name='Disclaimer',
        fontName=font_name,
        fontSize=9,
        leading=13,
        textColor=colors.gray,
        alignment=0
    )
    story.append(Paragraph(disclaimer_text, disclaimer_style))

    # PDF 빌드
    doc.build(story)
    buffer.seek(0)

    return buffer
