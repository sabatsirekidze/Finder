import { api } from './client'
import type {
  ProfileOut,
  ProfileUpdateRequest,
  DatingPreferencesOut,
  DatingPreferencesUpdateRequest,
} from '../types'

export const getMyProfile = () => api.get<ProfileOut>('/profiles/me')

export const updateMyProfile = (body: ProfileUpdateRequest) =>
  api.patch<ProfileOut>('/profiles/me', body)

export const getMyPreferences = () =>
  api.get<DatingPreferencesOut>('/profiles/me/preferences')

export const updateMyPreferences = (body: DatingPreferencesUpdateRequest) =>
  api.patch<DatingPreferencesOut>('/profiles/me/preferences', body)
