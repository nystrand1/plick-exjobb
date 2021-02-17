const aliases = (prefix = `src`) => ({
    '~services': `${prefix}/services`,
    '~components': `${prefix}/components`,
    '~styles': `${prefix}/styles`,
    '~contexts': `${prefix}/contexts`,
  });
  
  module.exports = aliases;