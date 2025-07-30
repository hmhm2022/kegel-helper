// Mock Tauri Global Shortcut API
export const register = async (shortcut: string, handler: () => void) => {
  console.log(`Mock register shortcut: ${shortcut}`)
  return Promise.resolve()
}

export const unregister = async (shortcut: string) => {
  console.log(`Mock unregister shortcut: ${shortcut}`)
  return Promise.resolve()
}
