// Mock Tauri Notification API
export const sendNotification = async (title: string, body: string) => {
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
}

export const isPermissionGranted = async () => {
  return 'Notification' in window && Notification.permission === 'granted'
}

export const requestPermission = async () => {
  if ('Notification' in window) {
    return await Notification.requestPermission()
  }
  return 'denied'
}
