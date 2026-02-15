import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_URL,
  timeout: 120000, // 2분 타임아웃 (분석 시간 고려)
})

export async function analyzeContract(file: File) {
  const formData = new FormData()
  formData.append('file', file)

  try {
    const response = await api.post('/api/v1/analyze', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  } catch (error: any) {
    if (error.response) {
      throw new Error(error.response.data.detail || '서버 오류가 발생했습니다.')
    }
    throw new Error('네트워크 오류가 발생했습니다.')
  }
}

export async function healthCheck() {
  const response = await api.get('/api/v1/health')
  return response.data
}

// 채팅 관련 타입
export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

export interface ContractContext {
  contract_type?: string
  high_risk_clauses?: any[]
  summary?: string
}

export interface CitedCase {
  case_number: string
  summary: string
  relevance: string
}

export interface ChatResponse {
  reply: string
  cited_cases: CitedCase[]
}

export async function sendChatMessage(
  message: string,
  conversationHistory: ChatMessage[] = [],
  contractContext?: ContractContext
): Promise<ChatResponse> {
  try {
    const response = await api.post('/api/v1/chat', {
      message,
      conversation_history: conversationHistory,
      contract_context: contractContext
    })
    return response.data
  } catch (error: any) {
    if (error.response) {
      throw new Error(error.response.data.detail || '서버 오류가 발생했습니다.')
    }
    throw new Error('네트워크 오류가 발생했습니다.')
  }
}

/**
 * 수정된 계약서 다운로드
 */
export async function downloadSafeContract(analysisResult: any): Promise<void> {
  try {
    const response = await api.post(
      '/api/v1/generate-safe-contract',
      {
        contract_type: analysisResult.contract_type,
        clauses: analysisResult.clauses,
        apply_alternatives: true
      },
      {
        responseType: 'blob'
      }
    )

    // Blob에서 파일 다운로드 트리거
    const blob = new Blob([response.data], {
      type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${analysisResult.contract_type}_수정본.docx`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (error: any) {
    if (error.response) {
      throw new Error(error.response.data.detail || '파일 생성 중 오류가 발생했습니다.')
    }
    throw new Error('네트워크 오류가 발생했습니다.')
  }
}
