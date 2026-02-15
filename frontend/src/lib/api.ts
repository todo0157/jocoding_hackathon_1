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
