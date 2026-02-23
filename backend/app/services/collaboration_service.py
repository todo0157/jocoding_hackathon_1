"""
협업 기능 서비스
- 분석 결과 공유
- 코멘트/주석
- 버전 관리
- 팀 협업
"""
import uuid
import hashlib
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
import json


class CommentType(Enum):
    """코멘트 유형"""
    GENERAL = "general"
    SUGGESTION = "suggestion"
    QUESTION = "question"
    APPROVAL = "approval"
    REJECTION = "rejection"


class SharePermission(Enum):
    """공유 권한"""
    VIEW = "view"  # 읽기 전용
    COMMENT = "comment"  # 코멘트 가능
    EDIT = "edit"  # 수정 가능
    ADMIN = "admin"  # 관리자


@dataclass
class Comment:
    """코멘트"""
    id: str
    clause_number: int
    author_id: str
    author_name: str
    content: str
    comment_type: CommentType
    created_at: str
    updated_at: Optional[str] = None
    resolved: bool = False
    resolved_by: Optional[str] = None
    parent_id: Optional[str] = None  # 답글인 경우
    mentions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["comment_type"] = self.comment_type.value
        return data


@dataclass
class AnalysisVersion:
    """분석 버전"""
    version_id: str
    version_number: int
    created_at: str
    created_by: str
    description: str
    analysis_data: Dict[str, Any]
    changes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SharedAnalysis:
    """공유된 분석"""
    share_id: str
    analysis_id: str
    owner_id: str
    owner_name: str
    title: str
    contract_type: str
    created_at: str
    expires_at: Optional[str]
    access_link: str
    permissions: Dict[str, SharePermission]  # user_id -> permission
    current_version: int
    versions: List[AnalysisVersion]
    comments: List[Comment]
    collaborators: List[Dict[str, str]]  # [{id, name, email}]

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["permissions"] = {k: v.value for k, v in self.permissions.items()}
        data["versions"] = [v.to_dict() for v in self.versions]
        data["comments"] = [c.to_dict() for c in self.comments]
        return data


