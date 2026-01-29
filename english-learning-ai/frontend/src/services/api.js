import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const generateExercise = async (data) => {
  const response = await api.post('/api/exercises/generate', data)
  return response.data
}

export const evaluateSpeaking = async (data) => {
  const response = await api.post('/api/speaking/evaluate', data)
  return response.data
}

export const generateAudio = async (text, language = 'en-US') => {
  const response = await api.post('/api/tts/generate', null, {
    params: { text, language }
  })
  return response.data
}

export default api
