import { api } from './client'
import type { DiscoveryBatch } from '../types'

export const getDiscoveryBatch = () => api.get<DiscoveryBatch>('/discovery/batch')
