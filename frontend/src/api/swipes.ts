import { api } from './client'
import type { SwipeDirection, SwipeResult } from '../types'

export const postSwipe = (target_user_id: number, direction: SwipeDirection) =>
  api.post<SwipeResult>('/swipes', { target_user_id, direction })
