import Vue from 'vue'
import App from './App.vue'
import router from './router'
import VTooltipPlugin from 'v-tooltip'
import VModalPlugin from 'vue-js-modal'

Vue.config.productionTip = false

Vue.use(VTooltipPlugin)
Vue.use(VModalPlugin, {
    dynamic: true,
    dynamicDefaults: {
        clickToClose: true,
        transition: 'modal',
    },
    dialog: true,
})

new Vue({
  router,
  render: h => h(App)
}).$mount('#app')
