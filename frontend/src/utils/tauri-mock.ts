/**
 * Tauri API Mock
 * 用于在浏览器环境中模拟Tauri API
 */

// Mock Tauri API
export const mockTauriApi = {
  invoke: async (command: string, args?: any) => {
    console.log(`Mock Tauri invoke: ${command}`, args)
    return Promise.resolve(true)
  },
  
  sendNotification: async (title: string, body: string) => {
    console.log(`Mock notification: ${title} - ${body}`)
    if ('Notification' in window) {
      if (Notification.permission === 'granted') {
        new Notification(title, { body })
      } else if (Notification.permission !== 'denied') {
        const permission = await Notification.requestPermission()
        if (permission === 'granted') {
          new Notification(title, { body })
        }
      }
    }
  },
  
  isPermissionGranted: async () => {
    return 'Notification' in window && Notification.permission === 'granted'
  },
  
  requestPermission: async () => {
    if ('Notification' in window) {
      return await Notification.requestPermission()
    }
    return 'denied'
  },
  
  register: async (shortcut: string, handler: () => void) => {
    console.log(`Mock register shortcut: ${shortcut}`)
    return Promise.resolve()
  },
  
  unregister: async (shortcut: string) => {
    console.log(`Mock unregister shortcut: ${shortcut}`)
    return Promise.resolve()
  },
  
  appWindow: {
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
}

// Mock OS API
export const mockOsApi = {
  platform: async () => 'web',
  version: async () => '1.0.0',
  type: async () => 'web',
  arch: async () => 'x64'
}

// Mock App API
export const mockAppApi = {
  getName: async () => '提肛小助手',
  getVersion: async () => '1.0.0'
}
