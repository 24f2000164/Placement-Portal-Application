import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'

const app = createApp(App)

app.use(store)   // MUST come before router
app.use(router)

app.mount('#app')