import { atom } from 'jotai'
import { atomWithStorage } from 'jotai/utils'
import type { DeviceIdentity } from './types'

export const sessionTokenAtom = atom('')

export const testModeAtom = atomWithStorage<boolean>('testMode', false)

export const identityAtom = atomWithStorage<DeviceIdentity | null>('identity', null)