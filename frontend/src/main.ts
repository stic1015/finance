import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './AppShell.vue'
import { router } from './router'
import './assets/styles.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.mount('#app')
