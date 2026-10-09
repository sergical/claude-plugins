export type Mode = 'on' | 'main' | 'off'

declare module 'claude-code' {
  interface PluginState {
    handoffs: { mode: Mode }
  }
}
