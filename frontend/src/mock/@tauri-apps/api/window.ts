// Mock Tauri Window API
export const appWindow = {
  hide: async () => {
    console.log('Mock hide window')
    return Promise.resolve()
  },
  show: async () => {
    console.log('Mock show window')
    return Promise.resolve()
  },
  setFocus: async () => {
    console.log('Mock set focus')
    return Promise.resolve()
  },
  minimize: async () => {
    console.log('Mock minimize window')
    return Promise.resolve()
  },
  toggleMaximize: async () => {
    console.log('Mock toggle maximize')
    return Promise.resolve()
  },
  close: async () => {
    console.log('Mock close window')
    return Promise.resolve()
  }
}
