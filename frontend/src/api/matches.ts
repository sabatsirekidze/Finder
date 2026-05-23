import { api } from './client'
import type { MatchOut } from '../types'

export const getMatches = () => api.get<MatchOut[]>('/matches')
