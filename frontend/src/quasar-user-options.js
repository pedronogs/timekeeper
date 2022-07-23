import './styles/quasar.sass'
import '@quasar/extras/roboto-font/roboto-font.css'
import '@quasar/extras/material-icons/material-icons.css'
import '@quasar/extras/fontawesome-v5/fontawesome-v5.css'
import { Notify } from 'quasar'

Notify.setDefaults({
  position: 'top-right',
  timeout: 1500
})

export default {
  config: {},
  plugins: {
    Notify
  }
}
