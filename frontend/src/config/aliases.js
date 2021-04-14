const aliases = (prefix = `src`) => ({
  '~services': `${prefix}/services`,
  '~components': `${prefix}/components`,
  '~styles': `${prefix}/styles`,
  '~contexts': `${prefix}/contexts`,
  '~static': `${prefix}/static`,
  '~utils': `${prefix}/utils`,
})

module.exports = aliases
