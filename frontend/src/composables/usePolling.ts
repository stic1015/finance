import { onBeforeUnmount } from 'vue'

export function usePolling(callback: () => Promise<void> | void, intervalMs = 5000) {
  const timer = window.setInterval(() => {
    void callback()
  }, intervalMs)

  onBeforeUnmount(() => {
    window.clearInterval(timer)
  })

  return timer
}
