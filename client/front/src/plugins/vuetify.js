import { createVuetify } from 'vuetify'
import { aliases, mdi } from 'vuetify/iconsets/mdi'
import '@fortawesome/fontawesome-free/css/all.css'
import { aliases, fa } from 'vuetify/iconsets/fa'


export default createVuetify({
  ssr: true,
  icons: {
    defaultSet: 'fa',
    aliases,
    sets: {
      fa,
      mdi
    },
  },
})
