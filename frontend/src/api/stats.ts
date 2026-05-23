import { api } from './client'
import type { StatsOut } from '../types'

export const getStats = () => api.get<StatsOut>('/stats/me')
