'use client'

import { useState } from 'react'
import {
  Share2,
  Users,
  MessageSquare,
  History,
  Link,
  Copy,
  Check,
  Send,
  X,
  ChevronDown,
  ChevronUp,
  Clock,
  User
} from 'lucide-react'

interface Comment {
  id: string
  clause_number: number
  author_name: string
  content: string
  comment_type: string
  created_at: string
  resolved: boolean
}

interface Collaborator {
  id: string
  name: string
  email?: string
  role: string
}

interface Version {
  version_number: number
  created_at: string
  description: string
  changes: string[]
}

interface CollaborationPanelProps {
  shareId?: string
  analysisData: any
  onShare?: (shareData: any) => void
}

export function CollaborationPanel({
  shareId,
  analysisData,
  onShare
}: CollaborationPanelProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [activeTab, setActiveTab] = useState<'share' | 'comments' | 'versions'>('share')
  const [shareLink, setShareLink] = useState('')
  const [copied, setCopied] = useState(false)
  const [newComment, setNewComment] = useState('')
  const [selectedClause, setSelectedClause] = useState<number>(0)
  const [comments, setComments] = useState<Comment[]>([])
  const [collaborators, setCollaborators] = useState<Collaborator[]>([])
  const [versions, setVersions] = useState<Version[]>([])
  const [inviteEmail, setInviteEmail] = useState('')
  const [invitePermission, setInvitePermission] = useState('view')

  const handleCreateShare = async () => {
    try {
      const response = await fetch('/api/collaboration/share', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          analysis_data: analysisData,
          title: `${analysisData.contract_type} 분석`,
          expires_in_days: 30
        })
      })
      const data = await response.json()
      setShareLink(window.location.origin + data.access_link)
      if (onShare) onShare(data)
    } catch (error) {
      console.error('공유 생성 실패:', error)
    }
  }

  const handleCopyLink = () => {
    navigator.clipboard.writeText(shareLink)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleAddComment = async () => {
    if (!newComment.trim() || !shareId) return

    try {
      const response = await fetch('/api/collaboration/comment', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          share_id: shareId,
          clause_number: selectedClause,
          content: newComment,
          comment_type: 'general'
        })
      })
      const comment = await response.json()
      setComments([...comments, comment])
      setNewComment('')
    } catch (error) {
      console.error('코멘트 추가 실패:', error)
    }
  }

  const handleInvite = async () => {
    if (!inviteEmail.trim() || !shareId) return

    try {
      await fetch('/api/collaboration/collaborator', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          share_id: shareId,
          user_id: `user_${Date.now()}`,
          user_name: inviteEmail.split('@')[0],
          user_email: inviteEmail,
          permission: invitePermission
        })
      })
      setCollaborators([
        ...collaborators,
        {
          id: `user_${Date.now()}`,
          name: inviteEmail.split('@')[0],
          email: inviteEmail,
          role: invitePermission
        }
      ])
      setInviteEmail('')
    } catch (error) {
      console.error('초대 실패:', error)
    }
  }

  const getPermissionLabel = (permission: string) => {
    const labels: Record<string, string> = {
      view: '읽기',
      comment: '코멘트',
      edit: '편집',
      admin: '관리자'
    }
    return labels[permission] || permission
  }

  const getCommentTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      general: 'bg-gray-100 text-gray-700',
      suggestion: 'bg-blue-100 text-blue-700',
      question: 'bg-yellow-100 text-yellow-700',
      approval: 'bg-green-100 text-green-700',
      rejection: 'bg-red-100 text-red-700'
    }
    return colors[type] || colors.general
  }

  return (
    <div className="fixed bottom-4 right-4 z-50">
      {/* Toggle Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-4 py-3 bg-indigo-600 text-white rounded-full shadow-lg hover:bg-indigo-700 transition"
      >
        <Users className="w-5 h-5" />
        <span className="font-medium">협업</span>
        {isOpen ? <ChevronDown className="w-4 h-4" /> : <ChevronUp className="w-4 h-4" />}
      </button>

      {/* Panel */}
      {isOpen && (
        <div className="absolute bottom-16 right-0 w-96 bg-white rounded-2xl shadow-2xl border overflow-hidden">
          {/* Header */}
          <div className="bg-indigo-600 text-white px-4 py-3">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold">협업 도구</h3>
              <button onClick={() => setIsOpen(false)}>
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Tabs */}
          <div className="flex border-b">
            <button
              onClick={() => setActiveTab('share')}
              className={`flex-1 py-3 text-sm font-medium flex items-center justify-center gap-2 ${
                activeTab === 'share'
                  ? 'text-indigo-600 border-b-2 border-indigo-600'
                  : 'text-gray-500'
              }`}
            >
              <Share2 className="w-4 h-4" />
              공유
            </button>
            <button
              onClick={() => setActiveTab('comments')}
              className={`flex-1 py-3 text-sm font-medium flex items-center justify-center gap-2 ${
                activeTab === 'comments'
                  ? 'text-indigo-600 border-b-2 border-indigo-600'
                  : 'text-gray-500'
              }`}
            >
              <MessageSquare className="w-4 h-4" />
              코멘트
            </button>
            <button
              onClick={() => setActiveTab('versions')}
              className={`flex-1 py-3 text-sm font-medium flex items-center justify-center gap-2 ${
                activeTab === 'versions'
                  ? 'text-indigo-600 border-b-2 border-indigo-600'
                  : 'text-gray-500'
              }`}
            >
              <History className="w-4 h-4" />
              버전
            </button>
          </div>

          {/* Content */}
          <div className="p-4 max-h-96 overflow-y-auto">
            {/* Share Tab */}
            {activeTab === 'share' && (
              <div className="space-y-4">
                {!shareLink ? (
                  <button
                    onClick={handleCreateShare}
                    className="w-full py-3 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 transition flex items-center justify-center gap-2"
                  >
                    <Link className="w-5 h-5" />
                    공유 링크 생성
                  </button>
                ) : (
                  <div className="space-y-3">
                    <div className="flex items-center gap-2 p-3 bg-gray-50 rounded-lg">
                      <input
                        type="text"
                        value={shareLink}
                        readOnly
                        className="flex-1 bg-transparent text-sm truncate"
                      />
                      <button
                        onClick={handleCopyLink}
                        className="p-2 hover:bg-gray-200 rounded transition"
                      >
                        {copied ? (
                          <Check className="w-4 h-4 text-green-600" />
                        ) : (
                          <Copy className="w-4 h-4 text-gray-600" />
                        )}
                      </button>
                    </div>
                  </div>
                )}

                {/* Invite */}
                <div className="space-y-2">
                  <h4 className="font-medium text-sm">팀원 초대</h4>
                  <div className="flex gap-2">
                    <input
                      type="email"
                      value={inviteEmail}
                      onChange={(e) => setInviteEmail(e.target.value)}
                      placeholder="이메일 주소"
                      className="flex-1 px-3 py-2 border rounded-lg text-sm"
                    />
                    <select
                      value={invitePermission}
                      onChange={(e) => setInvitePermission(e.target.value)}
                      className="px-3 py-2 border rounded-lg text-sm"
                    >
                      <option value="view">읽기</option>
                      <option value="comment">코멘트</option>
                      <option value="edit">편집</option>
                    </select>
                    <button
                      onClick={handleInvite}
                      className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm"
                    >
                      초대
                    </button>
                  </div>
                </div>

                {/* Collaborators List */}
                {collaborators.length > 0 && (
                  <div className="space-y-2">
                    <h4 className="font-medium text-sm">협업자</h4>
                    <div className="space-y-2">
                      {collaborators.map((collab) => (
                        <div
                          key={collab.id}
                          className="flex items-center justify-between p-2 bg-gray-50 rounded-lg"
                        >
                          <div className="flex items-center gap-2">
                            <div className="w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center">
                              <User className="w-4 h-4 text-indigo-600" />
                            </div>
                            <div>
                              <p className="text-sm font-medium">{collab.name}</p>
                              <p className="text-xs text-gray-500">{collab.email}</p>
                            </div>
                          </div>
                          <span className="text-xs px-2 py-1 bg-gray-200 rounded">
                            {getPermissionLabel(collab.role)}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Comments Tab */}
            {activeTab === 'comments' && (
              <div className="space-y-4">
                {/* Comment Input */}
                <div className="space-y-2">
                  <select
                    value={selectedClause}
                    onChange={(e) => setSelectedClause(Number(e.target.value))}
                    className="w-full px-3 py-2 border rounded-lg text-sm"
                  >
                    <option value={0}>조항 선택...</option>
                    {analysisData?.clauses?.map((clause: any, idx: number) => (
                      <option key={idx} value={clause.number}>
                        {clause.title || `조항 ${clause.number}`}
                      </option>
                    ))}
                  </select>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={newComment}
                      onChange={(e) => setNewComment(e.target.value)}
                      placeholder="코멘트 입력..."
                      className="flex-1 px-3 py-2 border rounded-lg text-sm"
                      onKeyPress={(e) => e.key === 'Enter' && handleAddComment()}
                    />
                    <button
                      onClick={handleAddComment}
                      className="p-2 bg-indigo-600 text-white rounded-lg"
                    >
                      <Send className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                {/* Comments List */}
                <div className="space-y-3">
                  {comments.length === 0 ? (
                    <p className="text-center text-gray-500 text-sm py-4">
                      아직 코멘트가 없습니다
                    </p>
                  ) : (
                    comments.map((comment) => (
                      <div
                        key={comment.id}
                        className={`p-3 rounded-lg ${
                          comment.resolved ? 'bg-gray-100 opacity-60' : 'bg-white border'
                        }`}
                      >
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex items-center gap-2">
                            <span className="font-medium text-sm">{comment.author_name}</span>
                            <span className={`text-xs px-2 py-0.5 rounded ${getCommentTypeColor(comment.comment_type)}`}>
                              {comment.comment_type}
                            </span>
                          </div>
                          <span className="text-xs text-gray-500">
                            조항 {comment.clause_number}
                          </span>
                        </div>
                        <p className="text-sm text-gray-700">{comment.content}</p>
                        <div className="flex items-center gap-2 mt-2 text-xs text-gray-500">
                          <Clock className="w-3 h-3" />
                          {new Date(comment.created_at).toLocaleString('ko-KR')}
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            )}

            {/* Versions Tab */}
            {activeTab === 'versions' && (
              <div className="space-y-3">
                {versions.length === 0 ? (
                  <div className="text-center py-4">
                    <History className="w-10 h-10 text-gray-300 mx-auto mb-2" />
                    <p className="text-gray-500 text-sm">버전 기록이 없습니다</p>
                    <p className="text-gray-400 text-xs">수정사항이 생기면 버전이 생성됩니다</p>
                  </div>
                ) : (
                  versions.map((version) => (
                    <div
                      key={version.version_number}
                      className="p-3 border rounded-lg hover:bg-gray-50 transition cursor-pointer"
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-medium">v{version.version_number}</span>
                        <span className="text-xs text-gray-500">
                          {new Date(version.created_at).toLocaleString('ko-KR')}
                        </span>
                      </div>
                      <p className="text-sm text-gray-700">{version.description}</p>
                      {version.changes.length > 0 && (
                        <ul className="mt-2 space-y-1">
                          {version.changes.slice(0, 3).map((change, idx) => (
                            <li key={idx} className="text-xs text-gray-500 flex items-center gap-1">
                              <span className="w-1 h-1 bg-gray-400 rounded-full" />
                              {change}
                            </li>
                          ))}
                        </ul>
                      )}
                    </div>
                  ))
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
