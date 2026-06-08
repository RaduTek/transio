import { Pn532 } from 'pn532.js'
import Pn532Hf14a from 'pn532.js/plugin/Hf14a.js'
import Pn532WebserialAdapter from 'pn532.js/plugin/WebserialAdapter.js'

type HexPacket = {
  hex?: string
  length?: number
}

type Hf14aTarget = {
  uid?: HexPacket
  atqa?: HexPacket
  sak?: HexPacket
}

export const PN532_WINDOW_EVENTS = {
  cardScanned: 'pn532:mifare-classic:scanned',
  cardRemoved: 'pn532:mifare-classic:removed',
} as const

export type Pn532CardScannedDetail = {
  uid: string
  atqa: string
  sak: string
  scannedAtIso: string
}

export type Pn532CardRemovedDetail = {
  uid: string
  removedAtIso: string
}

export type Pn532ScannerState = {
  isRunning: () => boolean
  isConnected: () => boolean
  requestConnection: () => Promise<void>
  disconnect: () => Promise<void>
}

declare global {
  interface WindowEventMap {
    'pn532:mifare-classic:scanned': CustomEvent<Pn532CardScannedDetail>
    'pn532:mifare-classic:removed': CustomEvent<Pn532CardRemovedDetail>
  }

  interface Window {
    pn532Scanner?: Pn532ScannerState
  }
}

const MIFARE_CLASSIC_SAK = new Set(['08', '09', '18', '88'])
const POLL_DELAY_MS = 250
const SCAN_TIMEOUT_MS = 550
const MISSED_READS_FOR_REMOVAL = 2

const delay = (ms: number) => new Promise<void>(resolve => {
  window.setTimeout(resolve, ms)
})

const normalizePacketHex = (value?: string) => (value ?? '').replace(/\s+/g, '').toUpperCase()

const isMifareClassicTarget = (target: Hf14aTarget | null | undefined): target is Hf14aTarget => {
  const sak = normalizePacketHex(target?.sak?.hex)
  if (!MIFARE_CLASSIC_SAK.has(sak)) return false

  const atqa = normalizePacketHex(target?.atqa?.hex)
  return atqa.length === 4
}

class Pn532MifareScannerService {
  private readonly pn532 = new Pn532()
  private running = false
  private removedAfterMisses = 0
  private activeCardUid: string | null = null

  constructor () {
    void this.pn532.use(new Pn532WebserialAdapter())
    void this.pn532.use(new Pn532Hf14a())
  }

  start () {
    if (this.running) return
    this.running = true
    void this.scanLoop()
    console.log('PN532 Mifare Classic scanner started')
  }

  stop () {
    this.running = false
    this.removedAfterMisses = 0
    this.activeCardUid = null
  }

  isRunning () {
    return this.running
  }

  isConnected () {
    return this.pn532.$adapter?.isOpen?.() ?? false
  }

  async requestConnection () {
    if (!this.pn532.$adapter?.connect) return
    if (this.isConnected()) return
    await this.pn532.$adapter.connect()
    await this.pn532.getFirmwareVersion()
  }

  async disconnect () {
    await this.pn532.$adapter?.disconnect?.()
  }

  private dispatchCardScanned (detail: Pn532CardScannedDetail) {
    window.dispatchEvent(new CustomEvent(PN532_WINDOW_EVENTS.cardScanned, { detail }))
  }

  private dispatchCardRemoved (detail: Pn532CardRemovedDetail) {
    window.dispatchEvent(new CustomEvent(PN532_WINDOW_EVENTS.cardRemoved, { detail }))
  }

  private trackNoCardSeen () {
    if (!this.activeCardUid) return

    this.removedAfterMisses += 1
    if (this.removedAfterMisses < MISSED_READS_FOR_REMOVAL) return

    const removedUid = this.activeCardUid
    this.activeCardUid = null
    this.removedAfterMisses = 0
    this.dispatchCardRemoved({
      uid: removedUid,
      removedAtIso: new Date().toISOString(),
    })
  }

  private trackCardSeen (target: Hf14aTarget) {
    const uid = normalizePacketHex(target.uid?.hex)
    if (!uid) return

    this.removedAfterMisses = 0
    if (this.activeCardUid === uid) return

    this.activeCardUid = uid
    this.dispatchCardScanned({
      uid,
      atqa: normalizePacketHex(target.atqa?.hex),
      sak: normalizePacketHex(target.sak?.hex),
      scannedAtIso: new Date().toISOString(),
    })
  }

  private async scanLoop () {
    while (this.running) {
      if (!this.isConnected()) {
        await delay(POLL_DELAY_MS)
        continue
      }

      try {
        const target = await this.pn532.$hf14a?.mfSelectCard({ timeout: SCAN_TIMEOUT_MS }) as Hf14aTarget | null | undefined
        if (isMifareClassicTarget(target)) {
          this.trackCardSeen(target)
        } else {
          this.trackNoCardSeen()
        }
      } catch {
        this.trackNoCardSeen()
      }

      await delay(POLL_DELAY_MS)
    }
  }
}

export const pn532MifareScannerService = new Pn532MifareScannerService()
