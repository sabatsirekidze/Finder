import { api } from './client'
import type { MessageOut } from '../types'

export const getMessages = (matchId: number) =>
  api.get<MessageOut[]>(`/matches/${matchId}/messages`)

export const sendMessage = (matchId: number, body: string) =>
  api.post<MessageOut>(`/matches/${matchId}/messages`, { body })
