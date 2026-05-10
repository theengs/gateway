import { defineConfig } from 'vitepress'
import { resolve, dirname } from 'path'
import { fileURLToPath } from 'url'
import { commonNav, commonHead } from './commonConfig.mts'

const __dirname = dirname(fileURLToPath(import.meta.url))

export default defineConfig({
  title: 'Theengs Gateway: BLE to MQTT bridge',
  description: 'Theengs Gateway is a multi-platform BLE to MQTT bridge built on the Theengs Decoder library.',
  base: '/',
  outDir: resolve(__dirname, '../../generated/site'),
  head: commonHead,
  ignoreDeadLinks: [/localhost/],
  lastUpdated: true,
  markdown: { lineNumbers: true },
  themeConfig: {
    siteTitle: 'Theengs Gateway',
    nav: commonNav,
    socialLinks: [
      { icon: 'github', link: 'https://github.com/theengs/gateway' }
    ],
    editLink: {
      pattern: 'https://github.com/theengs/gateway/edit/development/docs/:path'
    },
    sidebar: [
      { text: '0 - What is it for 🏠', link: '/' },
      {
        text: '1 - Prerequisites 🧭',
        collapsed: true,
        items: [
          { text: 'Hardware', link: '/prerequisites/hardware' },
          { text: 'Broker', link: '/prerequisites/broker' },
          { text: 'Controller', link: '/prerequisites/controller' }
        ]
      },
      { text: '2 - Install ✔️', link: '/install/install' },
      { text: '3 - Use ✈️', link: '/use/use' },
      {
        text: '4 - Participate 💻',
        collapsed: true,
        items: [
          { text: 'Adding decoders', link: '/participate/adding-decoders' },
          { text: 'Supporting the project', link: '/participate/support' },
          { text: 'Development contributions', link: '/participate/development' }
        ]
      }
    ],
    search: { provider: 'local' }
  },
  sitemap: { hostname: 'https://gateway.theengs.io' },
  vite: { publicDir: '.vitepress/public' }
})
