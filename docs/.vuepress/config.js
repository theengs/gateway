const commonConfig = require('./public/commonConfig');

module.exports = {
  ...commonConfig,
  title: 'Theengs Gateway: BLE to MQTT bridge',
  themeConfig: {
    repo: 'theengs/gateway',
    ...commonConfig.themeConfig,
    sidebar: [
      ['/','0 - What is it for 🏠'],
      {
        title: '1 - Prerequisites🧭',
        children: [
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
  }
}
