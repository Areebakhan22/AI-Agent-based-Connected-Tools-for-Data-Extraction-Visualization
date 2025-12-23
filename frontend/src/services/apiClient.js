import axios from 'axios'

const API_BASE_URL = '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

export const apiClient = {
  async getDiagrams() {
    try {
      const response = await api.get('/diagrams')
      return response
    } catch (error) {
      console.error('Error fetching diagrams:', error)
      throw error
    }
  },

  async getDiagram(diagramId) {
    try {
      const response = await api.get(`/diagram/${diagramId}`)
      return response
    } catch (error) {
      console.error('Error fetching diagram:', error)
      throw error
    }
  },

  async updateDiagram(diagramId, data) {
    try {
      const response = await api.post(`/diagram/${diagramId}`, data)
      return response
    } catch (error) {
      console.error('Error updating diagram:', error)
      throw error
    }
  }
}

