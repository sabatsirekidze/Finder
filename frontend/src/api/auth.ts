import { api } from './client'
import type { TokenResponse } from '../types'

export const register = (email: string, password: string) =>
  api.post<TokenResponse>('/auth/register', { email, password })

export const login = (email: string, password: string) =>
  api.post<TokenResponse>('/auth/login', { email, password })
