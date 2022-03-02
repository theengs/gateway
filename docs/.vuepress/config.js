module.exports = {
    markdown: {
      lineNumbers: true
    },
    title: 'Theengs gateway',
    description: 'Multi platform MQTT gateway leveraging Theengs Decoder',
    base:"/gateway/",
    head: [
      ['link', { rel: "apple-touch-icon", sizes: "180x180", href: ".apple-touch-icon.png"}],
      ['link', { rel: "icon", type: "image/png", sizes: "32x32", href: "/favicon-32x32.png"}],
      ['link', { rel: "icon", type: "image/png", sizes: "16x16", href: "/favicon-16x16.png"}],
      ['link', { rel: 'manifest', href: '/manifest.json' }],
      ['meta', { name: 'theme-color', content: '#3eaf7c' }],
      ['meta', { name: 'apple-mobile-web-app-capable', content: 'yes' }],
      ['meta', { name: 'apple-mobile-web-app-status-bar-style', content: 'black' }],
      ['link', { rel: 'mask-icon', href: '/icons/safari-pinned-tab.svg', color: '#3eaf7c' }],
      ['meta', { name: 'msapplication-TileImage', content: '/favicon-144x144.png' }],
      ['meta', { name: 'msapplication-TileColor', content: '#000000' }]
    ],
    themeConfig: {
      smoothScroll: true,
      repo: 'theengs/gateway',
      docsDir: 'docs',
      docsBranch: 'development',
      lastUpdated: 'Last Updated',
      editLinks: true,
      nav: [
        { text: 'Gateway', link: 'https://theengs.github.io/gateway'},
        { text: 'Decoder', link: 'https://theengs.github.io/decoder'}
      ],
      sidebar: [
        ['/','0 - What is it for 🏠'],
        {
          title: '1 - Prerequisites🧭',
          children: [
            'prerequisites/devices',
            'prerequisites/hardware',
            'prerequisites/broker',
            'prerequisites/controller']
        },
        ['/install/install','2 - Install ✔️'],
        ['/use/use','3 - Use ✈️'],
        {
          title: '4 - Participate 💻',
          children: [
            'participate/adding-decoders',
            'participate/support',
            'participate/development'
          ]
        }
    ]
    },
    plugins: [
      ['@vuepress/pwa', {
        serviceWorker: true,
        updatePopup: true
      }],
      ['@vuepress/medium-zoom', true],
      ['@vuepress/nprogress']
    ]
  }