class CollaborationService:
    """협업 서비스"""

    def __init__(self):
        # 인메모리 저장소 (프로덕션에서는 DB 사용)
        self._shared_analyses: Dict[str, SharedAnalysis] = {}
        self._user_analyses: Dict[str, List[str]] = {}  # user_id -> [share_id]

    def create_shared_analysis(
        self,
        analysis_data: Dict[str, Any],
        owner_id: str,
        owner_name: str,
        title: Optional[str] = None,
        expires_in_days: Optional[int] = None
    ) -> SharedAnalysis:
        """
        분석 결과 공유 생성

        Args:
            analysis_data: 분석 결과 데이터
            owner_id: 생성자 ID
            owner_name: 생성자 이름
            title: 공유 제목
            expires_in_days: 만료 기간 (일)
        """
        share_id = self._generate_id()
        analysis_id = self._generate_id()
        now = datetime.now().isoformat()

        expires_at = None
        if expires_in_days:
            expires_at = (datetime.now() + timedelta(days=expires_in_days)).isoformat()

        # 초기 버전 생성
        initial_version = AnalysisVersion(
            version_id=self._generate_id(),
            version_number=1,
            created_at=now,
            created_by=owner_id,
            description="초기 분석",
            analysis_data=analysis_data,
            changes=["최초 분석 생성"]
        )

        shared = SharedAnalysis(
            share_id=share_id,
            analysis_id=analysis_id,
            owner_id=owner_id,
            owner_name=owner_name,
            title=title or f"{analysis_data.get('contract_type', '계약서')} 분석",
            contract_type=analysis_data.get("contract_type", "일반계약서"),
            created_at=now,
            expires_at=expires_at,
            access_link=f"/shared/{share_id}",
            permissions={owner_id: SharePermission.ADMIN},
            current_version=1,
            versions=[initial_version],
            comments=[],
            collaborators=[{"id": owner_id, "name": owner_name, "role": "owner"}]
        )

        self._shared_analyses[share_id] = shared

        # 사용자 분석 목록에 추가
        if owner_id not in self._user_analyses:
            self._user_analyses[owner_id] = []
        self._user_analyses[owner_id].append(share_id)

        return shared

    def get_shared_analysis(self, share_id: str) -> Optional[SharedAnalysis]:
        """공유된 분석 조회"""
        shared = self._shared_analyses.get(share_id)

        if shared:
            # 만료 확인
            if shared.expires_at:
                if datetime.fromisoformat(shared.expires_at) < datetime.now():
                    return None

        return shared

    def add_collaborator(
        self,
        share_id: str,
        user_id: str,
        user_name: str,
        user_email: str,
        permission: SharePermission,
        added_by: str
    ) -> bool:
        """
        협업자 추가

        Args:
            share_id: 공유 ID
            user_id: 추가할 사용자 ID
            user_name: 사용자 이름
            user_email: 사용자 이메일
            permission: 권한
            added_by: 추가하는 사용자 ID
        """
        shared = self._shared_analyses.get(share_id)
        if not shared:
            return False

        # 권한 확인 (ADMIN만 추가 가능)
        if shared.permissions.get(added_by) != SharePermission.ADMIN:
            return False

        # 협업자 추가
        shared.permissions[user_id] = permission
        shared.collaborators.append({
            "id": user_id,
            "name": user_name,
            "email": user_email,
            "role": permission.value
        })

        # 사용자 분석 목록에 추가
        if user_id not in self._user_analyses:
            self._user_analyses[user_id] = []
        if share_id not in self._user_analyses[user_id]:
            self._user_analyses[user_id].append(share_id)

        return True

    def add_comment(
        self,
        share_id: str,
        clause_number: int,
        author_id: str,
        author_name: str,
        content: str,
        comment_type: CommentType = CommentType.GENERAL,
        parent_id: Optional[str] = None,
        mentions: Optional[List[str]] = None
    ) -> Optional[Comment]:
        """
        코멘트 추가

        Args:
            share_id: 공유 ID
            clause_number: 조항 번호
            author_id: 작성자 ID
            author_name: 작성자 이름
            content: 코멘트 내용
            comment_type: 코멘트 유형
            parent_id: 부모 코멘트 ID (답글인 경우)
            mentions: 멘션된 사용자 ID 목록
        """
        shared = self._shared_analyses.get(share_id)
        if not shared:
            return None

        # 권한 확인
        permission = shared.permissions.get(author_id)
        if permission not in [SharePermission.COMMENT, SharePermission.EDIT, SharePermission.ADMIN]:
            return None

        comment = Comment(
            id=self._generate_id(),
            clause_number=clause_number,
            author_id=author_id,
            author_name=author_name,
            content=content,
            comment_type=comment_type,
            created_at=datetime.now().isoformat(),
            parent_id=parent_id,
            mentions=mentions or []
        )

        shared.comments.append(comment)
        return comment

    def resolve_comment(
        self,
        share_id: str,
        comment_id: str,
        resolved_by: str
    ) -> bool:
        """코멘트 해결 처리"""
        shared = self._shared_analyses.get(share_id)
        if not shared:
            return False

        for comment in shared.comments:
            if comment.id == comment_id:
                comment.resolved = True
                comment.resolved_by = resolved_by
                return True

        return False

    def create_new_version(
        self,
        share_id: str,
        analysis_data: Dict[str, Any],
        created_by: str,
        description: str,
        changes: List[str]
    ) -> Optional[AnalysisVersion]:
        """
        새 버전 생성

        Args:
            share_id: 공유 ID
            analysis_data: 새 분석 데이터
            created_by: 생성자 ID
            description: 버전 설명
            changes: 변경 내역
        """
        shared = self._shared_analyses.get(share_id)
        if not shared:
            return None

        # 권한 확인
        permission = shared.permissions.get(created_by)
        if permission not in [SharePermission.EDIT, SharePermission.ADMIN]:
            return None

        new_version_number = shared.current_version + 1
        version = AnalysisVersion(
            version_id=self._generate_id(),
            version_number=new_version_number,
            created_at=datetime.now().isoformat(),
            created_by=created_by,
            description=description,
            analysis_data=analysis_data,
            changes=changes
        )

        shared.versions.append(version)
        shared.current_version = new_version_number

        return version

    def get_version(
        self,
        share_id: str,
        version_number: int
    ) -> Optional[AnalysisVersion]:
        """특정 버전 조회"""
        shared = self._shared_analyses.get(share_id)
        if not shared:
            return None

        for version in shared.versions:
            if version.version_number == version_number:
                return version

        return None

    def get_version_diff(
        self,
        share_id: str,
        version1: int,
        version2: int
    ) -> Optional[Dict[str, Any]]:
        """두 버전 비교"""
        v1 = self.get_version(share_id, version1)
        v2 = self.get_version(share_id, version2)

        if not v1 or not v2:
            return None

        return {
            "version1": version1,
            "version2": version2,
            "v1_created_at": v1.created_at,
            "v2_created_at": v2.created_at,
            "v2_changes": v2.changes,
            "clause_changes": self._compare_clauses(
                v1.analysis_data.get("clauses", []),
                v2.analysis_data.get("clauses", [])
            )
        }

    def get_comments_by_clause(
        self,
        share_id: str,
        clause_number: int
    ) -> List[Comment]:
        """특정 조항의 코멘트 조회"""
        shared = self._shared_analyses.get(share_id)
        if not shared:
            return []

        return [c for c in shared.comments if c.clause_number == clause_number]

    def get_user_analyses(self, user_id: str) -> List[SharedAnalysis]:
        """사용자의 분석 목록 조회"""
        share_ids = self._user_analyses.get(user_id, [])
        return [
            self._shared_analyses[sid]
            for sid in share_ids
            if sid in self._shared_analyses
        ]

    def update_permissions(
        self,
        share_id: str,
        user_id: str,
        new_permission: SharePermission,
        updated_by: str
    ) -> bool:
        """권한 변경"""
        shared = self._shared_analyses.get(share_id)
        if not shared:
            return False

        # ADMIN만 권한 변경 가능
        if shared.permissions.get(updated_by) != SharePermission.ADMIN:
            return False

        # 소유자 권한은 변경 불가
        if user_id == shared.owner_id:
            return False

        if user_id in shared.permissions:
            shared.permissions[user_id] = new_permission
            # collaborators 업데이트
            for collab in shared.collaborators:
                if collab["id"] == user_id:
                    collab["role"] = new_permission.value
                    break
            return True

        return False

    def remove_collaborator(
        self,
        share_id: str,
        user_id: str,
        removed_by: str
    ) -> bool:
        """협업자 제거"""
        shared = self._shared_analyses.get(share_id)
        if not shared:
            return False

        # ADMIN만 제거 가능
        if shared.permissions.get(removed_by) != SharePermission.ADMIN:
            return False

        # 소유자는 제거 불가
        if user_id == shared.owner_id:
            return False

        if user_id in shared.permissions:
            del shared.permissions[user_id]
            shared.collaborators = [
                c for c in shared.collaborators if c["id"] != user_id
            ]
            # 사용자 목록에서도 제거
            if user_id in self._user_analyses:
                self._user_analyses[user_id] = [
                    sid for sid in self._user_analyses[user_id]
                    if sid != share_id
                ]
            return True

        return False

    def generate_share_link(
        self,
        share_id: str,
        permission: SharePermission = SharePermission.VIEW,
        expires_in_hours: int = 24
    ) -> Optional[Dict[str, str]]:
        """공유 링크 생성"""
        shared = self._shared_analyses.get(share_id)
        if not shared:
            return None

        # 임시 토큰 생성
        token = hashlib.sha256(
            f"{share_id}-{datetime.now().isoformat()}-{uuid.uuid4()}".encode()
        ).hexdigest()[:32]

        expires_at = (datetime.now() + timedelta(hours=expires_in_hours)).isoformat()

        return {
            "link": f"/shared/{share_id}?token={token}",
            "token": token,
            "permission": permission.value,
            "expires_at": expires_at
        }

    def _generate_id(self) -> str:
        """고유 ID 생성"""
        return str(uuid.uuid4())[:8]

    def _compare_clauses(
        self,
        clauses1: List[Dict],
        clauses2: List[Dict]
    ) -> List[Dict[str, Any]]:
        """조항 비교"""
        changes = []

        # 간단한 비교 (조항 번호 기준)
        clauses1_dict = {c.get("number"): c for c in clauses1}
        clauses2_dict = {c.get("number"): c for c in clauses2}

        all_numbers = set(clauses1_dict.keys()) | set(clauses2_dict.keys())

        for num in sorted(all_numbers):
            c1 = clauses1_dict.get(num)
            c2 = clauses2_dict.get(num)

            if c1 and not c2:
                changes.append({"number": num, "type": "removed"})
            elif c2 and not c1:
                changes.append({"number": num, "type": "added"})
            elif c1 and c2:
                # 내용 비교
                if c1.get("content") != c2.get("content"):
                    changes.append({"number": num, "type": "modified"})
                # 대안 추가 여부
                if not c1.get("alternative") and c2.get("alternative"):
                    changes.append({"number": num, "type": "alternative_added"})

        return changes


# 싱글톤 인스턴스
_collaboration_service: Optional[CollaborationService] = None


def get_collaboration_service() -> CollaborationService:
    """협업 서비스 인스턴스 반환"""
    global _collaboration_service
    if _collaboration_service is None:
        _collaboration_service = CollaborationService()
    return _collaboration_service
