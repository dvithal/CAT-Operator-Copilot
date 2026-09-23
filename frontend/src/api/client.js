import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

// ── Machines ─────────────────────────────────────────────────
export const getMachines       = ()    => api.get('/machines').then(r => r.data)
export const getMachine        = (id)  => api.get(`/machines/${id}`).then(r => r.data)
export const getPassport       = (id)  => api.get(`/machines/${id}/passport`).then(r => r.data)
export const getMachineQR      = (id)  => api.get(`/machines/${id}/qr`).then(r => r.data)
export const getMachineHistory = (id)  => api.get(`/machines/${id}/history`).then(r => r.data)

// ── Context ───────────────────────────────────────────────────
export const getContext        = (id)  => api.get(`/context/${id}/current`).then(r => r.data)

// ── Safety ───────────────────────────────────────────────────
export const getSafety         = (id)  => api.get(`/safety/${id}`).then(r => r.data)

// ── XAI ──────────────────────────────────────────────────────
export const getXAITask        = (tid) => api.get(`/xai/task/${tid}`).then(r => r.data)
export const getXAIBehavior    = (id)  => api.get(`/xai/behavior/${id}`).then(r => r.data)
export const getXAIMachine     = (id)  => api.get(`/xai/machine/${id}`).then(r => r.data)

// ── Weather ───────────────────────────────────────────────────
export const getWeather        = (id)  => api.get(`/weather/${id}`).then(r => r.data)
export const getWeatherRisk    = (id, eta) => api.get(`/weather/${id}/risk`, { params: { eta_min: eta } }).then(r => r.data)

// ── Tasks ─────────────────────────────────────────────────────
export const getTasks          = ()    => api.get('/tasks').then(r => r.data)
export const getTask           = (id)  => api.get(`/tasks/${id}`).then(r => r.data)
export const getTaskETA        = (id)  => api.get(`/tasks/${id}/eta`).then(r => r.data)
export const getCurrentTask    = (id)  => api.get(`/tasks/machine/${id}/current`).then(r => r.data)

// ── Incidents ────────────────────────────────────────────────
export const getIncidents      = (mid) => api.get('/incidents', { params: { machine_id: mid } }).then(r => r.data)
export const createIncident    = (data) => api.post('/incidents', data).then(r => r.data)

// ── Support ───────────────────────────────────────────────────
export const getSupportRequests = (mid) => api.get('/support', { params: { machine_id: mid } }).then(r => r.data)
export const createSupportRequest = (data) => api.post('/support', data).then(r => r.data)

// ── Reports ───────────────────────────────────────────────────
export const getShiftHandover  = (id)  => api.get(`/reports/shift/${id}`).then(r => r.data)
export const getDailyReport    = (id)  => api.get(`/reports/daily/${id}`).then(r => r.data)

// ── Training ─────────────────────────────────────────────────
export const getTraining       = (oid) => api.get(`/training/${oid}`).then(r => r.data)
export const getAllTraining     = ()    => api.get('/training').then(r => r.data)

// ── Copilot ───────────────────────────────────────────────────
export const sendCopilotMessage = (data) => api.post('/copilot/chat', data).then(r => r.data)

// ── Intelligence (new features) ──────────────────────────────
export const getWhatIf             = (id, tid) => api.get(`/intelligence/whatif/${id}`, { params: tid ? { task_id: tid } : {} }).then(r => r.data)
export const getModelTransparency  = ()         => api.get('/intelligence/transparency').then(r => r.data)
export const getFleetAudit         = ()         => api.get('/intelligence/fleet-audit').then(r => r.data)
export const getSafetyCounterfactual = (id)     => api.get(`/intelligence/safety-counterfactual/${id}`).then(r => r.data)
export const getTimeline           = (id)       => api.get(`/intelligence/timeline/${id}`).then(r => r.data)
export const submitFeedback        = (id, data) => api.post(`/intelligence/feedback/${id}`, data).then(r => r.data)
export const getFeedbackComparison = (id)       => api.get(`/intelligence/feedback/${id}/comparison`).then(r => r.data)
