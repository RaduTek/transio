declare module 'pn532.js' {
  export class Pn532 {
    use: (plugin: unknown, option?: object) => Promise<void>
    getFirmwareVersion: () => Promise<unknown>
    $adapter?: {
      connect?: () => Promise<void>
      disconnect?: () => Promise<void>
      isOpen?: () => boolean
    }
    $hf14a?: {
      mfSelectCard: (args?: { timeout?: number }) => Promise<unknown>
    }
  }
}

declare module 'pn532.js/plugin/Hf14a.js' {
  const Pn532Hf14a: new () => unknown
  export default Pn532Hf14a
}

declare module 'pn532.js/plugin/WebserialAdapter.js' {
  const Pn532WebserialAdapter: new () => unknown
  export default Pn532WebserialAdapter
}
