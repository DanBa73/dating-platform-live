import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  base: '/static/', // Pfad für Assets anpassen, damit sie mit Django's STATIC_URL übereinstimmen
  plugins: [react()],
})
