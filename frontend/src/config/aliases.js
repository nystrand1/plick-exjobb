const aliases = (prefix = `src`) => ({
    '~services': `${prefix}/services`,
    '~components': `${prefix}/components`,
    '~styles': `${prefix}/styles`
  });
  
  module.exports = aliases;